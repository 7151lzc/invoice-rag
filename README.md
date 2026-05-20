# 🧾 智能发票管理系统

基于 **OCR + AI + RAG + 知识图谱** 的发票识别与智能查询系统。按月迭代开发，从基础 OCR 识别逐步演进到 Neo4j 知识图谱版本。

## 📺 演示视频

👉 [Bilibili 视频演示](https://www.bilibili.com/video/BV1g7L16WEpw/)

## 📁 项目结构

```
document_intelligence_system/
│
├── month1_invoice_extractor/      # 第1月：发票 OCR 识别
│   ├── ocr_engine.py              # PaddleOCR 引擎（含图像预处理）
│   ├── extractor.py               # AI 信息提取（ERNIE 多模态）
│   ├── invoice_extractor.py       # 命令行识别入口
│   ├── ui.py                      # PyQt5 桌面 GUI
│   └── debug_ocr.py               # OCR 调试工具
│
├── month2_rag_qa/                 # 第2月：RAG 知识库问答
│   ├── app.py                     # Gradio 问答界面
│   ├── api.py                     # FastAPI 接口
│   ├── document_loader.py         # 文档加载器
│   ├── vector_store.py            # ChromaDB 向量库
│   ├── qa_chain.py                # RAG 问答链
│   └── run.py                     # 启动入口
│
├── month3_knowledge_graph/        # 第3月：SQLite 数据管理
│   ├── app.py                     # Gradio 综合管理界面
│   ├── cli.py                     # 命令行交互
│   ├── db_manager.py              # SQLite 数据库管理
│   ├── invoice_manager.py         # 发票数据加载
│   ├── query_engine.py            # 自然语言查询引擎
│   └── run.py                     # 启动入口
│
├── sqlite_version/                # SQLite 完整版（推荐）
│   ├── app.py                     # 统一 Gradio 界面（含批量导入）
│   ├── db_manager.py
│   ├── document_parser.py         # 文档解析（PDF/Word/Excel → 图片）
│   ├── invoice_extractor.py
│   ├── invoice_manager.py
│   ├── query_engine.py
│   ├── rag_qa.py
│   └── run.py
│
├── neo4j/                         # Neo4j 知识图谱版本
│   ├── app.py                     # Gradio 界面（含图谱 Tab）
│   ├── config.py                  # Neo4j 连接配置
│   ├── document_parser.py
│   ├── invoice_extractor.py
│   ├── neo4j_manager.py           # Neo4j 数据库管理
│   ├── neo4j_query_engine.py      # 图谱查询引擎
│   └── run.py
│
└── test/                          # 测试样本
    ├── 发票.jpg
    ├── 发票.pdf
    ├── 发票.docx
    ├── 发票.xlsx
    └── 超市小票.jpg
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 填入配置：

```env
# 百度 AI Studio API Key（用于 ERNIE 模型）
# 获取地址：https://aistudio.baidu.com/
OPENAI_API_KEY=your_ernie_api_key_here

# Neo4j 配置（仅 neo4j 版本需要）
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
```

### 3. 选择版本启动

**第1月 — 桌面 GUI 识别单张发票：**
```bash
cd document_intelligence_system/month1_invoice_extractor
python invoice_extractor.py --gui
```

**第2月 — RAG 知识库问答：**
```bash
cd document_intelligence_system/month2_rag_qa
python run.py --mode web
```

**SQLite 完整版（推荐）：**
```bash
cd document_intelligence_system/sqlite_version
python run.py
```

**Neo4j 知识图谱版（需本地 Neo4j 服务）：**
```bash
cd document_intelligence_system/neo4j
python run.py
```

## 🗺️ 版本迭代路线

```
Month 1                Month 2                Month 3 / SQLite       Neo4j
发票图片识别    →    RAG 知识库问答    →    SQLite 数据管理    →    知识图谱版
PaddleOCR           ChromaDB               结构化存储              实体关系
ERNIE AI            向量检索               自然语言查询            图数据库
PyQt5 GUI           Gradio Web             批量导入导出            Cypher 查询
```

## 🖥️ 界面功能（SQLite / Neo4j 版）

| Tab | 功能 |
|-----|------|
| 📸 单张提取 | 上传图片/PDF/Word/Excel，AI 自动提取并保存 |
| 📦 批量提取 | 多文件批量 AI 识别 |
| 📁 批量导入 JSON | 导入已有提取结果 |
| 💬 智能问答 | 自然语言查询发票数据 |
| 📊 统计概览 | 金额统计、销售方排行 |
| 📋 发票列表 | 查看所有发票记录 |
| 🕸️ 知识图谱 | 实体关系可视化（Neo4j 版专有）|

## 💬 支持的查询示例

```
总共有多少张发票？
发票总金额是多少？
金额最大的发票是多少钱？
发票号码是 03531988 的金额是多少？
销售方是新昌世贸广场的发票有哪些？
统计信息 / 所有发票
```

## 📦 主要依赖

| 依赖 | 用途 |
|------|------|
| paddleocr | 中文 OCR 识别 |
| openai | 调用 ERNIE 多模态模型 |
| gradio | Web 界面 |
| chromadb | 向量数据库（Month2）|
| sentence-transformers | 中文 Embedding |
| PyMuPDF | PDF 解析 |
| python-docx | Word 解析 |
| openpyxl | Excel 解析 |
| neo4j | 知识图谱（Neo4j 版）|
| PyQt5 | 桌面 GUI（Month1）|

## ⚠️ 注意事项

- `.env` 文件包含密钥，已加入 `.gitignore`，不会上传
- `invoices.db` 包含本地数据，已加入 `.gitignore`
- `__pycache__`、`chroma_db`、`output` 等运行缓存已排除

## License

MIT
