#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改按键精灵脚本中的延时值
将除鼠标点击操作（LeftClick、LeftDown、LeftUp）前后的延时以外的所有延时数值变为原来的一半
"""

import re


def modify_delays(input_file, output_file):
    """
    修改脚本文件中的延时值
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
    """
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    modified_lines = []
    # 标记前一行是否是鼠标点击操作
    prev_is_click = False
    # 标记当前行是否是延时操作
    current_is_delay = False
    
    for i, line in enumerate(lines):
        # 检查当前行是否是延时操作
        delay_match = re.match(r'^\s*Delay\s+(\d+)\s*$', line)
        
        if delay_match:
            current_is_delay = True
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
                # 否则将延时值变为原来的二分之一
                new_delay_value = delay_value // 2
                modified_line = line.replace(str(delay_value), str(new_delay_value))
                modified_lines.append(modified_line)
        else:
            current_is_delay = False
            # 检查当前行是否是鼠标点击操作
            line_stripped = line.strip()
            if line_stripped.startswith('LeftClick') or line_stripped.startswith('LeftDown') or line_stripped.startswith('LeftUp'):
                prev_is_click = True
            else:
                prev_is_click = False
            modified_lines.append(line)
    
    with open(output_file, 'w', encoding='utf-8', errors='ignore') as f:
        f.writelines(modified_lines)
    
    print(f"修改完成，已保存到 {output_file}")


if __name__ == "__main__":
    # 直接指定完整的文件路径
    files_to_modify = [
        "c:\\Users\\ciallo~\\Desktop\\视觉脚本\\关卡脚本\\第三关.Q"
    ]
    
    print("开始修改延时值...")
    
    for file_path in files_to_modify:
        print(f"正在处理: {file_path}")
        modify_delays(file_path, file_path)  # 直接覆盖原文件
    
    print("所有文件修改完成!")
