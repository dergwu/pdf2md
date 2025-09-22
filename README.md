📑 PDF-to-Markdown Converter (GUI)

基于 Python + Tkinter 开发的 PDF 转 Markdown 工具。
支持 图形化界面、批量上传、多线程转换，可自动提取 文字和图片，生成结构化的 Markdown 文件。

适配 Windows 11，也可在其他操作系统运行。

✨ 功能特性

图形界面

支持批量上传 PDF

实时显示进度条

文件列表：文件名、大小、上传时间、处理状态

文件管理

上传文件保存到 uploads/

转换结果保存到 output/<PDF文件名_时分秒>/

自动生成 img/ 子目录存放提取的图片

Markdown 转换

单个文件："转 MD" 按钮

批量处理："批量转 MD" 按钮

5 线程并发处理，任务自动分配

转换完成后弹窗提示

中文支持 ✅

🛠️ 技术栈

Python 3.9+

Tkinter（图形界面）

PyMuPDF（PDF 解析，文字/图片提取）

threading（多线程任务管理）
