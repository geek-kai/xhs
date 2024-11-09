import requests
import random
import time
from datetime import datetime, timedelta
import schedule
import json
import os
import add
class XHSVideoPublisher:
    # def __init__(self):
    #     self.base_url = "http://creator.moreapi.cn/api/xhs/create_note?pwd=123"
    #     self.cookie = "a1=1916df77fa1l0c5ae6zrccrtzvy9rxx6kkuv3dg5x00000404108; webId=41e2ed5c11624b6ebc3c9fc5e9a38cb4; gid=yjyKfiWYfWTDyjyKfiWWiTfk0y18S20dKuFS72CSF9uhvh88jFCCKq888484y8Y8SKJqDq82; customerClientId=156982604702457; abRequestId=41e2ed5c11624b6ebc3c9fc5e9a38cb4; webBuild=4.42.0; web_session=040069b5068275111a11a9cc19354bbb3d37a6; x-user-id-ark.xiaohongshu.com=6472c13d0000000010034a47; access-token-ark.xiaohongshu.com=customer.ark.AT-68c517434463715168343073t2a1cdqbxvcjuxfr; beaker.session.id=483cc286c19987eb5a7934d5c82d7676a45fe5edgAJ9cQEoVQNfaWRxAlUgZTkzNzJkZjBlZGY3NGIzNGEzZDgxMDBiMjZlNjhlNzNxA1UOX2FjY2Vzc2VkX3RpbWVxBEdB2cshV1KLzlUOX2NyZWF0aW9uX3RpbWVxBUdB2cshV1KLznUu; x-user-id-fuwu.xiaohongshu.com=6472c13d0000000010034a47; access-token-fuwu.xiaohongshu.com=customer.fuwu.AT-68c517434465089547625396ouywuvbmubhsldaz; access-token-fuwu.beta.xiaohongshu.com=customer.fuwu.AT-68c517434465089547625396ouywuvbmubhsldaz; timestamp2=1730971360438a3b2e259e6727952e662ab5af78565bb87b4712133f9050082; timestamp2.sig=gGQNe-o4Ihzu9OESMuO_qB-ETM-Eq_W02Aieu0b17Zw; unread={%22ub%22:%226729d9d0000000001b0280b0%22%2C%22ue%22:%22672c39c1000000003c018f86%22%2C%22uc%22:25}; acw_tc=0a0d096b17309730993877993ed7d215e411c0275e19b43fafcbec2e05cdc0; xsecappid=ugc; customer-sso-sid=68c517434475792617494746a4017996c87c358a; x-user-id-creator.xiaohongshu.com=6472c13d0000000010034a47; access-token-creator.xiaohongshu.com=customer.creator.AT-68c517434475792617494747fho54ch47kdcwqux; galaxy_creator_session_id=Wx9waCxDAUdAVQyVwEb54Jq1l89EXexYyLZt; galaxy.creator.beaker.session.id=1730973784815085178475; websectiga=8886be45f388a1ee7bf611a69f3e174cae48f1ea02c0f8ec3256031b8be9c7ee; sec_poison_id=04a7dbfa-b116-4969-aad9-5c4771055a1e"  # 需要替换为实际的cookie
    #     self.cover_dir = r"E:\\小红书连怼\\封面"  # 添加封面目录路径
    #     self.current_cover_index = 0  # 添加封面索引计数器
    
    # def get_next_cover(self):
    #     # 获取所有封面文件
    #     cover_files = [f for f in os.listdir(self.cover_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    #     if not cover_files:
    #         raise Exception("封面文件夹为空")
        
    #     # 获取下一个封面文件
    #     cover_file = cover_files[self.current_cover_index]
    #     # 更新索引，如果达到最后则重置为0
    #     self.current_cover_index = (self.current_cover_index + 1) % len(cover_files)
        
    #     return os.path.join(self.cover_dir, cover_file)
    
    def publish_video(self):
        try:
            # 获取下一个封面路径
            add.add()
            # print(f"发布结果: {response.json()}")
            
            # 设置下一次发布时间
            self.schedule_next_publish()
            
        except Exception as e:
            print(f"发布失败: {str(e)}")
    
    def schedule_next_publish(self):
        # 计算下一次发布时间
        current_time = datetime.now()
        next_hour = current_time + timedelta(minutes=30)
        
        # 随机生成0-20分钟的延迟
        random_minutes = random.randint(0, 20)
        next_publish_time = next_hour + timedelta(minutes=random_minutes)
        
        # 设置下次发布任务
        schedule.every().day.at(next_publish_time.strftime("%H:%M")).do(self.publish_video)
        
        print(f"下次发布时间设定为: {next_publish_time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    publisher = XHSVideoPublisher()
    
    try:
        publisher.publish_video()
        
        # 添加退出机制
        print("程序运行中，按Ctrl+C退出...")
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("程序已停止")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main() 