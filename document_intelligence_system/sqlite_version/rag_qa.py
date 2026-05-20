"""
RAG问答 - 第2个月功能
"""

import os
from openai import OpenAI


class RAGQA:
    def __init__(self):
        self.llm = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://aistudio.baidu.com/llm/lmapi/v3"
        )
    
    def ask(self, question: str, context: str = "") -> str:
        """基于上下文回答问题"""
        prompt = f"""根据以下信息回答问题。如果信息不足，就说不知道。

信息：{context}

问题：{question}

回答："""
        
        try:
            response = self.llm.chat.completions.create(
                model="ernie-4.5-turbo-vl",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"调用失败: {e}"