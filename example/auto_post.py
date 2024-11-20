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

from add import add  # 使用绝对导入

class AutoPoster:
    def __init__(self, video_folder: str, cookie: str, title: str, content: str, threshold: int,
                 cover_folder: str = None, good_id=None, good_name=None, topics=None, proxies=None,
                 wait_time: int = 1800, log_output=None):
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

        # 初始化日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # 获取所有视频和封面文件
        self.video_files = self._get_files(video_folder, ['.mp4', '.MP4'])
        self.cover_files = self._get_files(cover_folder, ['.jpg', '.JPG', '.png', '.PNG'])

        # 添加调试信息
        logging.info(f"找到的视频文件: {self.video_files}")
        logging.info(f"找到的封面文件: {self.cover_files}")

        # 检查是否为空
        if not self.video_files:
            logging.warning("视频文件夹为空！")
        if not self.cover_files:
            logging.warning("封面文件夹为空！")

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
        """在日志输出框中显示信息"""
        logging.info(message)
        if self.log_output:
            self.log_output.insert(tk.END, message + "\n")
            self.log_output.see(tk.END)  # 滚动到文本框的底部

    def start_posting(self, mode: str, wait_time: int, first_post_immediate: bool = False):
        """开始自动发布流程"""
        post_count = 0
        if mode == "1":  # 现有模式
            while post_count < self.threshold:
                try:
                    video_path, cover_path = self._get_next_files()

                    # 发布笔记
                    self.log_message(f"正在发布视频: {video_path}")
                    self.log_message(f"使用封面: {cover_path if cover_path else '无封面'}")

                    # 确保 cover_path 有值
                    cover = cover_path if cover_path else None

                    add(
                        good_id=self.good_id,
                        good_name=self.good_name,
                        cookie=self.cookie,
                        proxies=self.proxies,
                        title=self.title,
                        content=self.content,
                        topics=self.topics,
                        cover_path=cover,  # 确保 cover 变量被传递
                        video_path=video_path
                    )

                    self.log_message("发布成功！")
                    post_count += 1

                    # 随机等待时间：30分钟 + (0-10分钟的随机值)
                    next_time = self.wait_time + random.randint(0, 600)
                    next_post_time = datetime.now().timestamp() + next_time
                    self.log_message(f"下次发布时间: {datetime.fromtimestamp(next_post_time).strftime('%Y-%m-%d %H:%M:%S')}")

                    time.sleep(next_time)
                except KeyboardInterrupt:
                    self.log_message("发布过程被用户中断。")
                    break  # 退出循环
                except Exception as e:
                    self.log_message(f"发布失败: {str(e)}")
                    traceback.print_exc()
                    time.sleep(300)  # 发生错误等待5分钟后继续
        elif mode == "2":  # 定时发布模式
            while post_count < self.threshold:
                try:
                    video_path, cover_path = self._get_next_files()
                    post_time = None

                    # 计算 post_time
                    if post_count == 0 and not first_post_immediate:
                        # 第一条是延时发布
                        post_time = (datetime.now() + timedelta(seconds=wait_time + random.randint(0, 600))).strftime("%Y-%m-%d %H:%M:%S")
                    elif post_count > 0:
                        if first_post_immediate:
                            time_num = post_count
                        else:
                            time_num = post_count + 1
                        # 后续条目
                        post_time = (datetime.now() + timedelta(seconds=(time_num) * wait_time + random.randint(0, 600))).strftime("%Y-%m-%d %H:%M:%S")
                    if post_time is None:
                        self.log_message(f"第{post_count + 1}条，立即发布")
                    else:
                        self.log_message(f"第{post_count + 1}条，定时发布时间{post_time}")

                    # 发布笔记时传入 post_time
                    add(
                        good_id=self.good_id,
                        good_name=self.good_name,
                        cookie=self.cookie,
                        proxies=self.proxies,
                        title=self.title,
                        content=self.content,
                        topics=self.topics,
                        cover_path=cover_path,
                        video_path=video_path,
                        post_time=post_time  # 传递定时发布时间
                    )
                    self.log_message("发布成功！")
                    post_count += 1
                    self.log_message(f"等待15秒后发布下一条...")
                    time.sleep(15)  # 每条发布后等待15秒
                except KeyboardInterrupt:
                    self.log_message("发布过程被用户中断。")
                    break  # 退出循环
                except Exception as e:
                    self.log_message(f"发布失败: {str(e)}")
                    traceback.print_exc()
                    time.sleep(300)  # 发生错误等待5分钟后继续
        else:
            self.log_message("无效的发布模式选择！")

def start_auto_posting():
    def submit():
        video_folder = video_folder_entry.get()
        cover_folder = cover_folder_entry.get() or None
        cookie = cookie_entry.get()
        title = title_entry.get()
        content = content_entry.get()
        threshold = int(threshold_entry.get())
        proxies = proxies_entry.get() or None
        mode = mode_var.get()
        wait_time = int(wait_time_entry.get() or 3600)
        first_post_immediate = first_post_immediate_var.get() == 'y'

        # 创建 AutoPoster 实例
        poster = AutoPoster(
            video_folder=video_folder,
            cover_folder=cover_folder,
            cookie=cookie,
            title=title,
            content=content,
            threshold=threshold,
            proxies=proxies,
            wait_time=wait_time,  # 传入用户的等待时间
            log_output=log_output  # 传递日志输出框
        )
        
        # 开始发布
        poster.start_posting(mode, wait_time, first_post_immediate)

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