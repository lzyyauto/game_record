#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏信息查询工具的配置文件
包含LLM API配置和其他设置
"""

import json
import os
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    # LLM配置
    "llm": {
        "provider": "openai",  # 可选: openai, azure, 等
        # 搜索相关配置
        "search": {
            "api_key": "",  # API密钥
            "api_base": "",  # 自定义API URL
            "model": "gpt-3.5-turbo",  # 使用的模型
            "temperature": 0.3,  # 温度参数
            "max_tokens": 150,  # 最大输出token数
        },
        # API相关配置
        "api": {
            "api_key": "",  # API密钥
            "api_base": "",  # 自定义API URL
            "model": "gpt-3.5-turbo",  # 使用的模型
            "temperature": 0.3,  # 温度参数
            "max_tokens": 1000,  # 最大输出token数
        },
        # Azure OpenAI特定配置
        "azure": {
            "api_version": "2023-05-15",
            "endpoint": ""
        }
    },

    # 搜索配置
    "search": {
        "max_results": 5  # 最大搜索结果数
    },

    # 用户界面配置
    "ui": {
        "language": "zh-CN"  # 界面语言
    }
}


def load_config(config_path=None):
    """
    加载配置文件
    
    参数:
        config_path (str, optional): 配置文件路径，如果为None则使用默认路径
        
    返回:
        dict: 配置字典
    """
    # 如果未指定配置文件路径，则使用默认路径
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "config.json")

    config = DEFAULT_CONFIG.copy()

    # 尝试从配置文件加载
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 递归更新配置
                deep_update(config, user_config)
    except Exception as e:
        print(f"警告: 加载配置文件时出错: {e}")
        print(f"使用默认配置继续运行")

    # 尝试从环境变量加载API密钥
    if not config["llm"]["search"]["api_key"]:
        if config["llm"]["provider"].lower() == "openai":
            config["llm"]["search"]["api_key"] = os.environ.get(
                "OPENAI_API_KEY", "")
        elif config["llm"]["provider"].lower() == "azure":
            config["llm"]["search"]["api_key"] = os.environ.get(
                "AZURE_OPENAI_API_KEY", "")

    return config


def save_config(config, config_path=None):
    """
    保存配置到文件
    
    参数:
        config (dict): 配置字典
        config_path (str, optional): 配置文件路径，如果为None则使用默认路径
    """
    # 如果未指定配置文件路径，则使用默认路径
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "config.json")

    # 确保目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def deep_update(d, u):
    """
    递归更新嵌套字典
    
    参数:
        d (dict): 要更新的字典
        u (dict): 包含更新的字典
        
    返回:
        dict: 更新后的字典
    """
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            deep_update(d[k], v)
        else:
            d[k] = v
    return d


# 创建默认配置文件（如果不存在）
def create_default_config():
    """
    创建默认配置文件（如果不存在）
    """
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "config.json")
    if not os.path.exists(default_path):
        save_config(DEFAULT_CONFIG, default_path)
        print(f"已创建默认配置文件: {default_path}")
        print("请编辑此文件以设置您的API密钥和其他选项")


# 当作为脚本运行时，创建默认配置文件
if __name__ == '__main__':
    create_default_config()
