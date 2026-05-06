---
name: xhs-ai-analysis
description: Use AI to analyze Xiaohongshu notes, rewrite content, analyze comments sentiment, and generate marketing insights. Use when the user wants AI-powered content analysis or content generation for XHS.
allowed-tools: ["Bash(python *)", "Read"]
argument-hint: "[operation: analyze_notes|rewrite_note|analyze_comments]"
---

## AI 分析工具（基于大模型）

> **项目路径**: `C:\Users\PC\Documents\Spider_XHS-xhs_new_api`
> 运行 Python 脚本前需先 `cd` 到项目目录，或在 `sys.path` 中添加该路径。

### 初始化

```python
import sys, os
sys.path.insert(0, r'C:\Users\PC\Documents\Spider_XHS-xhs_new_api')
from xhs_utils.ai_util import AI_Client, analyze_notes, rewrite_note, analyze_comments

ai_client = AI_Client()
```

### 配置（.env）

```
AI_PROVIDER=openai                    # claude / openai / ollama
AI_API_KEY=your_key_here
AI_MODEL=doubao-seed-2.0-pro
AI_BASE_URL=https://ark.cn-beijing.volces.com/api/coding/v3
```

### API

#### 批量笔记分析
```python
# 分析一批笔记（最多50条），返回 AI 分析结果
result = analyze_notes(
    ai_client,
    note_list,           # handle_note_info 返回的笔记列表
    analysis_type='trend'  # trend/titles/tags/summary
)
# trend   - 趋势分析（互动数据分布、高互动笔记特点）
# title   - 标题套路（爆款标题写作技巧）
# tags    - 热门标签（高频标签、内容方向）
# summary - 内容摘要（主题归纳、受众分析）
```

#### 笔记改写
```python
result = rewrite_note(
    ai_client,
    note_info,       # handle_note_info 返回的笔记信息
    style='爆款'      # 爆款/文艺/专业/幽默/口语化
)
# 返回：3个标题选项 + 完整正文 + 5-10个推荐标签
```

#### 评论情感分析
```python
result = analyze_comments(
    ai_client,
    comment_list     # handle_comment_info 返回的评论列表
)
# 返回：情感倾向 + 关注话题 + 负面反馈 + 用户画像
```

### 典型工作流

```python
# 采集 → AI 改写 → 发布
from apis.xhs_pc_apis import XHS_Apis
from apis.xhs_creator_apis import XHS_Creator_Apis

pc_api = XHS_Apis()
creator_api = XHS_Creator_Apis()
ai_client = AI_Client()

# 1. 采集竞品笔记
success, msg, note = pc_api.get_note_info(note_url, cookies_str)
note_info = handle_note_info(note['data']['items'][0])

# 2. AI 改写
rewritten = rewrite_note(ai_client, note_info, style='爆款')

# 3. 发布
creator_api.post_note({
    "title": "新标题",
    "desc": "改写后的正文",
    "postTime": None,
    "type": 0,
    "media_type": "image",
    "topics": ["话题1"],
    "images": [open("path/to/image.jpg", "rb").read()],
}, creator_cookies_str)
```
