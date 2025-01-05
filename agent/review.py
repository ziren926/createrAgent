import time
import pandas as pd
from xhs import XhsClient, DataFetchError
from playwright.sync_api import sync_playwright
import random
import threading
import queue
import logging

class PostBrowsing(threading.Thread):
    def __init__(self, post_queue, stop_signal,xhs_client,search_keywords):
        super().__init__()
        self.post_queue = post_queue
        self.stop_signal = stop_signal
        self.xhs_client= xhs_client
        self.search_keywords=search_keywords

    def download_items(self, items, keyword, searchlist, post_queue: queue.Queue, stop_signal: threading.Event):
        """下载并处理项目信息"""
        for item in items:
            if stop_signal.is_set():
                logging.info("Stop signal received. Exiting download_items.")
                return

            try:
                if not item.get('note_card'):
                    searchlist.extend(it['search_word'] for it in item.get(item['model_type'], {}).get('queries', []))
                    continue

                note_info = self.xhs_client.get_note_by_id(note_id=item['id'], xsec_token=item.get('xsec_token', 'N/A'))
                note_info['comments'] = "，另一个人说：".join(
                    self.xhs_client.get_note_all_comments(note_id=item['id'], xsec_token=item.get('xsec_token', 'N/A'))
                )
                note_info['is_comment'] = 0

                post_queue.put({
                    "Keyword": keyword,
                    "Item ID": item.get('id', 'N/A'),
                    "XSEC Token": item.get('xsec_token', 'N/A'),
                    "Collected Count": note_info['interact_info']['collected_count'],
                    "Comment Count": note_info['interact_info']['comment_count'],
                    "Share Count": note_info['interact_info']['share_count'],
                    "Last Update Time": note_info['last_update_time'],
                    "Title": note_info['title'].replace('\n', '').replace('\t', ''),
                    "Description": note_info['desc'].replace('\n', '').replace('\t', ''),
                    "Tag List": ','.join(tag['name'] for tag in note_info.get('tag_list', [])),
                    "IP Location": note_info.get('ip_location', 'N/A'),
                    "Liked Count": note_info['interact_info']['liked_count'],
                    "User ID": item['note_card']['user'].get('user_id', 'N/A'),
                    "Nickname": item['note_card']['user'].get('nickname', 'N/A'),
                    "Avatar URL": item['note_card']['user'].get('avatar', 'N/A'),
                    "Comments": note_info['comments'].replace('\n', '').replace('\t', ''),
                    "Image List": ','.join([img['url'] for img in note_info.get('image_list', [])]),
                    "is_comment": note_info['is_comment']
                })
                queue_size = post_queue.qsize()
                print(f"There are {queue_size} posts in the queue.")

            except KeyError as e:
                logging.warning(f"Missing key: {e} in item: {item}")
            except Exception as e:
                logging.error(f"An error occurred while processing item: {e}")
        stop_signal.set()

    def fetch_notes(self, post_queue: queue.Queue, stop_signal: threading.Event, keyword="约会", page_size=20, page=1, searchlist=None):
        """递归地获取笔记信息"""

        if searchlist is None:
            searchlist = []

        try:
            response = self.xhs_client.get_note_by_keyword(keyword=keyword, page_size=page_size, page=page)
            if response['has_more']:
                self.download_items(response['items'], keyword, searchlist, post_queue, stop_signal)
                time.sleep(2)  # 避免频繁请求
                if not stop_signal.is_set():
                    return self.fetch_notes(post_queue=post_queue, stop_signal=stop_signal, keyword=keyword, page_size=page_size, page=page + 1, searchlist=searchlist)
                else:
                    logging.info("Stop signal received during fetch_notes.")
            else:
                logging.info("No more pages.")
        except DataFetchError as e:
            logging.warning(f"Data fetch error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def save_to_csv(self, data, filename='danyin3.txt'):
        """保存数据到CSV文件"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, mode='a', header=not df.empty, index=False, encoding='utf-8', sep='\t')
            logging.info(f"Data saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving data to CSV: {e}")

    def run(self):
        """处理搜索关键词列表"""
        processed_keywords = set()  # 用于跟踪已处理的关键词，防止重复处理
        while self.search_keywords and not self.stop_signal.is_set():

            keyword = self.search_keywords.pop(0)  # 移除并获取第一个关键词
            if keyword in processed_keywords:
                logging.info(f"Keyword '{keyword}' has already been processed. Skipping.")
                continue

            self.fetch_notes(keyword=keyword, page_size=20, page=1, searchlist=self.search_keywords, post_queue=self.post_queue, stop_signal=self.stop_signal)
            processed_keywords.add(keyword)  # 标记为已处理
            time.sleep(random.uniform(1, 3))  # 在每次搜索之间等待随机时间，以降低被封禁的风险

    # def filter_posts(self, xhs_client, post_queue, interesting_queue, stop_signal, min_likes=100, keywords=None):
    #     """从队列中筛选有趣的帖子"""
    #     self.xhs_client = xhs_client
    #     if keywords is None:
    #         keywords = ["搞笑", "有趣", "趣味", "爆笑"]
    #
    #     while not stop_signal.is_set() or not post_queue.empty():
    #         try:
    #             post = post_queue.get(timeout=1)
    #
    #             if self.convert_to_int(post.get('Liked Count', '0')) >= min_likes:
    #                 interesting_queue.put(post)
    #             else:
    #                 for keyword in keywords:
    #                     if keyword in post['Title'] or keyword in post['Description']:
    #                         interesting_queue.put(post)
    #                         break
    #             queue_size = interesting_queue.qsize()
    #             print(f"There are {queue_size} interesting posts in the queue.")
    #         except queue.Empty:
    #             continue
    #     stop_signal.set()
    #
    # def convert_to_int(self,liked_count_str: str) -> int:
    #     if '万' in liked_count_str:
    #         # 去掉万字并转换为数字，假设万是10,000
    #         num_str = liked_count_str.replace('万', '')
    #         try:
    #             return int(float(num_str) * 10000)
    #         except ValueError:
    #             return 0  # 如果转换失败，返回0
    #     elif 'K' in liked_count_str:
    #         # 去掉K字并转换为数字，假设K是1,000
    #         num_str = liked_count_str.replace('K', '')
    #         try:
    #             return int(float(num_str) * 1000)
    #         except ValueError:
    #             return 0  # 如果转换失败，返回0
    #     else:
    #         # 如果没有单位，直接转换为数字
    #         try:
    #             return int(liked_count_str)
    #         except ValueError:
    #             return 0  # 如果转换失败，返回0