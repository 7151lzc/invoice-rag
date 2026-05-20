"""
OCR引擎封装 - 优化版
增加图像预处理，提高识别准确率
"""

import os
import cv2
import numpy as np
from paddleocr import PaddleOCR


class OCREngine:
    """OCR引擎类 - 带图像预处理"""
    
    def __init__(self, lang='ch'):
        """
        初始化OCR引擎
        :param lang: 语言，ch表示中文，en表示英文
        """
        # 使用更精确的OCR参数
        self.ocr = PaddleOCR(
            use_angle_cls=True,      # 启用文字方向分类
            lang=lang,
            det_db_thresh=0.3,       # 检测阈值，降低可检测更多文字
            det_db_box_thresh=0.5,   # 框置信度阈值
            use_gpu=False,           # 没有GPU就改False
            show_log=False           # 关闭日志输出
        )
    
    def preprocess_image(self, image_path):
        """
        图像预处理：提高OCR识别率
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        # 1. 转为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. 去噪（高斯滤波）
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 3. 增强对比度（直方图均衡化）
        enhanced = cv2.equalizeHist(denoised)
        
        # 4. 二值化（可选，让文字更清晰）
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 返回处理后的图片
        return binary
    
    def recognize(self, image_path, preprocess=True):
        """
        识别图片中的文字
        :param image_path: 图片路径
        :param preprocess: 是否预处理
        :return: 识别结果列表
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片不存在: {image_path}")
        
        # 预处理
        if preprocess:
            processed_img = self.preprocess_image(image_path)
            if processed_img is not None:
                result = self.ocr.ocr(processed_img, cls=True)
            else:
                result = self.ocr.ocr(image_path, cls=True)
        else:
            result = self.ocr.ocr(image_path, cls=True)
        
        if not result or not result[0]:
            return []
        
        return result[0]
    
    def get_text_with_confidence(self, image_path):
        """
        获取文字和置信度，用于调试
        """
        results = self.recognize(image_path)
        text_list = []
        for line in results:
            text = line[1][0]
            confidence = line[1][1]
            text_list.append({
                "text": text,
                "confidence": confidence,
                "position": line[0]
            })
        return text_list
    
    def get_text_only(self, image_path):
        """只获取文字内容"""
        results = self.recognize(image_path)
        texts = [line[1][0] for line in results]
        return texts


# 测试代码
if __name__ == "__main__":
    ocr = OCREngine()
    print("OCR引擎已就绪（优化版）")