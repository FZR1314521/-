#!/usr/bin/env python3
# YOLO检测器性能测试脚本

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.yolo_detector import YoloDetector
from src.core.window_manager import WindowManager


def test_yolo_performance():
    """
    测试YOLO检测器的性能
    """
    print("开始测试YOLO检测器性能...")
    
    # 初始化窗口管理器
    window_manager = WindowManager()
    
    # 查找窗口
    if not window_manager.find_window():
        print("未找到目标窗口，使用屏幕中心区域进行测试")
        # 使用屏幕中心区域进行测试
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        window_rect = (screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2)
    else:
        # 获取窗口区域
        window_rect = window_manager.get_window_rect()
        if not window_rect:
            print("获取窗口区域失败，使用屏幕中心区域进行测试")
            import pyautogui
            screen_width, screen_height = pyautogui.size()
            window_rect = (screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2)
    
    print(f"测试区域: {window_rect}")
    
    # 初始化YOLO检测器
    detector = YoloDetector()
    
    # 测试性能
    print("\n执行性能测试...")
    result = detector.benchmark(window_rect, iterations=5)
    
    # 打印测试结果
    print("\n性能测试结果:")
    print(f"成功: {result['success']}")
    print(f"平均检测时间: {result.get('average_time', 0):.3f}秒")
    print(f"最快检测时间: {result.get('minimum_time', 0):.3f}秒")
    print(f"最慢检测时间: {result.get('maximum_time', 0):.3f}秒")
    print(f"总检测目标数: {result.get('total_detections', 0)}")
    print(f"是否在0.5秒内: {result.get('within_threshold', False)}")
    print(f"消息: {result.get('message', '')}")
    
    # 测试实时检测
    print("\n测试实时检测...")
    import time
    start_time = time.time()
    detections = detector.detect_from_window(window_rect)
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"实时检测时间: {elapsed:.3f}秒")
    print(f"检测到 {len(detections)} 个目标")
    for i, detection in enumerate(detections):
        print(f"目标 {i+1}: {detection['class_name']} (置信度: {detection['confidence']:.2f})")
    
    return result


if __name__ == "__main__":
    test_yolo_performance()
