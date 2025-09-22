import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from tkinter import ttk
import requests
import html2text
import datetime
import os
import re
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

# ================== 工具函数 ==================

def thread_safe_log(message: str):
    """线程安全写日志"""
    root.after(0, lambda: log(message))

def log(message: str):
    """写入日志到调试窗口并滚动到底部"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
    debug_text.see(tk.END)

def sanitize_filename(name: str) -> str:
    """清理非法文件名字符"""
    return re.sub(r'[\/:*?"<>|]', '_', name).strip()

def unique_filepath(dirpath: str, basename: str) -> str:
    """生成唯一文件路径"""
    filename = f"{basename}.md"
    filepath = os.path.join(dirpath, filename)
    if not os.path.exists(filepath):
        return filepath
    idx = 1
    while True:
        filename2 = f"{basename}_{idx}.md"
        filepath2 = os.path.join(dirpath, filename2)
        if not os.path.exists(filepath2):
            return filepath2
        idx += 1

def find_title_in_obj(obj):
    """递归查找 JSON 对象中的 title 或 name"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and k.lower() in ("title", "name"):
                if isinstance(v, str) and v.strip():
                    return v.strip()
        for v in obj.values():
            res = find_title_in_obj(v)
            if res:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_title_in_obj(item)
            if res:
                return res
    return None

def extract_title_from_response(response, index_hint=None):
    """多种方式提取 title"""
    try:
        data = response.json()
        title = find_title_in_obj(data)
        if title:
            return title, "json_recursive"
    except Exception:
        pass
    try:
        text = response.text
        m = re.search(r'"title"\s*:\s*"([^"]{1,200}?)"', text)
        if m:
            return m.group(1).strip(), "regex_text"
        m2 = re.search(r"'title'\s*:\s*'([^']{1,200}?)'", text)
        if m2:
            return m2.group(1).strip(), "regex_text_single"
        m3 = re.search(r'"name"\s*:\s*"([^"]{1,200}?)"', text)
        if m3:
            return m3.group(1).strip(), "regex_name"
    except Exception:
        pass
    return None, None

def save_markdown(content: str, title: str, save_dir: str, index_hint=None):
    """保存 Markdown 文件"""
    safe_title = sanitize_filename(title if title else (f"未命名_{index_hint}" if index_hint is not None else "未命名"))
    filepath = unique_filepath(save_dir, safe_title)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    thread_safe_log(f"已保存: {filepath}")
    return filepath

# ================== 多线程批量请求 ==================

MAX_THREADS = 5  # 最大并发数

def fetch_url_task(url, index, save_dir, result_queue):
    """每个线程处理单个 URL"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        title, method = extract_title_from_response(response, index_hint=index)
        if title is None:
            title = f"未命名_{index}"

        try:
            data = response.json()
            md_source = json.dumps(data, ensure_ascii=False, indent=2)
        except:
            response.encoding = response.apparent_encoding
            md_source = response.text

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        md_content = h.handle(md_source)

        filepath = save_markdown(md_content, title, save_dir, index_hint=index)
        result_queue.put(f"[{url}] 保存成功 -> {filepath}")
    except Exception as e:
        result_queue.put(f"[{url}] 请求失败: {e}")

def batch_process(base_url, start, end, save_dir):
    """批量处理 URL"""
    total = end - start + 1
    progress_bar["maximum"] = total
    progress_bar["value"] = 0
    root.update_idletasks()

    result_queue = Queue()
    urls = [f"{base_url}{i}" for i in range(start, end + 1)]

    def update_gui():
        """定期轮询队列，更新日志和进度条"""
        updated = False
        while not result_queue.empty():
            msg = result_queue.get()
            thread_safe_log(msg)
            progress_bar["value"] += 1
            updated = True
        if progress_bar["value"] < total:
            root.after(200, update_gui)
        else:
            thread_safe_log("批量处理完成")
            messagebox.showinfo("完成", f"批量处理完成，文件保存在: {save_dir}")

    root.after(200, update_gui)

    # 使用线程池执行批量任务
    executor = ThreadPoolExecutor(max_workers=MAX_THREADS)
    for idx, url in enumerate(urls, 1):
        executor.submit(fetch_url_task, url, idx, save_dir, result_queue)

# ================== 主逻辑 ==================

def fetch_and_convert():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("提示", "请输入一个URL")
        thread_safe_log("未输入URL")
        return

    match = re.match(r"(.*?)(\d+)-(\d+)$", url)
    if match:
        base_url, start, end = match.groups()
        start, end = int(start), int(end)
        if end < start:
            messagebox.showwarning("范围错误", "结束数字应不小于起始数字")
            return

        save_dir = filedialog.askdirectory(title="选择保存MD文件的文件夹")
        if not save_dir:
            thread_safe_log("用户取消了保存目录选择")
            return

        thread_safe_log(f"开始批量请求：{start} -> {end}，基准URL：{base_url}{{i}}")
        batch_process(base_url, start, end, save_dir)
    else:
        # 单个 URL
        try:
            thread_safe_log(f"请求: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            html_content = response.text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            md_content = h.handle(html_content)

            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, md_content)
            thread_safe_log("单个URL转换成功")

        except Exception as e:
            messagebox.showerror("错误", f"请求失败: {e}")
            thread_safe_log(f"发生错误：{e}")

# ================== 界面 UI ==================

root = tk.Tk()
root.title("网页转Markdown工具（多线程批量）")
root.geometry("950x800")
root.configure(bg="#f9f9f9")

default_font = ("Microsoft YaHei", 10)
title_font = ("Microsoft YaHei", 11, "bold")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=default_font, padding=6)
style.configure("TLabel", font=default_font, background="#f9f9f9")
style.configure("TEntry", font=default_font)

# 顶部输入区
top_frame = ttk.Frame(root, padding=10)
top_frame.pack(fill="x")
ttk.Label(top_frame, text="请输入URL（支持范围，例如 https://.../2-100）：", font=title_font).pack(side="left")
url_entry = ttk.Entry(top_frame, width=70)
url_entry.pack(side="left", padx=8)
ttk.Button(top_frame, text="确认并转换", command=fetch_and_convert).pack(side="left", padx=8)

# 中部输出区
middle_frame = ttk.Frame(root, padding=(10, 5))
middle_frame.pack(fill="both", expand=True)
ttk.Label(middle_frame, text="转换结果：", font=title_font).pack(anchor="w")
output_text = scrolledtext.ScrolledText(middle_frame, wrap=tk.WORD, width=100, height=22, font=("Consolas", 10), bg="#ffffff")
output_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

# 进度条
progress_frame = ttk.Frame(root, padding=(10, 5))
progress_frame.pack(fill="x")
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=900, mode="determinate")
progress_bar.pack(fill="x", pady=5)

# 底部日志窗口
bottom_frame = ttk.Frame(root, padding=(10, 5))
bottom_frame.pack(fill="both")
ttk.Label(bottom_frame, text="调试日志：", font=title_font).pack(anchor="w")
debug_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, width=100, height=8, font=("Consolas", 9), bg="#f5f5f5")
debug_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

thread_safe_log("程序启动完成，等待用户输入 URL...")

root.mainloop()
