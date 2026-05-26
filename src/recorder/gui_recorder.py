import tkinter as tk
from tkinter import ttk, messagebox
import time
import keyboard
from pynput import mouse
import pyautogui
from pathlib import Path
import json

class RecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FZR塔防 - 键鼠操作录制工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 录制状态
        self.is_recording = False
        self.recorder = KeyMouseRecorder()
        
        # 配置选项
        self.record_mouse_move = tk.BooleanVar(value=True)
        self.record_delay = tk.BooleanVar(value=True)
        self.loop_count = tk.IntVar(value=1)
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        # 顶部工具栏
        toolbar = ttk.Frame(self.root, padding="10")
        toolbar.pack(fill=tk.X, side=tk.TOP)
        
        # 录制按钮
        self.record_btn = ttk.Button(toolbar, text="开始录制", command=self.start_recording, width=12)
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_btn = ttk.Button(toolbar, text="停止录制", command=self.stop_recording, width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        self.save_btn = ttk.Button(toolbar, text="保存脚本", command=self.save_script, width=12, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # 运行按钮
        self.run_btn = ttk.Button(toolbar, text="运行脚本", command=self.run_script, width=12)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        # 加载脚本按钮
        self.load_btn = ttk.Button(toolbar, text="加载脚本", command=self.load_script, width=12)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # 中间内容区域
        content = ttk.Frame(self.root, padding="10")
        content.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        # 左侧配置
        config_frame = ttk.LabelFrame(content, text="录制配置", padding="10")
        config_frame.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        
        # 录制鼠标移动
        ttk.Checkbutton(config_frame, text="录制鼠标移动轨迹", variable=self.record_mouse_move).pack(anchor=tk.W, pady=5)
        
        # 录制延迟
        ttk.Checkbutton(config_frame, text="录制操作延迟", variable=self.record_delay).pack(anchor=tk.W, pady=5)
        
        # 循环次数
        ttk.Label(config_frame, text="循环次数:").pack(anchor=tk.W, pady=5)
        loop_frame = ttk.Frame(config_frame)
        loop_frame.pack(anchor=tk.W, pady=5)
        ttk.Spinbox(loop_frame, from_=1, to=999, textvariable=self.loop_count, width=5).pack(side=tk.LEFT)
        ttk.Label(loop_frame, text="次").pack(side=tk.LEFT, padx=5)
        
        # 右侧操作列表
        action_frame = ttk.LabelFrame(content, text="操作列表", padding="10")
        action_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=5, pady=5)
        
        # 操作列表
        self.action_listbox = tk.Listbox(action_frame, width=80, height=20)
        self.action_listbox.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=5)
        
        # 操作按钮
        action_buttons = ttk.Frame(action_frame)
        action_buttons.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        ttk.Button(action_buttons, text="清空", command=self.clear_actions, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="删除选中", command=self.delete_selected, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="编辑", command=self.edit_action, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="添加点击坐标", command=self.add_click_coordinate, width=12).pack(side=tk.LEFT, padx=5)
        
        # 底部状态栏
        statusbar = ttk.Frame(self.root, padding="10")
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(statusbar, textvariable=self.status_var).pack(side=tk.LEFT)
    
    def start_recording(self):
        """
        开始录制
        """
        if not self.is_recording:
            self.is_recording = True
            self.recorder = KeyMouseRecorder()
            self.recorder.record_mouse_move = self.record_mouse_move.get()
            self.recorder.record_delay = self.record_delay.get()
            
            self.record_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.DISABLED)
            
            self.status_var.set("正在录制... 按ESC键停止")
            self.action_listbox.delete(0, tk.END)
            
            # 开始录制
            self.recorder.start_recording_async(callback=self.on_recording_stopped)
    
    def stop_recording(self):
        """
        停止录制
        """
        if self.is_recording:
            # 模拟按下ESC键停止录制
            keyboard.press_and_release('esc')
    
    def on_recording_stopped(self):
        """
        录制停止回调
        """
        self.is_recording = False
        self.record_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.NORMAL)
        
        self.status_var.set(f"录制完成，共记录 {len(self.recorder.actions)} 个操作")
        
        # 更新操作列表
        self.update_action_list()
    
    def update_action_list(self):
        """
        更新操作列表
        """
        self.action_listbox.delete(0, tk.END)
        for i, action in enumerate(self.recorder.actions):
            if action['type'] == 'key_press':
                text = f"{i+1}. 按下键盘: {action['key']}"
            elif action['type'] == 'key_release':
                text = f"{i+1}. 释放键盘: {action['key']}"
            elif action['type'] == 'mouse_move':
                text = f"{i+1}. 移动鼠标: ({action['x']}, {action['y']})"
            elif action['type'] == 'mouse_click':
                button = '左键' if action['button'] == 'left' else '右键'
                text = f"{i+1}. 点击鼠标{button}: ({action['x']}, {action['y']})"
            elif action['type'] == 'mouse_press':
                button = '左键' if action['button'] == 'left' else '右键'
                text = f"{i+1}. 按下鼠标{button}: ({action['x']}, {action['y']})"
            elif action['type'] == 'mouse_release':
                button = '左键' if action['button'] == 'left' else '右键'
                text = f"{i+1}. 释放鼠标{button}: ({action['x']}, {action['y']})"
            elif action['type'] == 'mouse_drag_move':
                text = f"{i+1}. 拖动鼠标: ({action['x']}, {action['y']})"
            elif action['type'] == 'mouse_drag_end':
                button = '左键' if action['button'] == 'left' else '右键'
                text = f"{i+1}. 结束拖动: ({action['x']}, {action['y']})"
            elif action['type'] == 'mouse_scroll':
                direction = '向上' if action['dy'] > 0 else '向下'
                text = f"{i+1}. 滚动鼠标{direction}: ({action['x']}, {action['y']})"
            else:
                text = f"{i+1}. 未知操作"
            
            if action.get('delay', 0) > 0:
                text += f" (延迟: {action['delay']:.3f}s)"
            
            self.action_listbox.insert(tk.END, text)
    
    def save_script(self):
        """
        保存脚本
        """
        if not self.recorder.actions:
            messagebox.showwarning("警告", "没有录制的操作")
            return
        
        # 弹出保存对话框
        from tkinter import simpledialog
        script_name = simpledialog.askstring("保存脚本", "请输入脚本名称:", initialvalue="recorded_script")
        
        if script_name:
            # 生成Python代码
            code = self.recorder.generate_python_code(script_name, loop_count=self.loop_count.get())
            
            # 保存到文件
            output_path = Path("src/scripts") / f"{script_name}.py"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            messagebox.showinfo("成功", f"脚本已保存到: {output_path}")
    
    def run_script(self):
        """
        运行脚本
        """
        if not self.recorder.actions:
            messagebox.showwarning("警告", "没有录制的操作")
            return
        
        try:
            # 运行脚本
            result = self.recorder.run_script(loop_count=self.loop_count.get())
            messagebox.showinfo("运行结果", f"操作执行{result['success'] and '成功' or '失败'}: {result['message']}")
        except Exception as e:
            messagebox.showerror("错误", f"运行脚本失败: {str(e)}")
    
    def clear_actions(self):
        """
        清空操作列表
        """
        if messagebox.askyesno("确认", "确定要清空操作列表吗?"):
            self.recorder.actions = []
            self.action_listbox.delete(0, tk.END)
            self.status_var.set("操作列表已清空")
    
    def delete_selected(self):
        """
        删除选中的操作
        """
        selected = self.action_listbox.curselection()
        if selected:
            index = selected[0]
            del self.recorder.actions[index]
            self.update_action_list()
            self.status_var.set("操作已删除")
    
    def edit_action(self):
        """
        编辑选中的操作
        """
        selected = self.action_listbox.curselection()
        if selected:
            index = selected[0]
            action = self.recorder.actions[index]
            
            # 弹出编辑对话框
            from tkinter import simpledialog
            
            if action['type'] == 'mouse_move' or action['type'] == 'mouse_click':
                x = simpledialog.askinteger("编辑操作", "X坐标:", initialvalue=action['x'])
                y = simpledialog.askinteger("编辑操作", "Y坐标:", initialvalue=action['y'])
                if x is not None and y is not None:
                    action['x'] = x
                    action['y'] = y
                    self.update_action_list()
                    self.status_var.set("操作已编辑")
            elif action['type'] == 'key_press' or action['type'] == 'key_release':
                key = simpledialog.askstring("编辑操作", "按键:", initialvalue=action['key'])
                if key:
                    action['key'] = key
                    self.update_action_list()
                    self.status_var.set("操作已编辑")
    
    def add_click_coordinate(self):
        """
        添加点击坐标
        """
        from tkinter import simpledialog
        
        # 弹出对话框输入坐标
        x = simpledialog.askinteger("添加点击坐标", "X坐标:")
        y = simpledialog.askinteger("添加点击坐标", "Y坐标:")
        
        if x is not None and y is not None:
            # 添加点击操作
            current_time = time.time()
            delay = current_time - (self.recorder.last_time or current_time)
            
            self.recorder.actions.append({
                'type': 'mouse_click',
                'button': 'left',
                'x': x,
                'y': y,
                'delay': delay if self.record_delay.get() else 0
            })
            
            self.recorder.last_time = current_time
            
            # 更新操作列表
            self.update_action_list()
            self.status_var.set(f"已添加点击坐标: ({x}, {y})")
    
    def load_script(self):
        """
        加载脚本
        """
        from tkinter import filedialog
        
        # 打开文件对话框
        file_path = filedialog.askopenfilename(
            title="加载脚本",
            filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")],
            initialdir=str(Path("src/scripts"))
        )
        
        if file_path:
            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析脚本内容，提取操作
                # 这里简化处理，实际项目中可能需要更复杂的解析
                
                # 重置录制器
                self.recorder = KeyMouseRecorder()
                
                # 这里可以添加解析逻辑，从脚本文件中提取操作
                # 为了演示，我们只是清空操作列表
                self.recorder.actions = []
                
                # 更新界面
                self.update_action_list()
                self.status_var.set(f"脚本已加载: {Path(file_path).name}")
                messagebox.showinfo("成功", f"脚本已加载: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("错误", f"加载脚本失败: {str(e)}")


class KeyMouseRecorder:
    def __init__(self):
        self.actions = []
        self.start_time = None
        self.last_time = None
        self.record_mouse_move = True
        self.record_delay = True
        self.callback = None
    
    def start_recording_async(self, callback=None):
        """
        异步开始录制
        """
        self.callback = callback
        import threading
        threading.Thread(target=self.start_recording, daemon=True).start()
    
    def start_recording(self):
        """
        开始录制
        """
        self.actions = []
        self.start_time = time.time()
        self.last_time = self.start_time
        
        # 记录键盘事件
        keyboard.on_press(self._on_key_press)
        keyboard.on_release(self._on_key_release)
        
        # 记录鼠标事件
        self.mouse_listener = None
        
        def on_move(x, y):
            if self.record_mouse_move:
                current_time = time.time()
                delay = current_time - self.last_time
                self.actions.append({
                    'type': 'mouse_move',
                    'x': x,
                    'y': y,
                    'delay': delay if self.record_delay else 0
                })
                self.last_time = current_time
        
        # 记录鼠标状态
        mouse_pressed = False
        mouse_press_time = 0
        mouse_press_position = (0, 0)
        drag_actions = []

        def on_click(x, y, button, pressed):
            nonlocal mouse_pressed, mouse_press_time, mouse_press_position, drag_actions
            current_time = time.time()
            delay = current_time - self.last_time
            
            if pressed:
                # 记录鼠标按下事件
                mouse_pressed = True
                mouse_press_time = current_time
                mouse_press_position = (x, y)
                drag_actions = []
                
                # 记录按下事件
                self.actions.append({
                    'type': 'mouse_press',
                    'button': 'left' if button == mouse.Button.left else 'right',
                    'x': x,
                    'y': y,
                    'delay': delay if self.record_delay else 0
                })
                self.last_time = current_time
            else:
                # 计算按下到释放的时间
                press_duration = current_time - mouse_press_time
                
                # 检查是否是长按拖动
                if mouse_pressed and press_duration > 0.1 and len(drag_actions) > 0:
                    # 记录拖动结束事件
                    self.actions.append({
                        'type': 'mouse_drag_end',
                        'button': 'left' if button == mouse.Button.left else 'right',
                        'x': x,
                        'y': y,
                        'duration': press_duration,
                        'delay': 0
                    })
                else:
                    # 记录普通点击释放事件
                    self.actions.append({
                        'type': 'mouse_release',
                        'button': 'left' if button == mouse.Button.left else 'right',
                        'x': x,
                        'y': y,
                        'delay': delay if self.record_delay else 0
                    })
                
                mouse_pressed = False
                self.last_time = current_time

        def on_move(x, y):
            nonlocal mouse_pressed, drag_actions
            if self.record_mouse_move:
                current_time = time.time()
                delay = current_time - self.last_time
                
                if mouse_pressed:
                    # 记录拖动过程中的移动
                    drag_actions.append((x, y))
                    self.actions.append({
                        'type': 'mouse_drag_move',
                        'x': x,
                        'y': y,
                        'delay': delay if self.record_delay else 0
                    })
                else:
                    # 记录普通移动
                    self.actions.append({
                        'type': 'mouse_move',
                        'x': x,
                        'y': y,
                        'delay': delay if self.record_delay else 0
                    })
                self.last_time = current_time
        
        def on_scroll(x, y, dx, dy):
            current_time = time.time()
            delay = current_time - self.last_time
            self.actions.append({
                'type': 'mouse_scroll',
                'dx': dx,
                'dy': dy,
                'x': x,
                'y': y,
                'delay': delay if self.record_delay else 0
            })
            self.last_time = current_time
        
        # 创建鼠标监听器
        self.mouse_listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll
        )
        self.mouse_listener.start()
        
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
            'delay': delay if self.record_delay else 0
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
            'delay': delay if self.record_delay else 0
        })
        self.last_time = current_time
    
    def _on_mouse_move(self, x, y):
        current_time = time.time()
        delay = current_time - self.last_time
        self.actions.append({
            'type': 'mouse_move',
            'x': x,
            'y': y,
            'delay': delay if self.record_delay else 0
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
                'delay': delay if self.record_delay else 0
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
            'delay': delay if self.record_delay else 0
        })
        self.last_time = current_time
    
    def stop_recording(self):
        """
        停止录制
        """
        # 停止键盘监听
        keyboard.unhook_all()
        
        # 停止鼠标监听
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.callback:
            self.callback()
    
    def generate_python_code(self, script_name="recorded_script", loop_count=1):
        """
        生成Python代码
        """
        code_parts = []
        code_parts.append(f"#!/usr/bin/env python3")
        code_parts.append(f"# 自动生成的键鼠操作脚本")
        code_parts.append(f"# 脚本名称: {script_name}")
        code_parts.append(f"# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        code_parts.append(f"# 操作数量: {len(self.actions)}")
        code_parts.append(f"# 循环次数: {loop_count}")
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
        
        if loop_count > 1:
            code_parts.append(f"        for _ in range({loop_count}):")
            indent = "            "
        else:
            indent = "        "
        
        for action in self.actions:
            if action['delay'] > 0:
                code_parts.append(f"{indent}time.sleep({action['delay']:.3f})")
            
            if action['type'] == 'key_press':
                code_parts.append(f"{indent}pyautogui.keyDown('{action['key']}')")
            elif action['type'] == 'key_release':
                code_parts.append(f"{indent}pyautogui.keyUp('{action['key']}')")
            elif action['type'] == 'mouse_move':
                code_parts.append(f"{indent}pyautogui.moveTo({action['x']}, {action['y']})")
            elif action['type'] == 'mouse_click':
                button = 'left' if action['button'] == 'left' else 'right'
                code_parts.append(f"{indent}pyautogui.click({action['x']}, {action['y']}, button='{button}')")
            elif action['type'] == 'mouse_press':
                button = 'left' if action['button'] == 'left' else 'right'
                code_parts.append(f"{indent}pyautogui.mouseDown({action['x']}, {action['y']}, button='{button}')")
            elif action['type'] == 'mouse_release':
                button = 'left' if action['button'] == 'left' else 'right'
                code_parts.append(f"{indent}pyautogui.mouseUp({action['x']}, {action['y']}, button='{button}')")
            elif action['type'] == 'mouse_drag_move':
                code_parts.append(f"{indent}pyautogui.moveTo({action['x']}, {action['y']})")
            elif action['type'] == 'mouse_drag_end':
                button = 'left' if action['button'] == 'left' else 'right'
                code_parts.append(f"{indent}pyautogui.mouseUp({action['x']}, {action['y']}, button='{button}')")
            elif action['type'] == 'mouse_scroll':
                code_parts.append(f"{indent}pyautogui.scroll({action['dy']}, {action['x']}, {action['y']})")
        
        code_parts.append(f"")
        code_parts.append(f"        return {{")
        code_parts.append(f"            'success': True,")
        code_parts.append(f"            'message': '操作执行完成',")
        code_parts.append(f"            'actions_count': {len(self.actions)},")
        code_parts.append(f"            'loop_count': {loop_count}")
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
    
    def run_script(self, loop_count=1):
        """
        运行脚本
        """
        try:
            # 设置pyautogui参数
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.01
            
            for _ in range(loop_count):
                for action in self.actions:
                    if action['delay'] > 0:
                        time.sleep(action['delay'])
                    
                    if action['type'] == 'key_press':
                        pyautogui.keyDown(action['key'])
                    elif action['type'] == 'key_release':
                        pyautogui.keyUp(action['key'])
                    elif action['type'] == 'mouse_move':
                        pyautogui.moveTo(action['x'], action['y'])
                    elif action['type'] == 'mouse_click':
                        button = 'left' if action['button'] == 'left' else 'right'
                        pyautogui.click(action['x'], action['y'], button=button)
                    elif action['type'] == 'mouse_press':
                        button = 'left' if action['button'] == 'left' else 'right'
                        pyautogui.mouseDown(action['x'], action['y'], button=button)
                    elif action['type'] == 'mouse_release':
                        button = 'left' if action['button'] == 'left' else 'right'
                        pyautogui.mouseUp(action['x'], action['y'], button=button)
                    elif action['type'] == 'mouse_drag_move':
                        pyautogui.moveTo(action['x'], action['y'])
                    elif action['type'] == 'mouse_drag_end':
                        button = 'left' if action['button'] == 'left' else 'right'
                        pyautogui.mouseUp(action['x'], action['y'], button=button)
                    elif action['type'] == 'mouse_scroll':
                        pyautogui.scroll(action['dy'], action['x'], action['y'])
            
            return {
                'success': True,
                'message': '操作执行完成',
                'actions_count': len(self.actions),
                'loop_count': loop_count
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'操作执行失败: {str(e)}',
                'actions_count': 0
            }


def main():
    """
    主函数
    """
    root = tk.Tk()
    app = RecorderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
