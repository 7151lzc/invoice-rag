"""
Neo4j 数据库配置
从环境变量读取，不要在此文件中硬编码密码
"""

import os

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")  # 通过环境变量设置，见 .env.example

# 数据目录
INVOICE_DIR = "data/invoices"

if not NEO4J_PASSWORD:
    raise EnvironmentError(
        "NEO4J_PASSWORD 未设置！请在项目根目录创建 .env 文件（参考 .env.example），或运行：\n"
        "  export NEO4J_PASSWORD=your_password"
    )