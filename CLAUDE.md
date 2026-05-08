# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# XHS New API 项目

## 小红书 (XHS) 相关 Skills

项目已安装以下 5 个小红书相关 Skills，位于 `.claude/skills/` 目录：

| Skill 名称 | 用途 |
|---|---|
| `xhs-ai-analysis` | AI 分析笔记、评论、营销洞察 |
| `xhs-creator-apis` | 创作者平台 API（发布/管理笔记，支持图文/视频上传） |
| `xhs-pc-apis` | PC 端数据抓取（搜索笔记、获取笔记详情、用户信息、评论、推荐） |
| `xhs-pugongying-apis` | 蒲公英平台 KOL/达人数据分析（粉丝画像、趋势、合作请求） |
| `xhs-qianfan-apis` | 千帆平台分销商/电商数据（分销商列表、分类、店铺、商品信息） |

## 使用方式

在对话中通过 `/skill-name` 调用，例如：
- `/xhs-pc-apis` — 抓取笔记数据
- `/xhs-creator-apis` — 发布新笔记
- `/xhs-ai-analysis` — AI 内容分析
- `/xhs-pugongying-apis` — KOL 达人分析
- `/xhs-qianfan-apis` — 分销商/电商数据查询

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt
npm install

# 运行主程序（交互式 CLI 菜单）
python main.py

# Docker 构建与运行
docker build -t spider_xhs .
docker run -e COOKIES='your_cookie_here' spider_xhs
```

## 架构概览

### 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| **主入口** | `main.py` | 交互式 CLI 菜单，编排爬虫流程，Cookie 过期自动检测与重试 |
| **PC 端 API** | `apis/xhs_pc_apis.py` | 小红书 PC 端完整接口（搜索、笔记详情、用户信息、评论、推荐、消息） |
| **创作者 API** | `apis/xhs_creator_apis.py` | 创作者平台上传发布（图集/视频） |
| **登录 API** | `apis/xhs_pc_login_apis.py`, `apis/xhs_creator_login_apis.py` | 二维码登录 / 手机验证码登录 |
| **蒲公英 API** | `apis/xhs_pugongying_apis.py` | KOL 达人数据（列表、粉丝画像、趋势、合作） |
| **千帆 API** | `apis/xhs_qianfan_apis.py` | 分销商/电商数据（列表、品类、店铺、商品） |

### 工具层

| 工具 | 文件 | 职责 |
|------|------|------|
| **签名算法** | `xhs_utils/xhs_util.py` | 通过 `execjs` 执行 `static/xhs_main_260411.js` 生成 x-s / x-t / x-s-common 签名 |
| **创作者签名** | `xhs_utils/xhs_creator_util.py` | 创作者平台签名（q-signature 等） |
| **数据处理** | `xhs_utils/data_util.py` | 笔记/评论数据解析、媒体下载、Excel 导出 |
| **Cookie 工具** | `xhs_utils/cookie_util.py` | Cookie 字符串解析 |
| **配置管理** | `xhs_utils/common_util.py` | `.env` 加载、Cookie 更新、登录过期检测 |
| **AI 工具** | `xhs_utils/ai_util.py` | 统一 AI 客户端（Claude / OpenAI / Ollama），笔记分析、改写、评论分析 |

### 签名机制

项目通过 `PyExecJS` 在 Python 中运行逆向的小红书签名 JS：

- `static/xhs_main_260411.js` — PC 端签名核心（x-s, x-t, x-s-common）
- `static/xhs_creator_260411.js` — 创作者平台签名核心（q-signature）
- `static/xhs_xray.js` — x-xray-traceid 生成

`xhs_utils/xhs_util.py` 中的 `generate_request_params()` 是核心入口，自动从 Cookie 中提取 `a1` 字段，调用 JS 生成签名并组装请求头。

### AI 分析能力

`xhs_utils/ai_util.py` 中的 `AI_Client` 统一封装了多模型调用，通过 `.env` 配置切换：

- **笔记分析** (`analyze_notes`): 趋势/标题/标签/摘要，批量分析最多 50 条
- **笔记改写** (`rewrite_note`): 5 种风格（爆款/文艺/专业/幽默/口语化）
- **评论分析** (`analyze_comments`): 情感倾向、关注点、负面反馈、用户画像

### 数据流

```
Cookie (.env) → init() → XHS_Apis → generate_request_params() → JS签名 → requests → JSON响应
                                                                        ↓
handle_note_info() → download_note() / save_to_xlsx() / AI分析
```

### Cookie 管理

- Cookie 存储在 `.env` 的 `COOKIES` 字段中
- `common_util.is_login_expired()` 通过关键词匹配检测过期（包含"登录""过期""401""token"等）
- `main.py` 中的 `check_cookie_expired_and_retry()` 在失败后提示输入新 Cookie，自动更新 `.env` 并重试

### 数据存储

- `datas/media_datas/` — 下载的媒体文件（图片 .jpg / 视频 .mp4）
- `datas/excel_datas/` — Excel 导出文件

## 注意事项

- Cookie 有时效性，需定期更新；代理可通过 `proxies` 参数传入
- `main.py` 是交互式入口，也可直接调用 `apis/` 中的类方法
- AI 功能需在 `.env` 中配置 `AI_PROVIDER` / `AI_API_KEY` / `AI_MODEL`
