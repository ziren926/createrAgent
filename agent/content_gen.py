from openai import OpenAI
from typing import Dict, Optional
import os
import json

# 设置 OpenAI API key

class ContentGenerator:
    def __init__(self,api_key):
        self.client = OpenAI(api_key=api_key)
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
            标题: {note_info.get('Title', '')}
            内容: {note_info.get('Description', '')}
            别人的回复:{note_info.get('Comments', '')}
            
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

    def generate_analytics_process(self,note_info: Dict) -> Dict:

        try:
            # 构建提示词
            prompt = f"""
            你是一个社交媒体助手。以下是一个帖子的内容：
            Title: {note_info['Title']}
            Description: {note_info['Description']}
            别人的回复: {note_info['Comments']}
            
            根据内容，决定以下操作：
            1. 是否回复？如果是，生成回复内容。
            2. 是否点赞？
            3. 是否比心？
            
            三个动作只可以选一个，输出格式必须是JSON，参考这个格式，只要{{}}和里面的内容，因为我要直接在下游转换成json
            {{
                "reply": true,
                "reply_content": "这是一个很有趣的帖子！",
                "like": true,
                "favorite": false
            }}
            
            """

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是一个友好的又幽默的社交媒体用户，善于与他人互动。"},
                    {"role": "user", "content": prompt}
                ]
            )

            print(response.choices[0].message.content)

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"生成回复时出错: {e}")
            return {}

