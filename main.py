import threading
import queue
from agent.review import PostBrowsing
# from agent.follower_manager import FollowerManager
# from agent.post_browser import PostBrowser
# from agent.post_responder import PostResponder


def main():
    # 初始化模块
    #content_gen = ContentGenerator()
    # follower_mgr = FollowerManager()
    # post_browser = PostBrowser()
    # post_responder = PostResponder()

    # 初始化队列和信号
    post_queue = queue.Queue()  # 存储所有浏览到的帖子
    interesting_queue = queue.Queue()  # 存储筛选出的有趣帖子
    stop_signal = threading.Event()  # 用于控制筛选线程的停止信号

    # 浏览和筛选的参数
    search_query = "搞笑"
    min_likes = 100
    keywords = ["搞笑", "有趣", "趣味", "爆笑"]

    # 定义浏览线程
    browse_thread = threading.Thread(
        target=PostBrowsing.run,
        args=(post_queue, stop_signal),
        name="BrowseThread"
    )

    # 定义筛选线程
    filter_thread = threading.Thread(
        target=post_browser.filter_posts,
        args=(post_queue, interesting_queue, stop_signal, min_likes, keywords),
        name="FilterThread"
    )

    # 启动线程
    browse_thread.start()
    filter_thread.start()

    # 等待线程完成
    browse_thread.join()
    filter_thread.join()

    # 处理筛选结果
    while not interesting_queue.empty():
        post = interesting_queue.get()
        print(f"有趣的帖子: {post['title']} (Likes: {post['likes']})")
        # 回复有趣的帖子
        response = content_gen.generate_response(post)
        post_responder.reply_to_post(post['user_id'], post['title'], response)

    print("所有任务已完成！")


if __name__ == "__main__":
    main()