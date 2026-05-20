"""
查询引擎：自然语言查询转SQL
"""

from db_manager import DBManager


class QueryEngine:
    """查询引擎"""
    
    def __init__(self, db: DBManager = None):
        self.db = db or DBManager()
    
    def query(self, question: str) -> str:
        """
        处理自然语言查询
        """
        q = question.lower().strip()
        
        # 统计类查询
        if "多少张" in q or "数量" in q or "count" in q:
            count = self.db.get_count()
            return f"共有 {count} 张发票"
        
        # 总金额
        if "总金额" in q or "合计" in q or "total" in q:
            stats = self.db.get_statistics()
            return f"发票总金额为 {stats['total_amount']:.2f} 元"
        
        # 平均金额
        if "平均" in q and ("金额" in q or "价格" in q):
            stats = self.db.get_statistics()
            return f"发票平均金额为 {stats['avg_amount']:.2f} 元"
        
        # 最大金额
        if "最大" in q or "最高" in q:
            stats = self.db.get_statistics()
            if stats['max_amount'] > 0:
                return f"最大发票金额为 {stats['max_amount']} 元"
            return "暂无数据"
        
        # 最小金额
        if "最小" in q or "最低" in q:
            stats = self.db.get_statistics()
            if stats['min_amount'] > 0:
                return f"最小发票金额为 {stats['min_amount']} 元"
            return "暂无数据"
        
        # 按发票号查询
        if "发票号码" in q or "发票号" in q:
            # 提取数字
            import re
            numbers = re.findall(r'\d{6,12}', q)
            if numbers:
                inv = self.db.get_invoice_by_number(numbers[0])
                if inv:
                    return f"发票 {inv['invoice_number']} 金额为 {inv['amount']} 元，日期 {inv['date']}"
                else:
                    return f"未找到发票号码为 {numbers[0]} 的发票"
        
        # 按销售方查询
        if "销售方" in q or "卖家" in q:
            # 提取可能的公司名
            import re
            # 简单处理：去掉问句前缀
            seller = q.replace("销售方", "").replace("是", "").replace("的", "").replace("哪些", "").replace("？", "").strip()
            if seller and len(seller) > 1:
                invoices = self.db.get_invoices_by_seller(seller)
                if invoices:
                    result = f"销售方为「{seller}」的发票有 {len(invoices)} 张：\n"
                    for inv in invoices:
                        result += f"  - {inv['invoice_number']}，{inv['amount']}元，{inv['date']}\n"
                    return result
                else:
                    return f"未找到销售方为「{seller}」的发票"
        
        # 统计信息
        if "统计" in q or "概况" in q:
            stats = self.db.get_statistics()
            result = f"""
📊 发票统计概况：
- 发票总数：{stats['total_count']} 张
- 总金额：{stats['total_amount']:.2f} 元
- 平均金额：{stats['avg_amount']:.2f} 元
- 最大金额：{stats['max_amount']} 元
- 最小金额：{stats['min_amount']} 元
"""
            if stats['seller_stats']:
                result += f"\n🏢 销售方排行：\n"
                for s in stats['seller_stats'][:5]:
                    result += f"  - {s['seller']}：{s['count']} 张\n"
            return result
        
        # 列出所有发票
        if "所有" in q and ("发票" in q or "列表" in q):
            invoices = self.db.get_all_invoices()
            if not invoices:
                return "暂无发票数据"
            result = f"📋 共 {len(invoices)} 张发票：\n"
            for inv in invoices:
                result += f"  - {inv['invoice_number']}：{inv['amount']}元，{inv['date']}，{inv['seller'] or '无销售方'}\n"
            return result
        
        return f"暂不支持该查询。\n\n试试这些问题：\n- 总共有多少张发票？\n- 发票总金额是多少？\n- 金额最大的发票是多少钱？\n- 统计信息\n- 所有发票"
    
    def execute_sql(self, sql: str) -> list:
        """直接执行SQL（高级用户）"""
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return rows


if __name__ == "__main__":
    engine = QueryEngine()
    
    test_questions = [
        "总共有多少张发票？",
        "发票总金额是多少？",
        "金额最大的发票是多少钱？",
        "统计信息",
        "所有发票"
    ]
    
    for q in test_questions:
        print(f"\n问: {q}")
        print(f"答: {engine.query(q)}")