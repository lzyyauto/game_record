#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys

import requests
from bs4 import BeautifulSoup


def translate_to_english(game_name, api_key=None, api_base=None, model=None):
    """
    使用LLM API查找游戏的英文名称（通过搜索而非简单翻译）
    
    支持多种LLM服务，包括OpenAI、Azure OpenAI和火山引擎等
    
    参数:
        game_name (str): 中文游戏名
        api_key (str, optional): API密钥，如果为None则从配置文件或环境变量获取
        api_base (str, optional): 自定义API URL，如果为None则从配置文件或使用默认URL
        model (str, optional): 使用的模型名称，如果为None则从配置文件或使用默认模型
    
    返回:
        str: 查找到的游戏英文名
    """
    import json
    import os

    import requests

    from config import load_config

    # 加载配置
    config = load_config()
    llm_config = config.get("llm", {})
    search_config = llm_config.get("search", {})

    # 获取LLM提供商
    provider = llm_config.get("provider", "openai").lower()

    # 设置API密钥
    if not api_key:
        api_key = search_config.get("api_key", "")
        if not api_key:
            # 尝试从环境变量获取
            if provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY", "")
            elif provider == "azure":
                api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
            elif provider == "huoshan":
                api_key = os.environ.get("HUOSHAN_API_KEY", "")

    if not api_key:
        print(f"错误: 未设置API密钥。请在配置文件中设置或通过环境变量提供。")
        return None

    # 设置API基础URL
    if not api_base:
        api_base = search_config.get("api_base", "")
        if not api_base:
            if provider == "huoshan":
                api_base = "https://ark.cn-beijing.volces.com/api/v3/bots/chat/completions"

    # 设置模型
    if not model:
        model = search_config.get("model", "")
        if not model:
            if provider == "openai":
                model = "gpt-3.5-turbo"
            elif provider == "azure":
                model = "gpt-35-turbo"
            elif provider == "huoshan":
                model = "bot-20250402210548-cns6x"

    # 设置温度和最大token数
    temperature = search_config.get("temperature", 0.3)
    max_tokens = search_config.get("max_tokens", 150)

    # 系统提示和用户提示
    system_prompt = "You are a video game expert. Your task is to find the official English name of video games. Use your knowledge and search capabilities to find the most accurate English title. If there are multiple possible English names, list the most likely ones in order of probability. If you're uncertain, indicate this clearly."
    user_prompt = f"请根据搜索结果找出游戏《{game_name}》的官方英文名称。不要简单翻译，而是查找真实的英文名称。如果有多个可能的结果，请列出最可能的几个。格式要求：1. 最可能的英文名称 2. 次可能的英文名称（如果有）"

    try:
        # 根据不同的提供商调用不同的API
        if provider == "openai":
            # OpenAI API调用
            try:
                import openai
                openai.api_key = api_key
                if api_base:
                    openai.api_base = api_base

                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{
                        "role": "system",
                        "content": system_prompt
                    }, {
                        "role": "user",
                        "content": user_prompt
                    }],
                    temperature=temperature,
                    max_tokens=max_tokens)

                result = response.choices[0].message.content.strip()
            except ImportError:
                print("错误: 未安装openai库。请运行: pip install openai")
                return None
            except Exception as e:
                print(f"OpenAI API调用出错: {e}")
                return None

        elif provider == "azure":
            # Azure OpenAI API调用
            try:
                import openai
                azure_config = llm_config.get("azure", {})
                api_version = azure_config.get("api_version", "2023-05-15")
                endpoint = azure_config.get("endpoint", "")

                if not endpoint and api_base:
                    endpoint = api_base

                if not endpoint:
                    print("错误: 未设置Azure OpenAI端点。")
                    return None

                openai.api_type = "azure"
                openai.api_key = api_key
                openai.api_base = endpoint
                openai.api_version = api_version

                response = openai.ChatCompletion.create(
                    deployment_id=model,
                    messages=[{
                        "role": "system",
                        "content": system_prompt
                    }, {
                        "role": "user",
                        "content": user_prompt
                    }],
                    temperature=temperature,
                    max_tokens=max_tokens)

                result = response.choices[0].message.content.strip()
            except ImportError:
                print("错误: 未安装openai库。请运行: pip install openai")
                return None
            except Exception as e:
                print(f"Azure OpenAI API调用出错: {e}")
                return None

        elif provider == "huoshan":
            # 火山引擎API调用
            if not api_base:
                print("错误: 未设置火山引擎API URL。")
                return None

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model":
                model,
                "messages": [{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": user_prompt
                }],
                "temperature":
                temperature,
                "max_tokens":
                max_tokens
            }

            response = requests.post(api_base, headers=headers, json=payload)

            # 检查响应状态
            if response.status_code != 200:
                print(f"火山引擎API调用失败: HTTP {response.status_code}")
                return None

            # 解析响应
            try:
                response_data = response.json()

                # 提取结果（根据火山引擎API的响应格式调整）
                if "choices" in response_data and len(
                        response_data["choices"]) > 0:
                    if "message" in response_data["choices"][0]:
                        result = response_data["choices"][0]["message"][
                            "content"].strip()
                    else:
                        print("错误: 响应格式不符合预期")
                        return None
                else:
                    print("错误: 响应中没有choices字段")
                    return None
            except json.JSONDecodeError:
                print(f"错误: 无法解析API响应为JSON")
                return None
            except Exception as e:
                print(f"处理火山引擎API响应时出错: {e}")
                return None
        else:
            print(f"错误: 不支持的LLM提供商: {provider}")
            return None

        # 处理结果，提取第一个（最可能的）英文名称
        lines = result.split('\n')
        english_name = None

        # 遍历所有行，查找格式为"1. 游戏名"的行
        for line in lines:
            line = line.strip()
            # 检查是否是编号格式（如"1. God of War: Ghost of Sparta"）
            if line.startswith('1. '):
                english_name = line[3:].strip()
                # 去除可能的星号或其他装饰字符
                english_name = english_name.replace('*',
                                                    '').replace('**',
                                                                '').strip()
                break

        # 如果没有找到编号格式，尝试其他方法提取
        if not english_name and lines:
            # 跳过可能的介绍性文本，查找实际的游戏名
            for line in lines:
                line = line.strip()
                # 避免选择介绍性文本
                if line and not line.startswith('根据') and not line.startswith(
                        '这是') and len(line) > 1:
                    english_name = line
                    break

        # 如果仍然没有找到，使用第一行非空文本
        if not english_name:
            for line in lines:
                if line.strip():
                    english_name = line.strip()
                    break

        if english_name:
            return english_name
        else:
            return result  # 返回完整结果

    except Exception as e:
        print(f"查找游戏英文名过程中出错: {e}")
        return None


def search_ign(game_name_en):
    """
    在IGN网站搜索游戏并返回可能的游戏列表
    使用IGN的GraphQL API进行搜索，返回所有可能的匹配结果
    """
    # GraphQL API URL
    api_url = "https://mollusk.apis.ign.com/graphql"

    # 构建GraphQL查询参数
    variables = {"term": game_name_en, "count": 20, "objectType": "Game"}

    # 查询参数
    params = {
        "operationName":
        "SearchObjectsByName",
        "variables":
        json.dumps(variables),
        "extensions":
        json.dumps({
            "persistedQuery": {
                "version":
                1,
                "sha256Hash":
                "e1c2e012a21b4a98aaa618ef1b43eb0cafe9136303274a34f5d9ea4f2446e884"
            }
        })
    }

    # 请求头
    headers = {
        "accept":
        "*/*",
        "accept-language":
        "zh-CN,zh;q=0.9",
        "apollographql-client-name":
        "kraken",
        "apollographql-client-version":
        "v0.90.0",
        "content-type":
        "application/json",
        "user-agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }

    try:
        # 发送GraphQL请求
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()

        # 解析JSON响应
        data = response.json()

        # 检查是否有搜索结果
        if "data" in data and "searchObjectsByName" in data[
                "data"] and "objects" in data["data"]["searchObjectsByName"]:
            objects = data["data"]["searchObjectsByName"]["objects"]

            if objects and len(objects) > 0:
                # 收集所有可能的游戏
                possible_games = []
                for obj in objects:
                    if "metadata" in obj and "names" in obj[
                            "metadata"] and "name" in obj["metadata"]["names"]:
                        result_name = obj["metadata"]["names"]["name"]
                        # 计算相似度分数
                        similarity_score = calculate_similarity(
                            game_name_en, result_name)

                        # 构建游戏详情页URL
                        game_url = f"https://www.ign.com{obj['url']}"

                        # 获取发售日期（如果有）
                        release_date = "未知"
                        if "objectRegions" in obj and len(
                                obj["objectRegions"]) > 0:
                            for region in obj["objectRegions"]:
                                if "releases" in region and len(
                                        region["releases"]) > 0:
                                    for release in region["releases"]:
                                        if "date" in release and release[
                                                "date"]:
                                            release_date = release["date"]
                                            break
                                if release_date != "未知":
                                    break

                        # 获取平台信息（如果有）
                        platforms = []
                        if "objectRegions" in obj and len(
                                obj["objectRegions"]) > 0:
                            for region in obj["objectRegions"]:
                                if "releases" in region and len(
                                        region["releases"]) > 0:
                                    for release in region["releases"]:
                                        if "platformAttributes" in release:
                                            for platform in release[
                                                    "platformAttributes"]:
                                                if "name" in platform and platform[
                                                        "name"] not in platforms:
                                                    platforms.append(
                                                        platform["name"])

                        possible_games.append({
                            "name": result_name,
                            "url": game_url,
                            "similarity": similarity_score,
                            "release_date": release_date,
                            "platforms": platforms
                        })

                # 按相似度排序
                possible_games.sort(key=lambda x: x["similarity"],
                                    reverse=True)

                # 如果找到多个可能的游戏，让用户选择
                if len(possible_games) > 1:
                    print("\n找到多个可能的游戏，请选择：")
                    for i, game in enumerate(possible_games, 1):
                        print(
                            f"{i}. {game['name']} (相似度: {game['similarity']:.2f})"
                        )
                        print(f"   发售日期: {game['release_date']}")
                        print(f"   平台: {', '.join(game['platforms'])}")
                        print(f"   URL: {game['url']}\n")

                    while True:
                        try:
                            choice = int(input("请输入选择的游戏编号: "))
                            if 1 <= choice <= len(possible_games):
                                return possible_games[choice - 1]["url"]
                            else:
                                print("无效的选择，请重新输入")
                        except ValueError:
                            print("请输入有效的数字")

                # 如果只有一个游戏，直接返回
                return possible_games[0]["url"]

        print(f"在IGN上未找到游戏 '{game_name_en}' 的详情页")
        return None

    except requests.RequestException as e:
        print(f"搜索IGN时出错: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"解析IGN API响应时出错: {e}")
        return None


def calculate_similarity(str1, str2):
    """
    计算两个字符串的相似度
    使用简单的方法，可以根据需要替换为更复杂的算法
    """
    # 转换为小写并去除特殊字符
    import re
    s1 = re.sub(r'[^\w\s]', '', str1.lower())
    s2 = re.sub(r'[^\w\s]', '', str2.lower())

    # 如果其中一个是另一个的子串，给予较高的分数
    if s1 in s2 or s2 in s1:
        return 0.8

    # 计算单词集合的交集比例
    words1 = set(s1.split())
    words2 = set(s2.split())

    if not words1 or not words2:
        return 0.0

    # 计算Jaccard相似度
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    return intersection / union if union > 0 else 0.0


def get_game_details(game_url):
    """
    从IGN游戏详情页获取信息
    使用GraphQL API获取详细信息，包括游戏封面图
    """
    if not game_url:
        return None

    # 从URL中提取游戏slug
    import re
    slug_match = re.search(r'/games/([^/]+)', game_url)
    if not slug_match:
        print(f"无法从URL中提取游戏ID: {game_url}")
        return None

    game_slug = slug_match.group(1)

    # GraphQL API URL
    api_url = "https://mollusk.apis.ign.com/graphql"

    # 构建GraphQL查询参数 - 使用游戏slug获取详细信息
    variables = {"slug": game_slug}

    # 查询参数 - 使用getObjectBySlug操作获取详细信息
    params = {
        "operationName":
        "GetObjectBySlug",
        "variables":
        json.dumps(variables),
        "extensions":
        json.dumps({
            "persistedQuery": {
                "version":
                1,
                "sha256Hash":
                "e8a0b931f1c950df2bac5f0291ed08fe7c5cbc519a73fd4a20dc61c4996d3b4f"
            }
        })
    }

    # 请求头
    headers = {
        "accept":
        "*/*",
        "accept-language":
        "zh-CN,zh;q=0.9",
        "apollographql-client-name":
        "kraken",
        "apollographql-client-version":
        "v0.90.0",
        "content-type":
        "application/json",
        "user-agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }

    try:
        # 首先尝试使用GraphQL API获取详细信息
        try:
            response = requests.get(api_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            # 如果API调用成功并返回了游戏数据，解析它
            if "data" in data and "getObjectBySlug" in data["data"] and data[
                    "data"]["getObjectBySlug"]:
                game_data = data["data"]["getObjectBySlug"]

                # 提取游戏信息
                game_details = {}

                # 获取游戏英文名
                if "metadata" in game_data and "names" in game_data["metadata"]:
                    game_details['english_name'] = game_data["metadata"][
                        "names"]["name"]

                # 获取封面图URL
                if "metadata" in game_data and "imageUrl" in game_data[
                        "metadata"]:
                    game_details['cover_image'] = game_data["metadata"][
                        "imageUrl"]
                elif "promoImages" in game_data and len(
                        game_data["promoImages"]) > 0:
                    for image in game_data["promoImages"]:
                        if "url" in image:
                            game_details['cover_image'] = image["url"]
                            break

                # 获取平台信息
                if "objectRegions" in game_data and len(
                        game_data["objectRegions"]) > 0:
                    platforms = []
                    for region in game_data["objectRegions"]:
                        if "releases" in region and len(
                                region["releases"]) > 0:
                            for release in region["releases"]:
                                if "platformAttributes" in release:
                                    for platform in release[
                                            "platformAttributes"]:
                                        if "name" in platform and platform[
                                                "name"] not in platforms:
                                            platforms.append(platform["name"])
                    game_details['platforms'] = platforms

                # 获取发售日期
                release_date = "未知"
                if "objectRegions" in game_data and len(
                        game_data["objectRegions"]) > 0:
                    for region in game_data["objectRegions"]:
                        if "releases" in region and len(
                                region["releases"]) > 0:
                            for release in region["releases"]:
                                if "date" in release and release["date"]:
                                    release_date = release["date"]
                                    break
                            if release_date != "未知":
                                break
                game_details['release_date'] = release_date

                # 获取评分
                if "reviewObject" in game_data and game_data[
                        "reviewObject"] and "score" in game_data[
                            "reviewObject"]:
                    game_details['score'] = str(
                        game_data["reviewObject"]["score"])
                else:
                    game_details['score'] = "未评分"

                # 添加详情页URL
                game_details['url'] = game_url

                return game_details
        except (requests.RequestException, KeyError,
                json.JSONDecodeError) as e:
            print(f"通过GraphQL API获取游戏详情时出错: {e}")
            # 如果API调用失败，回退到网页爬取方法
            print("尝试通过网页爬取获取游戏详情...")

        # 回退方法：通过网页爬取获取游戏详情
        response = requests.get(
            game_url,
            headers={
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取游戏信息
        game_details = {}

        # 获取游戏英文名
        title_element = soup.select_one('h1')
        if title_element:
            game_details['english_name'] = title_element.text.strip()
        else:
            # 尝试从title标签获取
            title_tag = soup.select_one('title')
            if title_tag:
                title_text = title_tag.text.strip()
                # 通常格式为"游戏名 - IGN"
                if " - IGN" in title_text:
                    game_details['english_name'] = title_text.replace(
                        " - IGN", "").strip()

        # 获取封面图URL
        # 尝试多种可能的选择器来获取封面图
        cover_image = None
        # 尝试获取主图片
        main_image = soup.select_one('meta[property="og:image"]')
        if main_image and main_image.get('content'):
            cover_image = main_image.get('content')

        # 如果没有找到，尝试其他选择器
        if not cover_image:
            image_element = soup.select_one('.article-header img')
            if image_element and image_element.get('src'):
                cover_image = image_element.get('src')

        # 如果仍然没有找到，尝试更多选择器
        if not cover_image:
            image_element = soup.select_one('.grid-image-container img')
            if image_element and image_element.get('src'):
                cover_image = image_element.get('src')

        if cover_image:
            game_details['cover_image'] = cover_image
        else:
            game_details['cover_image'] = "未找到封面图"

        # 获取平台信息 - 从meta标签中提取
        platforms = []
        keywords_meta = soup.select_one('meta[name="cXenseParse:keywords"]')
        if keywords_meta and keywords_meta.get('content'):
            # 格式通常为",游戏名,平台1,平台2,..."
            keywords = keywords_meta.get('content').split(',')
            # 第一个元素通常是空的，第二个是游戏名，之后的都是平台
            if len(keywords) > 2:
                platforms = [
                    platform.strip() for platform in keywords[2:]
                    if platform.strip()
                ]

        # 如果meta标签中没有找到，尝试其他选择器
        if not platforms:
            platforms_element = soup.select_one('div[data-testid="platforms"]')
            if platforms_element:
                platforms = [
                    platform.text.strip()
                    for platform in platforms_element.select('span')
                ]
            else:
                platform_elements = soup.select('.platformsText span')
                if platform_elements:
                    platforms = [p.text.strip() for p in platform_elements]

        game_details['platforms'] = platforms

        # 获取发售日期 - 尝试多种选择器和模式
        release_date = "未知"

        # 尝试查找包含"Release Date"的元素
        release_elements = soup.find_all(
            string=lambda text: text and "Release Date" in text)
        for element in release_elements:
            parent = element.parent
            if parent:
                # 查找相邻的日期文本
                next_sibling = parent.next_sibling
                if next_sibling and next_sibling.string and next_sibling.string.strip(
                ):
                    release_date = next_sibling.string.strip()
                    break
                # 或者查找父元素的下一个元素
                next_element = parent.find_next()
                if next_element and next_element.string and next_element.string.strip(
                ):
                    release_date = next_element.string.strip()
                    break

        # 如果上面的方法没有找到，尝试其他选择器
        if release_date == "未知":
            release_date_element = soup.select_one(
                'div[data-testid="release-date"]')
            if release_date_element:
                release_date = release_date_element.text.strip()
            else:
                release_date_div = soup.select_one('.releaseDate')
                if release_date_div:
                    release_date = release_date_div.text.strip()

        game_details['release_date'] = release_date

        # 获取评分 - 尝试多种选择器和模式
        score = "未评分"

        # 尝试查找包含评分的元素
        score_elements = soup.find_all(
            ['div', 'span'],
            class_=lambda c: c and
            ('score' in c.lower() or 'rating' in c.lower()))
        for element in score_elements:
            if element.text and element.text.strip() and element.text.strip(
            ).replace('.', '').isdigit():
                score = element.text.strip()
                break

        # 如果上面的方法没有找到，尝试其他选择器
        if score == "未评分":
            score_element = soup.select_one('span[data-testid="score"]')
            if score_element:
                score = score_element.text.strip()
            else:
                score_box = soup.select_one('.scoreBox-score')
                if score_box:
                    score = score_box.text.strip()

        game_details['score'] = score

        # 添加详情页URL
        game_details['url'] = game_url

        return game_details

    except requests.RequestException as e:
        print(f"获取游戏详情时出错: {e}")
        return None


def get_game_details_llm(game_url, api_key=None, api_base=None, model=None):
    """
    通过火山引擎API获取游戏详情
    使用Jina处理后的URL和火山引擎API来解析游戏信息
    """
    import json
    import os

    from config import load_config

    # 加载配置
    config = load_config()
    llm_config = config.get("llm", {})
    api_config = llm_config.get("api", {})

    # 获取API密钥
    if not api_key:
        api_key = api_config.get("api_key", "")
        if not api_key:
            api_key = os.environ.get("HUOSHAN_API_KEY", "")

    if not api_key:
        print("错误: 未设置火山引擎API密钥")
        return None

    # 设置API基础URL
    if not api_base:
        api_base = api_config.get("api_base", "")
        if not api_base:
            api_base = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    # 设置模型
    if not model:
        model = api_config.get("model", "")
        if not model:
            model = "ep-20250205181853-r9rxr"  # 使用不联网的模型

    # 设置温度和最大token数
    temperature = api_config.get("temperature", 0.3)
    max_tokens = api_config.get("max_tokens", 1000)

    # 构建Jina处理后的URL
    jina_url = f"https://r.jina.ai/{game_url}"

    try:
        # 获取Jina处理后的页面内容
        print(f"\n正在获取Jina处理后的页面内容: {jina_url}")
        response = requests.get(jina_url)
        response.raise_for_status()
        page_content = response.text
        print(f"获取到的页面内容长度: {len(page_content)}")

        # 构建系统提示
        system_prompt = """你是一个专业的游戏信息提取助手。请从以下网页内容中提取游戏信息，并以JSON格式返回。
需要提取的信息包括：
1. 游戏英文名 (english_name)
2. 游戏封面图URL (cover_image).不需要url上多余的参数.
3. 游戏平台 (platforms)
4. 发售日期 (release_date).返回格式2025-04-10
5. 评分 (score)
6. 游戏详情页URL (url)

请确保提取的信息准确无误。如果某些信息无法找到，请使用"未知"或"未评分"等默认值。"""

        # 构建用户提示
        user_prompt = f"请从以下网页内容中提取游戏信息：\n\n{page_content}"

        # 调用火山引擎API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model":
            model,
            "messages": [{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": user_prompt
            }],
            "temperature":
            temperature,
            "max_tokens":
            max_tokens
        }

        response = requests.post(api_base, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()

        # 解析API响应
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]

            try:
                # 清理Markdown标记
                if content.startswith('```json'):
                    content = content[7:]  # 移除 ```json
                if content.endswith('```'):
                    content = content[:-3]  # 移除结尾的 ```
                content = content.strip()

                # 尝试解析JSON
                game_details = json.loads(content)
                # 确保所有必要字段都存在
                required_fields = [
                    'english_name', 'cover_image', 'platforms', 'release_date',
                    'score', 'url'
                ]
                for field in required_fields:
                    if field not in game_details:
                        game_details[
                            field] = "未知" if field != 'score' else "未评分"
                return game_details
            except json.JSONDecodeError as e:
                print(f"\nJSON解析错误: {e}")
                print(f"原始内容: {content}")
                return None
        else:
            print("\n错误: API返回的响应格式不正确")
            print(f"完整响应: {result}")
            return None

    except Exception as e:
        print(f"\n通过火山引擎API获取游戏详情时出错: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return None


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='获取游戏信息并输出JSON')
    parser.add_argument('game_name', help='中文游戏名')
    parser.add_argument('--debug', action='store_true', help='启用调试输出')
    parser.add_argument('--method',
                        choices=['original', 'llm'],
                        default='original',
                        help='选择获取游戏详情的方法: original(原始方法) 或 llm(使用火山引擎API)')
    args = parser.parse_args()

    # 获取中文游戏名
    game_name_zh = args.game_name

    # 翻译成英文
    print(f"查找游戏 '{game_name_zh}' 的信息...")
    game_name_en = translate_to_english(game_name_zh)
    if not game_name_en:
        print("无法将游戏名翻译为英文")
        sys.exit(1)
    print(f"游戏英文名: {game_name_en}")

    # 在IGN搜索游戏
    print("在IGN搜索游戏信息...")
    game_url = search_ign(game_name_en)
    if not game_url:
        print("在IGN上未找到游戏信息")
        sys.exit(1)

    # 获取游戏详情
    print("获取游戏详细信息...")
    if args.method == 'llm':
        game_details = get_game_details_llm(game_url)
    else:
        game_details = get_game_details(game_url)

    if not game_details:
        print("无法获取游戏详情")
        sys.exit(1)

    # 添加原始中文名和翻译后的英文名
    game_details['chinese_name'] = game_name_zh
    game_details['translated_name'] = game_name_en

    # 输出JSON
    print(json.dumps(game_details, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
