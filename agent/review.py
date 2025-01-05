import time
import pandas as pd
from xhs import XhsClient, DataFetchError
from playwright.sync_api import sync_playwright
import random
import threading
import queue
from content_gen import ContentGenerator

class PostBrowsing:
    def __init__(self):
        self.base_url = "https://www.xiaohongshu.com"

    def sign(self,uri, data=None, a1="", web_session=""):
        """获取签名参数"""
        for attempt in range(10):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context()
                    context.add_init_script(path="xhs_aquirelikes/stealth.min.js")
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


    def download_items(self,items, keyword, data, searchlist, post_queue: queue.Queue, stop_signal: threading.Event):
        """下载并处理项目信息"""
        for item in items:
            try:
                if not item.get('note_card'):
                    searchlist.extend(it['search_word'] for it in item.get(item['model_type'], {}).get('queries', []))
                    continue
                print(item['id'],item.get('xsec_token', 'N/A'))

                note_info = self.xhs_client.get_note_by_id(note_id=item['id'], xsec_token=item.get('xsec_token', 'N/A'))
                note_info['comments']="，另一个人说：".join(self.xhs_client.get_note_all_comments(note_id=item['id'],xsec_token=item.get('xsec_token', 'N/A')))
                note_info['is_comment']=0
                # print("note_info:",note_info['desc'])

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
                    "is_comment":note_info['is_comment']
                })

            except KeyError as e:
                print(f"Missing key: {e} in item: {item}")
            except Exception as e:
                print(f"An error occurred while processing item: {e}")
        stop_signal.set()


    def fetch_notes(self, post_queue: queue.Queue, stop_signal: threading.Event,keyword="约会", page_size=20, page=1, searchlist=None, data=None):
        """递归地获取笔记信息"""
        if data is None:
            data = []
        if searchlist is None:
            searchlist = []

        try:
            response = self.xhs_client.get_note_by_keyword(keyword=keyword, page_size=page_size, page=page)
            if response['has_more']:
                self.download_items(response['items'], keyword, data, searchlist,post_queue, stop_signal)
                # print(f"Page {page} finished, total items: {len(data)}")
                time.sleep(2)  # 避免频繁请求
                return self.fetch_notes(post_queue=post_queue, stop_signal=stop_signal,keyword=keyword, page_size=page_size, page=page + 1, searchlist=searchlist, data=data)
            else:
                print("No more pages.")
        except DataFetchError as e:
            print(f"Data fetch error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return data


    def save_to_csv(self,data, filename='danyin3.txt'):
        """保存数据到CSV文件"""
        df = pd.DataFrame(data)
        df.to_csv(filename, mode='a', header=not df.empty, index=False, encoding='utf-8', sep='\t')
        print(f"Data saved to {filename}")


    def process_search_keywords(self,search_keywords, post_queue: queue.Queue, stop_signal: threading.Event):
        """处理搜索关键词列表"""
        processed_keywords = set()  # 用于跟踪已处理的关键词，防止重复处理
        while search_keywords:
            keyword=search_keywords.pop(0)  # 移除并获取第一个关键词
            if keyword in processed_keywords:
                print(f"Keyword '{keyword}' has already been processed. Skipping.")
                continue

            self.fetch_notes(keyword=keyword,page_size=20,page=1, searchlist=search_keywords,data=None,post_queue=post_queue, stop_signal=stop_signal)
            # if notes_data:
            #     self.save_to_csv(notes_data) 可以存下来，也可以托管到云端



            processed_keywords.add(keyword)  # 标记为已处理
            time.sleep(random.uniform(1, 3))  # 在每次搜索之间等待随机时间，以降低被封禁的风险


    def run(self,post_queue, stop_signal):
        search_keywords = [
            "萝卜快跑被叫停了是真的嘛"
            # 更多关键词可以添加到这里...
        ]

        cookie = [
            "abRequestId=3d38b6d7-54c6-506c-90e5-d24c17505174; xsecappid=xhs-pc-web; a1=19016ca0d3bcfqr92ya6kmo8j9t59is6ze0uwtrm050000197367; webId=c46e1637164e3aa8579de629d8d293c7; gid=yj8yKS0y4yuqyj8yKS08fd9FqDSiAFjJv0KT8686lYVj97282j3MKE888yjWqKW8JWjWqiiW; webBuild=4.53.0; acw_tc=0a4acac317359742330252411e81061c4e5a7bee696475b269684e67c3f360; websectiga=16f444b9ff5e3d7e258b5f7674489196303a0b160e16647c6c2b4dcb609f4134; sec_poison_id=a687ab8b-e8fa-4c0e-99c3-5aaeb0d8c208; web_session=0400697672710f8ee0f8ec954d354b96d9888f; unread={%22ub%22:%226777dbbe0000000013019905%22%2C%22ue%22:%2267776d65000000000b0144dd%22%2C%22uc%22:27}"]
        # "abRequestId=0a3e96df-8132-56e2-903e-e003e706cd4b; a1=193ed2577dcsxoj6vgymsyhyegofza5qs790witfu50000767340; webId=27ac00bd32768c12557b44e6d692ddec; gid=yjqdfJ2jqdMdyjqdfJ2WWW39fSMClVKhkv6Mji7vxvdkl828iu02AE888WKWq488YW0YK2fq; webBuild=4.50.0; xsecappid=xhs-pc-web; acw_tc=0a4ab81817352130829222677ee61f468e8401136dcde0a1d5b85386df60f4; websectiga=10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467; sec_poison_id=8d6c1e2c-098d-407e-b4e3-e1d0442d5c6e; web_session=0400697672658100aed3f80858354b13745238; unread={%22ub%22:%226762c7db000000000b01407f%22%2C%22ue%22:%22676b9693000000000900e88a%22%2C%22uc%22:28}"]
        self.xhs_client = XhsClient(cookie=random.choice(cookie), sign=self.sign)
        self.process_search_keywords(search_keywords=search_keywords,post_queue=post_queue,stop_signal= stop_signal)