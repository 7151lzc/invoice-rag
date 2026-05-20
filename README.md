# 🧾 智能发票管理系统

基于 **OCR + AI + RAG** 的发票识别与智能查询系统。支持从图片、PDF、Word、Excel 中自动提取发票信息，并通过自然语言进行查询。提供 SQLite 和 Neo4j 知识图谱两个版本。

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📷 多格式识别 | 支持图片、PDF、Word、Excel 发票文件 |
| 🤖 AI 提取 | 使用 ERNIE 多模态大模型结构化提取 |
| 🗄️ 双存储引擎 | SQLite（轻量）/ Neo4j 知识图谱（关系查询）|
| 💬 自然语言查询 | 无需 SQL，直接用中文提问 |
| 🌐 多种界面 | Gradio Web / FastAPI / PyQt5 桌面 GUI / CLI |

## 📁 项目结构

```
invoice-rag/
├── shared/                    # 共享模块
│   ├── invoice_extractor.py   # AI 发票信息提取器（ERNIE）
│   └── document_parser.py     # 文档解析器（PDF/Word/Excel → 图片）
│
├── sqlite_version/            # SQLite 版本（推荐入门使用）
│   ├── app.py                 # Gradio 主界面
│   ├── run.py                 # 启动入口
│   ├── db_manager.py          # SQLite 数据库管理
│   ├── invoice_manager.py     # 发票数据加载
│   ├── query_engine.py        # 自然语言查询引擎
│   └── rag_qa.py              # RAG 问答模块
│
├── neo4j_version/             # Neo4j 知识图谱版本
│   ├── app.py                 # Gradio 主界面（含图谱 Tab）
│   ├── run.py                 # 启动入口
│   ├── neo4j_manager.py       # Neo4j 数据库管理
│   ├── neo4j_query_engine.py  # 图谱查询引擎
│   └── config.py              # Neo4j 连接配置
│
└── data/
    └── invoices/              # 存放发票 JSON 文件（运行后生成）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

`.env` 内容：
```env
OPENAI_API_KEY=your_ernie_api_key    # 百度 AI Studio API Key
NEO4J_URI=bolt://localhost:7687       # Neo4j 地址（仅 neo4j 版需要）
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

### 3. 启动应用

**SQLite 版本（推荐）：**
```bash
cd sqlite_version
python run.py
```

**Neo4j 版本（需要本地 Neo4j 服务）：**
```bash
cd neo4j_version
python run.py
```

访问 http://localhost:7860 打开 Web 界面。

## 🖥️ 界面功能

| Tab | 功能 |
|-----|------|
| 📸 单张提取 | 上传单个文件，AI 提取发票信息并保存 |
| 📦 批量提取 | 上传多个文件，批量处理 |
| 📁 批量导入 JSON | 导入已有 JSON 结果文件 |
| 💬 智能问答 | 自然语言查询发票数据 |
| 📊 统计概览 | 金额统计、销售方排行等 |
| 📋 发票列表 | 查看所有发票记录 |
| 🕸️ 知识图谱 | 查看实体关系（Neo4j 版专有）|

## 💬 支持的问答示例

```
总共有多少张发票？
发票总金额是多少？
金额最大的发票是多少钱？
发票号码是 03531988 的金额是多少？
销售方是新昌世贸广场的发票有哪些？
统计信息
所有发票
```

## 🗺️ 系统架构

```
输入文件（图片/PDF/Word/Excel）
        ↓
  DocumentParser（格式转换）
        ↓
  InvoiceExtractor（ERNIE AI 提取）
        ↓
    ┌───────────────┐
    │  SQLite 版本  │  →  QueryEngine（自然语言 → SQL）
    │  Neo4j 版本   │  →  Neo4jQueryEngine（Cypher 图查询）
    └───────────────┘
        ↓
   Gradio Web 界面
```

## 📦 依赖说明

核心依赖：`paddleocr`, `openai`, `gradio`, `PyMuPDF`, `python-docx`, `openpyxl`

完整列表见 `requirements.txt`。

## ⚠️ 安全说明

- 不要将 `.env` 提交到 Git（已加入 `.gitignore`）
- `invoices.db` 含真实数据，已加入 `.gitignore`
- Neo4j 密码请通过环境变量配置，不要硬编码

## License

MIT
