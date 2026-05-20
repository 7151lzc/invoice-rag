"""
文档加载器
加载发票JSON和文本文档
"""

import os
import json
from typing import List, Dict


class DocumentLoader:
    """文档加载器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.documents = []
    
    def load_invoices(self, invoice_dir: str = "data/invoices") -> List[Dict]:
        """
        加载发票JSON文件
        每个JSON对应一张发票的提取结果
        """
        documents = []
        
        if not os.path.exists(invoice_dir):
            print(f"目录不存在: {invoice_dir}")
            return documents
        
        for filename in os.listdir(invoice_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(invoice_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 构造文档文本
                doc_text = self._invoice_to_text(data, filename)
                documents.append({
                    "id": filename.replace('.json', ''),
                    "text": doc_text,
                    "metadata": {
                        "source": filename,
                        "type": "invoice",
                        "invoice_number": data.get("invoice_number", ""),
                        "amount": data.get("amount", ""),
                        "date": data.get("date", ""),
                        "seller": data.get("seller", ""),
                        "buyer": data.get("buyer", "")
                    }
                })
        
        print(f"加载了 {len(documents)} 张发票")
        return documents
    
    def _invoice_to_text(self, data: Dict, filename: str) -> str:
        """将发票数据转换为文本"""
        text = f"""
发票信息：
- 发票号码：{data.get('invoice_number', '未知')}
- 金额：{data.get('amount', '未知')}元
- 开票日期：{data.get('date', '未知')}
- 销售方：{data.get('seller', '未知')}
- 购买方：{data.get('buyer', '未知')}
        """.strip()
        return text
    
    def load_text_files(self, text_dir: str = "data/knowledge") -> List[Dict]:
        """加载文本文档"""
        documents = []
        
        if not os.path.exists(text_dir):
            return documents
        
        for filename in os.listdir(text_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(text_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                documents.append({
                    "id": filename.replace('.txt', ''),
                    "text": content,
                    "metadata": {
                        "source": filename,
                        "type": "knowledge"
                    }
                })
        
        print(f"加载了 {len(documents)} 个文本文档")
        return documents
    
    def load_all(self) -> List[Dict]:
        """加载所有文档"""
        all_docs = []
        all_docs.extend(self.load_invoices())
        all_docs.extend(self.load_text_files())
        return all_docs


if __name__ == "__main__":
    loader = DocumentLoader()
    docs = loader.load_all()
    for doc in docs:
        print(f"文档: {doc['id']}")
        print(f"内容: {doc['text'][:100]}...")
        print()