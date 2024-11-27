import os
def update_video_filename(video_path: str) -> str:
    """更新视频文件名，添加使用次数标记"""
    base_name, ext = os.path.splitext(video_path)
    # 检查文件名是否已经包含 '-数字'
    if '-' in base_name:
        # 提取数字并增加1
        parts = base_name.rsplit('-', 1)
        if parts[-1].isdigit():
            new_count = int(parts[-1]) + 1
            new_base_name = f"{parts[0]}-{new_count}"
        else:
            new_base_name = f"{base_name}-1"  # 如果最后部分不是数字，重置为-1
    else:
        new_base_name = f"{base_name}-1"  # 第一次发布，添加-1

    new_video_path = f"{new_base_name}{ext}"
    os.rename(video_path, new_video_path)  # 重命名文件
    return new_video_path

if __name__=="__main__":

    update_video_filename('D:\\小红书\\白发\\每日一笑\\视频\\1-2.mp4')