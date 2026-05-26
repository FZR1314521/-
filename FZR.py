#!/usr/bin/env python3
# FZR塔防项目主入口

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.fzr_ui import FZRMainWindow
from PyQt6.QtWidgets import QApplication


def main():
    """
    主函数
    """
    print("启动FZR塔防自动化系统...")
    print("正在加载界面...")
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = FZRMainWindow()
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    print("FZR塔防自动化系统已启动")
    print("请在界面中选择目标窗口并开始执行")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
