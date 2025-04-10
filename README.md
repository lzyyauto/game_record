# 游戏信息查询工具

这是一个命令行工具，用于查询游戏信息。它接收中文游戏名作为输入，将其翻译成英文，然后从IGN网站获取游戏详情，并以JSON格式输出结果。

## 功能

- 将中文游戏名翻译成英文（通过LLM服务）
- 使用英文名在IGN网站搜索游戏
- 获取游戏的详细信息：英文名、平台、发售时间、评分和详情页URL
- 以JSON格式输出结果

## 安装依赖

```bash
pip install requests beautifulsoup4
```

## 使用方法

```bash
python game_record.py "游戏名称"
```

例如：

```bash
python game_record.py "塞尔达传说 旷野之息"
```

## 输出示例

```json
{
  "english_name": "The Legend of Zelda: Breath of the Wild",
  "platforms": ["Nintendo Switch", "Wii U"],
  "release_date": "March 3, 2017",
  "score": "10",
  "url": "https://www.ign.com/games/the-legend-of-zelda-breath-of-the-wild",
  "chinese_name": "塞尔达传说 旷野之息",
  "translated_name": "The Legend of Zelda: Breath of the Wild"
}
```

## 注意事项

- 目前LLM翻译功能使用的是模拟数据，需要自行实现与LLM服务的集成
- 网站结构可能会变化，可能需要更新爬虫代码
- 请遵守IGN网站的使用条款和爬虫政策