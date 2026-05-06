---
name: xhs-pugongying-apis
description: Use Xiaohongshu PuGongYing (Dandelion) platform API for KOL/creator data analysis including follower demographics, trends, and collaboration requests. Use when the user wants to analyze XHS influencers or KOLs.
allowed-tools: ["Bash(python *)"]
argument-hint: "[operation: get_kol_list|get_follower_profile|get_kol_trend]"
---

## 蒲公英平台 API（KOL数据）

> **项目路径**: `C:\Users\PC\Documents\Spider_XHS-xhs_new_api`
> 运行 Python 脚本前需先 `cd` 到项目目录。

### 初始化

```python
import sys, os
sys.path.insert(0, r'C:\Users\PC\Documents\Spider_XHS-xhs_new_api')
from apis.xhs_pugongying_apis import PuGongYingAPI

pgy_api = PuGongYingAPI()
from xhs_utils.common_util import load_env
cookies_str = load_env()
```

### 核心 API

#### 获取 KOL 列表
```python
success, msg, kol_list = pgy_api.get_some_user(
    num=50,           # 获取数量
    cookies=cookies_str,
    sort_type=0,      # 排序方式
    category="",      # 类目筛选
    fans_range="",    # 粉丝范围
    proxies=None
)
```

#### 获取博主粉丝画像
```python
success, msg, profile = pgy_api.get_user_follower_profile(user_id, cookies_str)
```

#### 获取博主历史趋势
```python
success, msg, trend = pgy_api.get_user_trend(user_id, cookies_str)
```

#### 发起合作邀请
```python
success, msg, result = pgy_api.send_collaboration(user_id, cookies_str, note_info={})
```

### 典型用法

```python
# KOL 筛选 + AI 分析
kol_list = pgy_api.get_some_user(num=50, cookies=cookies_str)
# 将 KOL 数据交给 AI 评估匹配度
```

### 注意事项
- 蒲公英平台为小红书官方商业合作平台
- 需要有效的商业合作账号 Cookie
