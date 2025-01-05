import threading
import queue
from agent.review import PostBrowsing
from agent.analyze_content import PostAnalyzer
from agent.content_gen import ContentGenerator
from agent.like import LikeThread
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
    search_keywords = config.get("search_keyword","AI AGENT")
    cookie = config.get("cookies")
    openai_api_key=config.get("openai_api_key")



    #启动小红书

    xhs_client = XhsClient(cookie=random.choice(cookie), sign=sign)

    # 初始化模块
    content_gen = ContentGenerator(openai_api_key)

    # 初始化队列和信号
    post_queue = queue.Queue()  # 存储所有浏览到的帖子
    action_queues = {
        "reply": queue.Queue(),
        "like": queue.Queue(),
        "favorite": queue.Queue(),
        # 可以根据需要添加更多队列
    }
    stop_signal = threading.Event()  # 用于控制筛选线程的停止信号


    # 定义浏览线程
    browse_thread = PostBrowsing(post_queue, stop_signal,xhs_client,search_keywords)

    # 定义筛选线程
    analyzer_thread = PostAnalyzer(post_queue, action_queues, stop_signal,openai_api_key)

    # 定义回复线程
    reply_thread = ReplyThread(action_queues["reply"], xhs_client, stop_signal)

    # 定义喜欢线程
    like_thread = LikeThread(action_queues["like"], xhs_client, stop_signal)


    # 启动线程
    browse_thread.start()
    analyzer_thread.start()
    reply_thread.start()
    like_thread.start()

    # 等待线程完成
    browse_thread.join()
    analyzer_thread.join()
    reply_thread.join()
    like_thread.join()


    print("所有任务已完成！")


if __name__ == "__main__":
    main()