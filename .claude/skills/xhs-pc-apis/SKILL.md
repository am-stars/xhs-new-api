---
name: xhs-pc-apis
description: Use Xiaohongshu PC API for data scraping including search notes, get note details, get user info, get user notes, get comments, and get recommendations. Use when the user wants to crawl or query XHS note data.
allowed-tools: ["Bash(python *)"]
argument-hint: "[operation: search_notes|get_note|get_user_notes|get_comments|get_user_info]"
---

## 小红书 PC 端数据采集 API

> **项目路径**: `C:\Users\PC\Documents\Spider_XHS-xhs_new_api`
> 运行 Python 脚本前需先 `cd` 到项目目录，或在 `sys.path` 中添加该路径。

### 初始化

```python
import sys, os
sys.path.insert(0, r'C:\Users\PC\Documents\Spider_XHS-xhs_new_api')
from apis.xhs_pc_apis import XHS_Apis

xhs_apis = XHS_Apis()
# Cookie 配置在 .env 文件中 COOKIES 字段
from xhs_utils.common_util import load_env
cookies_str = load_env()
```

### 核心 API

#### 获取笔记详情
```python
success, msg, note_info = xhs_apis.get_note_info(note_url, cookies_str)
# note_url 格式: https://www.xiaohongshu.com/explore/{note_id}?xsec_token=xxx&xsec_source=pc_user
```

#### 搜索笔记
```python
# 按数量搜索，支持排序、类型、时间、范围过滤
success, msg, notes = xhs_apis.search_some_note(
    query,           # 搜索关键词
    require_num,     # 需要数量
    cookies_str,
    sort_type=0,     # 0综合 1最新 2最多点赞 3最多评论 4最多收藏
    note_type=0,     # 0不限 1视频 2普通
    note_time=0,     # 0不限 1一天内 2一周内 3半年内
    note_range=0,    # 0不限 1已看过 2未看过 3已关注
    pos_distance=0,  # 0不限 1同城 2附近(需传geo)
    geo=None,        # {"latitude": 39.97, "longitude": 116.42}
    proxies=None
)
```

#### 获取用户所有笔记
```python
success, msg, notes = xhs_apis.get_user_all_notes(
    user_url,        # https://www.xiaohongshu.com/user/profile/{user_id}?xsec_token=xxx
    cookies_str,
    max_notes=0,     # 0表示全部，>0表示限制数量
    proxies=None
)
```

#### 获取用户信息
```python
success, msg, user_info = xhs_apis.get_user_info(user_id, cookies_str)
```

#### 获取笔记评论
```python
# 获取全部评论（含一级和二级）
success, msg, comments = xhs_apis.get_note_all_comment(note_url, cookies_str)
```

#### 获取用户喜欢/收藏的笔记
```python
success, msg, like_notes = xhs_apis.get_user_all_like_note_info(user_url, cookies_str)
success, msg, collect_notes = xhs_apis.get_user_all_collect_note_info(user_url, cookies_str)
```

#### 搜索用户
```python
success, msg, users = xhs_apis.search_some_user(query, require_num, cookies_str)
```

#### 获取推荐笔记
```python
success, msg, notes = xhs_apis.get_homefeed_recommend_by_num(category, require_num, cookies_str)
```

### 数据处理

```python
from xhs_utils.data_util import handle_note_info, save_to_xlsx, download_note

# 处理笔记信息为标准格式
note_info = handle_note_info(raw_note_data)

# 保存到 Excel
save_to_xlsx(note_list, 'output.xlsx')

# 下载媒体
download_note(note_info, save_path, save_choice)  # save_choice: all/media/excel/none
```

### 注意事项
- Cookie 有时效性，失效后需重新获取
- URL 中的 xsec_token 参数会过期
- 建议配合 proxies 参数使用代理，降低封号风险
