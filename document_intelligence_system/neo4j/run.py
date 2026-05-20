"""
启动入口 - Neo4j 版本
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

from app import IntegratedApp


def main():
    app = IntegratedApp()
    app.launch()


if __name__ == "__main__":
    main()