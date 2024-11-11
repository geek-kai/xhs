import os
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

class PublishTask:
    def __init__(self, 
                 cookie: str,
                 proxies: Dict,
              
                 video_folder: str,
                 mode: int,  # 1: 正常发布, 2: 循环发布
                 interval_minutes: int = 30,  # 循环发布间隔时间(分钟)
                 float_minutes: int = 15,     # 浮动时间(分钟)
                 threshold: int = 10          # 发布阈值
                ):
        self.cookie = cookie
        self.proxies = proxies
        self.video_folder = video_folder
        self.mode = mode
        self.interval_minutes = interval_minutes
        self.float_minutes = float_minutes
        self.threshold = threshold
        self.videos = []  # 存储视频信息列表
        
    def load_videos(self):
        """加载文件夹中的视频信息"""
        video_files = [f for f in os.listdir(self.video_folder) 
                      if f.endswith(('.mp4', '.mov', '.avi'))]
        for video_file in video_files:
            self.videos.append({
                'video_path': os.path.join(self.video_folder, video_file),
                'title': '',           # 待客户端填写
                'content': '',         # 待客户端填写
                'cover_path': '',    
                'good_id':'',
                'good_name' :'', # 待客户端填写
                'post_time': None      # 待客户端填写
            })
        return self.videos

    def execute(self):
        """执行发布任务"""
        if self.mode == 1:  # 正常发布
            self._normal_publish()
        else:  # 循环发布
            self._cycle_publish()

    def _normal_publish(self):
        """正常发布模式"""
        for video in self.videos:
            if video['post_time'] and datetime.now() < video['post_time']:
                # 等待到指定时间发布
                time.sleep((video['post_time'] - datetime.now()).total_seconds())
            
            self._publish_single_video(video)

    def _cycle_publish(self):
        """循环发布模式"""
        published_count = 0
        video_index = 0
        
        while published_count < self.threshold:
            current_video = self.videos[video_index]
            
            # 发布视频
            self._publish_single_video(current_video)
            published_count += 1
            
            # 如果还没达到阈值，计算下一次发布时间并等待
            if published_count < self.threshold:
                # 计算随机浮动时间
                float_time = random.randint(1, self.float_minutes)
                next_publish_delay = self.interval_minutes + float_time
                time.sleep(next_publish_delay * 60)
            
            # 更新视频索引，如果到达列表末尾则重新开始
            video_index = (video_index + 1) % len(self.videos)

    def _publish_single_video(self, video):
        """发布单个视频"""
        try:
            add(
                good_id=self.good_id,
                good_name=self.good_name,
                cookie=self.cookie,
                proxies=self.proxies,
                title=video['title'],
                content=video['content'],
                cover_path=video['cover_path'],
                video_path=video['video_path']
            )
            print(f"发布成功: {video['title']}")
        except Exception as e:
            print(f"发布失败: {str(e)}")

class MultiAccountPublisher:
    def __init__(self):
        self.tasks: List[PublishTask] = []
        
    def add_task(self, task: PublishTask):
        """添加发布任务"""
        self.tasks.append(task)
        
    def execute_all(self):
        """并行执行所有账号的发布任务"""
        with ThreadPoolExecutor() as executor:
            executor.map(lambda task: task.execute(), self.tasks)

# 使用示例
def main():
    # 创建多账号发布管理器
    publisher = MultiAccountPublisher()
    
    # 添加第一个账号的任务
    task1 = PublishTask(
        cookie="account1_cookie",
        proxies={"http": "socks5://user1:pass1@ip1:port1"},
        good_id="good1",
        good_name="商品1",
        video_folder="/path/to/videos1",
        mode=2,  # 循环发布
        interval_minutes=30,
        float_minutes=15,
        threshold=10
    )
    task1.load_videos()  # 加载视频列表
    publisher.add_task(task1)
    
    # 添加第二个账号的任务
    task2 = PublishTask(
        cookie="account2_cookie",
        proxies={"http": "socks5://user2:pass2@ip2:port2"},
        good_id="good2",
        good_name="商品2",
        video_folder="/path/to/videos2",
        mode=1  # 正常发布
    )
    task2.load_videos()  # 加载视频列表
    publisher.add_task(task2)
    
    # 执行所有任务
    publisher.execute_all()

if __name__ == "__main__":
    main() 