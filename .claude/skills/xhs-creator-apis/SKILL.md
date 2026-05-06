---
name: xhs-creator-apis
description: Use Xiaohongshu Creator Platform API for uploading notes (images/videos), managing published content. Use when the user wants to publish or manage content on XHS creator platform.
allowed-tools: ["Bash(python *)", "Read"]
argument-hint: "[operation: upload_image|upload_video|get_published_notes]"
---

## 小红书创作者平台 API

> **项目路径**: `C:\Users\PC\Documents\Spider_XHS-xhs_new_api`
> 运行 Python 脚本前需先 `cd` 到项目目录，或在 `sys.path` 中添加该路径。

### 初始化

```python
import sys, os
sys.path.insert(0, r'C:\Users\PC\Documents\Spider_XHS-xhs_new_api')
from apis.xhs_creator_apis import XHS_Creator_Apis

creator_api = XHS_Creator_Apis()
# 需要创作者平台的 Cookie（creator.xiaohongshu.com）
from xhs_utils.common_util import load_env
cookies_str = load_env()
```

### 发布笔记（图集）

```python
success, msg, result = creator_api.post_note({
    "title": "笔记标题",
    "desc": "笔记正文内容",
    "postTime": None,            # 13位时间戳，None表示立即发布
    "location": "南京",           # 地点，可选
    "type": 1,                   # 0公开 1私密
    "media_type": "image",       # "image" 或 "video"
    "topics": ["话题1", "话题2"], # 话题列表，可选
    "images": [
        open("path/to/image1.jpg", "rb").read(),  # 最多15张
        open("path/to/image2.jpg", "rb").read(),
    ],
}, cookies_str)
```

### 发布笔记（视频）

```python
success, msg, result = creator_api.post_note({
    "title": "笔记标题",
    "desc": "笔记正文内容",
    "postTime": None,
    "location": None,
    "type": 1,
    "media_type": "video",
    "topics": ["话题1"],
    "video": open("path/to/video.mp4", "rb").read(),
}, cookies_str)
```

### 获取已发布笔记

```python
# 获取单页
success, msg, res_json = creator_api.get_publish_note_info(page, cookies_str)

# 获取全部
success, msg, all_notes = creator_api.get_all_publish_note_info(cookies_str)
```

### 辅助功能

```python
# 搜索话题
success, msg, topics = creator_api.get_topic(keyword, cookies)

# 搜索地点
success, msg, locations = creator_api.get_location_info(keyword, cookies)

# 上传媒体（图片/视频）
success, msg, file_info = creator_api.upload_media(file_bytes, "image", cookies)
# file_info: {"fileIds": "...", "width": "...", "height": "..."}
```

### 注意事项
- 需要使用 creator.xiaohongshu.com 的 Cookie，与 PC 端 Cookie 不同
- 图片最多上传 15 张，视频上传后需要等待转码完成
- 话题和地点为可选参数，不传则不关联
