class QScriptParser:
    """
    解析按键精灵.Q文件的解析器
    """
    
    def __init__(self):
        pass
    
    def parse_file(self, file_path):
        """
        解析.Q文件
        参数: file_path - 文件路径
        返回: dict - 解析结果，包含脚本命令列表和元数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 解析元数据和脚本
            metadata = self._parse_metadata(content)
            commands = self._parse_commands(content)
            
            return {
                'metadata': metadata,
                'commands': commands,
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'解析文件失败: {str(e)}'
            }
    
    def _parse_metadata(self, content):
        """
        解析元数据
        参数: content - 文件内容
        返回: dict - 元数据
        """
        metadata = {}
        lines = content.split('\n')
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测节
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                metadata[current_section] = {}
            # 解析键值对
            elif '=' in line and current_section:
                key, value = line.split('=', 1)
                metadata[current_section][key.strip()] = value.strip()
        
        return metadata
    
    def _parse_commands(self, content):
        """
        解析脚本命令
        参数: content - 文件内容
        返回: list - 命令列表
        """
        commands = []
        
        # 找到[Script]部分
        script_start = content.find('[Script]')
        if script_start == -1:
            return commands
        
        # 提取脚本内容
        script_content = content[script_start:]
        lines = script_content.split('\n')
        
        # 解析每行命令
        for line in lines:
            line = line.strip()
            if not line or line.startswith('[') or line.startswith(';') or line.startswith('#') or line.startswith("'"):
                continue
            
            # 解析命令
            command = self._parse_line(line)
            if command:
                commands.append(command)
        
        return commands
    
    def _parse_line(self, line):
        """
        解析单行命令
        参数: line - 命令行
        返回: dict - 命令对象
        """
        # 分割命令和参数
        parts = line.split(' ', 1)
        if not parts:
            return None
        
        command_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''
        
        # 解析不同类型的命令
        if command_name == 'delay':
            try:
                delay_ms = int(args.strip())
                return {
                    'type': 'delay',
                    'params': {
                        'ms': delay_ms
                    }
                }
            except:
                return None
        
        elif command_name == 'moveto':
            try:
                coords = args.strip().split(',')
                x = int(coords[0].strip())
                y = int(coords[1].strip())
                return {
                    'type': 'moveto',
                    'params': {
                        'x': x,
                        'y': y
                    }
                }
            except:
                return None
        
        elif command_name == 'leftclick':
            try:
                times = int(args.strip()) if args.strip() else 1
                return {
                    'type': 'leftclick',
                    'params': {
                        'times': times
                    }
                }
            except:
                return None
        
        elif command_name == 'leftdown':
            try:
                times = int(args.strip()) if args.strip() else 1
                return {
                    'type': 'leftdown',
                    'params': {
                        'times': times
                    }
                }
            except:
                return None
        
        elif command_name == 'leftup':
            try:
                times = int(args.strip()) if args.strip() else 1
                return {
                    'type': 'leftup',
                    'params': {
                        'times': times
                    }
                }
            except:
                return None
        
        return None