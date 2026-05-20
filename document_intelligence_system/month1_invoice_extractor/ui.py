"""
PyQt5 用户界面
提供图片选择和结果展示
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTextEdit, 
    QFileDialog, QGroupBox, QFormLayout, QLineEdit,
    QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from ocr_engine import OCREngine
from extractor import InvoiceExtractor


class InvoiceExtractorUI(QMainWindow):
    """发票提取工具主界面"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化引擎
        self.ocr_engine = OCREngine()
        self.extractor = InvoiceExtractor()
        self.current_image_path = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面 - 简洁版"""
        self.setWindowTitle("智能票据识别工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # ========== 顶部：图片选择区域 ==========
        top_group = QGroupBox("图片选择")
        top_layout = QVBoxLayout()
        
        # 按钮和图片预览放在一行
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("📁 选择票据图片")
        self.select_btn.clicked.connect(self.select_image)
        btn_layout.addWidget(self.select_btn)
        
        self.image_label = QLabel("未选择图片")
        self.image_label.setMinimumHeight(200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        btn_layout.addWidget(self.image_label)
        
        top_layout.addLayout(btn_layout)
        top_group.setLayout(top_layout)
        main_layout.addWidget(top_group)
        
        # ========== 中间：识别按钮 ==========
        self.recognize_btn = QPushButton("🚀 开始识别")
        self.recognize_btn.setEnabled(False)
        self.recognize_btn.clicked.connect(self.recognize)
        self.recognize_btn.setMinimumHeight(50)
        self.recognize_btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white;")
        main_layout.addWidget(self.recognize_btn)
        
        # ========== 底部：结果显示区域 ==========
        result_group = QGroupBox("📋 识别结果")
        result_layout = QVBoxLayout()
        
        # 使用文本框显示所有结果
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(250)
        self.result_text.setStyleSheet("font-size: 14px; font-family: '微软雅黑';")
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)
        
        # ========== 底部：保存按钮 ==========
        self.save_btn = QPushButton("💾 保存为JSON")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_json)
        main_layout.addWidget(self.save_btn)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def select_image(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择发票图片", 
            "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.statusBar().showMessage(f"已选择: {os.path.basename(file_path)}")
            
            # 显示图片缩略图
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 缩放图片以适应label
                scaled_pixmap = pixmap.scaled(
                    300, 200, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setText("")
            else:
                self.image_label.setText("无法加载图片")
            
            self.recognize_btn.setEnabled(True)
    
    def recognize(self):
        """执行识别 - 使用AI"""
        if not self.current_image_path:
            QMessageBox.warning(self, "警告", "请先选择图片")
            return
        
        self.statusBar().showMessage("🤖 AI正在识别中，请稍候...")
        self.recognize_btn.setEnabled(False)
        
        try:
            # 调用AI提取
            result = self.extractor.extract_from_image(
                self.current_image_path, 
                self.ocr_engine
            )
            
            if result:
                # 格式化显示结果
                display_text = f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                        识别结果                          ║
    ╠══════════════════════════════════════════════════════════╣
    ║                                                          ║
    ║  📄 发票号码：  {result.get('invoice_number', '未识别')}                    
    ║                                                          ║
    ║  💰 总金额：    {result.get('amount', '未识别')} 元                      
    ║                                                          ║
    ║  📅 开票日期：  {result.get('date', '未识别')}                          
    ║                                                          ║
    ║  🏢 销售方：    {result.get('seller', '未识别')}                        
    ║                                                          ║
    ║  🛒 购买方：    {result.get('buyer', '未识别')}                        
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
                self.result_text.setText(display_text)
                
                self.current_result = result
                self.save_btn.setEnabled(True)
                self.statusBar().showMessage("✅ 识别完成")
            else:
                self.result_text.setText("识别失败，请检查图片是否清晰")
                QMessageBox.warning(self, "提示", "识别失败")
                
        except Exception as e:
            self.result_text.setText(f"出错：{str(e)}")
            QMessageBox.critical(self, "错误", f"识别出错:\n{str(e)}")
            self.statusBar().showMessage("❌ 识别出错")
        
        finally:
            self.recognize_btn.setEnabled(True)
    
    def save_json(self):
        """保存结果为JSON"""
        if not hasattr(self, 'current_result'):
            QMessageBox.warning(self, "警告", "没有可保存的结果")
            return
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存JSON文件",
            "output/extracted_data.json",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存
            self.extractor.save_to_json(self.current_result, file_path)
            self.statusBar().showMessage(f"已保存: {file_path}")


def main():
    """启动应用"""
    app = QApplication(sys.argv)
    window = InvoiceExtractorUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()