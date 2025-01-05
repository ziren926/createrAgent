import threading
import time
import queue

class ReplyThread(threading.Thread):
    def __init__(self, reply_queue, xhs_client, stop_signal):
        super().__init__()
        self.reply_queue = reply_queue
        self.xhs_client = xhs_client
        self.stop_signal = stop_signal

    def run(self):
        while not self.stop_signal.is_set():  # 检查停止信号
            # print(f"Queue size: {self.interesting_queue.qsize()}")  # 调试：检查队列大小
            try:
                post, reply_content = self.reply_queue.get(timeout=1)
                print(f"Replying to post {post['Item ID']} with content: {reply_content}")  # 立刻返回，无需等待

                # 生成回复内容
                # response = self.content_gen.generate_response(post)
                # print(f"有趣的帖子: {post['Title']} (Likes: {post['Liked Count']}), 回复了: {response}")

                # 回复帖子
                try:
                    self.xhs_client.comment_note(note_id=post['Item ID'], content=reply_content)
                except Exception as e:
                    print(f"评论失败，帖子 ID {post['Item ID']}， 错误: {e}")

            except queue.Empty:
                # 队列为空时休眠1秒再继续
                time.sleep(1)

        print("回复线程已停止")
