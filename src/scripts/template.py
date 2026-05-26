#!/usr/bin/env python3
# 键鼠操作脚本模板
# 脚本名称: template
# 功能: 脚本模板，用于创建新的键鼠操作脚本

import time
import pyautogui


def template(params=None):
    """
    键鼠操作脚本模板
    功能: 执行示例键鼠操作
    参数: params - 主脚本传递的参数
    返回值: dict - 操作结果
    """
    try:
        # 设置pyautogui参数
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01

        # 示例操作：移动鼠标到屏幕中心并点击
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        
        # 移动鼠标
        pyautogui.moveTo(center_x, center_y, duration=0.2)
        time.sleep(0.1)
        
        # 点击
        pyautogui.click()
        time.sleep(0.1)
        
        # 示例：使用传递的参数
        if params:
            print(f"接收到参数: {params}")
            # 可以根据参数执行不同的操作

        return {
            'success': True,
            'message': '操作执行完成',
            'actions_count': 2
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'操作执行失败: {str(e)}',
            'actions_count': 0
        }


if __name__ == "__main__":
    result = template()
    print(result)
