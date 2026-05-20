"""
OCR调试工具
查看PaddleOCR识别出的原始内容
"""

import sys
from ocr_engine import OCREngine


def debug_ocr(image_path):
    """调试OCR识别结果"""
    ocr = OCREngine()
    
    print(f"\n=== 调试: {image_path} ===\n")
    
    # 获取带置信度的识别结果
    results = ocr.get_text_with_confidence(image_path)
    
    if not results:
        print("未识别到任何文字！")
        return
    
    print("识别到的文字（按位置排序）：\n")
    for i, item in enumerate(results):
        text = item["text"]
        conf = item["confidence"]
        pos = item["position"]
        
        # 置信度标记
        conf_mark = "✓" if conf > 0.8 else "⚠️" if conf > 0.5 else "❌"
        
        print(f"{i+1}. [{conf_mark} {conf:.2f}] {text}")
        print(f"   位置: ({pos[0][0]:.0f}, {pos[0][1]:.0f}) -> ({pos[2][0]:.0f}, {pos[2][1]:.0f})")
    
    # 汇总
    print(f"\n=== 统计 ===")
    print(f"共识别 {len(results)} 条文字")
    low_conf = [r for r in results if r["confidence"] < 0.8]
    if low_conf:
        print(f"低置信度文字 {len(low_conf)} 条，可能影响提取准确性")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python debug_ocr.py <图片路径>")
        print("示例: python debug_ocr.py test_images/invoice.jpg")
    else:
        debug_ocr(sys.argv[1])