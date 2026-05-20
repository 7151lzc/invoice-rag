"""
启动入口
"""

import os
import sys

# 添加当前目录到路径（关键修复）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置离线模式
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

from app import IntegratedApp


def main():
    app = IntegratedApp()
    app.launch()


if __name__ == "__main__":
    main()