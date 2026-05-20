"""
启动入口
"""

import argparse


def main():
    parser = argparse.ArgumentParser(description="发票数据管理系统")
    parser.add_argument("--mode", choices=["cli", "web", "load"], default="web",
                        help="cli: 命令行, web: 图形界面, load: 仅加载数据")
    
    args = parser.parse_args()
    
    if args.mode == "load":
        from invoice_manager import InvoiceManager
        manager = InvoiceManager()
        manager.load_from_json_dir()
        manager.print_all()
    elif args.mode == "cli":
        from cli import main as cli_main
        cli_main()
    else:
        from app import InvoiceManagerApp
        app = InvoiceManagerApp()
        app.launch()


if __name__ == "__main__":
    main()