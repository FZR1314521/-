import time
import pyautogui
import ctypes
import logging

class QScriptExecutor:
    """
    执行按键精灵脚本命令的执行器
    """
    
    def __init__(self):
        # 配置pyautogui
        pyautogui.PAUSE = 0  # 禁用默认暂停，提高执行速度
        pyautogui.FAILSAFE = False  # 禁用安全模式，避免意外中断
        # 获取Windows API函数，用于更高效的鼠标操作
        self.user32 = ctypes.windll.user32
        self.SetCursorPos = self.user32.SetCursorPos
        self.mouse_event = self.user32.mouse_event
        # 鼠标事件常量
        self.MOUSEEVENTF_LEFTDOWN = 0x0002
        self.MOUSEEVENTF_LEFTUP = 0x0004
        self.MOUSEEVENTF_MOVE = 0x0001
        # 日志配置
        self.logger = logging.getLogger(__name__)
        # 执行状态跟踪
        self.execution_status = {
            'total_commands': 0,
            'executed_commands': 0,
            'failed_commands': 0,
            'command_details': [],
            'start_time': None,
            'end_time': None
        }
    
    def execute_commands(self, commands):
        """
        执行命令列表
        参数: commands - 命令列表
        返回: dict - 执行结果
        """
        try:
            self.execution_status['total_commands'] = len(commands)
            self.execution_status['executed_commands'] = 0
            self.execution_status['failed_commands'] = 0
            self.execution_status['command_details'] = []
            self.execution_status['start_time'] = time.time()
            
            for i, command in enumerate(commands):
                command_start = time.time()
                command_status = 'success'
                error_message = None
                retry_count = 0
                max_retries = 2  # 最多重试2次
                
                while retry_count <= max_retries:
                    try:
                        self._execute_command(command)
                        self.execution_status['executed_commands'] += 1
                        break  # 执行成功，跳出重试循环
                    except Exception as e:
                        retry_count += 1
                        if retry_count > max_retries:
                            command_status = 'failed'
                            error_message = str(e)
                            self.execution_status['failed_commands'] += 1
                            self.logger.error(f"执行第 {i+1} 条命令失败: {str(e)}")
                        else:
                            self.logger.warning(f"执行第 {i+1} 条命令失败，正在重试 ({retry_count}/{max_retries}): {str(e)}")
                            # 短暂延迟后重试
                            time.sleep(0.01)
                
                command_end = time.time()
                command_duration = (command_end - command_start) * 1000  # 转换为毫秒
                
                # 记录命令执行详情
                self.execution_status['command_details'].append({
                    'index': i + 1,
                    'type': command.get('type'),
                    'params': command.get('params'),
                    'status': command_status,
                    'error_message': error_message,
                    'retry_count': retry_count,
                    'start_time': command_start,
                    'end_time': command_end,
                    'duration_ms': command_duration
                })
                
                # 每执行10条命令记录一次进度
                if (i + 1) % 10 == 0:
                    self.logger.info(f"执行进度: {i+1}/{len(commands)} 条命令")
            
            self.execution_status['end_time'] = time.time()
            total_duration = self.execution_status['end_time'] - self.execution_status['start_time']
            
            return {
                'success': True,
                'message': f'成功执行 {self.execution_status["executed_commands"]}/{self.execution_status["total_commands"]} 条命令',
                'executed': self.execution_status['executed_commands'],
                'total': self.execution_status['total_commands'],
                'failed': self.execution_status['failed_commands'],
                'duration_seconds': total_duration,
                'details': self.execution_status
            }
        except Exception as e:
            self.logger.error(f"执行命令列表失败: {str(e)}")
            return {
                'success': False,
                'message': f'执行命令失败: {str(e)}'
            }
    
    def _execute_command(self, command):
        """
        执行单个命令
        参数: command - 命令对象
        """
        command_type = command.get('type')
        params = command.get('params', {})
        
        if command_type == 'delay':
            self._execute_delay(params)
        elif command_type == 'moveto':
            self._execute_moveto(params)
        elif command_type == 'leftclick':
            self._execute_leftclick(params)
        elif command_type == 'leftdown':
            self._execute_leftdown(params)
        elif command_type == 'leftup':
            self._execute_leftup(params)
        else:
            self.logger.warning(f"未知命令类型: {command_type}")
    
    def _execute_delay(self, params):
        """
        执行延迟命令
        参数: params - 参数，包含ms字段
        """
        ms = params.get('ms', 0)
        if ms > 0:
            # 使用高精度时间睡眠，确保精确的延时
            start_time = time.perf_counter()
            target_time = start_time + ms / 1000
            
            # 对于小延时（<10ms），使用busy wait确保精确性
            if ms < 10:
                while time.perf_counter() < target_time:
                    pass  # 忙等待，确保极小延时的精确性
            else:
                # 对于较大延时，使用sleep减少CPU占用
                remaining_time = target_time - time.perf_counter()
                while remaining_time > 0.01:
                    time.sleep(0.005)  # 每5ms检查一次
                    remaining_time = target_time - time.perf_counter()
                # 最后使用忙等待确保精确性
                while time.perf_counter() < target_time:
                    pass
            
            actual_duration = (time.perf_counter() - start_time) * 1000
            # 记录所有延时命令的执行情况，确保可追踪性
            self.logger.debug(f"延时命令执行: 请求 {ms}ms, 实际 {actual_duration:.2f}ms, 误差 {abs(actual_duration - ms):.2f}ms")
    
    def _execute_moveto(self, params):
        """
        执行鼠标移动命令
        参数: params - 参数，包含x和y字段
        """
        x = params.get('x', 0)
        y = params.get('y', 0)
        target_x, target_y = int(x), int(y)
        
        # 使用Windows API直接设置鼠标位置，性能更高
        result = self.SetCursorPos(target_x, target_y)
        
        # 验证鼠标移动是否成功
        if result == 0:
            # 如果失败，使用pyautogui作为备用
            pyautogui.moveTo(target_x, target_y, duration=0.01)
            self.logger.warning(f"Windows API移动鼠标失败，使用pyautogui备用")
        
        # 短暂延迟确保移动完成
        time.sleep(0.005)
        
        # 验证鼠标位置是否正确
        current_x, current_y = pyautogui.position()
        position_error = ((current_x - target_x) ** 2 + (current_y - target_y) ** 2) ** 0.5
        if position_error > 5:  # 允许5像素误差
            self.logger.warning(f"鼠标位置验证失败: 目标({target_x},{target_y}), 当前({current_x},{current_y}), 误差: {position_error:.2f}px")
            # 再次尝试移动到目标位置
            self.SetCursorPos(target_x, target_y)
            time.sleep(0.005)
    
    def _execute_leftclick(self, params):
        """
        执行鼠标左键点击命令
        参数: params - 参数，包含times字段
        """
        times = params.get('times', 1)
        for i in range(times):
            click_start = time.perf_counter()
            try:
                # 使用Windows API执行鼠标点击，性能更高
                self.mouse_event(self.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                # 精确控制按下时间
                press_duration = 0.01
                target_press_end = click_start + press_duration
                while time.perf_counter() < target_press_end:
                    pass
                self.mouse_event(self.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                # 精确控制释放后延迟
                release_duration = 0.01
                target_release_end = time.perf_counter() + release_duration
                while time.perf_counter() < target_release_end:
                    pass
            except Exception as e:
                # 如果Windows API失败，使用pyautogui作为备用
                pyautogui.click()
                self.logger.warning(f"Windows API点击失败，使用pyautogui备用: {str(e)}")
                time.sleep(0.02)
            
            click_duration = (time.perf_counter() - click_start) * 1000
            self.logger.debug(f"点击命令执行: 第{i+1}次, 持续时间: {click_duration:.2f}ms")
    
    def _execute_leftdown(self, params):
        """
        执行鼠标左键按下命令
        参数: params - 参数，包含times字段
        """
        times = params.get('times', 1)
        for i in range(times):
            try:
                # 使用Windows API执行鼠标按下，性能更高
                self.mouse_event(self.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                # 短暂延迟确保事件被系统处理
                time.sleep(0.005)
            except Exception as e:
                # 如果Windows API失败，使用pyautogui作为备用
                pyautogui.mouseDown(button='left')
                self.logger.warning(f"Windows API按下鼠标失败，使用pyautogui备用: {str(e)}")
                time.sleep(0.01)
    
    def _execute_leftup(self, params):
        """
        执行鼠标左键释放命令
        参数: params - 参数，包含times字段
        """
        times = params.get('times', 1)
        for i in range(times):
            try:
                # 使用Windows API执行鼠标释放，性能更高
                self.mouse_event(self.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                # 短暂延迟确保事件被系统处理
                time.sleep(0.005)
            except Exception as e:
                # 如果Windows API失败，使用pyautogui作为备用
                pyautogui.mouseUp(button='left')
                self.logger.warning(f"Windows API释放鼠标失败，使用pyautogui备用: {str(e)}")
                time.sleep(0.01)
    
    def execute_script_file(self, file_path):
        """
        直接执行脚本文件
        参数: file_path - 文件路径
        返回: dict - 执行结果
        """
        from src.core.q_script_parser import QScriptParser
        
        script_start_time = time.time()
        self.logger.info(f"========================================")
        self.logger.info(f"开始执行脚本文件: {file_path}")
        self.logger.info(f"执行开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(script_start_time))}")
        
        # 解析文件
        parser = QScriptParser()
        parse_result = parser.parse_file(file_path)
        
        if not parse_result['success']:
            self.logger.error(f"脚本解析失败: {parse_result['message']}")
            self.logger.info(f"========================================")
            return parse_result
        
        # 执行命令
        commands = parse_result['commands']
        self.logger.info(f"脚本解析成功，包含 {len(commands)} 条命令")
        
        # 分析命令类型分布
        command_types = {}
        for cmd in commands:
            cmd_type = cmd.get('type', 'unknown')
            command_types[cmd_type] = command_types.get(cmd_type, 0) + 1
        self.logger.info(f"命令类型分布: {command_types}")
        
        result = self.execute_commands(commands)
        
        script_end_time = time.time()
        total_script_duration = script_end_time - script_start_time
        
        self.logger.info(f"========================================")
        self.logger.info(f"脚本执行完成: {result['message']}")
        self.logger.info(f"总执行时间: {total_script_duration:.2f} 秒")
        self.logger.info(f"命令执行成功率: {(result['executed']/result['total']*100):.2f}%")
        if result['failed'] > 0:
            self.logger.warning(f"失败命令数: {result['failed']}")
        
        # 输出详细执行统计
        self.logger.debug(f"执行详情: {result['details']}")
        self.logger.info(f"========================================")
        
        return result