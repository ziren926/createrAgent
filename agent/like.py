import threading
import time
import queue


class LikeThread(threading.Thread):
    def __init__(self, like_queue, xhs_client, stop_signal):
        super().__init__()
        self.like_queue = like_queue
        self.xhs_client = xhs_client
        self.stop_signal = stop_signal

    def run(self):
        while not self.stop_signal.is_set() or not self.like_queue.empty():
            try:
                post = self.like_queue.get(timeout=1)
                print(f"Liking post {post['Title']}")
                self.xhs_client.like_note(post['Item ID'])
            except queue.Empty:
                continue
        print("Liking stopped.")