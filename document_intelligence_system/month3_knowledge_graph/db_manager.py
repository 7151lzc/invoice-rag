"""
数据库管理模块
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional


class DBManager:
    """SQLite 数据库管理"""
    
    def __init__(self, db_path: str = "invoices.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 发票表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                invoice_number TEXT,
                amount REAL,
                date TEXT,
                seller TEXT,
                buyer TEXT,
                type TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引，加速查询
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_amount ON invoices(amount)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON invoices(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_seller ON invoices(seller)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON invoices(type)')
        
        conn.commit()
        conn.close()
        print("数据库初始化完成")
    
    def insert_invoice(self, inv_id: str, invoice_number: str, amount: float,
                       date: str, seller: str, buyer: str, inv_type: str, raw_data: dict):
        """插入或更新发票"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO invoices 
            (id, invoice_number, amount, date, seller, buyer, type, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (inv_id, invoice_number, amount, date, seller, buyer, inv_type, json.dumps(raw_data, ensure_ascii=False)))
        conn.commit()
        conn.close()
    
    def get_all_invoices(self) -> List[Dict]:
        """获取所有发票"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, invoice_number, amount, date, seller, buyer, type FROM invoices ORDER BY date DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "invoice_number": row[1],
            "amount": row[2],
            "date": row[3],
            "seller": row[4],
            "buyer": row[5],
            "type": row[6]
        } for row in rows]
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict]:
        """根据发票号码查询"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, invoice_number, amount, date, seller, buyer, type FROM invoices WHERE invoice_number = ?', (invoice_number,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "invoice_number": row[1],
                "amount": row[2],
                "date": row[3],
                "seller": row[4],
                "buyer": row[5],
                "type": row[6]
            }
        return None
    
    def get_invoices_by_seller(self, seller: str) -> List[Dict]:
        """根据销售方查询"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, invoice_number, amount, date, seller, buyer, type FROM invoices WHERE seller LIKE ?', (f'%{seller}%',))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "invoice_number": row[1],
            "amount": row[2],
            "date": row[3],
            "seller": row[4],
            "buyer": row[5],
            "type": row[6]
        } for row in rows]
    
    def get_invoices_by_amount_range(self, min_amount: float, max_amount: float) -> List[Dict]:
        """根据金额范围查询"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, invoice_number, amount, date, seller, buyer, type 
            FROM invoices 
            WHERE amount >= ? AND amount <= ?
            ORDER BY amount DESC
        ''', (min_amount, max_amount))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "invoice_number": row[1],
            "amount": row[2],
            "date": row[3],
            "seller": row[4],
            "buyer": row[5],
            "type": row[6]
        } for row in rows]
    
    def get_invoices_by_year(self, year: str) -> List[Dict]:
        """根据年份查询"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, invoice_number, amount, date, seller, buyer, type FROM invoices WHERE date LIKE ?', (f'{year}%',))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "invoice_number": row[1],
            "amount": row[2],
            "date": row[3],
            "seller": row[4],
            "buyer": row[5],
            "type": row[6]
        } for row in rows]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM invoices')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(amount), AVG(amount), MAX(amount), MIN(amount) FROM invoices')
        row = cursor.fetchone()
        sum_amount, avg_amount, max_amount, min_amount = row
        
        cursor.execute('SELECT type, COUNT(*) FROM invoices GROUP BY type')
        type_stats = dict(cursor.fetchall())
        
        cursor.execute('SELECT seller, COUNT(*) FROM invoices WHERE seller != "" GROUP BY seller ORDER BY COUNT(*) DESC')
        seller_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_count": total,
            "total_amount": sum_amount or 0,
            "avg_amount": avg_amount or 0,
            "max_amount": max_amount or 0,
            "min_amount": min_amount or 0,
            "type_stats": type_stats,
            "seller_stats": [{"seller": s[0], "count": s[1]} for s in seller_stats]
        }
    
    def clear_all(self):
        """清空所有数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM invoices')
        conn.commit()
        conn.close()
        print("已清空数据库")
    
    def get_count(self) -> int:
        """获取发票数量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM invoices')
        count = cursor.fetchone()[0]
        conn.close()
        return count


if __name__ == "__main__":
    db = DBManager()
    print(f"当前发票数量: {db.get_count()}")