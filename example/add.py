import datetime
import json
import sys
import os
import requests
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("当前工作目录:", os.getcwd())
print("模块路径:", sys.path)
from xhs.core import XhsClient

def test_proxy():
   
    
    try:
        # 访问 ip 检测网站
        response = requests.get('http://httpbin.org/ip')
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
def add(

    cookie,  # 保持为必填参数

    title,   # 保持为必填参数

    content,  
    good_id=None, 

    good_name=None, 

    proxies=None,

    cover_path=None,

    topics=None, 

    video_path=None# 保持为必填参数

):
    """
    发布笔记接口
    :param good_id: 商品ID
    :param good_name: 商品名称
    :param cookie: 用户cookie
    :param proxies: 代理配置，格式如 {"http": "socks5://user:pass@ip:port", "https": "socks5://user:pass@ip:port"}
    :param title: 笔记标题
    :param content: 笔记内容
    :param cover_path: 封面图片路径，视频笔记可选
    :param topics: 话题列表，例如 ["话题1", "话题2"]
    :param image_list: 图片路径列表，例如 ["path/to/image1.jpg", "path/to/image2.jpg"]
    :param video_path: 视频路径，与 image_list 二选一
    :return: 
    """
    client = XhsClient(cookie=cookie, proxies=proxies,sign=sign,timeout=120)
    
    # 处理话题
    if topics:
        formatted_topics = [f"#{topic}" for topic in topics]
        content = content + " " + " ".join(formatted_topics)
    
    # 根据是否有视频来决定发布类型
    if video_path:
        media_path = video_path
        # 如果提供了封面，使用提供的封面
    if cover_path:
       cover = cover_path

    print(f"发布笔记参数: title={title}, video_path={media_path}, desc={content}, cover_path={cover}, goodId={good_id}, goodName={good_name}")

    try:
        client.create_video_note(
            title=title,
            video_path=media_path,
            desc=content,
            cover_path=cover,
            goodId=good_id,
            goodName=good_name
        )
    except Exception as e:
        print(f"发布笔记时发生错误: {str(e)}")
        traceback.print_exc()  # 输出完整的错误堆栈跟踪 

if __name__=="__main__":

      
    add(
        good_id="672df3667d7d360001c1b1b2",
        good_name="不锈钢台面锅架防烫隔热锅垫蒸架锅具收纳放锅桌面置物蒸菜隔热",
        topics=["厨房", "宜家"],
        proxies={
            "http": "socks5://ptI31320x3:blnstIJ2@101.89.108.232:8864",
            "https": "socks5://ptI31320x3:blnstIJ2@101.89.108.232:8864"
        },
        video_path="E:\\小红书连怼\\1.mp4 ",
        cover_path="E:\\小红书连怼\\封面\\1.jpg",
        cookie="a1=1930c3208c2st1lsvuv2vd79o36rlvlr891bx0fyf50000418831; webId=8edebd39d092a116b1ee22a59ada1647; gid=yjq8SqJySyY0yjq8SqJ8Yj8iSJM9y1Mh7hJhyvifWjlqKD28F1h1FC8884yYYqy8iWYW4DDK; x-user-id-creator.xiaohongshu.com=6472c13d0000000010034a47; customerClientId=736660462325024; access-token-creator.xiaohongshu.com=customer.creator.AT-68c5174349219452291637559ybuwz9w9kosyiop; galaxy_creator_session_id=9zLJ04tDKmDS1YWUlt0sT68p6fvEATGc1Syq; galaxy.creator.beaker.session.id=1731077662909005479993; access-token-ark.beta.xiaohongshu.com=; customer-sso-sid=68c5174356602028522753461f5ea207a2b6a303; x-user-id-ark.xiaohongshu.com=5f6c75da000000000100502a; access-token-ark.xiaohongshu.com=customer.ark.AT-68c5174356602114422099524mqinwrt7mjlbaif; beaker.session.id=15b5da170c5aead0cd4eb23a24b8b343bbafe50egAJ9cQEoWA4AAAByYS11c2VyLWlkLWFya3ECWBgAAAA2NWVjNjZkNWUzMDAwMDAwMDAwMDAwMDFxA1UIX2V4cGlyZXNxBGNkYXRldGltZQpkYXRldGltZQpxBVUKB+gLDQAQEASnxYVScQZYCwAAAGFyay1saWFzLWlkcQdYGAAAADY1ZWM2ODExYmY3ZmI2MDAwMWZjYzkyZnEIWA4AAABfYWNjZXNzZWRfdGltZXEJR0HZzLSJrzddVQNfaWRxClggAAAAZGVhNWIzZDg5ZTZkNGJmZTlkNDQ1MmRlNjg2MzYzOGNxC1gRAAAAcmEtYXV0aC10b2tlbi1hcmtxDFhBAAAAMjFlZTIxN2M3ZDllNDFhNTk1MmNhNDI4Zjg4MGQzMzEtYzk3Mzg4MzRmNmFkNDBiYzk3NjJmYTI5YTE1YjY0OGFxDVgOAAAAX2NyZWF0aW9uX3RpbWVxDkdB2ciLFdLQ5XUu; webBuild=4.42.2; xsecappid=xhs-pc-web; acw_tc=556206320c4b439a097a8eb65289f64745f551f2bb72733ae53f25b87ea20886; websectiga=cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c; sec_poison_id=735f8801-ca22-43a7-8478-e5d37f68f0d5; web_session=040069b5068275111a11407006354b83b4a1c3; unread={%22ub%22:%22672746cf000000001a01fc41%22%2C%22ue%22:%226731db9d000000001b0102d6%22%2C%22uc%22:26}",
        title="感谢宜家！🌈这个小东西也太好用了！🐂",
        content="姐妹们👭！！这个小东西一定要冲，有了这个厨房做饭可方便多了，锅台再也不怕被烫了！！😆😆",
    )
    # test_proxy()
