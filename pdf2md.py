import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import fitz  # PyMuPDF
import time
import queue
from datetime import datetime
import shutil

UPLOAD_DIR = "uploads"

# 创建上传目录
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


class PDF2MDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 转 Markdown 工具")
        self.root.geometry("900x600")

        # 队列：线程安全的任务分发
        self.task_queue = queue.Queue()
        self.lock = threading.Lock()

        # 文件列表存储
        self.files = []

        # UI 初始化
        self.create_widgets()

    def create_widgets(self):
        """初始化界面"""
        # 上传区域
        upload_frame = ttk.LabelFrame(self.root, text="文件上传")
        upload_frame.pack(fill="x", padx=10, pady=5)

        self.upload_btn = ttk.Button(upload_frame, text="选择 PDF 文件", command=self.upload_files)
        self.upload_btn.pack(side="left", padx=5, pady=5)

        self.batch_convert_btn = ttk.Button(upload_frame, text="批量转 MD", command=self.batch_convert)
        self.batch_convert_btn.pack(side="left", padx=5, pady=5)

        # 文件列表
        list_frame = ttk.LabelFrame(self.root, text="文件列表")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("文件名", "大小", "上传时间", "状态")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        self.tree.pack(fill="both", expand=True, side="left")

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # 日志窗口
        log_frame = ttk.LabelFrame(self.root, text="运行日志")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = tk.Text(log_frame, height=10, wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def log(self, msg):
        """写日志"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def upload_files(self):
        """选择 PDF 文件"""
        files = filedialog.askopenfilenames(filetypes=[("PDF 文件", "*.pdf")])
        for file in files:
            filename = os.path.basename(file)
            filesize = os.path.getsize(file) // 1024
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 保存到 uploads 目录
            save_path = os.path.join(UPLOAD_DIR, filename)
            shutil.copy(file, save_path)

            self.files.append({"path": save_path, "status": "未处理"})
            self.tree.insert("", "end", values=(filename, f"{filesize} KB", upload_time, "未处理"))

        self.log(f"成功上传 {len(files)} 个文件")

    def batch_convert(self):
        """批量转换"""
        if not self.files:
            messagebox.showwarning("提示", "请先上传文件！")
            return

        self.log("开始批量转换任务...")
        for f in self.files:
            if f["status"] == "未处理":
                self.task_queue.put(f)

        # 启动 5 个线程
        for i in range(5):
            t = threading.Thread(target=self.worker, args=(i + 1,))
            t.daemon = True
            t.start()

    def worker(self, worker_id):
        """工作线程"""
        while not self.task_queue.empty():
            try:
                file = self.task_queue.get_nowait()
            except queue.Empty:
                break

            path = file["path"]
            filename = os.path.basename(path)
            self.log(f"[线程 {worker_id}] 正在处理 {filename}")

            try:
                self.convert_pdf_to_md(path)
                file["status"] = "已处理"

                # 更新表格状态
                for child in self.tree.get_children():
                    if self.tree.item(child, "values")[0] == filename:
                        self.tree.item(child, values=(
                            filename,
                            f"{os.path.getsize(path) // 1024} KB",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "已处理 ✅"
                        ))
                        break

                self.log(f"[线程 {worker_id}] {filename} 转换完成")
            except Exception as e:
                self.log(f"[线程 {worker_id}] {filename} 转换失败: {e}")

    def convert_pdf_to_md(self, pdf_path):
        """PDF 转换为 Markdown"""
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        out_dir = os.path.join(os.getcwd(), f"{pdf_name}_{datetime.now().strftime('%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)
        img_dir = os.path.join(out_dir, "img")
        os.makedirs(img_dir, exist_ok=True)

        doc = fitz.open(pdf_path)
        md_content = []

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            md_content.append(f"## Page {page_num}\n\n{text}\n")

            # 提取图片
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                img_filename = f"page{page_num}_img{img_index}.png"
                img_path = os.path.join(img_dir, img_filename)
                pix.save(img_path)
                md_content.append(f"![{img_filename}](img/{img_filename})\n")

        md_file = os.path.join(out_dir, f"{pdf_name}.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_content))

        doc.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDF2MDApp(root)
    root.mainloop()
