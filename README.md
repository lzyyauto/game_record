# 游戏信息查询工具

这是一个命令行工具，用于查询游戏信息。它接收中文游戏名作为输入，将其翻译成英文，然后从IGN网站获取游戏详情，并以JSON格式输出结果。

## 功能

- 将中文游戏名翻译成英文（通过火山引擎API）
- 使用英文名在IGN网站搜索游戏，支持多作品选择
- 获取游戏的详细信息：英文名、平台、发售时间、评分和详情页URL
- 支持两种获取详情的方式：原始网页解析和LLM解析
- 以JSON格式输出结果

## 安装依赖

```bash
pip install requests beautifulsoup4
```

## 配置

在运行前，需要创建 `config.json` 文件，配置火山引擎API的相关信息：

```json
{
  "llm": {
    "provider": "huoshan",
    "search": {
      "api_key": "your_search_api_key",
      "api_base": "your_search_api_base",
      "model": "your_search_model"
    },
    "api": {
      "api_key": "your_api_key",
      "api_base": "your_api_base",
      "model": "your_api_model"
    }
  }
}
```

## 使用方法

```bash
python game_record.py "游戏名称" [--method {original,llm}]
```

参数说明：
- `游戏名称`：要查询的中文游戏名
- `--method`：选择获取游戏详情的方法（可选）
  - `original`：使用原始网页解析方法（默认）
  - `llm`：使用火山引擎API解析方法

例如：

```bash
# 使用默认方法
python game_record.py "塞尔达传说 旷野之息"

# 使用LLM方法
python game_record.py "塞尔达传说 旷野之息" --method llm
```

## 输出示例

```json
{
  "english_name": "The Legend of Zelda: Breath of the Wild",
  "cover_image": "https://assets1.ignimgs.com/2017/03/02/zelda-breath-of-the-wild---button-2017-1488491014083.jpg",
  "platforms": ["Nintendo Switch", "Wii U"],
  "release_date": "2017-03-03",
  "score": "10",
  "url": "https://www.ign.com/games/the-legend-of-zelda-breath-of-the-wild",
  "chinese_name": "塞尔达传说 旷野之息",
  "translated_name": "The Legend of Zelda: Breath of the Wild"
}
```

## 特点

- 支持系列游戏的多作品选择
- 自动清理游戏封面图URL中的多余参数
- 统一发售日期格式为 YYYY-MM-DD
- 支持两种获取详情的方式，可根据需要选择

## 注意事项

- 请确保配置文件中的API密钥和URL正确
- 网站结构可能会变化，可能需要更新爬虫代码
- 请遵守IGN网站的使用条款和爬虫政策