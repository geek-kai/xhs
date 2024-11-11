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

def add(
    good_id, 
    good_name, 
    cookie, 
    proxies,
    title, 
    content, 
    topics=None, 
    image_list=None, 
    video_path=None
):
    """
    发布笔记接口
    :param good_id: 商品ID
    :param good_name: 商品名称
    :param cookie: 用户cookie
    :param proxies: 代理配置，格式如 {"http": "socks5://user:pass@ip:port", "https": "socks5://user:pass@ip:port"}
    :param title: 笔记标题
    :param content: 笔记内容
    :param topics: 话题列表，例如 ["话题1", "话题2"]
    :param image_list: 图片路径列表，例如 ["path/to/image1.jpg", "path/to/image2.jpg"]
    :param video_path: 视频路径，与 image_list 二选一
    :return: 
    """
    client = XhsClient(cookie=cookie, proxies=proxies)
    
    # 处理话题
    if topics:
        formatted_topics = [f"#{topic}" for topic in topics]
        content = content + " " + " ".join(formatted_topics)
    
    # 根据是否有视频来决定发布类型
    if video_path:
        note_type = "video"
        media_path = video_path
    elif image_list:
        note_type = "image"
        media_path = image_list
    else:
        note_type = "text"
        media_path = None
    
    try:
        client.create_video_note(
            title=title,
            video_path=media_path,
            desc=content,
            cover_path="E:\\小红书连怼\\封面\\1.jpg",
            goodId=good_id,
            goodName=good_name
        )
    except Exception as e:
        print(f"发布笔记时发生错误: {str(e)}")

if __name__=="__main__":
    add(
        good_id="672df3667d7d360001c1b1b2",
        good_name="不锈钢台面锅架防烫隔热锅垫蒸架锅具收纳放锅桌面置物蒸菜隔热",
        cookie="abRequestId=d9b18de7-6ca8-55e9-8140-43dae230dbdb; a1=1930c3208c2st1lsvuv2vd79o36rlvlr891bx0fyf50000418831; webId=8edebd39d092a116b1ee22a59ada1647; gid=yjq8SqJySyY0yjq8SqJ8Yj8iSJM9y1Mh7hJhyvifWjlqKD28F1h1FC8884yYYqy8iWYW4DDK; Hm_lvt_ed0a6497a1fdcdb3cdca291a7692408d=1730293384,1730472630,1731076428,1731077526; HMACCOUNT=F2E2DD1CD05D59D2; Hm_lvt_b9c922e90e336685a1120680d95d84af=1730293384,1730472630,1731076428,1731077526; customer-sso-sid=68c517434921945230256995463d5d71daf05770; x-user-id-creator.xiaohongshu.com=6472c13d0000000010034a47; customerClientId=736660462325024; access-token-creator.xiaohongshu.com=customer.creator.AT-68c5174349219452291637559ybuwz9w9kosyiop; galaxy_creator_session_id=9zLJ04tDKmDS1YWUlt0sT68p6fvEATGc1Syq; galaxy.creator.beaker.session.id=1731077662909005479993; acw_tc=0a00d88117311284797368220e46719199aa8947313605debed51e52e8a608; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=ff560dcc-6082-4521-ba34-cfeb1979892e; unread={%22ub%22:%22672a04d8000000001b028caa%22%2C%22ue%22:%22672d7616000000001b02da5b%22%2C%22uc%22:25}; webBuild=4.42.2; xsecappid=xhs-pc-web; web_session=040069b659c8a523cc22a0a41b354b80bb84d8; Hm_lpvt_b9c922e90e336685a1120680d95d84af=1731128541; Hm_lpvt_ed0a6497a1fdcdb3cdca291a7692408d=1731128541",
        proxies={
            "http": "socks5://ptI31320x3:blnstIJ2@101.89.108.232:8864",
            "https": "socks5://ptI31320x3:blnstIJ2@101.89.108.232:8864"
        },
        title="感谢宜家！🌈这个小东西也太好用了！🐂",
        content="姐妹们👭！！这个小东西一定要冲，有了这个厨房做饭可方便多了，锅台再也不怕被烫了！！😆😆",
        topics=["厨房", "宜家"],
        image_list=["E:\\小红书连怼\\封面\\1.jpg"]
    )
    # test_proxy()
