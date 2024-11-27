import requests


# 贵州
# proxies = {"http": "http://fI128621f2:cenqvFZ0@182.43.137.236:8894", "https": "http://fI128621f2:cenqvFZ0@182.43.137.236:8894"}
# 杭州
proxies = {"http": "http://blH66715R7:knpsVYZ6@125.124.6.52:8893", "https": "http://blH66715R7:knpsVYZ6@125.124.6.52:8893"}
#     "http": "http://125.124.6.52:8893",
#     "https": "http://125.124.6.52:8893"
# }
try:
    response = requests.get("https://www.baidu.com", proxies=proxies)
    print("成功连接:", response.status_code)
except requests.exceptions.RequestException as e:
    print("连接失败:", str(e))