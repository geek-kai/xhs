import os
import time
import random
from datetime import datetime, timedelta
import logging
from typing import List, Tuple
import sys
import traceback
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import filedialog
from threading import Thread  # 导入线程模块
import json
from .add import add  # 使用绝对导入
from concurrent.futures import ThreadPoolExecutor, TimeoutError

class AutoPoster:
    def __init__(self, video_folder: str, cookie: str, title: str, content: str, threshold: int,
                 cover_folder: str = None, good_id=None, good_name=None, topics=None, proxies=None,
                 wait_time: int = 1800, log_output=None, first_post_immediate=False, mode=2, log_account_activity=None, log_user=None,count=0):
        self.video_folder = video_folder
        self.cover_folder = cover_folder
        self.cookie = cookie
        self.title = title
        self.content = content
        self.good_id = good_id
        self.good_name = good_name
        self.topics = topics
        self.proxies = proxies
        self.threshold = threshold
        self.wait_time = wait_time
        self.log_output = log_output  # 用于记录日志的文本框
        self.first_post_immediate = first_post_immediate
        self.mode = mode
        self.log_account_activity = log_account_activity  # 记录账号活动日志的函数
        self.log_user = log_user 
        self.count = count  # 记录发布次数

        # 初始化日志

        # 获取所有视频和封面文件
        self.video_files = self._get_files(video_folder, ['.mp4', '.MP4'])
        self.cover_files = self._get_files(cover_folder, ['.jpg', '.JPG', '.png', '.PNG'])

        # 检查是否为空
        if not self.video_files:
            self.log_message("视频文件夹为空！")
        if not self.cover_files:
            self.log_message("封面文件夹为空！")

        # 当前索引
        self.current_video_index = 0
        self.current_cover_index = 0

    def _get_files(self, folder: str, extensions: List[str]) -> List[str]:
        """获取指定文件夹下的所有指定扩展名的文件完整路径"""
        files = []
        for file in os.listdir(folder):
            if any(file.endswith(ext) for ext in extensions):
                files.append(os.path.join(folder, file))
        return sorted(files)  # 排序确保顺序一致

    def _get_next_files(self) -> Tuple[str, str]:
        """获取下一个要发布的视频和封面文件"""
        if not self.video_files:
            raise ValueError("视频文件夹为空！")

        video = self.video_files[self.current_video_index]

        # 检查封面文件列表是否为空
        cover = None  # 默认值为 None
        if self.cover_files:  # 只有在封面文件列表不为空时才访问
            cover = self.cover_files[self.current_cover_index]
            self.current_cover_index = (self.current_cover_index + 1) % len(self.cover_files)

        # 更新索引
        self.current_video_index = (self.current_video_index + 1) % len(self.video_files)

        return video, cover

    def log_message(self, message: str):
        """在日志输出框中显示信息并记录到账号日志"""
        logging.info(message)
        # if self.log_output:
        #     self.log_output.insert(tk.END, message + "\n")
        #     self.log_output.see(tk.END)  # 滚动到文本框的底部

        # 记录到账号日志
        if self.log_account_activity:
            self.log_account_activity(self.log_user, message)  # 使用传递的用户名
    def update_video_filename(self,video_path: str):
        """更新视频文件名，添加使用次数标记"""
        base_name, ext = os.path.splitext(video_path)
        # 检查文件名是否已经包含 '-数字'
        base_name, ext = os.path.splitext(video_path)
    # 检查文件名是否已经包含 '-数字'
        if '-' in base_name:
        # 提取数字并增加1
            parts = base_name.rsplit('-', 1)
            if parts[-1].isdigit():
                 new_count = int(parts[-1]) + 1
                 new_base_name = f"{parts[0]}-{new_count}"
            else:
                 new_base_name = f"{base_name}-1"  # 如果最后部分不是数字，重置为-1
        else:
           new_base_name = f"{base_name}-1"  # 第一次发布，添加-1

        new_video_path = f"{new_base_name}{ext}"
        os.rename(video_path, new_video_path) 

        # 更新 video_files 列表
        if video_path in self.video_files:
            index = self.video_files.index(video_path)
            self.video_files[index] = new_video_path  # 更新对应的文件名

        return new_video_path
    def start_posting(self):
        """开始自动发布流程"""
        video_path, cover_path = self._get_next_files()
        self.log_message(f"正在发布视频: {video_path}")
        self.log_message(f"使用封面: {cover_path if cover_path else '无封面'}")
        
        cover = cover_path if cover_path else None
        retries = 0
        
        def do_post():
            return 
        
        try:
            while retries < 3:
                try:
                    add(
                    good_id=self.good_id,
                    good_name=self.good_name,
                    cookie=self.cookie,
                    proxies=self.proxies,
                    title=self.title,
                    content=self.content,
                    topics=self.topics,
                    cover_path=cover,
                    video_path=video_path
                    )
                    self.log_message("发布成功！")
                    self.update_video_filename(video_path=video_path)
                    self.count += 1
                    break
                    
                except TimeoutError:
                    self.log_message(f"发布操作超时，条数：{self.count+1}，正在重试... (尝试次数: {retries + 1})")
                    retries += 1
                    time.sleep(10)
                except Exception as e:
                    retries += 1
                    self.log_message(f"发布笔记时发生错误: {str(e)}，条数：{self.count+1}，正在重试... (尝试次数: {retries})")
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            self.log_message("发布过程被用户中断。")
        except Exception as e:
            self.log_message(f"发布失败: {str(e)}，条数：{self.count+1}")
            self.count += 1

def start_auto_posting():
    def submit():
        video_folder = video_folder_entry.get()
        cover_folder = cover_folder_entry.get() or None
        cookie = cookie_entry.get()
        title = title_entry.get()
        content = content_entry.get()
        threshold = int(threshold_entry.get())
        proxies = proxies_entry.get() or None
        if proxies:
            try:
                proxies = json.loads(proxies)  # 将 JSON 字符串解析为字典
            except json.JSONDecodeError:
                messagebox.showerror("错误", "Proxies 格式错误，请输入有效的 JSON 字符串")
                return
        mode = int(mode_var.get())
        wait_time = int(wait_time_entry.get() or 3600)
        first_post_immediate = first_post_immediate_var.get() == 'y'
        
        poster = AutoPoster(
            video_folder=video_folder,
            cover_folder=cover_folder,
            cookie=cookie,
            title=title,
            content=content,
            threshold=threshold,
            proxies=proxies,
            wait_time=wait_time,  # 传入用户的等待时间
            log_output=log_output,
            first_post_immediate=first_post_immediate,
            mode=mode,  # 传递发布模式
          # 传递记录账号活动日志的函数
        )
        
        # 使用线程来启动发布
        thread = Thread(target=poster.start_posting)
        thread.start()

    def select_video_folder():
        folder_selected = filedialog.askdirectory()
        video_folder_entry.delete(0, tk.END)  # 清空当前输入
        video_folder_entry.insert(0, folder_selected)  # 插入选择的文件夹路径

    def select_cover_folder():
        folder_selected = filedialog.askdirectory()
        cover_folder_entry.delete(0, tk.END)  # 清空当前输入
        cover_folder_entry.insert(0, folder_selected)  # 插入选择的文件夹路径

    # 创建主窗口
    root = tk.Tk()
    root.title("自动发布工具")

    # 创建输入框和标签
    tk.Label(root, text="视频文件夹路径:").grid(row=0, column=0)
    video_folder_entry = tk.Entry(root)
    video_folder_entry.grid(row=0, column=1)
    tk.Button(root, text="选择文件夹", command=select_video_folder).grid(row=0, column=2)

    tk.Label(root, text="封面文件夹路径（可选）:").grid(row=1, column=0)
    cover_folder_entry = tk.Entry(root)
    cover_folder_entry.grid(row=1, column=1)
    tk.Button(root, text="选择文件夹", command=select_cover_folder).grid(row=1, column=2)

    tk.Label(root, text="Cookie:").grid(row=2, column=0)
    cookie_entry = tk.Entry(root)
    cookie_entry.grid(row=2, column=1)

    tk.Label(root, text="标题:").grid(row=3, column=0)
    title_entry = tk.Entry(root)
    title_entry.grid(row=3, column=1)

    tk.Label(root, text="内容:").grid(row=4, column=0)
    content_entry = tk.Entry(root)
    content_entry.grid(row=4, column=1)

    tk.Label(root, text="发布阈值:").grid(row=5, column=0)
    threshold_entry = tk.Entry(root)
    threshold_entry.grid(row=5, column=1)

    tk.Label(root, text="Proxies（可选）:").grid(row=6, column=0)
    proxies_entry = tk.Entry(root)
    proxies_entry.grid(row=6, column=1)

    tk.Label(root, text="发布模式:").grid(row=7, column=0)
    mode_var = tk.StringVar(value="1")
    tk.Radiobutton(root, text="循环发布", variable=mode_var, value="1").grid(row=7, column=1, sticky="w")
    tk.Radiobutton(root, text="定时发布", variable=mode_var, value="2").grid(row=7, column=1, sticky="e")

    tk.Label(root, text="等待时间（秒，默认为3600秒）:").grid(row=8, column=0)
    wait_time_entry = tk.Entry(root)
    wait_time_entry.grid(row=8, column=1)

    tk.Label(root, text="第一条是立即发布吗？（y/n）:").grid(row=9, column=0)
    first_post_immediate_var = tk.StringVar(value='n')
    tk.Radiobutton(root, text="是", variable=first_post_immediate_var, value='y').grid(row=9, column=1, sticky="w")
    tk.Radiobutton(root, text="否", variable=first_post_immediate_var, value='n').grid(row=9, column=1, sticky="e")

    # 日志输出框
    log_output = scrolledtext.ScrolledText(root, width=60, height=15)
    log_output.grid(row=11, columnspan=3)

    # 提交按钮
    submit_button = tk.Button(root, text="开始发布", command=submit)
    submit_button.grid(row=10, columnspan=3)

    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
       start_auto_posting()