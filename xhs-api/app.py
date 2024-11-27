import time
import threading
from flask import Flask, request
from gevent import monkey
from playwright.sync_api import sync_playwright
import os
import logging
monkey.patch_all()
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.log')

logging.basicConfig(
    filename=log_file_path,  # 日志文件名
    level=logging.DEBUG,  # 日志级别
    format='%(asctime)s - %(levelname)s - %(message)s', # 日志格式
    encoding='utf-8'  # 设置日志文件编码为 UTF-8

)
app = Flask(__name__)

global_a1 = ""

# 创建一个锁
page_lock = threading.Lock()


def get_context_page(instance, stealth_js_path):
    chromium = instance.chromium
    browser = chromium.launch(headless=True)
    context = browser.new_context()
    context.add_init_script(path=stealth_js_path)
    page = context.new_page()
    return context, page

current_dir = os.getcwd()

# 使用绝对路径
stealth_js_path = os.path.join(current_dir, "stealth.min.js")

logging.info("正在启动 playwright")
playwright = sync_playwright().start()
browser_context, context_page = get_context_page(playwright, stealth_js_path)
context_page.goto("https://www.xiaohongshu.com")
logging.info("正在跳转至小红书首页")
time.sleep(5)

context_page.reload()
time.sleep(1)
cookies = browser_context.cookies()
for cookie in cookies:
    if cookie["name"] == "a1":
        global_a1 = cookie["value"]
        logging.info("当前浏览器中 a1 值为：" + global_a1 + "，请将您的 cookie 中的 a1 也设置成一样，方可签名成功")
logging.info("跳转小红书首页成功，等待调用")


def sign(uri, data, a1, web_session):
    with page_lock:
        global global_a1
        if a1 != global_a1:
            logging.info(f"a1 值不一致，正在更新 a1 值: {a1}")
            browser_context.add_cookies([
                {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}
            ])
            context_page.reload()
            time.sleep(1)
            global_a1 = a1
        else:
            logging.info(f"a1 值一致，无需更新")
            context_page.reload()
            time.sleep(2)

        logging.info(f"开始签名")
        # 确保页面加载完成
        encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
        logging.info(f"签名成功")
        return {
            "x-s": encrypt_params["X-s"],
            "x-t": str(encrypt_params["X-t"])
        }


@app.route("/sign", methods=["POST"])
def hello_world():
    json = request.json
    uri = json["uri"]
    data = json["data"]
    a1 = json["a1"]
    web_session = json["web_session"]
    return sign(uri, data, a1, web_session)


@app.route("/a1", methods=["GET"])
def get_a1():
    return {'a1': global_a1}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5005)
