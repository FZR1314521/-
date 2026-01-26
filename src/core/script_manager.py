import importlib
import os
from pathlib import Path
from src.config.config import SCRIPTS_DIR, Q_SCRIPTS_DIR
from src.core.q_script_parser import QScriptParser
from src.core.q_script_executor import QScriptExecutor

class ScriptManager:
    def __init__(self):
        self.scripts = {}
        self.load_scripts()
    
    def load_scripts(self):
        """
        加载所有子脚本
        """
        try:
            # 加载Python脚本
            self._load_python_scripts()
            # 加载.Q脚本
            self._load_q_scripts()
        except Exception as e:
            print(f"加载脚本目录失败: {str(e)}")
    
    def _load_python_scripts(self):
        """
        加载Python脚本
        """
        try:
            script_files = [f for f in os.listdir(SCRIPTS_DIR) if f.endswith('.py')]
            for script_file in script_files:
                script_name = script_file[:-3]
                module_path = f"src.scripts.{script_name}"
                try:
                    module = importlib.import_module(module_path)
                    script_func = getattr(module, script_name, None)
                    if script_func and callable(script_func):
                        self.scripts[script_name] = {
                            'module': module,
                            'function': script_func,
                            'type': 'python'
                        }
                        print(f"加载脚本成功: {script_name}")
                except Exception as e:
                    print(f"加载脚本失败 {script_name}: {str(e)}")
        except Exception as e:
            print(f"加载Python脚本目录失败: {str(e)}")
    
    def _load_q_scripts(self):
        """
        加载.Q脚本
        """
        try:
            q_script_files = [f for f in os.listdir(Q_SCRIPTS_DIR) if f.endswith('.Q')]
            for q_script_file in q_script_files:
                script_name = q_script_file[:-2]  # 移除.Q后缀
                script_path = Q_SCRIPTS_DIR / q_script_file
                try:
                    # 解析.Q文件以验证其有效性
                    parser = QScriptParser()
                    parse_result = parser.parse_file(script_path)
                    if parse_result['success']:
                        self.scripts[script_name] = {
                            'path': script_path,
                            'type': 'q_script',
                            'commands': parse_result['commands'],
                            'metadata': parse_result['metadata']
                        }
                        print(f"加载.Q脚本成功: {script_name}")
                    else:
                        print(f"解析.Q脚本失败 {script_name}: {parse_result['message']}")
                except Exception as e:
                    print(f"加载.Q脚本失败 {script_name}: {str(e)}")
        except Exception as e:
            print(f"加载.Q脚本目录失败: {str(e)}")
    
    def get_script(self, script_name):
        """
        获取指定脚本
        参数: script_name - 脚本名称
        返回: dict - 脚本信息
        """
        return self.scripts.get(script_name)
    
    def run_script(self, script_name, params=None):
        """
        运行指定脚本
        参数: script_name - 脚本名称
              params - 传递给脚本的参数
        返回: dict - 脚本执行结果
        """
        script_info = self.get_script(script_name)
        if not script_info:
            return {'success': False, 'message': f'脚本 {script_name} 不存在'}
        
        try:
            script_type = script_info.get('type', 'python')
            
            if script_type == 'python':
                # 运行Python脚本
                result = script_info['function'](params)
                return result
            elif script_type == 'q_script':
                # 运行.Q脚本
                return self._run_q_script(script_info, params)
            else:
                return {'success': False, 'message': f'未知脚本类型: {script_type}'}
        except Exception as e:
            return {'success': False, 'message': f'执行脚本失败: {str(e)}'}
    
    def _run_q_script(self, script_info, params=None):
        """
        运行.Q脚本
        参数: script_info - 脚本信息
              params - 传递给脚本的参数
        返回: dict - 执行结果
        """
        try:
            # 获取命令列表
            commands = script_info.get('commands', [])
            
            # 创建执行器并执行命令
            executor = QScriptExecutor()
            result = executor.execute_commands(commands)
            
            return result
        except Exception as e:
            return {'success': False, 'message': f'执行.Q脚本失败: {str(e)}'}
    
    def list_scripts(self):
        """
        列出所有加载的脚本
        返回: list - 脚本名称列表
        """
        return list(self.scripts.keys())
