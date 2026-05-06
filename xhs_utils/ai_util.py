import os
import json
from loguru import logger
from dotenv import load_dotenv

"""
    AI 工具模块 - 支持多种大模型接入
    环境变量配置（.env 文件）：
        AI_PROVIDER=openai  # claude / openai / ollama
        AI_API_KEY=sk-xxx
        AI_MODEL=doubao-seed-2.0-pro  # 模型名称
        AI_BASE_URL=  # OpenAI 兼容接口地址，ollama 填 http://localhost:11434/v1
"""


class AI_Client:
    def __init__(self):
        load_dotenv()
        self.provider = os.getenv('AI_PROVIDER', 'claude')
        self.api_key = os.getenv('AI_API_KEY', '')
        self.model = os.getenv('AI_MODEL', 'claude-sonnet-4-6-20250514')
        self.base_url = os.getenv('AI_BASE_URL', '')
        self._client = None

    def _get_client(self):
        if self._client:
            return self._client
        if self.provider == 'claude':
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.api_key)
        elif self.provider in ('openai', 'ollama'):
            from openai import OpenAI
            kwargs = {'api_key': self.api_key}
            if self.base_url:
                kwargs['base_url'] = self.base_url
            self._client = OpenAI(**kwargs)
        else:
            raise ValueError(f'不支持的 AI 提供商: {self.provider}')
        return self._client

    def chat(self, system_prompt: str, user_prompt: str, max_tokens=4096, temperature=0.7):
        """通用对话接口"""
        client = self._get_client()
        try:
            if self.provider == 'claude':
                response = client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{'role': 'user', 'content': user_prompt}]
                )
                return response.content[0].text
            else:
                response = client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ]
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f'AI 调用失败: {e}')
            return f'[AI 调用失败] {e}'


def analyze_notes(ai_client: AI_Client, notes: list, analysis_type: str = 'trend'):
    """
    分析一批笔记，返回 AI 分析结果
    :param notes: handle_note_info 返回的笔记列表
    :param analysis_type: trend(趋势分析) / title(标题套路) / tags(热门标签) / summary(内容摘要)
    """
    analysis_prompts = {
        'trend': '请分析这批小红书笔记的数据趋势，包括互动数据（点赞/收藏/评论）的分布特征、高互动笔记的共同特点。',
        'title': '请分析这批小红书笔记的标题规律，总结爆款标题的写作套路和常用句式。',
        'tags': '请统计并分析这批笔记使用的标签/话题，找出高频标签和潜在的内容方向。',
        'summary': '请概括这批笔记的核心内容主题，归纳主要的内容分类和受众群体。',
    }
    prompt = analysis_prompts.get(analysis_type, analysis_prompts['summary'])

    note_data = []
    for n in notes[:50]:  # 最多分析 50 条
        note_data.append({
            'title': n.get('title', ''),
            'desc': n.get('desc', '')[:200],
            'liked_count': n.get('liked_count', 0),
            'collected_count': n.get('collected_count', 0),
            'comment_count': n.get('comment_count', 0),
            'tags': n.get('tags', []),
            'note_type': n.get('note_type', ''),
        })

    system = '你是一个专业的小红书内容运营分析师，擅长从数据中发现内容规律并给出可操作的建议。'
    user = f'{prompt}\n\n以下是 {len(note_data)} 条笔记的数据：\n{json.dumps(note_data, ensure_ascii=False, indent=2)}'

    logger.info(f'AI 笔记分析 ({analysis_type}): 提交 {len(note_data)} 条笔记')
    return ai_client.chat(system, user)


def rewrite_note(ai_client: AI_Client, note_info: dict, style: str = '爆款'):
    """
    改写一条笔记的标题和正文
    :param note_info: handle_note_info 返回的笔记信息
    :param style: 改写风格 爆款/文艺/专业/幽默/口语化
    """
    system = '你是一个资深小红书内容创作者，擅长写爆款笔记。你能根据原始笔记内容，重新撰写更有吸引力的标题和正文。'
    style_desc = {
        '爆款': '标题抓人眼球，正文多用emoji、数字、感叹号，分段清晰',
        '文艺': '语言优美有意境，多用比喻和诗意表达',
        '专业': '语言专业严谨，数据支撑，适合知识分享类内容',
        '幽默': '轻松搞笑，多用段子和网络热梗',
        '口语化': '像朋友聊天一样自然，多用口语化表达',
    }

    user = f"""请根据以下原始笔记内容，用【{style}】风格改写，要求：
1. 给出 3 个不同风格的标题选项
2. 给出完整的正文内容
3. 给出 5-10 个推荐标签

原始笔记：
标题：{note_info.get('title', '')}
正文：{note_info.get('desc', '')}
标签：{note_info.get('tags', [])}
类型：{note_info.get('note_type', '')}

风格要求：{style_desc.get(style, style_desc['爆款'])}"""

    return ai_client.chat(system, user)


def analyze_comments(ai_client: AI_Client, comments: list):
    """
    分析笔记评论的情感
    :param comments: handle_comment_info 返回的评论列表
    """
    comment_data = []
    for c in comments[:100]:
        comment_data.append({
            'content': c.get('content', ''),
            'like_count': c.get('like_count', 0),
        })

    system = '你是一个用户评论分析专家，擅长从评论中挖掘用户真实想法和情感倾向。'
    user = f"""请分析以下小红书笔记评论：
1. 整体情感倾向（正面/负面/中性比例）
2. 用户最关注的话题/卖点
3. 常见的负面反馈有哪些
4. 给用户画像总结

以下是 {len(comment_data)} 条评论：
{json.dumps(comment_data, ensure_ascii=False, indent=2)}"""

    return ai_client.chat(system, user)
