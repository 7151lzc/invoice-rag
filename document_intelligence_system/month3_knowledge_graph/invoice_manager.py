"""
发票管理器：从JSON文件加载数据到数据库
"""

import os
import json
from typing import List, Dict
from db_manager import DBManager


class InvoiceManager:
    """发票管理器"""
    
    def __init__(self, db: DBManager = None):
        self.db = db or DBManager()
    
    def load_from_json_dir(self, json_dir: str = "data/invoices") -> int:
        """从JSON目录加载所有发票"""
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
            
            # 提取字段
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
            
            # 插入数据库
            self.db.insert_invoice(
                inv_id=inv_id,
                invoice_number=invoice_number,
                amount=amount,
                date=date,
                seller=seller,
                buyer=buyer,
                inv_type=inv_type,
                raw_data=data
            )
            count += 1
            print(f"已加载: {filename} ({invoice_number}, {amount}元)")
        
        print(f"\n共加载 {count} 张发票")
        return count
    
    def print_all(self):
        """打印所有发票"""
        invoices = self.db.get_all_invoices()
        if not invoices:
            print("暂无发票数据")
            return
        
        print("\n" + "="*60)
        print("发票列表")
        print("="*60)
        for inv in invoices:
            print(f"  发票号: {inv['invoice_number']}")
            print(f"  金额: {inv['amount']} 元")
            print(f"  日期: {inv['date']}")
            print(f"  销售方: {inv['seller'] or '无'}")
            print(f"  类型: {inv['type']}")
            print("-"*40)


if __name__ == "__main__":
    manager = InvoiceManager()
    manager.load_from_json_dir()
    manager.print_all()