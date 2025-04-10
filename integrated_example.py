#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
这是一个集成了OpenAI翻译功能的完整示例脚本
用户可以直接使用此脚本，只需添加自己的OpenAI API密钥
"""

import argparse
import json
import requests
import os
import sys
from bs4 import BeautifulSoup

# 检查是否安装了openai库
try:
    import openai
except ImportError:
    print("请先安装OpenAI库: pip install openai")
    sys.exit(1)


def translate_to_english(game_name, api_key=None, api_base=None, model=None):
    """
    使用LLM API查找游戏的英文名称（通过搜索而非简单翻译）
    
    参数:
        game_name (str): 中文游戏名
        api_key (str, optional): API密钥，如果为None则从环境变量获取
        api_base (str, optional): 自定义API URL，如果为None则使用默认URL
        model (str, optional): 使用的模型名称，如果为None则使用默认模型
        
    返回:
        str: 查找到的游戏英文名
    """
    print(f"正在查找游戏 '{game_name}' 的英文名称...")
    
    # 设置API密钥
    if api_key:
        openai.api_key = api_key
    else:
        # 从环境变量获取API密钥
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            print("错误: 未设置API密钥。请设置OPENAI_API_KEY环境变量或通过参数提供。")
            return None
    
    # 设置自定义API URL（如果提供）
    if api_base:
        openai.api_base = api_base
    
    # 设置模型（如果未提供则使用默认值）
    if model is None:
        model = "gpt-3.5-turbo"
    
    try:
        # 使用LLM API查找游戏英文名
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a video game expert. Your task is to find the official English name of video games. Use your knowledge and search capabilities to find the most accurate English title. If there are multiple possible English names, list the most likely ones in order of probability. If you're uncertain, indicate this clearly."},
                {"role": "user", "content": f"请根据搜索结果找出游戏《{game_name}》的官方英文名称。不要简单翻译，而是查找真实的英文名称。如果有多个可能的结果，请列出最可能的几个。格式要求：1. 最可能的英文名称 2. 次可能的英文名称（如果有）"}
            ],
            temperature=0.3,  # 降低温度以获得更确定的回答
            max_tokens=150    # 增加输出长度以容纳多个可能的结果
        )
        
        # 提取查找结果
        result = response.choices[0].message.content.strip()
        
        # 处理结果，提取第一个（最可能的）英文名称
        lines = result.split('\n')
        if lines and lines[0]:
            # 如果结果是编号列表，提取第一个结果并去除编号
            if lines[0].startswith('1. '):
                english_name = lines[0][3:].strip()
            else:
                english_name = lines[0].strip()
            print(f"查找结果: '{english_name}'")
            return english_name
        else:
            print(f"查找结果: '{result}'")
            return result  # 返回完整结果
        
    except Exception as e:
        print(f"查找游戏英文名过程中出错: {e}")
        return None


def search_ign(game_name_en):
    """
    在IGN网站搜索游戏并返回详情页URL
    """
    print(f"正在IGN网站搜索游戏: '{game_name_en}'...")
    search_url = f"https://www.ign.com/search?q={requests.utils.quote(game_name_en)}"
    
    try:
        response = requests.get(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找搜索结果中的第一个游戏链接
        # 注意：IGN网站的HTML结构可能会变化，可能需要根据实际情况调整选择器
        game_link = soup.select_one('a[href*="/games/"]')
        
        if game_link:
            game_url = 'https://www.ign.com' + game_link['href'] if not game_link['href'].startswith('http') else game_link['href']
            print(f"找到游戏页面: {game_url}")
            return game_url
        else:
            print(f"在IGN上未找到游戏 '{game_name_en}' 的详情页")
            return None
            
    except requests.RequestException as e:
        print(f"搜索IGN时出错: {e}")
        return None


def get_game_details(game_url):
    """
    从IGN游戏详情页获取信息
    """
    if not game_url:
        return None
        
    print(f"正在获取游戏详情: {game_url}")
    
    try:
        response = requests.get(game_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取游戏信息
        # 注意：IGN网站的HTML结构可能会变化，可能需要根据实际情况调整选择器
        game_details = {}
        
        # 获取游戏英文名
        title_element = soup.select_one('h1')
        if title_element:
            game_details['english_name'] = title_element.text.strip()
        
        # 获取平台信息
        # 首先尝试从meta标签中获取平台信息
        platforms_meta = soup.select_one('meta[name="cXenseParse:keywords"]')
        if platforms_meta and platforms_meta.get('content'):
            # 格式通常是 ",It Takes Two,Nintendo Switch,PlayStation 4,Xbox Series X|S,PC,PlayStation 5,Xbox One"
            platforms_content = platforms_meta.get('content').strip(',')
            platforms_list = platforms_content.split(',')
            # 第一个元素是游戏名，移除它
            if len(platforms_list) > 1:
                platforms = platforms_list[1:]
            else:
                platforms = []
            game_details['platforms'] = platforms
        else:
            # 如果meta标签中没有，尝试其他选择器
            platforms_element = soup.select_one('div[data-testid="platforms"]')
            if platforms_element:
                game_details['platforms'] = [platform.text.strip() for platform in platforms_element.select('span')]
            else:
                platforms = []
                platform_elements = soup.select('.platformsText span')
                if platform_elements:
                    platforms = [p.text.strip() for p in platform_elements]
                game_details['platforms'] = platforms
        
        # 获取发售日期
        # 使用多种选择器尝试提取发售日期
        release_date_found = False
        
        # 调试输出
        print("正在尝试提取发售日期...")
        
        # 尝试方法1: 查找带有data-cy="release-date"属性的time元素
        release_date_element = soup.select_one('time[data-cy="release-date"]')
        if release_date_element:
            release_date = release_date_element.text.strip()
            game_details['release_date'] = release_date
            release_date_found = True
            print(f"从time[data-cy]找到发售日期: {release_date}")
        
        # 尝试方法2: 查找特定的data-testid属性
        if not release_date_found:
            release_date_element = soup.select_one('div[data-testid="release-date"]')
            if release_date_element:
                release_date = release_date_element.text.strip()
                game_details['release_date'] = release_date
                release_date_found = True
                print(f"从data-testid找到发售日期: {release_date}")
        
        # 如果上面的方法失败，尝试查找特定class的time元素
        if not release_date_found:
            time_element = soup.select_one('time.interface.bold.small[data-cy="release-date"]')
            if time_element:
                release_date = time_element.text.strip()
                game_details['release_date'] = release_date
                release_date_found = True
                print(f"从time元素找到发售日期: {release_date}")
        
        # 尝试方法2: 查找包含"Release Date"文本的元素
        if not release_date_found:
            # 查找所有可能包含发售日期的元素
            date_elements = soup.find_all(['div', 'span', 'p'], string=lambda text: text and 'Release Date' in text)
            for element in date_elements:
                # 获取父元素或相邻元素中的日期信息
                parent = element.parent
                date_text = parent.text.strip()
                if 'Release Date' in date_text and len(date_text) > 12:  # 确保文本长度足够包含日期
                    # 提取日期部分 (通常在"Release Date:"之后)
                    try:
                        date_part = date_text.split('Release Date:')[1].strip()
                        game_details['release_date'] = date_part
                        release_date_found = True
                        print(f"从文本中找到发售日期: {date_part}")
                        break
                    except IndexError:
                        continue
        
        # 尝试方法3: 查找特定的CSS类
        if not release_date_found:
            release_date = soup.select_one('.releaseDate, .release-date, .date')
            if release_date:
                date_text = release_date.text.strip()
                game_details['release_date'] = date_text
                release_date_found = True
                print(f"从CSS类找到发售日期: {date_text}")
        
        # 尝试方法4: 查找包含日期格式的文本
        if not release_date_found:
            import re
            # 查找常见的日期格式 (如 March 26, 2021 或 2021-03-26)
            date_pattern = re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}\b|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b')
            for element in soup.find_all(['div', 'span', 'p']):
                if element.string:
                    match = date_pattern.search(element.string)
                    if match:
                        date_text = match.group(0)
                        game_details['release_date'] = date_text
                        release_date_found = True
                        print(f"从日期格式找到发售日期: {date_text}")
                        break
        
        # 如果所有方法都失败，设置为未知
        if not release_date_found:
            # 最后尝试从meta描述中提取
            description_meta = soup.select_one('meta[name="description"]')
            if description_meta and description_meta.get('content'):
                description = description_meta.get('content')
                if 'Release Date' in description:
                    # 由于描述通常只包含"Release Date"字样而不包含具体日期
                    # 我们设置一个更明确的消息
                    game_details['release_date'] = "需要从页面内容中提取"
                    print("在meta描述中找到'Release Date'字样，但无具体日期")
                else:
                    game_details['release_date'] = "未知"
                    print("未在meta描述中找到发售日期信息")
            else:
                game_details['release_date'] = "未知"
                print("未找到任何发售日期信息")
        
        # 获取评分
        # 尝试多种可能的选择器来获取评分
        score_found = False
        
        # 尝试data-testid属性
        score_element = soup.select_one('span[data-testid="score"]')
        if score_element:
            game_details['score'] = score_element.text.strip()
            score_found = True
        
        # 尝试scoreBox-score类
        if not score_found:
            score = soup.select_one('.scoreBox-score')
            if score:
                game_details['score'] = score.text.strip()
                score_found = True
        
        # 尝试查找包含评分的其他元素
        if not score_found:
            # 尝试查找可能包含评分的div元素
            score_divs = soup.select('div.score, div.rating, div[class*="score"], div[class*="rating"]')
            for div in score_divs:
                if div.text and any(c.isdigit() for c in div.text):
                    game_details['score'] = div.text.strip()
                    score_found = True
                    break
        
        # 如果所有方法都失败，设置为未评分
        if not score_found:
            game_details['score'] = "未评分"
        
        # 添加详情页URL
        game_details['url'] = game_url
        
        return game_details
        
    except requests.RequestException as e:
        print(f"获取游戏详情时出错: {e}")
        return None


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='游戏信息查询工具')
    parser.add_argument('game_name', help='中文游戏名')
    parser.add_argument('--api-key', help='API密钥（如未提供则从环境变量获取）')
    parser.add_argument('--api-base', help='自定义API URL（如未提供则使用默认URL）')
    parser.add_argument('--model', help='使用的模型名称（如未提供则使用默认模型）')
    parser.add_argument('--config', help='配置文件路径')
    args = parser.parse_args()
    
    # 获取中文游戏名
    game_name_zh = args.game_name
    
    # 查找游戏英文名
    game_name_en = translate_to_english(game_name_zh, args.api_key, args.api_base, args.model)
    if not game_name_en:
        print("无法查找游戏的英文名称")
        sys.exit(1)
    
    # 在IGN搜索游戏
    game_url = search_ign(game_name_en)
    if not game_url:
        print("在IGN上未找到游戏信息")
        sys.exit(1)
    
    # 获取游戏详情
    game_details = get_game_details(game_url)
    if not game_details:
        print("无法获取游戏详情")
        sys.exit(1)
    
    # 添加原始中文名和翻译后的英文名
    game_details['chinese_name'] = game_name_zh
    game_details['translated_name'] = game_name_en
    
    # 输出JSON
    print("\n游戏信息:")
    print(json.dumps(game_details, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()