# 在原有的 create_video_note 方法中添加对 biz_relations 参数的处理

def create_video_note(self, title, video_path, desc="", cover_path=None, biz_relations=None, is_private=False):
    """
    创建视频笔记
    :param title: 标题
    :param video_path: 视频路径
    :param desc: 描述
    :param cover_path: 封面图片路径
    :param biz_relations: 商品ID
    :param is_private: 是否私密
    :return: 笔记ID
    """
    file_id, token = self.get_upload_files_permit("video")
    video_info = self.upload_file(video_path, file_id, token)
    
    if cover_path:
        file_id, token = self.get_upload_files_permit("image")
        cover_info = self.upload_file(cover_path, file_id, token)
    else:
        cover_info = None
        
    # 处理商品关联
    if biz_relations:
        if isinstance(biz_relations, str):
            # 如果传入的是字符串（商品ID），转换为标准格式
            biz_relations = [{
                "biz_type": "GOODS_SELLER_V2",
                "biz_id": biz_relations,
                "extra_info": json.dumps({
                    "goods_id": biz_relations,
                    "goods_type": "goods_seller",
                    "tab_id": 1,
                    "image_type": "spec",
                    "left_bottom_type": "BUY_GOODS",
                    "bind_order": 0
                })
            }]
    
    return self.create_note(
        title=title,
        desc=desc,
        note_type=NoteType.VIDEO.value,
        video_info=video_info,
        cover_info=cover_info,
        biz_relations=biz_relations,
        is_private=is_private
    )