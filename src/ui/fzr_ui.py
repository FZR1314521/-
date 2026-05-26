#!/usr/bin/env python3
# FZR塔防二次元风格用户界面

import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QSpinBox, QPushButton, QLabel, QGroupBox, QStyleFactory,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

from src.core.window_manager import WindowManager
from src.core.yolo_detector import YoloDetector
from src.core.script_manager import ScriptManager
from src.config.config import SCRIPTS_DIR

# 导入FZRzx执行器
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# 导入FZRzx模块
import importlib.util

# 动态导入FZRzx模块
spec = importlib.util.spec_from_file_location("FZRzx", "FZRzx.py")
FZRzx = importlib.util.module_from_spec(spec)
sys.modules["FZRzx"] = FZRzx
spec.loader.exec_module(FZRzx)
get_executor = FZRzx.get_executor


class FZRMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FZR塔防 - 自动化控制中心")
        self.setGeometry(100, 100, 500, 800)
        self.setFixedSize(500, 800)
        
        # 初始化核心组件
        self.window_manager = WindowManager()
        self.yolo_detector = YoloDetector()
        self.script_manager = ScriptManager()
        
        # 初始化FZRzx执行器
        self.executor = get_executor()
        
        # 执行状态
        self.is_running = False
        self.detection_timer = QTimer(self)
        self.detection_timer.timeout.connect(self.perform_detection)
        
        # 设置二次元风格
        self.setup_style()
        
        # 创建主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        # 创建界面组件
        self.create_header()
        self.create_window_selection()
        self.create_script_settings()
        self.create_repository_access()
        self.create_control_buttons()
        self.create_status_display()
        
        # 初始化窗口列表
        self.update_window_list()
        
    def setup_style(self):
        """
        设置二次元风格的界面样式
        """
        # 设置风格
        self.setStyleSheet("""
            /* 主窗口背景 */
            QMainWindow {
                background-color: #f0f0f0;
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
                    <rect width="100" height="100" fill="%23f5f5f5"/>
                    <circle cx="20" cy="20" r="2" fill="%23e0e0ff" opacity="0.5"/>
                    <circle cx="80" cy="20" r="2" fill="%23e0e0ff" opacity="0.5"/>
                    <circle cx="20" cy="80" r="2" fill="%23e0e0ff" opacity="0.5"/>
                    <circle cx="80" cy="80" r="2" fill="%23e0e0ff" opacity="0.5"/>
                    <circle cx="50" cy="50" r="2" fill="%23e0e0ff" opacity="0.5"/>
                </svg>');
            }
            
            /* 标签 */
            QLabel {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333366;
            }
            
            /* 标题标签 */
            QLabel#title_label {
                font-size: 20px;
                font-weight: bold;
                color: #663399;
            }
            
            /* 分组框 */
            QGroupBox {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-weight: bold;
                color: #663399;
                border: 2px solid #e0e0ff;
                border-radius: 8px;
                margin-top: 10px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #f0f0ff;
                border-radius: 4px;
            }
            
            /* 按钮 */
            QPushButton {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #663399;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #7a43b3;
            }
            
            QPushButton:pressed {
                background-color: #5a2a85;
            }
            
            /* 下拉框和数字框 */
            QComboBox, QSpinBox {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                border: 2px solid #e0e0ff;
                border-radius: 6px;
                padding: 6px;
                background-color: white;
            }
            
            QComboBox:hover, QSpinBox:hover {
                border-color: #c0c0ff;
            }
            
            /* 状态栏 */
            QLabel#status_label {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 12px;
                color: #666666;
                background-color: #f0f0ff;
                padding: 4px;
                border-radius: 4px;
            }
        """)
    
    def create_header(self):
        """
        创建界面头部
        """
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        # 标题
        title_label = QLabel("FZR塔防 - 自动化控制中心")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("基于YOLO的游戏自动化系统")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        self.main_layout.addWidget(header_widget)
    
    def create_window_selection(self):
        """
        创建窗口选择组件
        """
        window_group = QGroupBox("窗口选择")
        window_layout = QVBoxLayout()
        
        # 窗口选择标签
        window_label = QLabel("目标窗口:")
        window_layout.addWidget(window_label)
        
        # 窗口选择下拉框
        self.window_combo = QComboBox()
        self.window_combo.setMinimumHeight(30)
        window_layout.addWidget(self.window_combo)
        
        # 刷新按钮
        refresh_button = QPushButton("刷新窗口列表")
        refresh_button.clicked.connect(self.update_window_list)
        window_layout.addWidget(refresh_button)
        
        window_group.setLayout(window_layout)
        self.main_layout.addWidget(window_group)
    
    def create_script_settings(self):
        """
        创建脚本设置组件
        """
        settings_group = QGroupBox("脚本设置")
        settings_layout = QVBoxLayout()
        
        # 循环次数标签
        loop_label = QLabel("脚本循环次数:")
        settings_layout.addWidget(loop_label)
        
        # 循环次数选择
        self.loop_spinbox = QSpinBox()
        self.loop_spinbox.setMinimum(1)
        self.loop_spinbox.setMaximum(999)
        self.loop_spinbox.setValue(1)
        self.loop_spinbox.setMinimumHeight(30)
        settings_layout.addWidget(self.loop_spinbox)
        
        settings_group.setLayout(settings_layout)
        self.main_layout.addWidget(settings_group)
    
    def create_repository_access(self):
        """
        创建仓库访问组件
        """
        repo_group = QGroupBox("仓库访问")
        repo_layout = QVBoxLayout()
        
        # 脚本键鼠仓库按钮
        scripts_button = QPushButton("打开脚本键鼠仓库")
        scripts_button.clicked.connect(self.open_scripts_repository)
        repo_layout.addWidget(scripts_button)
        
        # 脚本图片仓库按钮
        images_button = QPushButton("打开脚本图片仓库")
        images_button.clicked.connect(self.open_images_repository)
        repo_layout.addWidget(images_button)
        
        repo_group.setLayout(repo_layout)
        self.main_layout.addWidget(repo_group)
    
    def create_control_buttons(self):
        """
        创建控制按钮组件
        """
        control_group = QGroupBox("控制中心")
        control_layout = QHBoxLayout()
        
        # 开始执行按钮
        self.start_button = QPushButton("开始执行 (F9)")
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.start_execution)
        control_layout.addWidget(self.start_button)
        
        # 停止执行按钮
        self.stop_button = QPushButton("停止执行 (F10)")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.clicked.connect(self.stop_execution)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        control_group.setLayout(control_layout)
        self.main_layout.addWidget(control_group)
    
    def create_status_display(self):
        """
        创建状态显示组件
        """
        status_widget = QWidget()
        status_layout = QVBoxLayout()
        
        # 状态标签
        status_label = QLabel("状态:")
        status_layout.addWidget(status_label)
        
        # 状态显示
        self.status_value_label = QLabel("就绪")
        self.status_value_label.setObjectName("status_label")
        self.status_value_label.setMinimumHeight(30)
        self.status_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_value_label)
        
        status_widget.setLayout(status_layout)
        self.main_layout.addWidget(status_widget)
    
    def update_window_list(self):
        """
        更新窗口列表
        """
        try:
            # 清空现有列表
            self.window_combo.clear()
            
            # 获取所有窗口
            import pygetwindow as gw
            windows = gw.getAllTitles()
            
            # 过滤空标题
            windows = [title for title in windows if title]
            
            # 添加到下拉框
            for window in windows:
                self.window_combo.addItem(window)
            
            # 更新状态
            self.status_value_label.setText(f"已发现 {len(windows)} 个窗口")
        except Exception as e:
            self.status_value_label.setText(f"更新窗口列表失败: {str(e)}")
    
    def open_scripts_repository(self):
        """
        打开脚本键鼠仓库
        """
        try:
            # 脚本仓库路径
            scripts_path = r"c:\Users\ciallo~\Desktop\视觉脚本\src\scripts\__pycache__"
            
            # 确保路径存在
            path = Path(scripts_path)
            if not path.exists():
                # 如果__pycache__不存在，打开scripts目录
                scripts_path = r"c:\Users\ciallo~\Desktop\视觉脚本\src\scripts"
                path = Path(scripts_path)
                path.mkdir(parents=True, exist_ok=True)
            
            # 打开文件夹
            subprocess.run(f"explorer {scripts_path}", shell=True)
            self.status_value_label.setText(f"已打开脚本键鼠仓库")
        except Exception as e:
            self.status_value_label.setText(f"打开脚本仓库失败: {str(e)}")
    
    def open_images_repository(self):
        """
        打开脚本图片仓库
        """
        try:
            # 图片仓库路径
            images_path = r"c:\Users\ciallo~\Desktop\视觉脚本\data\images"
            
            # 确保路径存在
            path = Path(images_path)
            path.mkdir(parents=True, exist_ok=True)
            
            # 打开文件夹
            subprocess.run(f"explorer {images_path}", shell=True)
            self.status_value_label.setText(f"已打开脚本图片仓库")
        except Exception as e:
            self.status_value_label.setText(f"打开图片仓库失败: {str(e)}")
    
    def start_execution(self):
        """
        开始执行脚本
        """
        try:
            # 获取选中的窗口
            selected_window = self.window_combo.currentText()
            if not selected_window:
                QMessageBox.warning(self, "警告", "请选择目标窗口")
                return
            
            # 获取循环次数
            loop_count = self.loop_spinbox.value()
            
            # 更新状态
            self.status_value_label.setText(f"正在执行，循环 {loop_count} 次")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
            # 设置执行器参数
            self.executor.set_target_window(selected_window)
            self.executor.set_loop_count(loop_count)
            
            # 在后台线程中执行，避免阻塞UI
            import threading
            threading.Thread(target=self.execute_in_background, daemon=True).start()
            
        except Exception as e:
            self.status_value_label.setText(f"开始执行失败: {str(e)}")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def execute_in_background(self):
        """
        在后台线程中执行FZRzx
        """
        try:
            # 执行FZRzx
            result = self.executor.start_execution()
            
            # 更新UI状态
            self.status_value_label.setText(result['message'])
        
        except Exception as e:
            self.status_value_label.setText(f"执行失败: {str(e)}")
        
        finally:
            # 恢复按钮状态
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def stop_execution(self):
        """
        停止执行脚本
        """
        try:
            # 停止执行器
            result = self.executor.stop_execution()
            
            # 更新状态
            self.status_value_label.setText(result['message'])
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
        except Exception as e:
            self.status_value_label.setText(f"停止执行失败: {str(e)}")
    
    def perform_detection(self):
        """
        执行目标检测
        """
        if not self.is_running:
            return
        
        try:
            # 查找窗口
            if not self.window_manager.find_window():
                self.status_value_label.setText("未找到目标窗口")
                return
            
            # 获取窗口区域
            window_rect = self.window_manager.get_window_rect()
            if not window_rect:
                self.status_value_label.setText("获取窗口区域失败")
                return
            
            # 执行检测
            detections = self.yolo_detector.detect_from_window(window_rect)
            
            # 更新状态
            self.status_value_label.setText(f"检测到 {len(detections)} 个目标")
            
            # 处理检测结果
            for detection in detections:
                class_name = detection['class_name']
                bbox = detection['bbox']
                print(f"检测到目标: {class_name}, 位置: {bbox}")
                
                # 这里可以添加调用脚本的逻辑
                
        except Exception as e:
            self.status_value_label.setText(f"检测失败: {str(e)}")
    
    def keyPressEvent(self, event):
        """
        处理键盘事件
        """
        # 处理F9键，开始执行
        if event.key() == Qt.Key.Key_F9:
            if self.start_button.isEnabled():
                self.start_execution()
        
        # 处理F10键，停止执行
        elif event.key() == Qt.Key.Key_F10:
            if self.stop_button.isEnabled():
                self.stop_execution()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FZRMainWindow()
    window.show()
    sys.exit(app.exec())
