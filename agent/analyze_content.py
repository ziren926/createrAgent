import time
import pandas as pd
from xhs import XhsClient, DataFetchError
from playwright.sync_api import sync_playwright
import random
import threading
import queue
from agent.content_gen import ContentGenerator


class PostAnalyzer(threading.Thread):
    def __init__(self, post_queue, action_queues, stop_signal,openai_api_key):
        super().__init__()
        self.post_queue = post_queue
        self.action_queues = action_queues
        self.stop_signal = stop_signal
        self.openai_api_key=openai_api_key


    def run(self):
        while not self.stop_signal.is_set() or not self.post_queue.empty():
            try:
                post = self.post_queue.get(timeout=1)
                print(f"Analyzing post: {post['Title']}")
                action_plan = ContentGenerator(self.openai_api_key).generate_analytics_process(post)

                if action_plan.get("reply"):
                    self.action_queues["reply"].put((post, action_plan["reply_content"]))
                if action_plan.get("like"):
                    self.action_queues["like"].put(post)
                if action_plan.get("favorite"):
                    self.action_queues["favorite"].put(post)
                print(self.action_queues)

            except queue.Empty:
                continue
        print("Post analysis stopped.")