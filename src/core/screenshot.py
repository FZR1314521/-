import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab

class ScreenshotManager:
    def __init__(self):
        pass
    
    def capture_window(self, window_rect):
        """
        捕获指定窗口区域的截图
        参数: window_rect - 窗口矩形区域 (left, top, width, height)
        返回: numpy.ndarray - 截图图像
        """
        if not window_rect:
            return None
        
        try:
            left, top, width, height = window_rect
            # 使用PIL截图
            screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))
            # 转换为OpenCV格式
            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return image
        except Exception as e:
            print(f"截图失败: {str(e)}")
            return None
    
    def capture_fullscreen(self):
        """
        捕获全屏
        返回: numpy.ndarray - 截图图像
        """
        try:
            screenshot = ImageGrab.grab()
            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return image
        except Exception as e:
            print(f"全屏截图失败: {str(e)}")
            return None
    
    def save_screenshot(self, image, file_path):
        """
        保存截图
        参数: image - 图像
              file_path - 保存路径
        返回: bool - 是否保存成功
        """
        if image is None:
            return False
        
        try:
            cv2.imwrite(file_path, image)
            return True
        except Exception as e:
            print(f"保存截图失败: {str(e)}")
            return False
