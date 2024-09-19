# PDF文件标题和关键词提取器

这个Python脚本可以自动处理PDF文件，提取标题和关键词，并根据提取的标题重命名文件。

## 功能

- 从PDF文件中提取文本
- 使用Google Gemini AI模型提取标题和关键词
- 根据提取的标题重命名PDF文件
- 处理整个文件夹中的所有PDF文件

## 安装

1. 克隆此仓库
2. 安装所需的依赖：
   ```pip install google-generativeai PyPDF2```

## 配置

1. 复制 `config.example.py` 并重命名为 `config.py`
2. 在 `config.py` 中填入您的实际Google API密钥

## 使用方法

1. 将需要处理的PDF文件放入 `paper` 文件夹
2. 运行脚本：
   ```python extract_info_gemini.py```

## 注意事项

- 确保您有足够的Google API使用额度
- 处理大量文件可能需要较长时间
- 如果遇到网络问题，脚本会自动重试

## 贡献

欢迎提交问题和拉取请求。

## 许可

[MIT](https://choosealicense.com/licenses/mit/)