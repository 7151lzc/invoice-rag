"""
命令行交互界面
"""

import os
import sys
from db_manager import DBManager
from invoice_manager import InvoiceManager
from query_engine import QueryEngine


def main():
    print("\n" + "="*50)
    print("📊 发票数据管理系统")
    print("="*50)
    
    db = DBManager()
    manager = InvoiceManager(db)
    engine = QueryEngine(db)
    
    # 检查是否有数据
    if db.get_count() == 0:
        print("\n数据库为空，正在从JSON文件加载...")
        manager.load_from_json_dir()
    
    print(f"\n当前共有 {db.get_count()} 张发票")
    
    print("\n" + "-"*50)
    print("支持的命令：")
    print("  - 查询类：总共有多少张发票？、发票总金额是多少？")
    print("  - 统计类：统计信息、平均金额")
    print("  - 列表类：所有发票")
    print("  - 其他：q 退出")
    print("-"*50)
    
    while True:
        try:
            question = input("\n🔍 你: ").strip()
            
            if question.lower() in ['q', 'quit', 'exit']:
                print("再见！")
                break
            
            if not question:
                continue
            
            # 特殊命令
            if question == "reload":
                manager.load_from_json_dir()
                continue
            
            if question == "list":
                manager.print_all()
                continue
            
            # 查询
            answer = engine.query(question)
            print(f"\n🤖 答: {answer}")
            
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main()