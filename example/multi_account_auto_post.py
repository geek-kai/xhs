import os
import json
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, simpledialog
from auto_post import AutoPoster  # 导入 AutoPoster 类

class AccountManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("多账号自动发布工具")

        self.json_file_path = os.path.join(os.getcwd(), "accounts.json")  # 使用当前工作目录
        self.accounts = []  # 用于存储账号信息
        self.create_widgets()
        self.load_accounts()  # 加载账号信息

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

        # 将封面文件夹路径移动到视频文件夹路径下方
        tk.Label(self.master, text="封面文件夹路径:").grid(row=1, column=1)
        self.cover_folder_entry = tk.Entry(self.master)
        self.cover_folder_entry.grid(row=1, column=2)  # 调整为 row=1
        tk.Button(self.master, text="选择文件夹", command=self.select_cover_folder).grid(row=1, column=3)

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
        self.cookie_entry = tk.Entry(self.master)
        self.cookie_entry.grid(row=5, column=2)

        tk.Label(self.master, text="代理（可选）:").grid(row=6, column=1)
        self.proxy_entry = tk.Entry(self.master)
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

        # 账号管理按钮
        tk.Button(self.master, text="新增账号", command=self.add_account).grid(row=11, column=0)
        tk.Button(self.master, text="删除账号", command=self.delete_account).grid(row=11, column=1)
        tk.Button(self.master, text="更改 Cookie", command=self.change_cookie).grid(row=11, column=2)

        self.update_account_listbox()

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
            self.cookie_entry.config(state='normal')  # 设置为可编辑
            self.cookie_entry.delete(0, tk.END)
            self.cookie_entry.insert(0, self.selected_account.get("cookie", ""))  # 显示 Cookie
            self.proxy_entry.config(state='normal')  # 设置为可编辑
            self.proxy_entry.delete(0, tk.END)
            self.proxy_entry.insert(0, self.selected_account.get("proxy", ""))  # 显示代理
            self.cover_folder_entry.delete(0, tk.END)
            self.cover_folder_entry.insert(0, self.selected_account.get("cover_folder", ""))
            self.wait_time_entry.delete(0, tk.END)
            self.wait_time_entry.insert(0, self.selected_account.get("wait_time", "3600")) 

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
        if not self.selected_account:
            messagebox.showwarning("警告", "请先选择一个账号！")
            return

        # 更新选中账号的信息
        self.selected_account["title"] = self.title_entry.get()
        self.selected_account["content"] = self.content_entry.get()
        self.selected_account["threshold"] = int(self.threshold_entry.get())
        self.selected_account["cookie"] = self.cookie_entry.get()  # 更新 Cookie
        self.selected_account["proxy"] = self.proxy_entry.get()  # 更新代理
        self.selected_account["wait_time"] = int(self.wait_time_entry.get() or 3600)  # 更新等待时间，默认为3600秒
        self.selected_account["first_post_immediate"] = self.first_post_immediate_var.get()  # 更新立即发布选项
        self.save_accounts()  # 保存更新后的账号信息

        # 创建 AutoPoster 实例
        poster = AutoPoster(
            video_folder=self.selected_account.get("video_folder", ""),  # 视频文件夹路径
            cover_folder=self.selected_account.get("cover_folder", ""),  # 封面文件夹路径
            cookie=self.selected_account["cookie"],  # Cookie
            title=self.selected_account["title"],  # 标题
            content=self.selected_account["content"],  # 内容
            threshold=self.selected_account["threshold"],  # 发布阈值
            proxies=self.selected_account.get("proxy", None),  # 代理
            wait_time=self.selected_account["wait_time"],  # 等待时间
            log_output=self.log_output,  # 传递日志输出框
            first_post_immediate=self.selected_account["first_post_immediate"] == 'y',  # 立即发布选项
            mode=2  # 发布模式，假设为2
        )
        
        # 开始发布
        poster.start_posting()

    def add_account(self):
        """新增账号"""
        username = simpledialog.askstring("新增账号", "请输入账号名称:")
        cookie = simpledialog.askstring("新增账号", "请输入账号 Cookie:")
        proxy = simpledialog.askstring("新增账号", "请输入账号代理:")
        if username and cookie:
            # 确保在新增账号时创建 accounts.json 文件
            if not os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)  # 创建一个空的 JSON 数组

            self.accounts.append({
                "username": username,
                "cookie": cookie,
                "proxy": proxy,
                "video_folder": "",  # 新账号的文件夹路径
                "title": "",         # 新账号的标题
                "content": "",       # 新账号的内容
                "threshold": 10,     # 默认阈值
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
        """清空发布信息区域"""
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

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManagerApp(root)
    root.mainloop()