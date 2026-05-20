"""
Neo4j 查询引擎
"""

from neo4j_manager import Neo4jManager


class Neo4jQueryEngine:
    def __init__(self, db: Neo4jManager = None):
        self.db = db or Neo4jManager()
    
    def query(self, question: str) -> str:
        q = question.lower().strip()
        
        if "多少张" in q or "数量" in q:
            count = self.db.get_count()
            return f"共有 {count} 张发票"
        
        if "总金额" in q or "合计" in q:
            stats = self.db.get_statistics()
            return f"发票总金额为 {stats['total_amount']:.2f} 元"
        
        if "平均" in q and "金额" in q:
            stats = self.db.get_statistics()
            return f"发票平均金额为 {stats['avg_amount']:.2f} 元"
        
        if "最大" in q or "最高" in q:
            stats = self.db.get_statistics()
            return f"最大发票金额为 {stats['max_amount']} 元" if stats['max_amount'] > 0 else "暂无数据"
        
        if "最小" in q or "最低" in q:
            stats = self.db.get_statistics()
            return f"最小发票金额为 {stats['min_amount']} 元" if stats['min_amount'] > 0 else "暂无数据"
        
        if "统计" in q or "概况" in q:
            stats = self.db.get_statistics()
            result = f"📊 发票统计：\n- 总数：{stats['total_count']} 张\n- 总金额：{stats['total_amount']:.2f} 元\n- 平均：{stats['avg_amount']:.2f} 元\n- 最大：{stats['max_amount']} 元\n- 最小：{stats['min_amount']} 元"
            if stats['seller_stats']:
                result += "\n\n🏢 销售方排行："
                for s in stats['seller_stats'][:3]:
                    result += f"\n  - {s['seller']}：{s['count']} 张"
            if stats['year_stats']:
                result += "\n\n📅 按年份统计："
                for y in stats['year_stats']:
                    result += f"\n  - {y['year']}年：{y['count']} 张，{y['total']:.2f} 元"
            return result
        
        if "所有" in q and "发票" in q:
            invoices = self.db.get_all_invoices()
            if not invoices:
                return "暂无发票数据"
            result = f"共 {len(invoices)} 张发票：\n"
            for inv in invoices:
                result += f"- {inv['invoice_number']}：{inv['amount']}元，{inv['date']}\n"
            return result
        
        import re
        numbers = re.findall(r'\d{6,12}', q)
        if numbers and ("发票号码" in q or "发票号" in q):
            inv = self.db.get_invoice_by_number(numbers[0])
            if inv:
                return f"发票 {inv['invoice_number']} 金额为 {inv['amount']} 元，日期 {inv['date']}，销售方：{inv.get('seller', '无')}"
        
        seller_match = re.search(r'销售方[是为]*(.+)', q)
        if seller_match and "发票" in q:
            seller = seller_match.group(1).replace("的", "").replace("哪些", "").replace("？", "").strip()
            if seller and len(seller) > 1:
                invoices = self.db.get_invoices_by_seller(seller)
                if invoices:
                    result = f"销售方「{seller}」的发票 {len(invoices)} 张：\n"
                    for inv in invoices:
                        result += f"- {inv['invoice_number']}：{inv['amount']}元，{inv['date']}\n"
                    return result
        
        return f"暂不支持该查询。试试：总共有多少张发票？、发票总金额是多少？、统计信息、所有发票"