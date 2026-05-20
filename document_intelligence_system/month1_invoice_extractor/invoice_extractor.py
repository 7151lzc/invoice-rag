"""
发票信息提取工具 - 主程序
整合OCR引擎和提取器，提供命令行接口
"""

import sys
import os
import argparse
import json

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_engine import OCREngine
from extractor import InvoiceExtractor


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="发票信息提取工具")
    parser.add_argument("image_path", nargs="?", help="发票图片路径")
    parser.add_argument("--output", "-o", default="output/result.json", help="输出JSON文件路径")
    parser.add_argument("--gui", "-g", action="store_true", help="启动图形界面")
    
    args = parser.parse_args()
    args.gui = args.gui or not args.image_path  # 如果没有指定图片路径，默认启用GUI模式
    
    # 如果指定了GUI模式，启动图形界面
    if args.gui:
        from ui import main as gui_main
        gui_main()
        return
    
    # 命令行模式
    if not args.image_path:
        print("请指定图片路径，或使用 -g 启动图形界面")
        parser.print_help()
        return
    
    # 检查图片是否存在
    if not os.path.exists(args.image_path):
        print(f"错误: 图片不存在 - {args.image_path}")
        return
    
    print("正在识别...")
    
    # 初始化引擎
    ocr_engine = OCREngine()
    extractor = InvoiceExtractor()
    
    # 执行提取
    result = extractor.extract_from_image(args.image_path, ocr_engine)
    
    if result:
        print("\n=== 提取结果 ===")
        print(f"发票号码: {result.get('invoice_number', '未识别')}")
        print(f"金额: {result.get('amount', '未识别')}")
        print(f"开票日期: {result.get('date', '未识别')}")
        print(f"销售方: {result.get('seller', '未识别')}")
        print(f"购买方: {result.get('buyer', '未识别')}")
        print(f"税额: {result.get('tax', '未识别')}")
        
        # 保存JSON
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        extractor.save_to_json(result, args.output)
        print(f"\n结果已保存到: {args.output}")
    else:
        print("识别失败")


if __name__ == "__main__":
    main()