import time
import keyboard
import mouse
import pyautogui
from pathlib import Path
import json

class KeyMouseRecorder:
    def __init__(self):
        self.actions = []
        self.start_time = None
        self.last_time = None

    def start_recording(self):
        print("开始录制键鼠操作...")
        print("按ESC键停止录制")
        self.start_time = time.time()
        self.last_time = self.start_time

        # 记录键盘事件
        keyboard.on_press(self._on_key_press)
        keyboard.on_release(self._on_key_release)

        # 记录鼠标事件
        mouse.on_move(self._on_mouse_move)
        mouse.on_click(self._on_mouse_click)
        mouse.on_scroll(self._on_mouse_scroll)

        # 等待停止
        keyboard.wait('esc')
        self.stop_recording()

    def _on_key_press(self, event):
        if event.name == 'esc':
            return
        current_time = time.time()
        delay = current_time - self.last_time
        self.actions.append({
            'type': 'key_press',
            'key': event.name,
            'delay': delay
        })
        self.last_time = current_time

    def _on_key_release(self, event):
        if event.name == 'esc':
            return
        current_time = time.time()
        delay = current_time - self.last_time
        self.actions.append({
            'type': 'key_release',
            'key': event.name,
            'delay': delay
        })
        self.last_time = current_time

    def _on_mouse_move(self, x, y):
        current_time = time.time()
        delay = current_time - self.last_time
        self.actions.append({
            'type': 'mouse_move',
            'x': x,
            'y': y,
            'delay': delay
        })
        self.last_time = current_time

    def _on_mouse_click(self, x, y, button, pressed):
        current_time = time.time()
        delay = current_time - self.last_time
        if pressed:
            self.actions.append({
                'type': 'mouse_click',
                'button': button,
                'x': x,
                'y': y,
                'delay': delay
            })
        self.last_time = current_time

    def _on_mouse_scroll(self, x, y, dx, dy):
        current_time = time.time()
        delay = current_time - self.last_time
        self.actions.append({
            'type': 'mouse_scroll',
            'dx': dx,
            'dy': dy,
            'x': x,
            'y': y,
            'delay': delay
        })
        self.last_time = current_time

    def stop_recording(self):
        keyboard.unhook_all()
        mouse.unhook_all()
        print(f"录制完成，共记录 {len(self.actions)} 个操作")

    def generate_python_code(self, script_name="recorded_script"):
        code_parts = []
        code_parts.append(f"#!/usr/bin/env python3")
        code_parts.append(f"# 自动生成的键鼠操作脚本")
        code_parts.append(f"# 脚本名称: {script_name}")
        code_parts.append(f"# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        code_parts.append(f"# 操作数量: {len(self.actions)}")
        code_parts.append(f"")
        code_parts.append(f"import time")
        code_parts.append(f"import pyautogui")
        code_parts.append(f"")
        code_parts.append(f"")
        code_parts.append(f"def {script_name}(params=None):")
        code_parts.append(f"    '''")
        code_parts.append(f"    键鼠操作脚本")
        code_parts.append(f"    功能: 执行录制的键鼠操作")
        code_parts.append(f"    参数: params - 主脚本传递的参数")
        code_parts.append(f"    返回值: dict - 操作结果")
        code_parts.append(f"    '''")
        code_parts.append(f"    try:")
        code_parts.append(f"        # 设置pyautogui参数")
        code_parts.append(f"        pyautogui.FAILSAFE = False")
        code_parts.append(f"        pyautogui.PAUSE = 0.01")
        code_parts.append(f"")
        code_parts.append(f"        # 执行操作")

        for action in self.actions:
            if action['delay'] > 0:
                code_parts.append(f"        time.sleep({action['delay']:.3f})")
            
            if action['type'] == 'key_press':
                code_parts.append(f"        pyautogui.keyDown('{action['key']}')")
            elif action['type'] == 'key_release':
                code_parts.append(f"        pyautogui.keyUp('{action['key']}')")
            elif action['type'] == 'mouse_move':
                code_parts.append(f"        pyautogui.moveTo({action['x']}, {action['y']})")
            elif action['type'] == 'mouse_click':
                button = 'left' if action['button'] == 'left' else 'right'
                code_parts.append(f"        pyautogui.click({action['x']}, {action['y']}, button='{button}')")
            elif action['type'] == 'mouse_scroll':
                code_parts.append(f"        pyautogui.scroll({action['dy']}, {action['x']}, {action['y']})")

        code_parts.append(f"")
        code_parts.append(f"        return {{")
        code_parts.append(f"            'success': True,")
        code_parts.append(f"            'message': '操作执行完成',")
        code_parts.append(f"            'actions_count': {len(self.actions)}")
        code_parts.append(f"        }}")
        code_parts.append(f"    except Exception as e:")
        code_parts.append(f"        return {{")
        code_parts.append(f"            'success': False,")
        code_parts.append(f"            'message': f'操作执行失败: {{str(e)}}',")
        code_parts.append(f"            'actions_count': 0")
        code_parts.append(f"        }}")
        code_parts.append(f"")
        code_parts.append(f"")
        code_parts.append(f"if __name__ == '__main__':")
        code_parts.append(f"    result = {script_name}()")
        code_parts.append(f"    print(result)")

        return "\n".join(code_parts)

    def save_to_file(self, script_name="recorded_script"):
        code = self.generate_python_code(script_name)
        output_path = Path("src/scripts") / f"{script_name}.py"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"脚本已保存到: {output_path}")
        return output_path

def main():
    recorder = KeyMouseRecorder()
    recorder.start_recording()

    if recorder.actions:
        script_name = input("请输入脚本名称: ")
        if not script_name:
            script_name = "recorded_script"
        recorder.save_to_file(script_name)


if __name__ == "__main__":
    main()
