import json
import os
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.common_util import init, update_cookies_in_env, is_login_expired, load_env
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx
from xhs_utils.ai_util import AI_Client, analyze_notes, rewrite_note, analyze_comments


class Data_Spider():
    def __init__(self):
        self.xhs_apis = XHS_Apis()

    def spider_note(self, note_url: str, cookies_str: str, proxies=None):
        """
        爬取一个笔记的信息
        :param note_url:
        :param cookies_str:
        :return:
        """
        note_info = None
        try:
            success, msg, note_info = self.xhs_apis.get_note_info(note_url, cookies_str, proxies)
            if success:
                note_info = note_info['data']['items'][0]
                note_info['url'] = note_url
                note_info = handle_note_info(note_info)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取笔记信息 {note_url}: {success}, msg: {msg}')
        return success, msg, note_info

    def spider_some_note(self, notes: list, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一些笔记的信息
        :param notes:
        :param cookies_str:
        :param base_path:
        :return:
        """
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name 不能为空')
        note_list = []
        for note_url in notes:
            success, msg, note_info = self.spider_note(note_url, cookies_str, proxies)
            if note_info is not None and success:
                note_list.append(note_info)
        for note_info in note_list:
            if save_choice == 'all' or 'media' in save_choice:
                download_note(note_info, base_path['media'], save_choice)
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)


    def spider_user_all_note(self, user_url: str, cookies_str: str, base_path: dict, save_choice: str, excel_name: str = '', max_notes: int = 0, proxies=None):
        """
        爬取一个用户的所有笔记
        :param user_url:
        :param cookies_str:
        :param base_path:
        :param max_notes: 限制爬取数量，0 表示全部
        :return:
        """
        note_list = []
        try:
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies_str, max_notes, proxies)
            if success:
                logger.info(f'用户 {user_url} 作品数量: {len(all_note_info)}')
                for simple_note_info in all_note_info:
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    note_list.append(note_url)
            if save_choice in ['all', 'excel'] and not excel_name:
                excel_name = user_url.split('/')[-1].split('?')[0]
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'爬取用户所有视频 {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

    def spider_some_search_note(self, query: str, require_num: int, cookies_str: str, base_path: dict, save_choice: str, sort_type_choice=0, note_type=0, note_time=0, note_range=0, pos_distance=0, geo: dict = None,  excel_name: str = '', proxies=None):
        """
            指定数量搜索笔记，设置排序方式和笔记类型和笔记数量
            :param query 搜索的关键词
            :param require_num 搜索的数量
            :param cookies_str 你的cookies
            :param base_path 保存路径
            :param sort_type_choice 排序方式 0 综合排序, 1 最新, 2 最多点赞, 3 最多评论, 4 最多收藏
            :param note_type 笔记类型 0 不限, 1 视频笔记, 2 普通笔记
            :param note_time 笔记时间 0 不限, 1 一天内, 2 一周内天, 3 半年内
            :param note_range 笔记范围 0 不限, 1 已看过, 2 未看过, 3 已关注
            :param pos_distance 位置距离 0 不限, 1 同城, 2 附近 指定这个必须要指定 geo
            返回搜索的结果
        """
        note_list = []
        try:
            success, msg, notes = self.xhs_apis.search_some_note(query, require_num, cookies_str, sort_type_choice, note_type, note_time, note_range, pos_distance, geo, proxies)
            if success:
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                logger.info(f'搜索关键词 {query} 笔记数量: {len(notes)}')
                for note in notes:
                    note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = query
            self.spider_some_note(note_list, cookies_str, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = e
        logger.info(f'搜索关键词 {query} 笔记: {success}, msg: {msg}')
        return note_list, success, msg


def check_cookie_expired_and_retry(operation_name: str, success: bool, msg: str, data_spider, cookies_str: str, proxies=None) -> tuple:
    """
    检查 Cookie 是否过期，如果是则询问用户新的 Cookie 并更新
    :param operation_name: 操作名称
    :param success: 是否成功
    :param msg: 错误消息
    :param data_spider: Data_Spider 实例
    :param cookies_str: 当前 Cookie
    :param proxies: 代理
    :return: (新的成功状态, 新的消息, 新的 Cookie)
    """
    if success:
        return success, msg, cookies_str

    if not is_login_expired(str(msg)):
        return success, msg, cookies_str

    print(f"\n{'=' * 50}")
    print(f"  ⚠ 检测到【{operation_name}】Cookie 可能已过期")
    print(f"  错误信息: {msg}")
    print(f"{'=' * 50}")
    print()
    new_cookie = input("请输入新的 Cookie（或输入空行跳过）: ").strip()
    if not new_cookie:
        print("跳过，请重新运行。")
        return False, "Cookie 已过期", cookies_str

    # 更新并保存到 .env
    updated = update_cookies_in_env(new_cookie)
    if updated:
        print("Cookie 已更新并保存，正在重试...")
        return True, "Cookie 已更新，请重试", new_cookie
    else:
        print("Cookie 更新失败。")
        return False, "Cookie 更新失败", cookies_str

if __name__ == '__main__':
    """
        此文件为爬虫的入口文件，可以直接运行
        apis/xhs_pc_apis.py 为爬虫的api文件，包含小红书的全部数据接口，可以继续封装
        apis/xhs_creator_apis.py 为小红书创作者中心的api文件
        感谢star和follow
    """

    cookies_str, base_path = init()
    data_spider = Data_Spider()
    ai_client = AI_Client()

    # 用一个可变容器持有 cookie，使得 check 函数可以更新它
    cookie_holder = {'cookies': cookies_str}

    def run_once():
        print("=" * 50)
        print("  Spider_XHS - 小红书数据采集 & AI 分析工具")
        print("=" * 50)
        print()
        print("请选择模式：")
        print("  1. 爬取指定笔记列表")
        print("  2. 爬取用户所有笔记")
        print("  3. 搜索关键词爬取笔记")
        print("  4. AI 笔记内容分析（趋势/标题/标签）")
        print("  5. AI 笔记改写（生成爆款文案）")
        print("  6. AI 评论情感分析")
        print()
        mode = input("请输入模式编号 (1-6): ").strip()

        # AI 模式不需要保存方式选择
        if mode in ['4', '5', '6']:
            pass
        else:
            # 保存方式
            print()
            print("请选择保存方式：")
            print("  all     - 保存所有信息（媒体 + Excel）")
            print("  media   - 只保存媒体（视频和图片）")
            print("  excel   - 只保存到 Excel")
            print("  none    - 不保存")
            save_choice = input("请输入保存方式 (all/media/excel/none): ").strip().lower()
            if save_choice not in ['all', 'media', 'excel', 'none']:
                save_choice = 'all'

            excel_name = ''
            if save_choice in ['all', 'excel']:
                excel_name = input("请输入 Excel 文件名（不含后缀）: ").strip()

        proxies = None  # 如需代理，可在此配置

        if mode == '1':
            # 爬取指定笔记列表
            print()
            print("请输入笔记链接（每行一个，输入空行结束）：")
            notes = []
            while True:
                line = input().strip()
                if not line:
                    break
                notes.append(line)
            if not notes:
                print("未输入任何笔记链接。")
                return
            if not excel_name:
                excel_name = 'notes'

            print(f"开始爬取 {len(notes)} 条笔记...")
            success = True
            msg = 'success'
            for note_url in notes:
                s, m, info = data_spider.spider_note(note_url, cookie_holder['cookies'], proxies)
                if not s:
                    success = False
                    msg = m
                    break

            if not success and is_login_expired(str(msg)):
                success, msg, new_cookie = check_cookie_expired_and_retry(
                    '爬取笔记', False, msg, data_spider, cookie_holder['cookies'], proxies)
                if success:
                    cookie_holder['cookies'] = new_cookie
                    cookie_holder['cookies'] = load_env() or cookie_holder['cookies']
                    data_spider.spider_some_note(notes, cookie_holder['cookies'], base_path, save_choice, excel_name, proxies)
                    return
                else:
                    print(f"操作失败: {msg}")
                    return

            if success:
                data_spider.spider_some_note(notes, cookie_holder['cookies'], base_path, save_choice, excel_name, proxies)

        elif mode == '2':
            # 爬取用户所有笔记
            print()
            user_url = input("请输入用户主页链接: ").strip()
            if not user_url:
                print("未输入用户链接。")
                return

            max_notes_str = input("请输入爬取数量（0 表示全部，默认 0）: ").strip()
            try:
                max_notes = int(max_notes_str) if max_notes_str else 0
            except ValueError:
                max_notes = 0

            if max_notes > 0:
                print(f"将爬取该用户最多 {max_notes} 条笔记")
            else:
                print("将爬取该用户全部笔记")

            note_list, success, msg = data_spider.spider_user_all_note(user_url, cookie_holder['cookies'], base_path, save_choice, excel_name or 'user_notes', max_notes, proxies)

            if not success and is_login_expired(str(msg)):
                success, msg, new_cookie = check_cookie_expired_and_retry(
                    '爬取用户笔记', False, msg, data_spider, cookie_holder['cookies'], proxies)
                if success:
                    cookie_holder['cookies'] = load_env() or cookie_holder['cookies']
                    data_spider.spider_user_all_note(user_url, cookie_holder['cookies'], base_path, save_choice, excel_name or 'user_notes', max_notes, proxies)
                    return
                else:
                    print(f"操作失败: {msg}")
                    return

        elif mode == '3':
            # 搜索关键词爬取
            print()
            query = input("请输入搜索关键词: ").strip()
            if not query:
                print("未输入关键词。")
                return

            require_num_str = input("请输入搜索数量 (默认 10): ").strip()
            require_num = int(require_num_str) if require_num_str else 10

            print()
            print("排序方式：0 综合排序, 1 最新, 2 最多点赞, 3 最多评论, 4 最多收藏")
            sort_type_str = input("请输入排序方式 (默认 0): ").strip()
            sort_type = int(sort_type_str) if sort_type_str else 0

            print("笔记类型：0 不限, 1 视频笔记, 2 普通笔记")
            note_type_str = input("请输入笔记类型 (默认 0): ").strip()
            note_type = int(note_type_str) if note_type_str else 0

            print("笔记时间：0 不限, 1 一天内, 2 一周内, 3 半年内")
            note_time_str = input("请输入笔记时间 (默认 0): ").strip()
            note_time = int(note_time_str) if note_time_str else 0

            print("笔记范围：0 不限, 1 已看过, 2 未看过, 3 已关注")
            note_range_str = input("请输入笔记范围 (默认 0): ").strip()
            note_range = int(note_range_str) if note_range_str else 0

            print("位置距离：0 不限, 1 同城, 2 附近（选 1 或 2 需指定经纬度）")
            pos_distance_str = input("请输入位置距离 (默认 0): ").strip()
            pos_distance = int(pos_distance_str) if pos_distance_str else 0

            geo = None
            if pos_distance in [1, 2]:
                lat_str = input("请输入纬度 (如 39.9725): ").strip()
                lon_str = input("请输入经度 (如 116.4207): ").strip()
                geo = {"latitude": float(lat_str), "longitude": float(lon_str)}

            note_list, success, msg = data_spider.spider_some_search_note(query, require_num, cookie_holder['cookies'], base_path, save_choice, sort_type, note_type, note_time, note_range, pos_distance, geo, excel_name or query, proxies)

            if not success and is_login_expired(str(msg)):
                success, msg, new_cookie = check_cookie_expired_and_retry(
                    '搜索笔记', False, msg, data_spider, cookie_holder['cookies'], proxies)
                if success:
                    cookie_holder['cookies'] = load_env() or cookie_holder['cookies']
                    data_spider.spider_some_search_note(query, require_num, cookie_holder['cookies'], base_path, save_choice, sort_type, note_type, note_time, note_range, pos_distance, geo, excel_name or query, proxies)
                    return
                else:
                    print(f"操作失败: {msg}")
                    return

        elif mode == '4':
            # AI 笔记分析
            print()
            print("分析方式：")
            print("  1. 趋势分析（互动数据分布、高互动笔记特点）")
            print("  2. 标题套路（爆款标题写作技巧）")
            print("  3. 热门标签（高频标签、内容方向）")
            print("  4. 内容摘要（主题归纳、受众分析）")
            analysis_choice = input("请选择分析方式 (1-4): ").strip()
            analysis_map = {'1': 'trend', '2': 'title', '3': 'tags', '4': 'summary'}
            analysis_type = analysis_map.get(analysis_choice, 'summary')

            print()
            print("请输入要分析的笔记链接（每行一个，输入空行结束）：")
            notes = []
            while True:
                line = input().strip()
                if not line:
                    break
                notes.append(line)
            if not notes:
                print("未输入任何笔记链接。")
                return

            # 爬取笔记
            print(f"正在爬取 {len(notes)} 条笔记...")
            note_list = []
            for note_url in notes:
                success, msg, note_info = data_spider.spider_note(note_url, cookie_holder['cookies'], proxies)
                if success and note_info:
                    note_list.append(note_info)
                elif not success and is_login_expired(str(msg)):
                    success, msg, new_cookie = check_cookie_expired_and_retry(
                        'AI 笔记分析', False, msg, data_spider, cookie_holder['cookies'], proxies)
                    if success:
                        cookie_holder['cookies'] = load_env() or cookie_holder['cookies']
                        # 重新爬取
                        note_list = []
                        for n_url in notes:
                            s, m, info = data_spider.spider_note(n_url, cookie_holder['cookies'], proxies)
                            if s and info:
                                note_list.append(info)
                    else:
                        print(f"操作失败: {msg}")
                        return
                    break

            if not note_list:
                print("未能成功爬取任何笔记。")
                return

            print(f"成功爬取 {len(note_list)} 条笔记，正在调用 AI 分析...")
            result = analyze_notes(ai_client, note_list, analysis_type)
            print("\n" + "=" * 50)
            print("AI 分析结果：")
            print("=" * 50)
            print(result)

        elif mode == '5':
            # AI 笔记改写
            print()
            note_url = input("请输入要改写的笔记链接: ").strip()
            if not note_url:
                print("未输入笔记链接。")
                return

            print()
            print("改写风格：1. 爆款  2. 文艺  3. 专业  4. 幽默  5. 口语化")
            style_choice = input("请选择风格 (默认 1): ").strip()
            style_map = {'1': '爆款', '2': '文艺', '3': '专业', '4': '幽默', '5': '口语化'}
            style = style_map.get(style_choice, '爆款')

            # 爬取笔记
            print("正在爬取笔记...")
            success, msg, note_info = data_spider.spider_note(note_url, cookie_holder['cookies'], proxies)
            if not success and is_login_expired(str(msg)):
                success, msg, new_cookie = check_cookie_expired_and_retry(
                    'AI 笔记改写', False, msg, data_spider, cookie_holder['cookies'], proxies)
                if success:
                    cookie_holder['cookies'] = load_env() or cookie_holder['cookies']
                    success, msg, note_info = data_spider.spider_note(note_url, cookie_holder['cookies'], proxies)
                else:
                    print(f"操作失败: {msg}")
                    return

            if not success or not note_info:
                print(f"爬取失败: {msg}")
                return

            print(f"正在用【{style}】风格改写...")
            result = rewrite_note(ai_client, note_info, style)
            print("\n" + "=" * 50)
            print("AI 改写结果：")
            print("=" * 50)
            print(result)

        elif mode == '6':
            # AI 评论分析
            print()
            note_url = input("请输入要分析评论的笔记链接: ").strip()
            if not note_url:
                print("未输入笔记链接。")
                return

            # 获取评论
            print("正在获取评论...")
            from urllib import parse
            url_parse = parse.urlparse(note_url)
            note_id = url_parse.path.split("/")[-1]
            kvs = url_parse.query.split('&')
            kv_dist = {kv.split('=')[0]: kv.split('=')[1] for kv in kvs}
            xsec_token = kv_dist.get('xsec_token', '')

            success, msg, comments = data_spider.xhs_apis.get_note_all_out_comment(note_id, xsec_token, cookie_holder['cookies'], proxies)
            if not success and is_login_expired(str(msg)):
                success, msg, new_cookie = check_cookie_expired_and_retry(
                    'AI 评论分析', False, msg, data_spider, cookie_holder['cookies'], proxies)
                if success:
                    cookie_holder['cookies'] = load_env() or cookie_holder['cookies']
                    success, msg, comments = data_spider.xhs_apis.get_note_all_out_comment(note_id, xsec_token, cookie_holder['cookies'], proxies)
                else:
                    print(f"操作失败: {msg}")
                    return

            if not success or not comments:
                print(f"获取评论失败: {msg}")
                return

            print(f"共获取到 {len(comments)} 条评论，正在调用 AI 分析...")
            result = analyze_comments(ai_client, comments)
            print("\n" + "=" * 50)
            print("AI 评论分析结果：")
            print("=" * 50)
            print(result)

        else:
            print("无效的模式编号。")

    while True:
        try:
            run_once()
        except (KeyboardInterrupt, EOFError):
            print("\n程序已退出。")
            break
        print()
