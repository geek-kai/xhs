from selenium import webdriver  # 新增导入
from selenium.webdriver.chrome.service import Service  # 新增导入
from webdriver_manager.chrome import ChromeDriverManager  # 新增导入

# ... 现有代码 ...

class AutoPoster:
    # ... 现有代码 ...

    def get_cookie_from_browser(self) -> str:
        """打开浏览器并获取用户登录后的 cookie"""
        # 启动 Chrome 浏览器
        options = webdriver.ChromeOptions()
        options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  # 替换为实际的 Chrome 安装路径
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # 打开登录页面
        driver.get("https://www.xiaohongshu.com/explore")  # 替换为实际登录页面的 URL

        input("请扫码登录后按回车继续...")  # 等待用户扫码登录

        # 获取 cookie
        cookies = driver.get_cookies()
        driver.quit()  # 关闭浏览器

        # 将 cookie 转换为字符串格式
        cookie_str = ";".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        return cookie_str

    def start_posting(self):
        """开始自动发布流程"""
        # 获取 cookie
        self.cookie = self.get_cookie_from_browser()  # 更新 cookie 获取方式
        # ... 现有代码 ...

if __name__ == "__main__":
    poster = AutoPoster()  # 创建 AutoPoster 实例
    print(poster.get_cookie_from_browser())  # 调用实例方法
    # ... 现有代码 ...