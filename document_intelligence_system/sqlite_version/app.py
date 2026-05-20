"""
统一界面 - 整合所有功能（支持 PDF/Word/Excel）
"""

import gradio as gr
import os
import uuid
import json
from db_manager import DBManager
from invoice_manager import InvoiceManager
from query_engine import QueryEngine
from invoice_extractor import InvoiceExtractor
from document_parser import DocumentParser


class IntegratedApp:
    def __init__(self):
        self.db = DBManager()
        self.manager = InvoiceManager(self.db)
        self.engine = QueryEngine(self.db)
        self.extractor = InvoiceExtractor()
        self.parser = DocumentParser()
        
        # 加载已有数据
        if self.db.get_count() == 0:
            print("正在加载已有发票数据...")
            self.manager.load_from_json_dir()
    
    def get_stats(self):
        stats = self.db.get_statistics()
        return f"""
### 📊 统计概况

| 项目 | 数值 |
|------|------|
| 发票总数 | {stats['total_count']} 张 |
| 总金额 | {stats['total_amount']:.2f} 元 |
| 平均金额 | {stats['avg_amount']:.2f} 元 |
| 最大金额 | {stats['max_amount']} 元 |
| 最小金额 | {stats['min_amount']} 元 |
"""
    
    def get_all_invoices(self):
        invoices = self.db.get_all_invoices()
        if not invoices:
            return []
        return [[inv['invoice_number'], inv['amount'], inv['date'], inv['seller'] or "-", inv['type'] or "-"] for inv in invoices]
    
    def ask_question(self, question):
        if not question:
            return "请输入问题"
        return self.engine.query(question)
    
    def extract_and_save(self, file):
        """单张提取（支持图片/PDF/Word/Excel）"""
        if file is None:
            return "请先上传文件"
        
        try:
            # 解析文档为图片
            images = self.parser.parse_to_images(file)
            if not images:
                return "文档解析失败，请检查文件格式"
            
            # 取第一页
            first_image = images[0]
            result = self.extractor.extract_from_image(first_image)
            
            # 清理临时文件
            for img in images:
                if img != file and os.path.exists(img):
                    os.unlink(img)
            
            if "error" in result:
                return f"提取失败: {result['error']}"
            
            inv_id = str(uuid.uuid4())[:8]
            self.manager.add_invoice_from_extract(inv_id, result)
            
            display = f"""
### ✅ 提取成功

| 字段 | 值 |
|------|------|
| 发票号码 | {result.get('invoice_number', '-')} |
| 金额 | {result.get('amount', '-')} 元 |
| 开票日期 | {result.get('date', '-')} |
| 销售方 | {result.get('seller', '-')} |
| 购买方 | {result.get('buyer', '-')} |

已保存到数据库！
"""
            return display
        except Exception as e:
            return f"处理失败: {str(e)}"
    
    def batch_extract_files(self, files):
        """批量提取文件（支持图片/PDF/Word/Excel）"""
        if not files:
            return "请先上传文件"
        
        results = []
        success_count = 0
        fail_count = 0
        
        for file in files:
            try:
                # 解析文档为图片列表
                images = self.parser.parse_to_images(file.name)
                if not images:
                    results.append(f"❌ {os.path.basename(file.name)}: 解析失败")
                    fail_count += 1
                    continue
                
                # 处理每一张图片
                file_success = 0
                for img_path in images:
                    result = self.extractor.extract_from_image(img_path)
                    
                    # 清理临时文件（如果不是原文件）
                    if img_path != file.name and os.path.exists(img_path):
                        os.unlink(img_path)
                    
                    if result and "error" not in result and result.get("invoice_number"):
                        inv_id = str(uuid.uuid4())[:8]
                        self.manager.add_invoice_from_extract(inv_id, result)
                        file_success += 1
                        success_count += 1
                        results.append(f"✅ {os.path.basename(file.name)} (图片{file_success}): {result.get('invoice_number')} - {result.get('amount')}元")
                    else:
                        fail_count += 1
                        results.append(f"❌ {os.path.basename(file.name)} (图片{file_success+1}): 提取失败")
                
                if file_success == 0:
                    fail_count += 1
                    results.append(f"❌ {os.path.basename(file.name)}: 未提取到有效发票")
                    
            except Exception as e:
                fail_count += 1
                results.append(f"❌ {os.path.basename(file.name)}: {str(e)}")
        
        summary = f"\n### 📊 批量导入完成\n- 成功: {success_count} 张发票\n- 失败: {fail_count} 个文件\n"
        return summary + "\n".join(results)
    
    def batch_import_json(self, files):
        """批量导入JSON文件"""
        if not files:
            return "请先上传JSON文件"
        
        success_count = 0
        fail_count = 0
        results = []
        
        for file in files:
            try:
                with open(file.name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                inv_id = os.path.basename(file.name).replace('.json', '')
                invoice_number = data.get("invoice_number", "")
                amount_str = data.get("amount", "0")
                try:
                    amount = float(amount_str) if amount_str else 0
                except:
                    amount = 0
                date = data.get("date", "")
                seller = data.get("seller", "")
                buyer = data.get("buyer", "")
                inv_type = data.get("type", "imported")
                
                self.db.insert_invoice(inv_id, invoice_number, amount, date, seller, buyer, inv_type, data)
                success_count += 1
                results.append(f"✅ {os.path.basename(file.name)}: {invoice_number}")
            except Exception as e:
                fail_count += 1
                results.append(f"❌ {os.path.basename(file.name)}: {str(e)}")
        
        summary = f"\n### 📊 JSON导入完成\n- 成功: {success_count} 个\n- 失败: {fail_count} 个\n"
        return summary + "\n".join(results)
    
    def clear_all_data(self):
        """清空所有数据"""
        self.db.clear_all()
        return "✅ 已清空所有发票数据"
    
    def launch(self):
        with gr.Blocks(title="智能发票管理系统") as demo:
            gr.Markdown("# 🧾 智能发票管理系统")
            gr.Markdown("支持图片、PDF、Word、Excel批量导入")
            
            with gr.Tabs():
                # Tab 1: 单张提取
                with gr.TabItem("📸 单张提取"):
                    gr.Markdown("上传发票文件（图片/PDF/Word/Excel），AI自动提取信息")
                    file_input = gr.File(label="选择文件", file_types=[".jpg", ".png", ".jpeg", ".pdf", ".doc", ".docx", ".xls", ".xlsx"])
                    extract_btn = gr.Button("开始提取", variant="primary")
                    extract_result = gr.Markdown("等待上传...")
                    extract_btn.click(self.extract_and_save, [file_input], [extract_result])
                
                # Tab 2: 批量提取
                with gr.TabItem("📦 批量提取"):
                    gr.Markdown("上传多个文件（图片/PDF/Word/Excel），批量AI提取")
                    batch_input = gr.File(file_count="multiple", label="选择多个文件", file_types=[".jpg", ".png", ".jpeg", ".pdf", ".doc", ".docx", ".xls", ".xlsx"])
                    batch_btn = gr.Button("批量提取", variant="primary")
                    batch_result = gr.Markdown("等待上传...")
                    batch_btn.click(self.batch_extract_files, [batch_input], [batch_result])
                
                # Tab 3: 批量导入JSON
                with gr.TabItem("📁 批量导入JSON"):
                    gr.Markdown("上传第1个月生成的JSON文件，直接导入数据库")
                    json_input = gr.File(file_count="multiple", label="选择JSON文件", file_types=[".json"])
                    json_btn = gr.Button("导入JSON", variant="primary")
                    json_result = gr.Markdown("等待上传...")
                    json_btn.click(self.batch_import_json, [json_input], [json_result])
                
                # Tab 4: 智能问答
                with gr.TabItem("💬 智能问答"):
                    gr.Markdown("""
                    **示例问题：**
                    - 总共有多少张发票？
                    - 发票总金额是多少？
                    - 金额最大的发票是多少钱？
                    - 统计信息
                    - 所有发票
                    """)
                    question_input = gr.Textbox(label="输入问题", lines=3)
                    answer_output = gr.Markdown(label="回答")
                    ask_btn = gr.Button("发送", variant="primary")
                    ask_btn.click(self.ask_question, [question_input], [answer_output])
                    question_input.submit(self.ask_question, [question_input], [answer_output])
                
                # Tab 5: 统计概览
                with gr.TabItem("📊 统计概览"):
                    stats_btn = gr.Button("刷新统计")
                    stats_output = gr.Markdown()
                    stats_btn.click(self.get_stats, None, stats_output)
                
                # Tab 6: 发票列表
                with gr.TabItem("📋 发票列表"):
                    list_btn = gr.Button("刷新列表")
                    list_output = gr.Dataframe(headers=["发票号码", "金额", "日期", "销售方", "类型"])
                    list_btn.click(self.get_all_invoices, None, list_output)
                
                # Tab 7: 数据管理
                with gr.TabItem("⚙️ 数据管理"):
                    gr.Markdown("### 危险操作")
                    clear_btn = gr.Button("清空所有数据", variant="stop")
                    clear_result = gr.Markdown()
                    clear_btn.click(self.clear_all_data, None, clear_result)
        
        demo.launch()


if __name__ == "__main__":
    app = IntegratedApp()
    app.launch()