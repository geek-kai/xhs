import requests

proxies = {
    "http": "socks5://uEU17768qt:mzFGHKLV@121.224.7.202:8864",
    "https": "socks5://uEU17768qt:mzFGHKLV@121.224.7.202:8864"
}

try:
    response = requests.get("https://www.baidu.com", proxies=proxies)
    print("成功连接:", response.status_code)
except requests.exceptions.RequestException as e:
    print("连接失败:", str(e))