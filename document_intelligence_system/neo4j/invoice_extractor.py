"""
发票提取器 - 调用第1个月的AI提取功能
"""

import os
import json
import re
import base64
from openai import OpenAI


class InvoiceExtractor:
    def __init__(self):
        self.llm = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://aistudio.baidu.com/llm/lmapi/v3"
        )
    
    def _parse_json_response(self, text: str) -> dict:
        """解析AI返回的JSON，处理各种格式问题"""
        # 尝试提取JSON部分
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group()
        
        # 尝试修复常见问题
        text = text.replace("'", '"')  # 单引号转双引号
        text = re.sub(r',\s*}', '}', text)  # 去掉末尾逗号
        text = re.sub(r',\s*]', ']', text)  # 去掉数组末尾逗号
        
        # 尝试解析
        try:
            return json.loads(text)
        except:
            pass
        
        # 手动提取字段
        result = {}
        fields = ["invoice_number", "amount", "date", "seller", "buyer"]
        for field in fields:
            # 匹配 "field": "value" 或 "field": "value"
            pattern = rf'"{field}"\s*:\s*"([^"]*)"'
            match = re.search(pattern, text)
            if match:
                result[field] = match.group(1)
            else:
                result[field] = ""
        
        return result
    
    def extract_from_image(self, image_path: str) -> dict:
        """从图片提取发票信息"""
        if not os.path.exists(image_path):
            return {"error": "图片不存在"}
        
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        
        try:
            response = self.llm.chat.completions.create(
                model="ernie-4.5-turbo-vl",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """从这张图片中提取发票信息，只返回JSON，不要有其他内容。

{
    "invoice_number": "发票号码",
    "amount": "总金额数字",
    "date": "开票日期",
    "seller": "销售方名称",
    "buyer": "购买方名称"
}

如果某个字段没有，就写空字符串。"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }],
                temperature=0.1,
            )
            
            result_text = response.choices[0].message.content
            print(f"AI返回原始内容: {result_text}")  # 调试用
            
            result = self._parse_json_response(result_text)
            
            # 确保所有字段都有值
            default_fields = {"invoice_number": "", "amount": "", "date": "", "seller": "", "buyer": ""}
            default_fields.update(result)
            
            return default_fields
            
        except Exception as e:
            return {"error": str(e)}
        
    def extract_from_file(self, file_path: str) -> dict:
        """从文件路径提取（兼容批量）"""
        return self.extract_from_image(file_path)


# 测试代码
if __name__ == "__main__":
    extractor = InvoiceExtractor()
    # 测试图片路径
    # result = extractor.extract_from_image("test.jpg")
    # print(result)