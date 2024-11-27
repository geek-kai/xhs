import requests

proxies = {
    "http": "socks5://blH66715R7:knpsVYZ6@125.124.6.52:8863",
    "https": "socks5://blH66715R7:knpsVYZ6@125.124.6.52:8863"
}

try:
    response = requests.get("https://www.baidu.com", proxies=proxies)
    print("成功连接:", response.status_code)
except requests.exceptions.RequestException as e:
    print("连接失败:", str(e))