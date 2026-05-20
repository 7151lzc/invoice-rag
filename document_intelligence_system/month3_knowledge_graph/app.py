"""
Gradio 图形界面 - 简单版（无 Chatbot 格式问题）
"""

import gradio as gr
from db_manager import DBManager
from invoice_manager import InvoiceManager
from query_engine import QueryEngine


class InvoiceManagerApp:
    def __init__(self):
        self.db = DBManager()
        self.manager = InvoiceManager(self.db)
        self.engine = QueryEngine(self.db)
        
        if self.db.get_count() == 0:
            print("正在加载发票数据...")
            self.manager.load_from_json_dir()
    
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
        return result
    
    def get_all_invoices(self):
        invoices = self.db.get_all_invoices()
        if not invoices:
            return []
        return [[inv['invoice_number'], inv['amount'], inv['date'], inv['seller'] or "-", inv['type'] or "-"] for inv in invoices]
    
    def ask_question(self, question):
        """回答问题，返回字符串"""
        if not question:
            return "请输入问题"
        return self.engine.query(question)
    
    def search_by_number(self, number):
        if not number:
            return "请输入发票号码"
        inv = self.db.get_invoice_by_number(number)
        if inv:
            return f"发票 {inv['invoice_number']} 金额为 {inv['amount']} 元，日期 {inv['date']}"
        return f"未找到发票号码为 {number} 的发票"
    
    def search_by_seller(self, seller):
        if not seller:
            return "请输入销售方名称"
        invoices = self.db.get_invoices_by_seller(seller)
        if invoices:
            result = f"销售方「{seller}」的发票 {len(invoices)} 张：\n"
            for inv in invoices:
                result += f"- {inv['invoice_number']}：{inv['amount']}元，{inv['date']}\n"
            return result
        return f"未找到销售方为「{seller}」的发票"
    
    def search_by_amount(self, min_amt, max_amt):
        try:
            min_a = float(min_amt) if min_amt else 0
            max_a = float(max_amt) if max_amt else 99999999
        except:
            return "请输入有效的数字"
        invoices = self.db.get_invoices_by_amount_range(min_a, max_a)
        if invoices:
            result = f"金额 {min_a}-{max_a} 元的发票 {len(invoices)} 张：\n"
            for inv in invoices:
                result += f"- {inv['invoice_number']}：{inv['amount']}元，{inv['date']}\n"
            return result
        return "未找到符合条件的发票"
    
    def search_by_year(self, year):
        if not year or len(year) != 4:
            return "请输入4位年份"
        invoices = self.db.get_invoices_by_year(year)
        if invoices:
            result = f"{year}年的发票 {len(invoices)} 张：\n"
            for inv in invoices:
                result += f"- {inv['invoice_number']}：{inv['amount']}元，{inv['date']}\n"
            return result
        return f"未找到 {year} 年的发票"
    
    def launch(self):
        with gr.Blocks(title="发票数据管理系统") as demo:
            gr.Markdown("# 🧾 发票数据管理系统")
            
            with gr.Tabs():
                # Tab 1: 智能问答
                with gr.TabItem("💬 智能问答"):
                    gr.Markdown("""
                    **示例问题：**
                    - 总共有多少张发票？
                    - 发票总金额是多少？
                    - 金额最大的发票是多少钱？
                    - 统计信息
                    - 所有发票
                    """)
                    
                    question_input = gr.Textbox(label="输入问题", lines=3, placeholder="在这里输入你的问题...")
                    answer_output = gr.Markdown(label="回答")
                    ask_btn = gr.Button("发送", variant="primary")
                    
                    ask_btn.click(self.ask_question, [question_input], [answer_output])
                    question_input.submit(self.ask_question, [question_input], [answer_output])
                
                # Tab 2: 统计概览
                with gr.TabItem("📊 统计概览"):
                    stats_btn = gr.Button("刷新统计")
                    stats_output = gr.Markdown("点击刷新按钮查看统计")
                    stats_btn.click(self.get_stats, None, stats_output)
                
                # Tab 3: 发票列表
                with gr.TabItem("📋 发票列表"):
                    list_btn = gr.Button("刷新列表")
                    list_output = gr.Dataframe(headers=["发票号码", "金额", "日期", "销售方", "类型"])
                    list_btn.click(self.get_all_invoices, None, list_output)
                
                # Tab 4: 精确查询
                with gr.TabItem("🔍 精确查询"):
                    gr.Markdown("### 按发票号码查询")
                    with gr.Row():
                        num_in = gr.Textbox(label="发票号码", scale=3)
                        num_btn = gr.Button("查询", scale=1)
                    num_out = gr.Markdown()
                    num_btn.click(self.search_by_number, [num_in], [num_out])
                    
                    gr.Markdown("### 按销售方查询")
                    with gr.Row():
                        sel_in = gr.Textbox(label="销售方", scale=3)
                        sel_btn = gr.Button("查询", scale=1)
                    sel_out = gr.Markdown()
                    sel_btn.click(self.search_by_seller, [sel_in], [sel_out])
                    
                    gr.Markdown("### 按金额范围查询")
                    with gr.Row():
                        min_in = gr.Textbox(label="最低金额", scale=2)
                        max_in = gr.Textbox(label="最高金额", scale=2)
                        amt_btn = gr.Button("查询", scale=1)
                    amt_out = gr.Markdown()
                    amt_btn.click(self.search_by_amount, [min_in, max_in], [amt_out])
                    
                    gr.Markdown("### 按年份查询")
                    with gr.Row():
                        year_in = gr.Textbox(label="年份", scale=3)
                        year_btn = gr.Button("查询", scale=1)
                    year_out = gr.Markdown()
                    year_btn.click(self.search_by_year, [year_in], [year_out])
        
        demo.launch()


if __name__ == "__main__":
    app = InvoiceManagerApp()
    app.launch()