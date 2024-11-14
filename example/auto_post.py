import os
import time
import random
from datetime import datetime
import logging
from typing import List, Tuple
import sys

# 添加项目根目录到 Python 路径
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from add import add  # 使用绝对导入

class AutoPoster:
    def __init__(
        self,
        video_folder: str,
        cover_folder: str,
        cookie: str,
        title: str,
        content: str,
        good_id=None,
        good_name=None,
        topics=None,
        proxies=None
    ):
        self.video_folder = video_folder
        self.cover_folder = cover_folder
        self.cookie = cookie
        self.title = title
        self.content = content
        self.good_id = good_id
        self.good_name = good_name
        self.topics = topics
        self.proxies = proxies
        
        # 初始化日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 获取所有视频和封面文件
        self.video_files = self._get_files(video_folder, ['.mp4', '.MP4'])
        self.cover_files = self._get_files(cover_folder, ['.jpg', '.JPG', '.png', '.PNG'])
        
        # 添加调试信息
        logging.info(f"找到的视频文件: {self.video_files}")
        logging.info(f"找到的封面文件: {self.cover_files}")

        # 检查是否为空
        if not self.video_files:
            logging.warning("视频文件夹为空！")
        if not self.cover_files:
            logging.warning("封面文件夹为空！")

        # 当前索引
        self.current_video_index = 0
        self.current_cover_index = 0

    def _get_files(self, folder: str, extensions: List[str]) -> List[str]:
        """获取指定文件夹下的所有指定扩展名的文件完整路径"""
        files = []
        for file in os.listdir(folder):
            if any(file.endswith(ext) for ext in extensions):
                files.append(os.path.join(folder, file))
        return sorted(files)  # 排序确保顺序一致

    def _get_next_files(self) -> Tuple[str, str]:
        """获取下一个要发布的视频和封面文件"""
        if not self.video_files or not self.cover_files:
            raise ValueError("视频或封面文件夹为空！")

        video = self.video_files[self.current_video_index]
        cover = self.cover_files[self.current_cover_index]

        # 更新索引
        self.current_video_index = (self.current_video_index + 1) % len(self.video_files)
        self.current_cover_index = (self.current_cover_index + 1) % len(self.cover_files)

        return video, cover

    def start_posting(self):
        """开始自动发布流程"""
        while True:
            try:
                video_path, cover_path = self._get_next_files()
                
                # 发布笔记
                logging.info(f"正在发布视频: {video_path}")
                logging.info(f"使用封面: {cover_path}")
                
                add(
                    good_id=self.good_id,
                    good_name=self.good_name,
                    cookie=self.cookie,
                    proxies=self.proxies,
                    title=self.title,
                    content=self.content,
                    topics=self.topics,
                    cover_path=cover_path,
                    video_path=video_path
                )
                
                logging.info("发布成功！")
                
                # 随机等待时间：30分钟 + (0-10分钟的随机值)
                wait_time = 1800 + random.randint(0, 600)
                next_post_time = datetime.now().timestamp() + wait_time
                logging.info(f"下次发布时间: {datetime.fromtimestamp(next_post_time).strftime('%Y-%m-%d %H:%M:%S')}")
                
                time.sleep(wait_time)
                
            except Exception as e:
                logging.error(f"发布失败: {str(e)}")
                time.sleep(300)  # 发生错误等待5分钟后继续

if __name__ == "__main__":
    # 使用示例
    poster = AutoPoster(
        video_folder="E:\\小红书连怼\\夹子\\视频",
        cover_folder="E:\\小红书连怼\\夹子\\封面",
        cookie="a1=1930c3208c2st1lsvuv2vd79o36rlvlr891bx0fyf50000418831; webId=8edebd39d092a116b1ee22a59ada1647; gid=yjq8SqJySyY0yjq8SqJ8Yj8iSJM9y1Mh7hJhyvifWjlqKD28F1h1FC8884yYYqy8iWYW4DDK; x-user-id-creator.xiaohongshu.com=6472c13d0000000010034a47; customerClientId=736660462325024; access-token-creator.xiaohongshu.com=customer.creator.AT-68c5174349219452291637559ybuwz9w9kosyiop; galaxy_creator_session_id=9zLJ04tDKmDS1YWUlt0sT68p6fvEATGc1Syq; galaxy.creator.beaker.session.id=1731077662909005479993; access-token-ark.beta.xiaohongshu.com=; customer-sso-sid=68c5174356602028522753461f5ea207a2b6a303; x-user-id-ark.xiaohongshu.com=5f6c75da000000000100502a; access-token-ark.xiaohongshu.com=customer.ark.AT-68c5174356602114422099524mqinwrt7mjlbaif; beaker.session.id=15b5da170c5aead0cd4eb23a24b8b343bbafe50egAJ9cQEoWA4AAAByYS11c2VyLWlkLWFya3ECWBgAAAA2NWVjNjZkNWUzMDAwMDAwMDAwMDAwMDFxA1UIX2V4cGlyZXNxBGNkYXRldGltZQpkYXRldGltZQpxBVUKB+gLDQAQEASnxYVScQZYCwAAAGFyay1saWFzLWlkcQdYGAAAADY1ZWM2ODExYmY3ZmI2MDAwMWZjYzkyZnEIWA4AAABfYWNjZXNzZWRfdGltZXEJR0HZzLSJrzddVQNfaWRxClggAAAAZGVhNWIzZDg5ZTZkNGJmZTlkNDQ1MmRlNjg2MzYzOGNxC1gRAAAAcmEtYXV0aC10b2tlbi1hcmtxDFhBAAAAMjFlZTIxN2M3ZDllNDFhNTk1MmNhNDI4Zjg4MGQzMzEtYzk3Mzg4MzRmNmFkNDBiYzk3NjJmYTI5YTE1YjY0OGFxDVgOAAAAX2NyZWF0aW9uX3RpbWVxDkdB2ciLFdLQ5XUu; webBuild=4.42.2; xsecappid=xhs-pc-web; acw_tc=556206320c4b439a097a8eb65289f64745f551f2bb72733ae53f25b87ea20886; websectiga=cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c; sec_poison_id=735f8801-ca22-43a7-8478-e5d37f68f0d5; web_session=040069b5068275111a11407006354b83b4a1c3; unread={%22ub%22:%22672746cf000000001a01fc41%22%2C%22ue%22:%226731db9d000000001b0102d6%22%2C%22uc%22:26}",
        title="感谢宜家，打开收纳新思路！！",
        content="感谢宜家，打开收纳新思路！！",
        good_id="672cc6436a6c1800019115ff",
        proxies={
            "http": "socks5://ptI31320x3:blnstIJ2@101.89.108.232:8864",
            "https": "socks5://ptI31320x3:blnstIJ2@101.89.108.232:8864"
        },
    )
    poster.start_posting() 