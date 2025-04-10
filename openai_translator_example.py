#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
这是一个使用OpenAI API实现游戏名称翻译的示例脚本
可以将此代码集成到主脚本中，或者根据需要修改为使用其他LLM服务
"""

import os
import sys
import argparse

# 检查是否安装了openai库
try:
    import openai
except ImportError:
    print("请先安装OpenAI库: pip install openai")
    sys.exit(1)


def translate_game_name(game_name_zh, api_key=None, api_base=None, model="gpt-3.5-turbo"):
    """
    使用LLM API查找游戏的英文名称（通过搜索而非简单翻译）
    
    参数:
        game_name_zh (str): 中文游戏名
        api_key (str, optional): API密钥，如果为None则从环境变量获取
        api_base (str, optional): 自定义API URL，如果为None则使用默认URL
        model (str, optional): 使用的模型名称
        
    返回:
        str: 查找到的游戏英文名
    """
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
    
    try:
        # 使用LLM API查找游戏英文名
        # 注意: 根据API的版本，可能需要调整此代码
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a video game expert. Your task is to find the official English name of video games. Use your knowledge and search capabilities to find the most accurate English title. If there are multiple possible English names, list the most likely ones in order of probability. If you're uncertain, indicate this clearly."}, 
                {"role": "user", "content": f"请根据搜索结果找出游戏《{game_name_zh}》的官方英文名称。不要简单翻译，而是查找真实的英文名称。如果有多个可能的结果，请列出最可能的几个。格式要求：1. 最可能的英文名称 2. 次可能的英文名称（如果有）"}
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
            return english_name
        else:
            return result  # 返回完整结果
        
    except Exception as e:
        print(f"查找游戏英文名过程中出错: {e}")
        return None


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='使用LLM API查找游戏的英文名称')
    parser.add_argument('game_name', help='中文游戏名')
    parser.add_argument('--api-key', help='API密钥（如未提供则从环境变量获取）')
    parser.add_argument('--api-base', help='自定义API URL（如未提供则使用默认URL）')
    parser.add_argument('--model', default='deepseek-v3', help='使用的模型名称（默认：deepseek-v3）')
    args = parser.parse_args()
    
    # 查找游戏英文名
    english_name = translate_game_name(args.game_name, args.api_key, args.api_base, args.model)
    
    if english_name:
        print(f"中文名: {args.game_name}")
        print(f"英文名: {english_name}")
    else:
        print("查找游戏英文名失败")
        sys.exit(1)


if __name__ == '__main__':
    main()