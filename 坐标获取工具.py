import pynput
from pynput.keyboard import Listener, KeyCode
from pynput.mouse import Controller
import win32gui
import win32api
import win32con
import sys

# 初始化鼠标控制器
mouse = Controller()

def get_window_at_mouse():
    """获取鼠标当前位置下的窗口句柄和位置"""
    # 获取鼠标绝对坐标
    mx, my = win32api.GetCursorPos()
    # 获取鼠标指向的窗口句柄
    hwnd = win32gui.WindowFromPoint((mx, my))
    
    if hwnd == 0:
        return None, mx, my
    
    # 获取窗口的矩形区域（left, top, right, bottom）
    rect = win32gui.GetWindowRect(hwnd)
    win_left, win_top, win_right, win_bottom = rect
    
    # 获取窗口标题
    title = win32gui.GetWindowText(hwnd)
    if not title:
        title = "无标题窗口"
    
    return (title, win_left, win_top), mx, my

def on_key_press(key):
    """按F键获取坐标，按ESC退出"""
    try:
        # 响应F键（大小写都支持）
        if key == KeyCode(char='f') or key == KeyCode(char='F'):
            window_info, mx, my = get_window_at_mouse()
            
            if window_info:
                title, win_left, win_top = window_info
                # 计算窗口相对坐标
                rel_x = mx - win_left
                rel_y = my - win_top
                
                print(f"""
=================================
✅ 坐标获取成功！
当前窗口：{title}
- 桌面绝对坐标：({mx}, {my})
- 窗口相对坐标：({rel_x}, {rel_y})
=================================
                """)
            else:
                print("❌ 未检测到鼠标下的窗口！")
        
        # 按ESC退出
        if key == pynput.keyboard.Key.esc:
            print("🚪 退出程序...")
            return False
    except Exception as e:
        print(f"⚠️ 出错：{e}")

def main():
    print("=== 极简窗口坐标获取工具 ===")
    print("💡 使用方法：")
    print("1. 把鼠标移到你要测的位置（比如投屏窗口内）")
    print("2. 按 F 键 → 直接显示当前窗口的相对坐标")
    print("3. 按 ESC 键 → 退出程序\n")
    print("▶️ 已开始监听，移动鼠标后按F键即可...")
    
    # 启动按键监听
    with Listener(on_press=on_key_press) as listener:
        listener.join()

if __name__ == "__main__":
    # 检查依赖（win32api是windows自带，pynput需要安装）
    try:
        import pynput
        import win32gui
        import win32api
    except ImportError as e:
        if "pynput" in str(e):
            print("请先安装依赖：pip install pynput pywin32")
        else:
            print(f"缺少组件：{e}")
        sys.exit(1)
    
    main()