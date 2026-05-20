"""
Neo4j 数据库管理模块
"""

from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from typing import List, Dict, Optional


class Neo4jManager:
    """Neo4j 数据库管理类"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        self._init_db()
    
    def _init_db(self):
        """初始化数据库：创建约束和索引"""
        with self.driver.session() as session:
            # 创建唯一约束
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (i:Invoice) REQUIRE i.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Seller) REQUIRE s.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (b:Buyer) REQUIRE b.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (y:Year) REQUIRE y.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:AmountRange) REQUIRE r.id IS UNIQUE")
            
            # 创建索引
            session.run("CREATE INDEX IF NOT EXISTS FOR (i:Invoice) ON (i.invoice_number)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (i:Invoice) ON (i.amount)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (i:Invoice) ON (i.date)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (s:Seller) ON (s.name)")
            
            print("Neo4j 数据库初始化完成")
    
    def close(self):
        self.driver.close()
    
    def clear_all(self):
        """清空所有数据"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("已清空 Neo4j 数据库")
    
    def add_invoice(self, inv_id: str, invoice_number: str, amount: float,
                    date: str, seller: str = "", buyer: str = "", inv_type: str = ""):
        """添加发票节点"""
        with self.driver.session() as session:
            session.run("""
                MERGE (i:Invoice {id: $id})
                SET i.invoice_number = $invoice_number,
                    i.amount = $amount,
                    i.date = $date,
                    i.type = $type
                RETURN i
            """, id=inv_id, invoice_number=invoice_number, amount=amount, 
               date=date, type=inv_type)
            
            # 添加年份节点和关系
            if date and len(date) >= 4:
                year = date[:4]
                if year.isdigit():
                    session.run("""
                        MERGE (y:Year {id: $year_id})
                        SET y.year = $year
                        MERGE (i:Invoice {id: $inv_id})
                        MERGE (i)-[:IN_YEAR]->(y)
                    """, year_id=f"year_{year}", year=year, inv_id=inv_id)
            
            # 添加金额区间节点和关系
            if amount > 0:
                if amount < 1000:
                    range_label = "SMALL"
                elif amount < 10000:
                    range_label = "MEDIUM"
                else:
                    range_label = "LARGE"
                
                session.run("""
                    MERGE (r:AmountRange {id: $range_id})
                    SET r.range = $range_label
                    MERGE (i:Invoice {id: $inv_id})
                    MERGE (i)-[:HAS_AMOUNT]->(r)
                """, range_id=f"range_{range_label}", range_label=range_label, inv_id=inv_id)
            
            # 添加销售方节点和关系
            if seller and seller not in ["", "未识别", "unknown"]:
                seller_id = f"seller_{seller}"
                session.run("""
                    MERGE (s:Seller {id: $seller_id})
                    SET s.name = $seller_name
                    MERGE (i:Invoice {id: $inv_id})
                    MERGE (i)-[:HAS_SELLER]->(s)
                """, seller_id=seller_id, seller_name=seller, inv_id=inv_id)
            
            # 添加购买方节点和关系
            if buyer and buyer not in ["", "未识别", "unknown"]:
                buyer_id = f"buyer_{buyer}"
                session.run("""
                    MERGE (b:Buyer {id: $buyer_id})
                    SET b.name = $buyer_name
                    MERGE (i:Invoice {id: $inv_id})
                    MERGE (i)-[:HAS_BUYER]->(b)
                """, buyer_id=buyer_id, buyer_name=buyer, inv_id=inv_id)
            
            print(f"已添加发票: {invoice_number}")
    
    def get_all_invoices(self) -> List[Dict]:
        """获取所有发票"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (i:Invoice)
                RETURN i.id as id, i.invoice_number as invoice_number, 
                       i.amount as amount, i.date as date, i.type as type
                ORDER BY i.date DESC
            """)
            return [dict(record) for record in result]
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict]:
        """根据发票号码查询"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (i:Invoice {invoice_number: $number})
                OPTIONAL MATCH (i)-[:HAS_SELLER]->(s:Seller)
                OPTIONAL MATCH (i)-[:HAS_BUYER]->(b:Buyer)
                RETURN i.id as id, i.invoice_number as invoice_number,
                       i.amount as amount, i.date as date, i.type as type,
                       s.name as seller, b.name as buyer
            """, number=invoice_number)
            record = result.single()
            return dict(record) if record else None
    
    def get_invoices_by_seller(self, seller_name: str) -> List[Dict]:
        """根据销售方查询"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Seller {name: $name})
                MATCH (i:Invoice)-[:HAS_SELLER]->(s)
                RETURN i.id as id, i.invoice_number as invoice_number,
                       i.amount as amount, i.date as date
                ORDER BY i.amount DESC
            """, name=seller_name)
            return [dict(record) for record in result]
    
    def get_invoices_by_amount_range(self, min_amount: float, max_amount: float) -> List[Dict]:
        """根据金额范围查询"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (i:Invoice)
                WHERE i.amount >= $min AND i.amount <= $max
                RETURN i.id as id, i.invoice_number as invoice_number,
                       i.amount as amount, i.date as date
                ORDER BY i.amount DESC
            """, min=min_amount, max=max_amount)
            return [dict(record) for record in result]
    
    def get_invoices_by_year(self, year: str) -> List[Dict]:
        """根据年份查询"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (i:Invoice)-[:IN_YEAR]->(y:Year {year: $year})
                RETURN i.id as id, i.invoice_number as invoice_number,
                       i.amount as amount, i.date as date
                ORDER BY i.amount DESC
            """, year=year)
            return [dict(record) for record in result]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self.driver.session() as session:
            # 总数
            total_count = session.run("MATCH (i:Invoice) RETURN count(i) as count").single()["count"]
            
            # 总金额、平均、最大、最小
            stats = session.run("""
                MATCH (i:Invoice)
                RETURN sum(i.amount) as total, avg(i.amount) as avg,
                       max(i.amount) as max, min(i.amount) as min
            """).single()
            
            # 销售方排行
            sellers = session.run("""
                MATCH (s:Seller)<-[:HAS_SELLER]-(i:Invoice)
                RETURN s.name as name, count(i) as count
                ORDER BY count DESC
                LIMIT 5
            """).data()
            
            # 按年份统计
            years = session.run("""
                MATCH (i:Invoice)-[:IN_YEAR]->(y:Year)
                RETURN y.year as year, count(i) as count, sum(i.amount) as total
                ORDER BY year DESC
            """).data()
            
            return {
                "total_count": total_count,
                "total_amount": stats["total"] or 0,
                "avg_amount": stats["avg"] or 0,
                "max_amount": stats["max"] or 0,
                "min_amount": stats["min"] or 0,
                "seller_stats": [{"seller": s["name"], "count": s["count"]} for s in sellers],
                "year_stats": [{"year": y["year"], "count": y["count"], "total": y["total"]} for y in years]
            }
    
    def get_count(self) -> int:
        """获取发票数量"""
        with self.driver.session() as session:
            result = session.run("MATCH (i:Invoice) RETURN count(i) as count")
            return result.single()["count"]
    
    def get_sellers(self) -> List[str]:
        """获取所有销售方"""
        with self.driver.session() as session:
            result = session.run("MATCH (s:Seller) RETURN s.name as name")
            return [record["name"] for record in result]
    
    def get_graph_data(self) -> Dict:
        """获取图谱数据（用于前端可视化）"""
        with self.driver.session() as session:
            # 获取节点
            nodes = session.run("""
                MATCH (n)
                WHERE n:Invoice OR n:Seller OR n:Buyer OR n:Year OR n:AmountRange
                RETURN n.id as id, 
                       CASE 
                           WHEN n:Invoice THEN 'Invoice'
                           WHEN n:Seller THEN 'Seller'
                           WHEN n:Buyer THEN 'Buyer'
                           WHEN n:Year THEN 'Year'
                           WHEN n:AmountRange THEN 'AmountRange'
                       END as type,
                       n.invoice_number as invoice_number,
                       n.name as name,
                       n.year as year,
                       n.range as range
                LIMIT 50
            """).data()
            
            # 获取关系
            relations = session.run("""
                MATCH (a)-[r]->(b)
                WHERE (a:Invoice OR a:Seller OR a:Buyer OR a:Year OR a:AmountRange)
                  AND (b:Invoice OR b:Seller OR b:Buyer OR b:Year OR b:AmountRange)
                RETURN a.id as source, b.id as target, type(r) as type
                LIMIT 100
            """).data()
            
            return {"nodes": nodes, "relations": relations}
    
    def execute_query(self, cypher: str) -> List[Dict]:
        """执行自定义 Cypher 查询（高级功能）"""
        with self.driver.session() as session:
            result = session.run(cypher)
            return [dict(record) for record in result]