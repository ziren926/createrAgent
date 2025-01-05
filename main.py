import threading
import queue
from agent.review import PostBrowsing
from agent.content_gen import ContentGenerator
from agent.load_yaml import load_config
# from xhs import XhsClient
import random
from playwright.sync_api import sync_playwright
import time
from agent.xhs_api import XhsClient
from agent.reply import ReplyThread

# from agent.follower_manager import FollowerManager
# from agent.post_browser import PostBrowser
# from agent.post_responder import PostResponder


def sign(uri, data=None, a1="", web_session=""):
    """获取签名参数"""
    for attempt in range(10):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                context.add_init_script(path="stealth.min.js")
                page = context.new_page()
                page.goto("https://www.xiaohongshu.com")
                context.add_cookies([{'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}])
                page.reload()
                time.sleep(2)  # 等待加载完成
                encrypt_params = page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {"x-s": encrypt_params["X-s"], "x-t": str(encrypt_params["X-t"])}
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    raise Exception("Failed to get signature after multiple attempts.")






def main():
    #读取配置
    config = load_config("config.yaml")
    search_keywords = config.get("search_keyword","萝卜快跑")
    min_likes = config.get("min_likes",1)
    filter_keywords = config.get("filter_keywords")
    cookie = config.get("cookies")
    openai_api_key=config.get("openai_api_key")



    #启动小红书

    xhs_client = XhsClient(cookie=random.choice(cookie), sign=sign)

    # 初始化模块
    content_gen = ContentGenerator(openai_api_key)

    # 初始化队列和信号
    post_queue = queue.Queue()  # 存储所有浏览到的帖子
    interesting_queue = queue.Queue()  # 存储筛选出的有趣帖子
    stop_signal = threading.Event()  # 用于控制筛选线程的停止信号


    # 定义浏览线程
    browse_thread = threading.Thread(
        target=PostBrowsing().process_search_keywords,
        args=(xhs_client,search_keywords,post_queue, stop_signal),
        name="BrowseThread"
    )

    # 定义筛选线程
    filter_thread = threading.Thread(
        target=PostBrowsing().filter_posts,
        args=(xhs_client,post_queue, interesting_queue, stop_signal, min_likes, filter_keywords),
        name="FilterThread"
    )


    # 启动线程
    browse_thread.start()
    filter_thread.start()

    reply_thread = ReplyThread(interesting_queue, xhs_client, content_gen, stop_signal)
    reply_thread.start()

    # 等待线程完成
    browse_thread.join()
    filter_thread.join()
    reply_thread.join()


    print("所有任务已完成！")


if __name__ == "__main__":
    main()