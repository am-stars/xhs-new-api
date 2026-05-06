

<div align="center">

#XHS

**专业的小红书数据采集 & 全域运营解决方案 & Agent Skills**
## 原项目是https://github.com/cv-cat/Spider_XHS
## 本项目是在原项目的基础上加了终端选择输入，接入ai，加了ai智能体的skills调用等功能

[![Skills](https://img.shields.io/badge/skills-supported-success)](https://github.com/cv-cat/XhsSkills)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/nodejs-20%2B-green)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

</div>

> **在 AI 大模型爆发的时代，内容运营的竞争本质是效率竞争。**
> 本项目封装了小红书平台完整的数据采集与内容发布能力，为开发者构建 AI 运营智能体提供可靠、稳定的底层 API 支撑。

**⚠️ 本项目仅供学习交流使用，禁止任何商业化行为，如有违反，后果自负**

---

## 为什么需要这个项目？

```
采集竞品笔记 ──► [Spider_XHS] ──► 你的 AI Agent（改写 / 生成 / 分析）──► 自动上传发布
                     ▲                                                        │
                     └──────────── 获取数据 / 管理账号 ◄──────────────────────┘
```

小红书没有开放完整的内容运营接口。想要接入 AI 大模型实现内容批量采集、智能改写、一键发布，首先需要能**稳定读写平台数据**。Spider_XHS 解决的正是这个前置问题：

- 逆向还原了小红书 PC 端与创作者平台的签名算法（x-s / x-t / x-s-common / x_b3_traceid / sign / q-signature参数）
- 封装全部核心 HTTP 接口，签名参数已透明处理
- 同时覆盖 **数据采集**（PC端）、**内容发布**（创作者平台）、**KOL数据**（蒲公英）三大场景

**你负责接 AI 大脑，我们负责打通小红书的神经。**

---

## ⭐ 已实现功能

| 模块 | 功能 | 状态 |
|------|------|------|
| **小红书 PC 端** | 二维码登录 / 手机验证码登录 | ✅ |
| | 获取主页所有频道 & 推荐笔记 | ✅ |
| | 获取用户主页信息 / 自己的账号信息 | ✅ |
| | 获取用户发布 / 喜欢 / 收藏的所有笔记 | ✅ |
| | 获取笔记详细内容（无水印图片 & 视频） | ✅ |
| | 搜索笔记 & 搜索用户 | ✅ |
| | 获取笔记评论 | ✅ |
| | 获取未读消息 / 评论@提醒 / 点赞收藏 / 新增关注 | ✅ |
| **创作者平台** | 二维码登录 / 手机验证码登录 | ✅ |
| | 上传图集作品 | ✅ |
| | 上传视频作品 | ✅ |
| | 查看已发布作品列表 | ✅ |
| **蒲公英平台** | 获取 KOL 博主列表 & 详细数据 | ✅ |
| | 获取博主粉丝画像 & 历史趋势 | ✅ |
| | 发起合作邀请 | ✅ |
| **千帆平台** | 获取分销商列表 & 详细数据 | ✅ |
| | 获取分销商合作品类 / 店铺 / 商品信息 | ✅ |
| **AI 智能分析** | 接入 Claude / OpenAI / Ollama | ✅ |
| | 笔记趋势分析 / 标题套路 / 热门标签 / 内容摘要 | ✅ |
| | 笔记改写（爆款/文艺/专业/幽默/口语化） | ✅ |
| | 评论情感分析 & 用户画像 | ✅ |

---

## 🤖 AI 智能体接入

项目内置 `AI_Client` 统一封装，支持多模型切换。在 `.env` 中配置即可：

```
# AI 提供商：claude / openai / ollama
AI_PROVIDER=claude
AI_API_KEY=sk-xxx
AI_MODEL=claude-sonnet-4-6-20250514
AI_BASE_URL=  # OpenAI 兼容接口地址，ollama 填 http://localhost:11434/v1
```

### 支持的 AI 功能

| 功能 | 说明 |
|------|------|
| **趋势分析** | 分析互动数据分布，找出高互动笔记的共同特征 |
| **标题套路** | 总结爆款标题的写作套路和常用句式 |
| **热门标签** | 统计高频标签，发现潜在内容方向 |
| **内容摘要** | 归纳内容主题和受众群体 |
| **笔记改写** | 5 种风格（爆款/文艺/专业/幽默/口语化）自动生成标题和正文 |
| **评论分析** | 情感倾向、用户关注点、负面反馈、用户画像 |

### 快速调用示例

```python
from xhs_utils.ai_util import AI_Client, analyze_notes, rewrite_note, analyze_comments
from apis.xhs_pc_apis import XHS_Apis

pc_api = XHS_Apis()
ai = AI_Client()

# 1. 采集笔记
success, msg, notes = pc_api.search_some_note("穿搭", 20, cookies)

# 2. AI 趋势分析
result = analyze_notes(ai, notes, analysis_type='trend')

# 3. AI 改写单条笔记
rewritten = rewrite_note(ai, note_info, style='爆款')

# 4. AI 评论分析
result = analyze_comments(ai, comments)
```

---

## 🎯 交互式命令行工具

运行 `python main.py` 后进入交互式菜单，支持以下操作：

```
Spider_XHS - 小红书数据采集 & AI 分析工具
==================================================

请选择模式：
  1. 爬取指定笔记列表
  2. 爬取用户所有笔记
  3. 搜索关键词爬取笔记
  4. AI 笔记内容分析（趋势/标题/标签）
  5. AI 笔记改写（生成爆款文案）
  6. AI 评论情感分析
```

模式 1-3 支持选择保存方式（全部信息 / 仅媒体 / 仅 Excel / 不保存），
模式 4-6 直接调用 AI 大模型输出分析结果。

---

## 🧩 Skills 支持

当前项目已经支持基于 skills 的能力接入，既可以直接作为 `Spider_XHS` 的底层能力仓库使用，也可以通过标准化 skills 方式被上层 Agent 工具链引入。

如果你希望直接复用已经封装好的 skills，可以查看 [XhsSkills](https://github.com/cv-cat/XhsSkills)。该仓库专门用于存放基于 `Spider_XHS` 封装的 Agent Skills，目前可被 `Clawbot`、`Claude Code`、`Codex` 等支持 skills 的工具直接引入与集成。

---

## 🎨 爬虫效果图

### 处理后的所有用户
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/00902dbd-4da1-45bc-90bb-19f5856a04ad)

### 某个用户所有的笔记
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/880884e8-4a1d-4dc1-a4dc-e168dd0e9896)

### 某个笔记具体的内容
![image](https://github.com/cv-cat/Spider_XHS/assets/94289429/d17f3f4e-cd44-4d3a-b9f6-d880da626cc8)

### 保存的 Excel
![image](https://github.com/user-attachments/assets/707f20ed-be27-4482-89b3-a5863bc360e7)

---

## 🛠️ 快速开始

### ⛳ 环境要求

- Python 3.10+
- Node.js 20+

### 🎯 安装依赖

```bash
pip install -r requirements.txt
npm install
```

### 🎨 配置 Cookie

在项目根目录的 `.env` 文件中填入你的登录 Cookie 和 AI 配置：

```
# 小红书 Cookie
COOKIES='your_cookie_here'

# AI 配置（可选）
AI_PROVIDER=claude
AI_API_KEY=sk-xxx
AI_MODEL=claude-sonnet-4-6-20250514
AI_BASE_URL=
```

Cookie 获取方式：浏览器登录小红书后，按 `F12` 打开开发者工具 → 网络 → Fetch/XHR → 找任意一个请求 → 复制请求头中的 `cookie` 字段。

![image](https://github.com/user-attachments/assets/6a7e4ecb-0432-4581-890a-577e0eae463d)

![image](https://github.com/user-attachments/assets/5e62bc35-d758-463e-817c-7dcaacbee13c)

> **注意：必须是登录后的 Cookie，未登录状态无效。**

### 🚀 运行项目

```bash
python main.py
```

### 🐳 Docker 部署（可选）

```bash
docker build -t spider_xhs .
docker run -e COOKIES='your_cookie_here' spider_xhs
```

---

## 📁 项目结构

```
Spider_XHS/
├── main.py                          # 主入口：爬虫调用示例
├── apis/
│   ├── xhs_pc_apis.py               # 小红书PC端完整API（采集）
│   ├── xhs_creator_apis.py          # 创作者平台API（上传发布）
│   ├── xhs_pc_login_apis.py         # PC端登录（二维码/手机验证码）
│   ├── xhs_creator_login_apis.py    # 创作者平台登录
│   ├── xhs_pugongying_apis.py       # 蒲公英平台API（KOL数据）
│   └── xhs_qianfan_apis.py          # 千帆平台API（分销商数据）
├── xhs_utils/
│   ├── common_util.py               # 初始化工具（读取.env配置）
│   ├── cookie_util.py               # Cookie解析
│   ├── data_util.py                 # 数据处理（Excel保存、媒体下载）
│   ├── xhs_util.py                  # PC端签名算法封装
│   ├── xhs_creator_util.py          # 创作者平台签名算法封装
│   ├── xhs_pugongying_util.py       # 蒲公英平台工具
│   ├── xhs_qianfan_util.py          # 千帆平台工具
│   └── ai_util.py                   # AI 工具（Claude/OpenAI/Ollama 接入、笔记分析、改写、评论分析）
├── static/
│   ├── xhs_main_260411.js           # PC端签名核心JS（最新版）
│   ├── xhs_creator_260411.js        # 创作者平台签名核心JS（最新版）
│   └── ...
├── .env                             # Cookie配置（不要提交到git）
├── requirements.txt
├── Dockerfile
└── package.json
```

---

## 🗝️ 注意事项

- `main.py` 是爬虫入口，提供交互式 CLI 菜单，也可直接调用 `apis/` 中的模块
- `apis/xhs_pc_apis.py` 包含所有 PC 端数据接口
- `apis/xhs_creator_apis.py` 包含创作者平台发布接口
- `xhs_utils/ai_util.py` 封装了 AI 分析能力，支持 Claude/OpenAI/Ollama
- Cookie 有时效性，失效后需重新获取
- 建议配合代理（proxies 参数）使用，降低封号风险
- AI 功能需在 `.env` 中配置对应的 API Key

---

## 🍥 更新日志

| 日期 | 说明 |
|------|------|
| 23/08/09 | 首次提交 |
| 23/09/13 | API 更改 params 增加两个字段，修复图片无法下载，修复部分页面无法访问报错 |
| 23/09/16 | 修复较大视频编码问题，加入异常处理 |
| 23/09/18 | 代码重构，加入失败重试 |
| 23/09/19 | 新增下载搜索结果功能 |
| 23/10/05 | 新增跳过已下载功能，获取更详细的笔记和用户信息 |
| 23/10/08 | 上传至 PyPI，可通过 pip install 安装 |
| 23/10/17 | 搜索下载新增排序方式（综合 / 热门 / 最新） |
| 23/10/21 | 新增图形化界面，上传至 release v2.1.0 |
| 23/10/28 | Fix Bug：修复搜索功能隐藏问题 |
| 25/03/18 | 更新 API，修复部分问题 |
| 25/06/07 | 更新 search 接口，区分视频和图集下载，新增创作者平台 API |
| 25/07/15 | 更新 xs version56 & 小红书创作者接口 |
| 26/04/11 | 重构创作者平台 API（图集 / 视频上传），新增蒲公英 KOL 数据 API，新增千帆分销商 API，签名算法升级至最新版 |
| 26/05/06 | 新增 AI 智能分析模块（趋势/标题/标签/改写/评论分析），支持 Claude/OpenAI/Ollama 多模型接入，新增交互式 CLI 菜单 |

---

## 🧸 额外说明

1. 感谢 Star ⭐ 和 Follow，项目会持续更新
2. 作者联系方式在主页，有问题随时联系
3. 欢迎 PR 和 Issue，也欢迎关注作者其他项目
4. 如果此项目对您有帮助，欢迎请作者喝一杯奶茶 ~~（开心一整天 😊）



---

