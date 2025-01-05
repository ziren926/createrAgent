from openai import OpenAI
from typing import Dict, Optional
import os

# 设置 OpenAI API key

class ContentGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    def generate_response(self,note_info: Dict) -> str:
        """
        根据笔记内容生成回复

        Args:
            note_info: 笔记信息字典
        Returns:
            str: 生成的回复内容
        """

        try:
            # 构建提示词
            prompt = f"""
            标题: {note_info.get('title', '')}
            内容: {note_info.get('desc', '')}
            别人的回复:{note_info.get('comments', '')}
            
            请根据以上内容生成一个幽默的回复，要求：
            1. 语气诙谐幽默，要让别人觉得你的回复很好笑
            2. 不要出现期待、希望 这两个词语，不要各种祝愿性的句子
            3. 与内容相关
            4. 长度适中（30字以内），尽量控制在一句话里。
            5. 避免过于营销化的语言
            6. 尽量模仿别人回复的语气
            """

            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "system", "content": "你是一个友好的社交媒体用户，善于与他人互动。"},
            #         {"role": "user", "content": prompt}
            #     ],
            #     temperature=0.7,
            #     max_tokens=100
            # )

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是一个友好的又幽默的社交媒体用户，善于与他人互动。"},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"生成回复时出错: {e}")
            return ""

