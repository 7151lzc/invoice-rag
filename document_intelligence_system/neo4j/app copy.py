"""
统一界面 - Neo4j 版本
"""

import gradio as gr
import os
import uuid
import json
from neo4j_manager import Neo4jManager
from neo4j_query_engine import Neo4jQueryEngine
from invoice_extractor import InvoiceExtractor
from document_parser import DocumentParser


class IntegratedApp:
    def __init__(self):
        self.db = Neo4jManager()
        self.engine = Neo4jQueryEngine(self.db)
        self.extractor = InvoiceExtractor()
        self.parser = DocumentParser()
    
    def get_stats(self):
        stats = self.db.get_statistics()
        result = f"""
### 📊 统计概况

| 项目 | 数值 |
|------|------|
| 发票总数 | {stats['total_count']} 张 |
| 总金额 | {stats['total_amount']:.2f} 元 |
| 平均金额 | {stats['avg_amount']:.2f} 元 |
| 最大金额 | {stats['max_amount']} 元 |
| 最小金额 | {stats['min_amount']} 元 |
"""
        if stats['seller_stats']:
            result += f"\n### 🏢 销售方排行\n"
            for s in stats['seller_stats'][:5]:
                result += f"- {s['seller']}：{s['count']} 张\n"
        
        if stats['year_stats']:
            result += f"\n### 📅 按年份统计\n"
            for y in stats['year_stats']:
                result += f"- {y['year']}年：{y['count']} 张，{y['total']:.2f} 元\n"
        
        return result
    
    def get_all_invoices(self):
        invoices = self.db.get_all_invoices()
        if not invoices:
            return []
        return [[inv['invoice_number'], inv['amount'], inv['date'], inv.get('type', '-')] for inv in invoices]
    
    def ask_question(self, question):
        if not question:
            return "请输入问题"
        return self.engine.query(question)
    
    def extract_and_save(self, file):
        if file is None:
            return "请先上传文件"
        
        try:
            images = self.parser.parse_to_images(file)
            if not images:
                return "文档解析失败"
            
            results = []
            for img_path in images:
                result = self.extractor.extract_from_image(img_path)
                if result and "error" not in result and result.get("invoice_number"):
                    inv_id = str(uuid.uuid4())[:8]
                    amount_str = result.get("amount", "0")
                    try:
                        amount = float(amount_str) if amount_str else 0
                    except:
                        amount = 0
                    self.db.add_invoice(
                        inv_id=inv_id,
                        invoice_number=result.get("invoice_number", ""),
                        amount=amount,
                        date=result.get("date", ""),
                        seller=result.get("seller", ""),
                        buyer=result.get("buyer", ""),
                        inv_type="extracted"
                    )
                    results.append(f"- {result.get('invoice_number')}：{amount}元")
            
            if results:
                return f"✅ 提取成功 {len(results)} 张发票：\n" + "\n".join(results)
            return "未提取到有效发票"
        except Exception as e:
            return f"处理失败: {str(e)}"
    
    def batch_extract_files(self, files):
        if not files:
            return "请先上传文件"
        
        results = []
        success_count = 0
        
        for file in files:
            try:
                images = self.parser.parse_to_images(file.name)
                if not images:
                    results.append(f"❌ {os.path.basename(file.name)}: 解析失败")
                    continue
                
                for img_path in images:
                    result = self.extractor.extract_from_image(img_path)
                    if result and "error" not in result and result.get("invoice_number"):
                        inv_id = str(uuid.uuid4())[:8]
                        amount_str = result.get("amount", "0")
                        try:
                            amount = float(amount_str) if amount_str else 0
                        except:
                            amount = 0
                        self.db.add_invoice(
                            inv_id=inv_id,
                            invoice_number=result.get("invoice_number", ""),
                            amount=amount,
                            date=result.get("date", ""),
                            seller=result.get("seller", ""),
                            buyer=result.get("buyer", ""),
                            inv_type="extracted"
                        )
                        success_count += 1
                        results.append(f"✅ {os.path.basename(file.name)}: {result.get('invoice_number')} - {amount}元")
            except Exception as e:
                results.append(f"❌ {os.path.basename(file.name)}: {str(e)}")
        
        summary = f"\n### 📊 批量导入完成\n- 成功: {success_count} 张发票\n"
        return summary + "\n".join(results)
    
    def clear_all_data(self):
        self.db.clear_all()
        return "✅ 已清空所有发票数据"
    
    def show_graph(self):
        """显示图谱（返回可视化HTML）"""
        graph_data = self.db.get_graph_data()
        if not graph_data["nodes"]:
            return "暂无图谱数据"
        
        # 简单文本展示
        result = "### 🕸️ 知识图谱节点\n\n"
        for node in graph_data["nodes"]:
            if node["type"] == "Invoice":
                result += f"- 📄 发票: {node.get('invoice_number', '未知')}\n"
            elif node["type"] == "Seller":
                result += f"- 🏢 销售方: {node.get('name', '未知')}\n"
            elif node["type"] == "Buyer":
                result += f"- 👤 购买方: {node.get('name', '未知')}\n"
            elif node["type"] == "Year":
                result += f"- 📅 年份: {node.get('year', '未知')}\n"
            elif node["type"] == "AmountRange":
                result += f"- 💰 金额区间: {node.get('range', '未知')}\n"
        
        result += "\n### 🔗 关系\n"
        for rel in graph_data["relations"]:
            result += f"- {rel['source']} →[{rel['type']}]→ {rel['target']}\n"
        
        return result
    
    def launch(self):
        with gr.Blocks(title="智能发票管理系统 - Neo4j版") as demo:
            gr.Markdown("# 🧾 智能发票管理系统 (Neo4j知识图谱版)")
            gr.Markdown("支持图片、PDF、Word、Excel批量导入，基于图数据库的智能查询")
            
            with gr.Tabs():
                with gr.TabItem("📸 单张提取"):
                    file_input = gr.File(label="选择文件", file_types=[".jpg", ".png", ".jpeg", ".pdf", ".doc", ".docx", ".xls", ".xlsx"])
                    extract_btn = gr.Button("开始提取", variant="primary")
                    extract_result = gr.Markdown("等待上传...")
                    extract_btn.click(self.extract_and_save, [file_input], [extract_result])
                
                with gr.TabItem("📦 批量提取"):
                    batch_input = gr.File(file_count="multiple", label="选择多个文件")
                    batch_btn = gr.Button("批量提取", variant="primary")
                    batch_result = gr.Markdown("等待上传...")
                    batch_btn.click(self.batch_extract_files, [batch_input], [batch_result])
                
                with gr.TabItem("💬 智能问答"):
                    gr.Markdown("""
                    **示例问题：**
                    - 总共有多少张发票？
                    - 发票总金额是多少？
                    - 金额最大的发票是多少钱？
                    - 统计信息
                    - 所有发票
                    - 销售方是新昌世贸广场的发票有哪些？
                    """)
                    question_input = gr.Textbox(label="输入问题", lines=3)
                    answer_output = gr.Markdown(label="回答")
                    ask_btn = gr.Button("发送", variant="primary")
                    ask_btn.click(self.ask_question, [question_input], [answer_output])
                    question_input.submit(self.ask_question, [question_input], [answer_output])
                
                with gr.TabItem("📊 统计概览"):
                    stats_btn = gr.Button("刷新统计")
                    stats_output = gr.Markdown()
                    stats_btn.click(self.get_stats, None, stats_output)
                
                with gr.TabItem("📋 发票列表"):
                    list_btn = gr.Button("刷新列表")
                    list_output = gr.Dataframe(headers=["发票号码", "金额", "日期", "类型"])
                    list_btn.click(self.get_all_invoices, None, list_output)
                
                with gr.TabItem("🕸️ 知识图谱"):
                    graph_btn = gr.Button("查看图谱")
                    graph_output = gr.Markdown()
                    graph_btn.click(self.show_graph, None, graph_output)
                
                with gr.TabItem("⚙️ 数据管理"):
                    clear_btn = gr.Button("清空所有数据", variant="stop")
                    clear_result = gr.Markdown()
                    clear_btn.click(self.clear_all_data, None, clear_result)
        
        demo.launch()


if __name__ == "__main__":
    app = IntegratedApp()
    app.launch()