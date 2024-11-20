import os
import time
import json
from datetime import datetime, timedelta
import logging
from typing import List, Dict
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, simpledialog

class AutoPoster:
    def __init__(self, account: Dict, log_output=None):
        self.account = account
        self.video_folder = account.get("video_folder", "")
        self.title = account.get("title", "")
        self.content = account.get("content", "")
        self.threshold = account.get("threshold", 10)
        self.wait_time = account.get("wait_time", 3600)
        self.log_output = log_output  # 用于记录日志的文本框

        # 初始化日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # 获取所有视频文件
        self.video_files = self._get_files(self.video_folder, ['.mp4', '.MP4'])

        # 添加调试信息
        logging.info(f"找到的视频文件: {self.video_files}")

        # 检查是否为空
        if not self.video_files:
            logging.warning("视频文件夹为空！")

    def _get_files(self, folder: str, extensions: List[str]) -> List[str]:
        """获取指定文件夹下的所有指定扩展名的文件完整路径"""
        files = []
        for file in os.listdir(folder):
            if any(file.endswith(ext) for ext in extensions):
                files.append(os.path.join(folder, file))
        return sorted(files)  # 排序确保顺序一致

    def log_message(self, message: str):
        """在日志输出框中显示信息"""
        logging.info(message)
        if self.log_output:
            self.log_output.insert(tk.END, message + "\n")
            self.log_output.see(tk.END)  # 滚动到文本框的底部

    def start_posting(self):
        """开始自动发布流程"""
        cookie = self.account.get("cookie")
        if not cookie:
            self.log_message("账号缺少 cookie，无法发布。")
            return

        self.log_message(f"开始发布账号: {self.account.get('username')}")

        for post_count in range(self.threshold):
            try:
                video_path = self.video_files[post_count % len(self.video_files)]  # 循环使用视频文件
                post_time = (datetime.now() + timedelta(seconds=(post_count + 1) * self.wait_time)).strftime("%Y-%m-%d %H:%M:%S")

                # 发布笔记时传入 cookie 和 post_time
                self.log_message(f"发布第 {post_count + 1} 条，定时发布时间: {post_time}")

                # 这里调用实际的发布函数
                # add(good_id=..., good_name=..., cookie=cookie, title=self.title, content=self.content, video_path=video_path, post_time=post_time)

                self.log_message("发布成功！")
                time.sleep(15)  # 每条发布后等待15秒
            except Exception as e:
                self.log_message(f"发布失败: {str(e)}")
                time.sleep(300)  # 发生错误等待5分钟后继续

def load_accounts(file_path: str) -> List[Dict]:
    """从 JSON 文件加载账号信息"""
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_accounts(file_path: str, accounts: List[Dict]):
    """将账号信息保存到 JSON 文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, ensure_ascii=False, indent=4)

class AccountManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("多账号自动发布工具")

        self.accounts = load_accounts('accounts.json')
        self.selected_account = None

        # 布局
        self.create_widgets()

    def create_widgets(self):
        # 账号列表框
        self.account_listbox = tk.Listbox(self.master, selectmode=tk.SINGLE)
        self.account_listbox.grid(row=0, column=0, rowspan=6, sticky="nsew")
        self.account_listbox.bind('<<ListboxSelect>>', self.on_account_select)

        # 右侧发布区域
        tk.Label(self.master, text="视频文件夹路径:").grid(row=0, column=1)
        self.video_folder_entry = tk.Entry(self.master)
        self.video_folder_entry.grid(row=0, column=2)
        tk.Button(self.master, text="选择文件夹", command=self.select_video_folder).grid(row=0, column=3)

        tk.Label(self.master, text="标题:").grid(row=1, column=1)
        self.title_entry = tk.Entry(self.master)
        self.title_entry.grid(row=1, column=2)

        tk.Label(self.master, text="内容:").grid(row=2, column=1)
        self.content_entry = tk.Entry(self.master)
        self.content_entry.grid(row=2, column=2)

        tk.Label(self.master, text="发布阈值:").grid(row=3, column=1)
        self.threshold_entry = tk.Entry(self.master)
        self.threshold_entry.grid(row=3, column=2)

        tk.Label(self.master, text="Cookie:").grid(row=4, column=1)
        self.cookie_entry = tk.Entry(self.master)
        self.cookie_entry.grid(row=4, column=2)

        # 日志输出框
        self.log_output = scrolledtext.ScrolledText(self.master, width=60, height=15)
        self.log_output.grid(row=5, column=1, columnspan=3)

        # 提交按钮
        self.submit_button = tk.Button(self.master, text="开始发布", command=self.start_posting)
        self.submit_button.grid(row=6, column=1)

        # 账号管理按钮
        tk.Button(self.master, text="新增账号", command=self.add_account).grid(row=7, column=0)
        tk.Button(self.master, text="删除账号", command=self.delete_account).grid(row=7, column=1)
        tk.Button(self.master, text="更改 Cookie", command=self.change_cookie).grid(row=7, column=2)

        self.update_account_listbox()

    def update_account_listbox(self):
        """更新账号列表框"""
        self.account_listbox.delete(0, tk.END)
        for account in self.accounts:
            self.account_listbox.insert(tk.END, account.get("username"))

    def on_account_select(self, event):
        """处理账号选择事件"""
        selection = self.account_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_account = self.accounts[index]
            # 更新发布信息区域
            self.update_publish_info()

    def update_publish_info(self):
        """更新发布信息区域"""
        if self.selected_account:
            self.video_folder_entry.delete(0, tk.END)
            self.video_folder_entry.insert(0, self.selected_account.get("video_folder", ""))
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, self.selected_account.get("title", ""))
            self.content_entry.delete(0, tk.END)
            self.content_entry.insert(0, self.selected_account.get("content", ""))
            self.threshold_entry.delete(0, tk.END)
            self.threshold_entry.insert(0, self.selected_account.get("threshold", "10"))  # 默认阈值为10
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, self.selected_account.get("cookie", ""))  # 显示 Cookie

    def select_video_folder(self):
        folder_selected = filedialog.askdirectory()
        self.video_folder_entry.delete(0, tk.END)  # 清空当前输入
        self.video_folder_entry.insert(0, folder_selected)  # 插入选择的文件夹路径

        # 更新选中账号的视频文件夹路径
        if self.selected_account:
            self.selected_account["video_folder"] = folder_selected
            save_accounts('accounts.json', self.accounts)  # 保存更新后的账号信息

    def start_posting(self):
        if not self.selected_account:
            messagebox.showwarning("警告", "请先选择一个账号！")
            return

        # 更新选中账号的信息
        self.selected_account["title"] = self.title_entry.get()
        self.selected_account["content"] = self.content_entry.get()
        self.selected_account["threshold"] = int(self.threshold_entry.get())
        self.selected_account["cookie"] = self.cookie_entry.get()  # 更新 Cookie
        save_accounts('accounts.json', self.accounts)  # 保存更新后的账号信息

        # 创建 AutoPoster 实例
        poster = AutoPoster(
            account=self.selected_account,
            log_output=self.log_output  # 传递日志输出框
        )
        
        # 开始发布
        poster.start_posting()

    def add_account(self):
        """新增账号"""
        username = simpledialog.askstring("新增账号", "请输入账号名称:")
        cookie = simpledialog.askstring("新增账号", "请输入账号 Cookie:")
        if username and cookie:
            self.accounts.append({
                "username": username,
                "cookie": cookie,
                "video_folder": "",  # 新账号的文件夹路径
                "title": "",         # 新账号的标题
                "content": "",       # 新账号的内容
                "threshold": 10,     # 默认阈值
                "wait_time": 3600    # 默认等待时间
            })
            save_accounts('accounts.json', self.accounts)
            self.update_account_listbox()

    def delete_account(self):
        """删除账号"""
        if self.selected_account:
            self.accounts.remove(self.selected_account)
            save_accounts('accounts.json', self.accounts)
            self.update_account_listbox()
            self.selected_account = None
            self.clear_publish_info()

    def clear_publish_info(self):
        """清空发布信息区域"""
        self.video_folder_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.content_entry.delete(0, tk.END)
        self.threshold_entry.delete(0, tk.END)
        self.cookie_entry.delete(0, tk.END)  # 清空 Cookie

    def change_cookie(self):
        """更改 Cookie"""
        if self.selected_account:
            new_cookie = simpledialog.askstring("更改 Cookie", "请输入新的 Cookie:")
            if new_cookie:
                self.selected_account["cookie"] = new_cookie
                save_accounts('accounts.json', self.accounts)
                self.update_account_listbox()

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManagerApp(root)
    root.mainloop()