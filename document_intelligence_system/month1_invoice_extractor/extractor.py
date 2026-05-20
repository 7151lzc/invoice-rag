"""
发票信息提取器 - AI版
使用文心大模型直接识别，同时支持超市小票和增值税发票
"""

import re
import json
import os
import base64
from openai import OpenAI


class InvoiceExtractor:
    def __init__(self):
        self.ocr_results = []
        self.all_text = ""
        self.text_with_pos = []
        # 初始化AI客户端
        self.llm = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url="https://aistudio.baidu.com/llm/lmapi/v3"
        )
    
    def load_ocr_results(self, ocr_results):
        """加载OCR结果（保留用于调试）"""
        self.ocr_results = ocr_results
        self.text_with_pos = []
        texts = []
        for line in ocr_results:
            text = line[1][0]
            confidence = line[1][1]
            position = line[0]
            texts.append(text)
            self.text_with_pos.append({
                "text": text,
                "confidence": confidence,
                "position": position
            })
        self.all_text = "".join(texts)
    
    def extract_with_ai(self, image_path):
        """使用AI模型提取发票信息 - 禁止编造版"""
        
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        
        response = self.llm.chat.completions.create(
            model="ernie-4.5-turbo-vl",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格的票据信息提取助手。你的规则：只能从图片中直接读取信息，绝对不能编造任何内容。图片中没有的字段，必须返回空字符串。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """从这张票据图片中提取信息。

    只返回JSON，格式如下：
    {"invoice_number": "", "amount": "", "date": "", "seller": "", "buyer": ""}

    规则：
    - invoice_number：发票号码或小票号，没有就""
    - amount：总金额数字（如10000.00），没有就""
    - date：日期（YYYY-MM-DD），没有就""
    - seller：销售方/店铺名，必须在图片中明确出现，否则就""
    - buyer：购买方，必须在图片中明确出现，否则""

    警告：如果你不确定某个字段，或者图片中没有，必须返回空字符串""！不要编造任何公司名！"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,  # 设为0，完全按照规则输出
        )
        
        result_text = response.choices[0].message.content
        print(f"AI返回: {result_text}")
        
        try:
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_text)
            
            # 确保所有字段都是字符串
            for key in ["invoice_number", "amount", "date", "seller", "buyer"]:
                if key not in result:
                    result[key] = ""
            
            return result
        except Exception as e:
            print(f"解析失败: {e}")
            return {"invoice_number": "", "amount": "", "date": "", "seller": "", "buyer": ""}
    
    def extract_from_image(self, image_path, ocr_engine=None):
        """完整流程 - 使用AI提取"""
        print("正在使用AI识别发票...")
        
        # 直接用AI提取
        result = self.extract_with_ai(image_path)
        
        # 同时运行OCR用于调试（可选）
        if ocr_engine:
            ocr_results = ocr_engine.recognize(image_path)
            if ocr_results:
                self.load_ocr_results(ocr_results)
        
        return result
    
    def save_to_json(self, data, output_path):
        """保存到JSON"""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_path}")