import os
import re
from loguru import logger
from dotenv import load_dotenv

def load_env():
    load_dotenv()
    cookies_str = os.getenv('COOKIES')
    return cookies_str

def update_cookies_in_env(new_cookies: str) -> bool:
    """
    更新 .env 文件中的 COOKIES 字段
    :param new_cookies: 新的 cookie 字符串
    :return: 是否更新成功
    """
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 替换 COOKIES='...' 中的值（支持单引号或双引号）
        new_content = re.sub(
            r"(COOKIES\s*=\s*['\"])(?:[^'\"]*)(['\"])",
            rf"\g<1>{new_cookies}\g<2>",
            content,
            count=1
        )
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        # 重新加载环境变量
        load_dotenv(env_path, override=True)
        logger.info('Cookie 已更新并保存到 .env 文件')
        return True
    except Exception as e:
        logger.error(f'更新 Cookie 失败: {e}')
        return False

def is_login_expired(msg: str) -> bool:
    """
    判断错误信息是否表示登录已过期
    """
    if not msg:
        return False
    expired_keywords = [
        '登录', '过期', '失效', 'expire', 'login', 'session',
        'unauthorized', 'Unauthorized', '401', '重新登录',
        '凭证', 'token', 'auth',
    ]
    for keyword in expired_keywords:
        if keyword in msg:
            return True
    return False

def init():
    media_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datas/media_datas'))
    excel_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../datas/excel_datas'))
    for base_path in [media_base_path, excel_base_path]:
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            logger.info(f'创建目录 {base_path}')
    cookies_str = load_env()
    base_path = {
        'media': media_base_path,
        'excel': excel_base_path,
    }
    return cookies_str, base_path
