import datetime
import json

import requests

import xhs.help
from xhs import XhsClient

def test_proxy():
    proxies = {
        "http": "socks5://cyGL8848PW:gmrvzN69@125.124.149.156:8865",
        "https": "socks5://cyGL8848PW:gmrvzN69@125.124.149.156:8865"
    }
    
    try:
        # 访问 ip 检测网站
        response = requests.get('http://httpbin.org/ip', proxies=proxies)
        print(f"当前IP: {response.json()['origin']}")
    except Exception as e:
        print(f"代理测试失败: {str(e)}")

def sign(uri, data=None, a1="", web_session=""):
    try:
        # 填写自己的 flask 签名服务端口地址
        res = requests.post("http://localhost:5005/sign",
                          json={"uri": uri, "data": data, "a1": a1, "web_session": web_session},
                          verify=False)
        
        # 打印响应内容和状态码，用于调试
        print(f"签名服务器状态码: {res.status_code}")
        print(f"签名服务器响应内容: {res.text}")
        
        # 检查响应状态码
        if res.status_code != 200:
            raise Exception(f"签名服务器返回错误状态码: {res.status_code}")
            
        signs = res.json()
        return {
            "x-s": signs["x-s"],
            "x-t": signs["x-t"]
        }
    except requests.exceptions.RequestException as e:
        print(f"请求签名服务器时发生错误: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        print(f"解析签名服务器响应时发生错误: {str(e)}")
        print(f"响应内容: {res.text}")
        raise

def add():
    cookie = "abRequestId=d9b18de7-6ca8-55e9-8140-43dae230dbdb; xsecappid=xhs-pc-web; a1=1930c3208c2st1lsvuv2vd79o36rlvlr891bx0fyf50000418831; webId=8edebd39d092a116b1ee22a59ada1647; acw_tc=66988f016322f8651a1a9b5a68ed3bf07810bb5d01216b35651c740f0c807f74; gid=yjq8SqJySyY0yjq8SqJ8Yj8iSJM9y1Mh7hJhyvifWjlqKD28F1h1FC8884yYYqy8iWYW4DDK; webBuild=4.42.1; websectiga=16f444b9ff5e3d7e258b5f7674489196303a0b160e16647c6c2b4dcb609f4134; sec_poison_id=67447be5-333e-44f3-b92e-6f791c0aa197; web_session=040069b5068275111a11c36d1b354b9298c896; unread={%22ub%22:%22672de00d000000003c01cb83%22%2C%22ue%22:%22671e07e00000000024014f3f%22%2C%22uc%22:24}"
    # proxies = {
    #     "http": "socks5://cyGL8848PW:gmrvzN69@125.124.149.156:8865",
    #     "https": "socks5://cyGL8848PW:gmrvzN69@125.124.149.156:8865"
    # }

    proxies = {
        "http": "socks5://ptI31320x3:blnstIJ2@101.89.108.232:8864",
        "https": "socks5://ptI31320x3:blnstIJ2@101.89.108.232:8864"
    }
    
    
    

    xhs_client = XhsClient(cookie, sign=sign, proxies=proxies)
    
    try:
        xhs_client.create_video_note(
            title="感谢宜家！🌈这个小东西也太好用了！🐂", 
            video_path="E:\\小红书连怼\\8.mp4", 
            desc="姐妹们👭！！这个小东西一定要冲，有了这个厨房做饭可方便多了，锅台再也不怕被烫了！！😆😆",
            cover_path="E:\\小红书连怼\\封面\\1.jpg",
            goodId="672df3667d7d360001c1b1b2", 
             goodName="不锈钢台面锅架防烫隔热锅垫蒸架锅具收纳放锅桌面置物蒸菜隔热" ,# 直接传递商品ID字符串
        )
    except Exception as e:
        print(f"发布笔记时发生错误: {str(e)}")
if __name__=="__main__":
    add()
    # test_proxy()
