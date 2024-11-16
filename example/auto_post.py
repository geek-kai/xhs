import os
import time
import random
from datetime import datetime
import logging
from typing import List, Tuple
import sys
import traceback

# 添加项目根目录到 Python 路径
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from add import add  # 使用绝对导入

class AutoPoster:
    def __init__(
        self,
        video_folder: str,
        cookie: str,
        title: str,
        content: str,
        threshold: int,
        cover_folder: str = None,
        good_id=None,
        good_name=None,
        topics=None,
        proxies =None
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
        self.threshold = threshold
        
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
        if not self.video_files:
            raise ValueError("视频文件夹为空！")

        video = self.video_files[self.current_video_index]

        # 检查封面文件列表是否为空
        cover = None  # 默认值为 None
        if self.cover_files:  # 只有在封面文件列表不为空时才访问
            cover = self.cover_files[self.current_cover_index]
            self.current_cover_index = (self.current_cover_index + 1) % len(self.cover_files)

        # 更新索引
        self.current_video_index = (self.current_video_index + 1) % len(self.video_files)

        return video, cover

    def start_posting(self):
        """开始自动发布流程"""
        post_count = 0
        while post_count < self.threshold:
            try:
                video_path, cover_path = self._get_next_files()
                
                # 发布笔记
                logging.info(f"正在发布视频: {video_path}")
                logging.info(f"使用封面: {cover_path if cover_path else '无封面'}")
                
                # 确保 cover_path 有值
                cover = cover_path if cover_path else None
                
                add(
                    good_id=self.good_id,
                    good_name=self.good_name,
                    cookie=self.cookie,
                    proxies=self.proxies,
                    title=self.title,
                    content=self.content,
                    topics=self.topics,
                    cover_path=cover,  # 确保 cover 变量被传递
                    video_path=video_path
                )
                
                logging.info("发布成功！")
                post_count += 1
                
                # 随机等待时间：30分钟 + (0-10分钟的随机值)
                wait_time = 1800 + random.randint(0, 600)
                next_post_time = datetime.now().timestamp() + wait_time
                logging.info(f"下次发布时间: {datetime.fromtimestamp(next_post_time).strftime('%Y-%m-%d %H:%M:%S')}")
                
                time.sleep(wait_time)
                
            except Exception as e:
                logging.error(f"发布失败: {str(e)}")
                traceback.print_exc()
                time.sleep(300)  # 发生错误等待5分钟后继续

if __name__ == "__main__":
    # 引导用户输入参数
    video_folder = input("请输入视频文件夹路径: ")
    cover_folder = input("请输入封面文件夹路径（可选，直接按回车跳过）: ") or None
    cookie = input("请输入cookie: ")
    title = input("请输入标题: ")
    content = input("请输入内容: ")
    threshold = int(input("请输入发布阈值: "))
    proxies= str(input("请输入proxies: （可选，直接按回车跳过）:  "))
    topics=str(input("请输入话题: （可选，直接按回车跳过）:  "))
    goodId=str(input("请输入商品id: （可选，直接按回车跳过）:  "))

    # 创建 AutoPoster 实例
    poster = AutoPoster(
        video_folder=video_folder,
        cover_folder=cover_folder,
        cookie=cookie,
        topics=topics,
        title=title,
        content=content,
        threshold=threshold,
        proxies= proxies,
        good_id=goodId,
    )
    #  # 创建 AutoPoster 实例
    # poster = AutoPoster(
    #     video_folder="D:\小红书\酸枣仁\视频",
    #     cover_folder="D:\小红书\酸枣仁\封面",
    #     cookie="a1=18f04f026c73hvt0qbnsxsexoyxv1aeoiranzb4qp00000182341; webId=2b6b30997506d15bd44b819bc2eadd02; gid=yYi84i82DK32yYi84i8JKFD4SWqxh98ADIMC0AUMdClvCI88hy0dlu888yYJq4y8DYq8Wiq2; customerClientId=616579123539810; timestamp2=17149807288790a3c5b7db37505101975fd3d2e564e3368345efd7b7a2b8450; timestamp2.sig=HgAIE6q7IQZXGeN5ut5i_sqyHhbmu5JvGGgavFgRAVs; x-user-id-redlive.xiaohongshu.com=663b87510000000003031657; customer-sso-sid=68c51739000404764324813072b71ba8d6351cba; x-user-id-ark.xiaohongshu.com=5f6c75da000000000100502a; abRequestId=2b6b30997506d15bd44b819bc2eadd02; webBuild=4.43.0; xsecappid=xhs-pc-web; acw_tc=3f16768d123ed0d2176001127b9fddb6660d5689a9aef4b0f2766a740b632d98; websectiga=634d3ad75ffb42a2ade2c5e1705a73c845837578aeb31ba0e442d75c648da36a; sec_poison_id=1d640f81-2120-488d-94eb-6a0a69824091; web_session=040069b6404ca42493dd1b3300354b096f00cc; unread={%22ub%22:%2267347048000000001901a740%22%2C%22ue%22:%2267162fa10000000024019cce%22%2C%22uc%22:29}",
    #     title="这个小妙招很有用",
    #     content="这个小妙招很有用",
    #     threshold=3,
    #     proxies= {
    #         "http": "socks5://uEU17768qt:mzFGHKLV@121.224.7.202:8864",
    #         # "https": "socks5://uEU17768qt:mzFGHKLV@121.224.7.202:8864"
    #     }
    # )
    # logging.info(poster)
    poster.start_posting() 