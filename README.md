PDF-to-Markdown Converter with GUI

这是一个基于 Python 开发的 PDF 转 Markdown 工具，支持 图形化界面、批量上传、多线程转换，并能够从 PDF 中提取文字和图片。工具适配 Windows 11，也可在其他支持 Python 的操作系统上运行。

✨ 功能特性

图形界面

使用 Tkinter 构建，简单易用

支持单个 / 批量 PDF 文件上传

上传进度条实时显示

文件列表展示文件名、大小、上传时间、状态

文件管理

上传的 PDF 文件会保存到 uploads/ 文件夹

转换后的 Markdown 文件保存到 output/<PDF文件名_时分秒>/ 文件夹

每个转换文件夹自动生成 img/ 子目录，用于存放提取的图片

Markdown 转换

点击 "转 MD" 按钮可单独转换文件

点击 "批量转 MD" 可并发处理所有文件

使用 5 个线程并发，自动分配任务，处理效率更高

转换完成后弹出提示

中文支持

确保 PDF 中的中文内容可以正常提取并保存

🛠️ 技术栈

Python 3.9+

Tkinter - 构建图形用户界面

PyMuPDF (fitz) - PDF 解析、文字与图片提取

threading - 多线程任务管理

📦 安装与运行
1. 克隆项目
git clone https://github.com/your-username/pdf-to-md-gui.git
cd pdf-to-md-gui

2. 安装依赖
pip install -r requirements.txt


requirements.txt 内容：

PyMuPDF

3. 运行程序
python main.py

📂 项目结构
pdf-to-md-gui/
│── main.py                # 主程序
│── requirements.txt       # 依赖
│── README.md              # 使用说明
│── uploads/               # 上传的 PDF 文件（自动生成）
│── output/                # 转换后的 Markdown 文件夹（自动生成）
│    ├── <PDF文件名_时分秒>/  
│        ├── xxx.md  
│        ├── img/          # 提取的图片

🚀 使用说明

打开程序后，点击 "上传 PDF" 按钮选择文件（可多选）

文件会保存到 uploads/ 文件夹，并显示在列表中

选择某个文件，点击 "转 MD" 按钮即可单独转换

点击顶部的 "批量转 MD" 按钮，可一次性处理所有文件

转换完成后，结果会保存在 output/ 文件夹中
