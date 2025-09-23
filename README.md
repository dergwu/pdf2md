PDF-to-MD Converter

一个支持 单文件 / 批量 将 PDF 转换为 Markdown 格式 的桌面工具，基于 Python + Tkinter 开发。
适用于需要快速从 PDF 文档中提取内容并生成 Markdown 文件的场景，例如：

技术文档整理

学术论文笔记

电子书转笔记

✨ 功能特性

📂 支持单文件 & 批量模式

🚀 多线程加速，提升批量转换性能

📝 自动提取 PDF 文本并转换为 Markdown 格式

📊 进度条显示，实时查看处理进度

🖥️ 图形化界面，无需命令行操作

🔖 批量模式下自动使用 PDF 内标题作为文件名

📦 安装与运行
方式一：直接运行（推荐）

前往 Releases
 页面下载最新的 PDF-to-MD-Converter.exe

双击运行即可使用，无需安装 Python 环境

方式二：源码运行

克隆仓库：

git clone https://github.com/你的仓库.git
cd PDF-to-MD-Converter


安装依赖：

pip install -r requirements.txt


运行程序：

python main.py

📖 使用方法

打开程序，选择 单文件模式 或 批量模式

在输入框中粘贴 URL 或通过文件选择框加载 PDF 文件

设置输出目录（可选，默认为当前目录）

点击 开始转换

转换完成后，在输出目录中即可看到生成的 Markdown 文件

🛠️ 开发者指南
本地调试
git clone https://github.com/你的仓库.git
cd PDF-to-MD-Converter
pip install -r requirements.txt
python main.py

打包为 EXE
pip install pyinstaller
pyinstaller --onefile --noconsole main.py -n PDF-to-MD-Converter


打包完成后，dist/ 目录下会生成 PDF-to-MD-Converter.exe

📌 Roadmap

 单文件 PDF 转换

 批量 PDF 转换

 多线程加速

 界面优化 & 进度条显示

 增加 PDF 图片提取

 增加导出 HTML 格式

 增加配置文件支持

🤝 贡献

欢迎提交 Issue 或 Pull Request 来改进本项目。

📜 License

MIT License © 2025 [dergwu]
