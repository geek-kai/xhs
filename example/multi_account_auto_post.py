import os
import json
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, simpledialog
from auto_post_sign import AutoPoster  # 导入 AutoPoster 类
import threading  # 导入 threading 模块
import time
from datetime import datetime, timedelta
import random
import logging
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')

logging.basicConfig(
    filename=log_file_path,  # 日志文件名
    level=logging.DEBUG,  # 日志级别
    format='%(asctime)s - %(levelname)s - %(message)s' ,# 日志格式
    encoding='utf-8'  # 设置日志文件编码为 UTF-8

)

class AccountManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("小红书自动发布")

        self.json_file_path = os.path.join(os.getcwd(), "accounts.json")  # 使用当前工作目录
        self.accounts = []  # 用于存储账号信息
        self.check_vars = []  # 用于存储勾选框的变量
        self.logs = {}  # 用于存储每个账号的日志
        self.thread_terminated_accounts = {}  # 用于存储每个线程的终止账号集合
        self.threads = {}  # 用于存储线程对象
        self.create_widgets()
        self.load_accounts()  # 加载账号信息

        self.title_entry.focus_set()  # 确保标题输入框在启动时获得焦点

    def create_widgets(self):
        # 账号列表框
        self.account_listbox = tk.Listbox(self.master, selectmode=tk.MULTIPLE)
        self.account_listbox.grid(row=0, column=0, rowspan=6, sticky="nsew")
        self.account_listbox.bind('<<ListboxSelect>>', self.on_account_select)

        # 右侧发布区域
        tk.Label(self.master, text="视频文件夹路径:").grid(row=0, column=1)
        self.video_folder_entry = tk.Entry(self.master)
        self.video_folder_entry.grid(row=0, column=2)
        tk.Button(self.master, text="选择文件夹", command=self.select_video_folder, bg="#4CAF50", fg="white").grid(row=0, column=3)

        # 将封面文件夹路径移动到视频文件夹路径下方
        tk.Label(self.master, text="封面文件夹路径:").grid(row=1, column=1)
        self.cover_folder_entry = tk.Entry(self.master)
        self.cover_folder_entry.grid(row=1, column=2)  # 调整为 row=1
        tk.Button(self.master, text="选择文件夹", command=self.select_cover_folder, bg="#4CAF50", fg="white").grid(row=1, column=3)

        tk.Label(self.master, text="标题:").grid(row=2, column=1)
        self.title_entry = tk.Entry(self.master)
        self.title_entry.grid(row=2, column=2)

        tk.Label(self.master, text="内容:").grid(row=3, column=1)
        self.content_entry = tk.Entry(self.master)
        self.content_entry.grid(row=3, column=2)

        tk.Label(self.master, text="发布阈值:").grid(row=4, column=1)
        self.threshold_entry = tk.Entry(self.master)
        self.threshold_entry.grid(row=4, column=2)

        tk.Label(self.master, text="Cookie:").grid(row=5, column=1)
        self.cookie_entry = tk.Entry(self.master, state='readonly')  # 设置为只读
        self.cookie_entry.grid(row=5, column=2)

        tk.Label(self.master, text="代理（可选）:").grid(row=6, column=1)
        self.proxy_entry = tk.Entry(self.master, state='readonly')  # 设置为只读
        self.proxy_entry.grid(row=6, column=2)

        tk.Label(self.master, text="等待时间（秒，默认为3600秒）:").grid(row=7, column=1)
        self.wait_time_entry = tk.Entry(self.master)
        self.wait_time_entry.grid(row=7, column=2)

        tk.Label(self.master, text="第一条是否立即发布:").grid(row=8, column=1)
        self.first_post_immediate_var = tk.StringVar(value='n')
        tk.Radiobutton(self.master, text="是", variable=self.first_post_immediate_var, value='y').grid(row=8, column=2, sticky="w")
        tk.Radiobutton(self.master, text="否", variable=self.first_post_immediate_var, value='n').grid(row=8, column=2, sticky="e")

        # 日志输出框
        self.log_output = scrolledtext.ScrolledText(self.master, width=60, height=15)
        self.log_output.grid(row=9, column=1, columnspan=3)

        # 美化的开始发布按钮
        self.submit_button = tk.Button(self.master, text="开始发布", command=self.start_posting,
                                       bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                       relief="raised", padx=10, pady=5)
        self.submit_button.grid(row=10, column=1)

        # 保存账号信息按钮
        self.save_button = tk.Button(self.master, text="保存账号信息", command=self.save_account_content, bg="#2196F3", fg="white", font=("Arial", 12, "bold"))
        self.save_button.grid(row=10, column=2, padx=5, pady=5)

        # 账号管理按钮
        tk.Button(self.master, text="新增账号", command=self.add_account).grid(row=11, column=0)
        tk.Button(self.master, text="删除账号", command=self.delete_account).grid(row=11, column=1)
        tk.Button(self.master, text="更改 Cookie", command=self.change_cookie).grid(row=11, column=2)

        # 新增更改账号名字按钮
        tk.Button(self.master, text="更改账号名字", command=self.change_account_name).grid(row=12, column=0)
        
        # 新增更改代理按钮
        tk.Button(self.master, text="更改代理", command=self.change_proxy).grid(row=12, column=1)

        self.create_thread_widgets()  # 创建线程管理的UI组件

        self.update_account_listbox()

    def create_thread_widgets(self):
        """创建线程管理的UI组件"""
        tk.Label(self.master, text="正在运行的线程:").grid(row=13, column=0, sticky="w")
        self.thread_listbox = tk.Listbox(self.master, selectmode=tk.SINGLE)
        self.thread_listbox.grid(row=14, column=0, columnspan=4, sticky="nsew")
        tk.Button(self.master, text="终止选中线程", command=self.terminate_selected_thread).grid(row=15, column=0)

    def load_accounts(self):
        """加载账号信息"""
        if not os.path.exists(self.json_file_path):
            # 如果文件不存在，创建一个新的 JSON 文件
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)  # 创建一个空的 JSON 数组
            messagebox.showinfo("信息", "未找到账号文件，已创建新的文件。")
            self.accounts = []  # 初始化为空
        else:
            try:
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)  # 加载 JSON 数据
                messagebox.showinfo("成功", "账号信息加载成功！")
                self.update_account_listbox()  # 更新账号列表框
            except json.JSONDecodeError:
                messagebox.showerror("错误", "账号文件格式不正确，无法加载。")
                self.accounts = []  # 初始化为空
            except Exception as e:
                messagebox.showerror("错误", f"加载账号信息失败: {str(e)}")

    def save_accounts(self):
        """将账号信息保存到 JSON 文件"""
        with open(self.json_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=4)

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
            # 显示该账号的日志
            self.show_account_logs(self.selected_account['username'])

    def update_publish_info(self):
        """更新发布信"""
        selection = self.account_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_account = self.accounts[index]
            self.video_folder_entry.delete(0, tk.END)
            self.video_folder_entry.insert(0, self.selected_account.get("video_folder", ""))
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, self.selected_account.get("title", ""))
            self.content_entry.delete(0, tk.END)
            self.content_entry.insert(0, self.selected_account.get("content", ""))
            self.threshold_entry.delete(0, tk.END)
            self.threshold_entry.insert(0, self.selected_account.get("threshold", "10"))  # 默认阈值为10
            self.cookie_entry.config(state='normal')  # 设置为可编辑
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, self.selected_account.get("cookie", ""))  # 显示 Cookie
            self.cookie_entry.config(state='readonly')  # 设置为只读
            self.proxy_entry.config(state='normal')  # 设置为可编辑
            self.proxy_entry.delete(0, tk.END)
            self.proxy_entry.insert(0, self.selected_account.get("proxy", ""))  # 显示代理
            self.proxy_entry.config(state='readonly')  # 设置为只读
            self.cover_folder_entry.delete(0, tk.END)
            self.cover_folder_entry.insert(0, self.selected_account.get("cover_folder", ""))
            self.wait_time_entry.delete(0, tk.END)
            self.wait_time_entry.insert(0, self.selected_account.get("wait_time", "3600"))

            # 回显 first_post_immediate
            self.first_post_immediate_var.set(self.selected_account.get("first_post_immediate", 'n'))  # 默认值为 'n'

    def select_video_folder(self):
        folder_selected = filedialog.askdirectory()
        self.video_folder_entry.delete(0, tk.END)  # 清空当前输入
        self.video_folder_entry.insert(0, folder_selected)  # 插入选择的文件夹路径

        # 更新选中账号的视频文件夹路径
        if self.selected_account:
            self.selected_account["video_folder"] = folder_selected
            self.save_accounts()  # 保存更新后的账号信息

    def select_cover_folder(self):
        folder_selected = filedialog.askdirectory()
        self.cover_folder_entry.delete(0, tk.END)  # 清空当前输入
        self.cover_folder_entry.insert(0, folder_selected)  # 插入选择的文件夹路径

        # 更新选中账号的封面文件夹路径
        if self.selected_account:
            self.selected_account["cover_folder"] = folder_selected
            self.save_accounts()  # 保存更新后的账号信息

    def start_posting(self):
        selected_indices = self.account_listbox.curselection()  # 获取选中的账号索引
        if not selected_indices:
            messagebox.showwarning("警告", "请先选择至少一个账号！")
            return

        # 禁用开始发布按钮
        self.submit_button.config(state=tk.DISABLED)

        # 收集所有选中账号的信息
        accounts_info = []
        for index in selected_indices:
            account_info = {
                "username": self.accounts[index]["username"],
                "title": self.accounts[index].get("title", ""),
                "content": self.accounts[index].get("content", ""),
                "threshold": int(self.accounts[index].get("threshold", 10)),
                "cookie": self.accounts[index].get("cookie", ""),
                "proxy": self.accounts[index].get("proxy", ""),
                "wait_time": int(self.accounts[index].get("wait_time", 3600)),
                "first_post_immediate": self.accounts[index].get("first_post_immediate", 'y'),
                "video_folder": self.accounts[index].get("video_folder", ""),
                "cover_folder": self.accounts[index].get("cover_folder", ""),
            }
            accounts_info.append(account_info)

        # 创建线程名，包含所有选中账号的名字
        thread_name = "发布账号: " + ", ".join([account_info['username'] for account_info in accounts_info])
        posting_thread = threading.Thread(target=self.post_to_accounts, args=(accounts_info,), name=thread_name)
        posting_thread.start()
        # self.threads[posting_thread.ident] = posting_thread
        # 在 listbox 中插入线程名，并将 thread_id 作为附加数据存储
        # self.thread_listbox.insert(tk.END, f"{posting_thread.ident}: {thread_name}")
        # # 为每个线程添加一个终止按钮
        # terminate_button = tk.Button(self.master, text="终止", command=lambda tid=posting_thread.ident: self.prompt_terminate_account(posting_thread.ident))
        # self.thread_listbox.window_create(tk.END, window=terminate_button)

    def prompt_terminate_account(self, thread_id):
        """提示用户输入账号名字以终止"""
        username = simpledialog.askstring("终止账号", "请输入要终止的账号名称:")
        if username:
            self.terminate_account_in_thread(username, thread_id)

    def post_to_accounts(self, accounts_info):
        thread_id = threading.get_ident()
        # 初始化当前线程的终止账号集合
        if thread_id not in self.thread_terminated_accounts:
            self.thread_terminated_accounts[thread_id] = set()

        first_round = True  # 标志是否为第一轮发布
        while accounts_info:
            next_post_times = []
            remaining_accounts = []  # 用于存储未完成的账号信息
            for account_info in accounts_info:
                # 检查账号是否在当前线程中被终止
                if account_info['username'] in self.thread_terminated_accounts[thread_id]:
                    continue  # 跳过被终止的账号
                # 检查是否需要跳过
                if 'next_post_time' in account_info and account_info['next_post_time'] > datetime.now():
                    remaining_accounts.append(account_info)
                    next_post_times.append((account_info['next_post_time'], account_info))
                    continue

                # 创建 AutoPoster 实例（如果不存在）
                if 'poster' not in account_info:
                    account_info['poster'] = AutoPoster(
                        video_folder=account_info["video_folder"],
                        cover_folder=account_info["cover_folder"],
                        cookie=account_info["cookie"],
                        title=account_info["title"],
                        content=account_info["content"],
                        threshold=account_info["threshold"],
                        proxies=account_info["proxy"],
                        wait_time=account_info["wait_time"],
                        log_output=self.log_output,
                        first_post_immediate=account_info["first_post_immediate"] == 'y',
                        mode=2,
                        log_account_activity=self.log_account_activity,
                        log_user=account_info['username']
                    )
                
                # 开始发布
                poster = account_info['poster']
                     # 日志输出账号开始发布
                self.log_account_activity(account_info['username'], f"账号 {account_info['username']} 开始发布:第{poster.count}条")

                timeout_event = threading.Event()
                posting_thread = threading.Thread(target=self.run_posting_with_timeout, args=(poster, timeout_event))
                posting_thread.start()
                posting_thread.join(timeout=300)  # 等待最多5分钟

                if not timeout_event.is_set():
                    remaining_accounts.append(account_info)
                    if('next_post_time' in account_info):
                        next_post_times.append((account_info['next_post_time'], account_info))
                    self.log_account_activity(account_info['username'], f"账号 {account_info['username']} 发布超时，跳过...")
                    continue  # 跳过当前账号，继续下一个

                # 检查发布计数
                if poster.count < account_info['threshold']:
                    # 计算下一次发布的时间并更新 account_info
                    next_post_time = datetime.now() + timedelta(seconds=account_info['wait_time']) + timedelta(minutes=random.randint(1, 10))
                    account_info['next_post_time'] = next_post_time
                    self.log_account_activity(account_info['username'], f"账号 {account_info['username']} 第{poster.count} 条计算下一次发布时间：{next_post_time}后，下一条文件索引{poster.current_video_index}\n")
                    next_post_times.append((next_post_time, account_info))
                    remaining_accounts.append(account_info)

            accounts_info = remaining_accounts  # 更新 accounts_info

            if first_round:
                # 第一轮发布完成后重新启用按钮
                self.submit_button.config(state=tk.NORMAL)
                first_round = False  # 更新标志

            if not accounts_info:
                break
            if next_post_times:
                # 找到最近的下一次发布时间
                next_post_times.sort()
                next_time, next_account_info = next_post_times[0]
                if next_time < datetime.now():
                    wait_seconds = 600
                else:
                    wait_seconds = (next_time - datetime.now()).total_seconds()
                # 如果 wait_seconds 小于 600 秒，则将其赋值为 600 秒
                if wait_seconds < 600:
                    wait_seconds = 600
                for account_info in accounts_info:
                    self.log_account_activity(account_info['username'], f"账号 {account_info['username']} 第{wait_seconds} 分钟后进行全局检测\n")
                time.sleep(max(0, wait_seconds))
            else:
                break

        # 所有发布完成后（如果需要）可以再次启用按钮
        # self.submit_button.config(state=tk.NORMAL)

    def run_posting_with_timeout(self, poster, timeout_event):
        try:
            poster.start_posting()
            timeout_event.set()  # 如果成功完成，设置事件
        except Exception as e:
            self.log_account_activity(poster.log_user, f"发布失败: {str(e)}")
          

    def add_account(self):
        """新增账号"""
        username = simpledialog.askstring("新增账号", "请输入账号名称:")
        cookie = simpledialog.askstring("新增账号", "请输入账号 Cookie:")
        proxy = simpledialog.askstring("新增账号", "请输入账号代理:")
        if username and cookie:
            # 确保在新增账号时创建 accounts.json 文件
            if not os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)  # 创建一个的 JSON 数组

            self.accounts.append({
                "username": username,
                "cookie": cookie,
                "proxy": proxy,
                "video_folder": "",  # 新账号的文件夹路径
                "title": "",         # 新账号的标题
                "content": "",       # 新账号的内容
                "threshold": 10,     # 认阈值
                "wait_time": 3600    # 默认等待时间
            })
            self.save_accounts()  # 保存更新后的账号信息
            self.update_account_listbox()

    def delete_account(self):
        """删除账号"""
        if self.selected_account:
            self.accounts.remove(self.selected_account)
            self.save_accounts()  # 保存更新后的账号信息
            self.update_account_listbox()
            self.selected_account = None
            self.clear_publish_info()

    def clear_publish_info(self):
        """清空发布信息域"""
        self.video_folder_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.content_entry.delete(0, tk.END)
        self.threshold_entry.delete(0, tk.END)
        self.cookie_entry.delete(0, tk.END)  # 清空 Cookie
        self.proxy_entry.delete(0, tk.END)  # 清空 代理
        self.cover_folder_entry.delete(0, tk.END)

    def change_cookie(self):
        """更改 Cookie"""
        if self.selected_account:
            new_cookie = simpledialog.askstring("更改 Cookie", "请输入新的 Cookie:")
            if new_cookie:
                self.selected_account["cookie"] = new_cookie
                self.save_accounts()  # 保存更新后的账号信息
                self.update_account_listbox()

    def change_account_name(self):
        """更改账号名字"""
        if self.selected_account:
            new_name = simpledialog.askstring("更改账号名字", "请输入新的账号名称:")
            if new_name:
                self.selected_account["username"] = new_name
                self.save_accounts()  # 保存更新后的账号信息
                self.update_account_listbox()  # 更新账号列表框

    def change_proxy(self):
        """更改代理"""
        if self.selected_account:
            new_proxy = simpledialog.askstring("更改代理", "请输入新的代理:")  # 输入格式为 JSON 字符串
            if new_proxy:
                try:
                    # 将输入的 JSON 字符串转换为字典
                    self.selected_account["proxy"] = json.loads(new_proxy)
                    self.save_accounts()  # 保存更新后的账号信息
                    self.update_account_listbox()  # 更新账号列表框
                except json.JSONDecodeError:
                    messagebox.showerror("错误", "代理格式不正确，请使用有效的 JSON 格式。")

    # 新增保存账号内容的方
    def save_account_content(self):
        """保存当前填写的账号内容"""
        if self.selected_account:
            self.selected_account["title"] = self.title_entry.get()
            self.selected_account["content"] = self.content_entry.get()
            self.selected_account["threshold"] = int(self.threshold_entry.get())
            self.selected_account["wait_time"] = int(self.wait_time_entry.get() or 3600)
            self.selected_account["cover_folder"] = self.cover_folder_entry.get()
            self.selected_account["video_folder"] = self.video_folder_entry.get()  # 保存视频文件夹路径
            
            # 保存每个账号的 first_post_immediate 值
            self.selected_account["first_post_immediate"] = self.first_post_immediate_var.get()

            self.save_accounts()  # 保存更新后的账号信息
            messagebox.showinfo("成功", "账号内容已保存！")

    def show_account_logs(self, username):
        """显示指定账号的日志"""
        self.log_output.delete(1.0, tk.END)  # 清空当前日志
        if username in self.logs:
            self.log_output.insert(tk.END, self.logs[username])  # 显示该账号的日志

    def log_account_activity(self, username, message):
        logging.info(message)
        """记录账号活动日志"""
        if username not in self.logs:
            self.logs[username] = ""
        self.logs[username] += f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]:{message}\n"  # 添加时间戳
    def terminate_account_in_thread(self, username, thread_id):
        """在指定线程中标记账号为终止"""
        if thread_id in self.threads:
            # 标记账号为终止
            if thread_id not in self.thread_terminated_accounts:
                self.thread_terminated_accounts[thread_id] = set()
            self.thread_terminated_accounts[thread_id].add(username)
            messagebox.showinfo("信息", f"账号 {username} 在线程 {thread_id} 中已被终止发布。")

    def terminate_selected_thread(self):
        """终止选中的线程"""
        selection = self.thread_listbox.curselection()
        if selection:
            # 从 listbox 中获取选中的项目，并提取 thread_id
            selected_item = self.thread_listbox.get(selection[0])
            thread_id_str, thread_name = selected_item.split(": ", 1)
            thread_id = int(thread_id_str)

            if thread_id in self.threads:
                # 终止线程中的所有账号
                for account_info in self.threads[thread_id].accounts_info:
                    self.log_account_activity(account_info['username'], f"账号 {account_info['username']} 在线程 {thread_id} 中已被终止发布。")
                # 终止线程
                self.threads[thread_id].join(timeout=0)  # 假设线程可以被安全终止
                del self.threads[thread_id]
                self.thread_listbox.delete(selection[0])
                messagebox.showinfo("信息", f"线程 {thread_id} 已被终止。")

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManagerApp(root)
    root.mainloop()