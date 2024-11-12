import time
import random
import logging
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from threading import Thread, Lock
from queue import Queue
import concurrent.futures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('publish.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

@dataclass
class PublishStatus:
    """发布状态数据类"""
    cookie: str
    current_index: int
    published_count: int
    last_publish_time: float
    next_publish_time: float
    completed: bool = False
    is_paused: bool = False

class PublishTask:
    """单个发布任务"""
    def __init__(self, 
                 cookie: str,
                 proxies: Dict,
                 video_list: List[Dict],
                 mode: int = 1,
                 interval_minutes: int = 30,
                 float_minutes: int = 15,
                 threshold: int = 10):
        self.cookie = cookie
        self.proxies = proxies
        self.video_list = video_list
        self.mode = mode
        self.interval_minutes = interval_minutes
        self.float_minutes = float_minutes
        self.threshold = threshold
        self.is_running = False
        self.lock = Lock()  # 添加线程锁
        
        # 加载或初始化状态
        self.status = self._load_status() or PublishStatus(
            cookie=cookie,
            current_index=0,
            published_count=0,
            last_publish_time=0,
            next_publish_time=0
        )

    def _get_status_file(self) -> str:
        os.makedirs("status", exist_ok=True)
        return f"status/publish_status_{hash(self.cookie)}.json"

    def _load_status(self) -> Optional[PublishStatus]:
        try:
            if os.path.exists(self._get_status_file()):
                with open(self._get_status_file(), 'r', encoding='utf-8') as f:
                    return PublishStatus(**json.load(f))
        except Exception as e:
            logging.error(f"加载状态失败: {e}")
        return None

    def _save_status(self):
        try:
            with open(self._get_status_file(), 'w', encoding='utf-8') as f:
                json.dump(asdict(self.status), f)
        except Exception as e:
            logging.error(f"保存状态失败: {e}")

    def get_next_video(self) -> Optional[Dict]:
        with self.lock:
            if not self.video_list:
                return None
                
            if self.mode == 1:  # 正常发布
                if self.status.current_index >= len(self.video_list):
                    self.status.completed = True
                    return None
            else:  # 循环发布
                if self.status.published_count >= self.threshold:
                    self.status.completed = True
                    return None
                    
                if self.status.current_index >= len(self.video_list):
                    self.status.current_index = 0
                    
            return self.video_list[self.status.current_index]

    def update_status(self, publish_success: bool):
        with self.lock:
            current_time = time.time()
            
            if publish_success:
                self.status.published_count += 1
                self.status.current_index += 1
                self.status.last_publish_time = current_time
                
                if self.mode == 2:
                    float_seconds = random.randint(1, self.float_minutes * 60)
                    next_delay = self.interval_minutes * 60 + float_seconds
                    self.status.next_publish_time = current_time + next_delay
            
            self._save_status()

class PublishManager:
    """发布管理器"""
    def __init__(self, max_workers: int = 5):
        self.tasks: Dict[str, PublishTask] = {}  # 使用字典存储任务，key为cookie
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures: Dict[str, concurrent.futures.Future] = {}
        self.error_queue = Queue()
        self.status_lock = Lock()

    def add_task(self, task: PublishTask) -> bool:
        """添加发布任务"""
        with self.status_lock:
            if task.cookie in self.tasks:
                logging.warning(f"任务已存在: {task.cookie}")
                return False
            self.tasks[task.cookie] = task
            return True

    def start_task(self, cookie: str) -> bool:
        """启动单个任务"""
        with self.status_lock:
            if cookie not in self.tasks:
                logging.error(f"任务不存在: {cookie}")
                return False
            
            task = self.tasks[cookie]
            if task.is_running:
                logging.warning(f"任务已在运行: {cookie}")
                return False
            
            task.is_running = True
            task.status.is_paused = False
            self.futures[cookie] = self.executor.submit(self._run_task, task)
            return True

    def start_all(self):
        """启动所有任务"""
        for cookie in list(self.tasks.keys()):
            self.start_task(cookie)

    def pause_task(self, cookie: str) -> bool:
        """暂停任务"""
        with self.status_lock:
            if cookie not in self.tasks:
                return False
            task = self.tasks[cookie]
            task.status.is_paused = True
            return True

    def resume_task(self, cookie: str) -> bool:
        """恢复任务"""
        with self.status_lock:
            if cookie not in self.tasks:
                return False
            task = self.tasks[cookie]
            task.status.is_paused = False
            return True

    def stop_task(self, cookie: str) -> bool:
        """停止任务"""
        with self.status_lock:
            if cookie not in self.tasks:
                return False
            task = self.tasks[cookie]
            task.is_running = False
            if cookie in self.futures:
                self.futures[cookie].cancel()
            return True

    def stop_all(self):
        """停止所有任务"""
        for cookie in list(self.tasks.keys()):
            self.stop_task(cookie)

    def _run_task(self, task: PublishTask):
        """运行单个任务"""
        logging.info(f"开始任务: {task.cookie}")
        
        try:
            if task.mode == 1:
                self._normal_publish(task)
            else:
                self._cycle_publish(task)
        except Exception as e:
            logging.error(f"任务异常: {task.cookie}, 错误: {str(e)}")
            self.error_queue.put({
                'cookie': task.cookie,
                'error': str(e)
            })
        finally:
            task.is_running = False
            logging.info(f"任务结束: {task.cookie}")

    def _normal_publish(self, task: PublishTask):
        """正常发布模式"""
        while task.is_running and not task.status.completed:
            if task.status.is_paused:
                time.sleep(1)
                continue
                
            video = task.get_next_video()
            if not video:
                break
                
            self._publish_single_video(task, video)

    def _cycle_publish(self, task: PublishTask):
        """循环发布模式"""
        while task.is_running and not task.status.completed:
            if task.status.is_paused:
                time.sleep(1)
                continue
                
            current_time = time.time()
            
            # 检查是否需要等待到下次发布时间
            if task.status.next_publish_time > 0:  # 添加判断，确保有下次发布时间
                if current_time < task.status.next_publish_time:
                    # 计算需要等待的时间，但最多等待10秒
                    wait_time = min(10, task.status.next_publish_time - current_time)
                    time.sleep(wait_time)
                    continue
                
            video = task.get_next_video()
            if not video:
                break
                
            try:
                self._publish_single_video(task, video)
                
                # 如果是第一次发布，设置下次发布时间
                if task.status.next_publish_time == 0:
                    current_time = time.time()
                    float_seconds = random.randint(1, task.float_minutes * 60)
                    next_delay = task.interval_minutes * 60 + float_seconds
                    task.status.next_publish_time = current_time + next_delay
                    task._save_status()
                    
            except Exception as e:
                logging.error(f"发布失败: {task.cookie}, 视频: {video['title']}, 错误: {str(e)}")
                time.sleep(60)  # 发布失败后等待1分钟

    def _publish_single_video(self, task: PublishTask, video: Dict):
        """发布单个视频"""
        try:
            from xhs.example.add import add
            add(
                good_id=video['good_id'],
                good_name=video['good_name'],
                cookie=task.cookie,
                proxies=task.proxies,
                title=video['title'],
                content=video['content'],
                cover_path=video['cover_path'],
                video_path=video['video_path']
            )
            task.update_status(True)
            logging.info(f"发布成功: {task.cookie}, 视频: {video['title']}")
        except Exception as e:
            logging.error(f"发布失败: {task.cookie}, 视频: {video['title']}, 错误: {str(e)}")
            self.error_queue.put({
                'cookie': task.cookie,
                'video': video['title'],
                'error': str(e)
            })
            task.update_status(False)
            time.sleep(60)  # 发布失败后等待1分钟

    def get_task_status(self, cookie: str) -> Optional[Dict]:
        """获取任务状态"""
        if cookie not in self.tasks:
            return None
            
        task = self.tasks[cookie]
        return {
            'cookie': task.cookie,
            'mode': '循环发布' if task.mode == 2 else '正常发布',
            'published': task.status.published_count,
            'total': task.threshold if task.mode == 2 else len(task.video_list),
            'is_running': task.is_running,
            'is_paused': task.status.is_paused,
            'completed': task.status.completed,
            'next_publish': datetime.fromtimestamp(task.status.next_publish_time).strftime('%Y-%m-%d %H:%M:%S') 
                          if task.status.next_publish_time > 0 else '-'
        }

    def get_all_status(self) -> List[Dict]:
        """获取所有任务状态"""
        return [self.get_task_status(cookie) for cookie in self.tasks.keys()]

    def get_errors(self) -> List[Dict]:
        """获取错误信息"""
        errors = []
        while not self.error_queue.empty():
            errors.append(self.error_queue.get())
        return errors