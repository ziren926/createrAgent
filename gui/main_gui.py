import tkinter as tk
from tkinter import messagebox
from agent.content_gen import ContentGenerator  # 引入之前实现的 ContentGenerator
from agent.follower_manage import FollowerManager  # 假设你写了 follower_manager.py

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("社交媒体管理工具")
        self.root.geometry("500x400")

        # 创建 ContentGenerator 实例
        self.content_generator = ContentGenerator()

        # 创建 FollowerManager 实例
        self.follower_manager = FollowerManager()

        # 设置界面控件
        self.create_widgets()

    def create_widgets(self):
        # 标题和内容输入框
        self.title_label = tk.Label(self.root, text="标题:")
        self.title_label.grid(row=0, column=0, padx=10, pady=5)
        self.title_entry = tk.Entry(self.root, width=40)
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)

        self.desc_label = tk.Label(self.root, text="内容:")
        self.desc_label.grid(row=1, column=0, padx=10, pady=5)
        self.desc_entry = tk.Entry(self.root, width=40)
        self.desc_entry.grid(row=1, column=1, padx=10, pady=5)

        self.comments_label = tk.Label(self.root, text="评论:")
        self.comments_label.grid(row=2, column=0, padx=10, pady=5)
        self.comments_entry = tk.Entry(self.root, width=40)
        self.comments_entry.grid(row=2, column=1, padx=10, pady=5)

        # 生成回复按钮
        self.generate_button = tk.Button(self.root, text="生成幽默回复", command=self.generate_response)
        self.generate_button.grid(row=3, column=0, columnspan=2, pady=20)

        # 显示生成的回复
        self.response_label = tk.Label(self.root, text="生成的回复:")
        self.response_label.grid(row=4, column=0, padx=10, pady=5)
        self.response_text = tk.Text(self.root, width=40, height=5, wrap=tk.WORD)
        self.response_text.grid(row=4, column=1, padx=10, pady=5)

        # 管理粉丝按钮
        self.manage_followers_button = tk.Button(self.root, text="管理粉丝", command=self.manage_followers)
        self.manage_followers_button.grid(row=5, column=0, columnspan=2, pady=20)

    def generate_response(self):
        # 获取输入的内容
        note_info = {
            "title": self.title_entry.get(),
            "desc": self.desc_entry.get(),
            "comments": self.comments_entry.get()
        }

        # 调用 ContentGenerator 生成回复
        response = self.content_generator.generate_response(note_info)

        # 在文本框中显示回复
        self.response_text.delete(1.0, tk.END)  # 清空之前的回复
        self.response_text.insert(tk.END, response)

    def manage_followers(self):
        # 这个方法用来管理粉丝
        followers = self.follower_manager.get_followers()  # 获取粉丝数据（假设你已经写了这个方法）

        # 在此展示粉丝信息，或者弹出新窗口管理粉丝
        messagebox.showinfo("粉丝信息", f"当前粉丝数量: {len(followers)}")  # 这里只是示例

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()