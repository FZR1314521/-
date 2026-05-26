import pygetwindow as gw
import win32gui
import win32con
import win32api
from src.config.config import WINDOW_TITLE

class WindowManager:
    def __init__(self, window_title=WINDOW_TITLE):
        self.window_title = window_title
        self.window = None
    
    def find_window(self):
        """
        查找指定标题的窗口
        返回: bool - 是否找到窗口
        """
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                self.window = windows[0]
                return True
            return False
        except Exception as e:
            print(f"查找窗口失败: {str(e)}")
            return False
    
    def get_window_rect(self):
        """
        获取窗口矩形区域
        返回: tuple - (left, top, width, height)
        """
        if not self.window:
            if not self.find_window():
                return None
        
        try:
            left, top = self.window.left, self.window.top
            width, height = self.window.width, self.window.height
            return (left, top, width, height)
        except Exception as e:
            print(f"获取窗口区域失败: {str(e)}")
            return None
    
    def activate_window(self):
        """
        激活窗口
        返回: bool - 是否激活成功
        """
        if not self.window:
            if not self.find_window():
                return False
        
        try:
            self.window.activate()
            return True
        except Exception as e:
            print(f"激活窗口失败: {str(e)}")
            return False
    
    def is_window_active(self):
        """
        检查窗口是否激活
        返回: bool - 是否激活
        """
        try:
            active_window = gw.getActiveWindow()
            return active_window and self.window_title in active_window.title
        except Exception as e:
            print(f"检查窗口激活状态失败: {str(e)}")
            return False
    
    def bring_to_front(self):
        """
        将窗口置顶
        返回: bool - 是否成功
        """
        if not self.window:
            if not self.find_window():
                return False
        
        try:
            hwnd = win32gui.FindWindow(None, self.window.title)
            if hwnd:
                # 显示窗口
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # 置顶窗口
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                # 取消置顶（可选）
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                return True
            return False
        except Exception as e:
            print(f"窗口置顶失败: {str(e)}")
            return False
