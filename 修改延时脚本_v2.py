#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改按键精灵脚本中的延时值
将除鼠标点击操作（LeftClick、LeftDown、LeftUp）前后的延时以外的所有延时数值变为原来的三分之一
"""

import re
import os

def modify_delays(file_path):
    """
    修改脚本文件中的延时值
    
    Args:
        file_path: 文件路径
    """
    print(f"正在处理文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        print(f"成功读取文件，共 {len(lines)} 行")
        
        modified_lines = []
        # 标记前一行是否是鼠标点击操作
        prev_is_click = False
        
        for i, line in enumerate(lines):
            # 检查当前行是否是延时操作
            delay_match = re.match(r'^\s*Delay\s+(\d+)\s*$', line)
            
            if delay_match:
                delay_value = int(delay_match.group(1))
                
                # 检查下一行是否是鼠标点击操作
                next_is_click = False
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('LeftClick') or next_line.startswith('LeftDown') or next_line.startswith('LeftUp'):
                        next_is_click = True
                
                # 如果前一行是鼠标点击操作，或者下一行是鼠标点击操作，则保留原值
                if prev_is_click or next_is_click:
                    modified_lines.append(line)
                else:
                    # 否则将延时值变为原来的三分之一
                    new_delay_value = delay_value // 3
                    modified_line = line.replace(str(delay_value), str(new_delay_value))
                    modified_lines.append(modified_line)
            else:
                # 检查当前行是否是鼠标点击操作
                line_stripped = line.strip()
                if line_stripped.startswith('LeftClick') or line_stripped.startswith('LeftDown') or line_stripped.startswith('LeftUp'):
                    prev_is_click = True
                else:
                    prev_is_click = False
                modified_lines.append(line)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.writelines(modified_lines)
        
        print(f"文件修改完成: {file_path}")
        return True
    except Exception as e:
        print(f"处理文件时出错: {file_path}, 错误信息: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始修改延时值...")
    
    # 需要修改的文件列表
    files_to_modify = [
        "c:\\Users\\ciallo~\\Desktop\\视觉脚本\\关卡脚本\\第四关.Q",
        "c:\\Users\\ciallo~\\Desktop\\视觉脚本\\关卡脚本\\第五关.Q",
        "c:\\Users\\ciallo~\\Desktop\\视觉脚本\\关卡脚本\\六七八.Q",
        "c:\\Users\\ciallo~\\Desktop\\视觉脚本\\关卡脚本\\BOSS.Q"
    ]
    
    success_count = 0
    total_count = len(files_to_modify)
    
    for file_path in files_to_modify:
        if modify_delays(file_path):
            success_count += 1
        print("-" * 50)
    
    print(f"修改完成! 成功: {success_count}/{total_count}")
