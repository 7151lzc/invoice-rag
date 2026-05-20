"""
发票管理器 - 加载JSON到数据库
"""

import os
import json
from db_manager import DBManager  # 修复：去掉前缀


class InvoiceManager:
    def __init__(self, db: DBManager = None):
        self.db = db or DBManager()
    
    def load_from_json_dir(self, json_dir: str = "data/invoices") -> int:
        if not os.path.exists(json_dir):
            print(f"目录不存在: {json_dir}")
            return 0
        
        count = 0
        for filename in os.listdir(json_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(json_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            inv_id = filename.replace('.json', '')
            invoice_number = data.get("invoice_number", "")
            amount_str = data.get("amount", "0")
            try:
                amount = float(amount_str) if amount_str else 0
            except:
                amount = 0
            date = data.get("date", "")
            seller = data.get("seller", "")
            buyer = data.get("buyer", "")
            inv_type = data.get("type", "")
            
            self.db.insert_invoice(inv_id, invoice_number, amount, date, seller, buyer, inv_type, data)
            count += 1
            print(f"已加载: {filename}")
        
        print(f"共加载 {count} 张发票")
        return count
    
    def add_invoice_from_extract(self, inv_id: str, extracted_data: dict):
        """添加从图片提取的发票"""
        invoice_number = extracted_data.get("invoice_number", "")
        amount_str = extracted_data.get("amount", "0")
        try:
            amount = float(amount_str) if amount_str else 0
        except:
            amount = 0
        date = extracted_data.get("date", "")
        seller = extracted_data.get("seller", "")
        buyer = extracted_data.get("buyer", "")
        
        self.db.insert_invoice(inv_id, invoice_number, amount, date, seller, buyer, "extracted", extracted_data)
        print(f"已添加发票: {invoice_number}")