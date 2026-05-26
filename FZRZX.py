#!/usr/bin/env python3
# FZR塔防主执行程序
# 功能：通过UI界面触发，执行YOLO目标检测并执行相应操作

import time
import logging
from pathlib import Path
import pyautogui
import cv2
import numpy as np
import psutil
import win32gui
from pynput.keyboard import Controller
import threading

# 导入核心模块
from src.core.window_manager import WindowManager
from src.core.yolo_detector import YoloDetector
from src.core.script_manager import ScriptManager
from src.core.screenshot import ScreenshotManager
from src.config.config import LOGS_DIR, PROJECT_ROOT

# 配置日志
# 将日志保存在同目录下的"运行日志.txt"
log_file_path = Path(__file__).parent / "运行日志.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FZRExecutor:
    """
    FZR塔防执行器
    负责执行YOLO目标检测并根据结果执行操作
    """
    def __init__(self):
        """
        初始化执行器
        """
        self.window_manager = WindowManager()
        self.yolo_detector = YoloDetector()
        self.script_manager = ScriptManager()
        self.is_running = False
        self.loop_count = 5  # 增加默认循环次数，确保所有界面都能被检测到
        self.current_loop = 0
        self.afk_detection_running = False
        self.afk_detection_thread = None
    
    def set_target_window(self, window_title):
        """
        设置目标窗口
        参数: window_title - 窗口标题
        """
        self.window_manager.window_title = window_title
        logger.info(f"目标窗口已设置为: {window_title}")
    
    def set_loop_count(self, loop_count):
        """
        设置循环次数
        参数: loop_count - 循环次数
        """
        self.loop_count = loop_count
        logger.info(f"循环次数已设置为: {loop_count}")
    
    def start_execution(self):
        """
        开始执行
        返回: dict - 执行结果
        """
        logger.info("开始执行FZR塔防自动化")
        self.is_running = True
        self.current_loop = 0
        
        results = []
        
        try:
            # 首先检查并激活目标窗口，确保它在最前面
            if not self.window_manager.find_window():
                logger.warning("未找到目标窗口")
                return {'success': False, 'message': '未找到目标窗口'}
            
            # 激活窗口，确保它在最前面
            self.window_manager.activate_window()
            logger.info("目标窗口已激活并前置")
            
            # 等待1秒，确保窗口完全前置
            time.sleep(1)
            
            while self.is_running and self.current_loop < self.loop_count:
                self.current_loop += 1
                logger.info(f"执行第 {self.current_loop}/{self.loop_count} 轮")
                
                # 再次激活窗口，确保它仍然在最前面
                self.window_manager.activate_window()
                
                # 执行一轮检测和操作
                loop_result = self.execute_once()
                results.append(loop_result)
                
                # 等待一段时间再进行下一轮，确保界面有足够的时间切换
                if self.current_loop < self.loop_count:
                    time.sleep(3)  # 增加等待时间到3秒，确保界面有足够的时间切换
            
            return {
                'success': True,
                'message': f'执行完成，共执行 {self.current_loop} 轮',
                'results': results
            }
        
        except Exception as e:
            logger.error(f"执行失败: {str(e)}")
            return {
                'success': False,
                'message': f'执行失败: {str(e)}',
                'results': []
            }
        
        finally:
            self.is_running = False
            logger.info("执行结束")
    
    def execute_once(self):
        """
        执行一次检测和操作
        返回: dict - 执行结果
        """
        try:
            # 检查窗口
            if not self.window_manager.find_window():
                logger.warning("未找到目标窗口")
                return {'success': False, 'message': '未找到目标窗口'}
            
            # 激活窗口
            self.window_manager.activate_window()
            
            # 处理选择玩法界面
            select_game_mode_path = str(Path(__file__).parent / "data" / "images" / "选择玩法.png")
            game_mode_result = self.handle_select_game_mode(select_game_mode_path)
            logger.info(f"处理选择玩法界面结果: {game_mode_result['message']}")
            
            # 处理选择塔防模式界面
            select_tower_defense_path = str(Path(__file__).parent / "data" / "images" / "选择塔防模式.png")
            tower_defense_result = self.handle_select_game_mode(select_tower_defense_path)
            logger.info(f"处理选择塔防模式界面结果: {tower_defense_result['message']}")
            
            # 处理创建房间界面
            create_room_path = str(Path(__file__).parent / "data" / "images" / "创建房间.png")
            single_mode_path = str(Path(__file__).parent / "data" / "images" / "单人模式.png")
            create_room_result = self.handle_create_room(create_room_path, single_mode_path)
            logger.info(f"处理创建房间界面结果: {create_room_result['message']}")
            
            # 处理炼狱选择界面
            purgatory_done_path = str(Path(__file__).parent / "data" / "images" / "炼狱选择完毕.png")
            purgatory_select_path = str(Path(__file__).parent / "data" / "images" / "炼狱选择.png")
            purgatory_result = self.handle_purgatory_selection(purgatory_done_path, purgatory_select_path)
            logger.info(f"处理炼狱选择界面结果: {purgatory_result['message']}")
            
            # 处理开始按钮和挑战提示界面
            start_button_path = str(Path(__file__).parent / "data" / "images" / "开始按钮.png")
            challenge_tip_path = str(Path(__file__).parent / "data" / "images" / "挑战提示.png")
            no_tip_today_path = str(Path(__file__).parent / "data" / "images" / "今日不再提示.png")
            confirm_start_path = str(Path(__file__).parent / "data" / "images" / "确认开启.png")
            start_challenge_result = self.handle_start_and_challenge(start_button_path, challenge_tip_path, no_tip_today_path, confirm_start_path)
            logger.info(f"处理开始按钮和挑战提示界面结果: {start_challenge_result['message']}")
            
            # 处理进入游戏和平面切换界面
            enter_game_path = str(Path(__file__).parent / "data" / "images" / "进入游戏.png")
            plane_switch_path = str(Path(__file__).parent / "data" / "images" / "平面切换.png")
            plane_switch_success_path = str(Path(__file__).parent / "data" / "images" / "平面切换成功.png")
            enter_game_result = self.handle_enter_game_and_plane_switch(enter_game_path, plane_switch_path, plane_switch_success_path)
            logger.info(f"处理进入游戏和平面切换界面结果: {enter_game_result['message']}")
            
            # 获取窗口区域
            window_rect = self.window_manager.get_window_rect()
            if not window_rect:
                logger.warning("获取窗口区域失败")
                return {'success': False, 'message': '获取窗口区域失败'}
            
            # 执行YOLO检测
            detections = self.yolo_detector.detect_from_window(window_rect)
            logger.info(f"检测到 {len(detections)} 个目标")
            
            # 处理检测结果
            action_results = []
            for detection in detections:
                action_result = self.process_detection(detection)
                action_results.append(action_result)
            
            # 添加选择玩法、选择塔防模式、创建房间、炼狱选择、开始挑战和进入游戏界面处理结果
            additional_results = {
                'select_game_mode': game_mode_result,
                'select_tower_defense': tower_defense_result,
                'create_room': create_room_result,
                'purgatory_selection': purgatory_result,
                'start_challenge': start_challenge_result,
                'enter_game': enter_game_result
            }
            
            return {
                'success': True,
                'message': f'检测完成，处理了 {len(action_results)} 个目标',
                'detections': detections,
                'actions': action_results,
                'additional_results': additional_results
            }
        
        except Exception as e:
            logger.error(f"执行一轮失败: {str(e)}")
            return {'success': False, 'message': f'执行失败: {str(e)}'}
    
    def process_detection(self, detection):
        """
        处理单个检测结果
        参数: detection - 检测结果
        返回: dict - 处理结果
        """
        try:
            class_name = detection['class_name']
            bbox = detection['bbox']
            confidence = detection['confidence']
            
            logger.info(f"处理目标: {class_name}, 置信度: {confidence:.2f}, 位置: {bbox}")
            
            # 获取对应的操作脚本
            script_name = self.get_script_for_detection(class_name)
            if not script_name:
                logger.info(f"未找到对应 {class_name} 的操作脚本")
                return {
                    'success': False,
                    'class_name': class_name,
                    'message': f'未找到对应 {class_name} 的操作脚本'
                }
            
            # 执行操作脚本
            params = {
                'class_name': class_name,
                'bbox': bbox,
                'confidence': confidence,
                'timestamp': time.time()
            }
            
            script_result = self.script_manager.run_script(script_name, params)
            logger.info(f"执行脚本 {script_name} 结果: {script_result}")
            
            return {
                'success': script_result.get('success', False),
                'class_name': class_name,
                'script_name': script_name,
                'message': script_result.get('message', '执行脚本失败')
            }
        
        except Exception as e:
            logger.error(f"处理检测结果失败: {str(e)}")
            return {
                'success': False,
                'class_name': detection.get('class_name', 'unknown'),
                'message': f'处理失败: {str(e)}'
            }
    
    def get_script_for_detection(self, class_name):
        """
        根据检测结果获取对应的操作脚本
        参数: class_name - 目标类别名称
        返回: str - 脚本名称
        """
        # 这里是类别到脚本的映射关系
        # 可以根据实际需求修改
        script_mapping = {
            # 示例映射
            # 'enemy': 'attack_enemy',
            # 'tower': 'upgrade_tower'
        }
        
        return script_mapping.get(class_name)
    
    def detect_template(self, template_path, threshold=0.8):
        """
        模板匹配检测
        参数: template_path - 模板图片路径
              threshold - 匹配阈值
        返回: dict - 检测结果，包含是否检测到和位置信息
        """
        try:
            # 加载模板图像
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                logger.error(f"无法加载模板图像: {template_path}")
                return {'detected': False, 'message': '无法加载模板图像'}
            
            # 获取窗口截图
            screenshot_manager = ScreenshotManager()
            window_rect = self.window_manager.get_window_rect()
            if not window_rect:
                logger.error("无法获取窗口区域")
                return {'detected': False, 'message': '无法获取窗口区域'}
            
            screenshot = screenshot_manager.capture_window(window_rect)
            if screenshot is None:
                logger.error("无法获取窗口截图")
                return {'detected': False, 'message': '无法获取窗口截图'}
            
            # 转换为灰度图像以提高匹配速度
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # 执行模板匹配
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            
            # 找到匹配度最高的位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            logger.info(f"模板匹配最大匹配值: {max_val:.2f}")
            
            if max_val >= threshold:
                # 计算模板中心位置
                template_height, template_width = template_gray.shape[:2]
                center_x = max_loc[0] + template_width // 2
                center_y = max_loc[1] + template_height // 2
                
                # 转换为屏幕坐标
                screen_x = window_rect[0] + center_x
                screen_y = window_rect[1] + center_y
                
                return {
                    'detected': True,
                    'message': '检测到模板图像',
                    'position': (screen_x, screen_y),
                    'confidence': max_val,
                    'bbox': (max_loc[0], max_loc[1], template_width, template_height)
                }
            else:
                return {'detected': False, 'message': '未检测到模板图像', 'confidence': max_val}
        
        except Exception as e:
            logger.error(f"模板匹配失败: {str(e)}")
            return {'detected': False, 'message': f'模板匹配失败: {str(e)}'}
    
    def click_at_position(self, position):
        """
        在指定位置执行鼠标左击
        参数: position - 点击位置 (x, y)
        返回: dict - 执行结果
        """
        try:
            x, y = position
            logger.info(f"执行鼠标左击 at ({x}, {y})")
            
            # 移动鼠标到指定位置
            pyautogui.moveTo(x, y, duration=0.2)
            
            # 执行左击
            pyautogui.click(x, y)
            
            return {'success': True, 'message': f'成功执行鼠标左击 at ({x}, {y})'}
        
        except Exception as e:
            logger.error(f"执行鼠标点击失败: {str(e)}")
            return {'success': False, 'message': f'执行鼠标点击失败: {str(e)}'}
    

    

    
    def handle_select_game_mode(self, template_path):
        """
        处理选择玩法界面
        参数: template_path - 选择玩法模板图片路径
        返回: dict - 处理结果
        """
        try:
            # 检测选择玩法图片
            detection_result = self.detect_template(template_path)
            
            if not detection_result['detected']:
                logger.info("未检测到选择玩法界面")
                return {'success': True, 'message': '未检测到选择玩法界面'}
            
            # 获取检测到的位置
            position = detection_result['position']
            confidence = detection_result['confidence']
            
            logger.info(f"检测到选择玩法界面，置信度: {confidence:.2f}，位置: {position}")
            
            # 执行第一次点击
            click_result = self.click_at_position(position)
            if not click_result['success']:
                logger.error(f"第一次点击失败: {click_result['message']}")
                return click_result
            
            # 等待2秒
            logger.info("等待2秒检查选择玩法界面是否仍然存在")
            time.sleep(2)
            
            # 再次检测
            second_detection = self.detect_template(template_path)
            
            if second_detection['detected']:
                logger.info("选择玩法界面仍然存在，执行第二次点击")
                # 执行第二次点击
                second_click_result = self.click_at_position(position)
                if not second_click_result['success']:
                    logger.error(f"第二次点击失败: {second_click_result['message']}")
                    return second_click_result
                return {'success': True, 'message': '执行了两次点击操作'}
            else:
                logger.info("选择玩法界面已消失，无需重复点击")
                return {'success': True, 'message': '执行了一次点击操作'}
        
        except Exception as e:
            logger.error(f"处理选择玩法界面失败: {str(e)}")
            return {'success': False, 'message': f'处理选择玩法界面失败: {str(e)}'}
    
    def handle_create_room(self, create_room_path, single_mode_path):
        """
        处理创建房间界面
        参数: create_room_path - 创建房间模板图片路径
              single_mode_path - 单人模式模板图片路径
        返回: dict - 处理结果
        """
        try:
            # 检测创建房间图片
            create_room_result = self.detect_template(create_room_path)
            
            if not create_room_result['detected']:
                logger.info("未检测到创建房间界面")
                return {'success': True, 'message': '未检测到创建房间界面'}
            
            logger.info("检测到创建房间界面")
            
            # 检测单人模式图片
            single_mode_result = self.detect_template(single_mode_path)
            
            if not single_mode_result['detected']:
                logger.error("未检测到单人模式界面")
                return {'success': False, 'message': '未检测到单人模式界面'}
            
            # 获取单人模式的位置
            single_mode_position = single_mode_result['position']
            single_mode_confidence = single_mode_result['confidence']
            
            logger.info(f"检测到单人模式界面，置信度: {single_mode_confidence:.2f}，位置: {single_mode_position}")
            
            # 执行第一次点击单人模式
            click_result = self.click_at_position(single_mode_position)
            if not click_result['success']:
                logger.error(f"第一次点击单人模式失败: {click_result['message']}")
                return click_result
            
            # 等待1秒
            logger.info("等待1秒检查创建房间界面是否仍然存在")
            time.sleep(1)
            
            # 再次检测创建房间界面
            second_create_room_detection = self.detect_template(create_room_path)
            
            if second_create_room_detection['detected']:
                logger.info("创建房间界面仍然存在，执行第二次点击单人模式")
                # 执行第二次点击单人模式
                second_click_result = self.click_at_position(single_mode_position)
                if not second_click_result['success']:
                    logger.error(f"第二次点击单人模式失败: {second_click_result['message']}")
                    return second_click_result
                return {'success': True, 'message': '执行了两次点击单人模式操作'}
            else:
                logger.info("创建房间界面已消失，无需重复点击")
                return {'success': True, 'message': '执行了一次点击单人模式操作'}
        
        except Exception as e:
            logger.error(f"处理创建房间界面失败: {str(e)}")
            return {'success': False, 'message': f'处理创建房间界面失败: {str(e)}'}
    
    def handle_purgatory_selection(self, purgatory_done_path, purgatory_select_path):
        """
        处理炼狱选择界面
        参数: purgatory_done_path - 炼狱选择完毕模板图片路径
              purgatory_select_path - 炼狱选择模板图片路径
        返回: dict - 处理结果
        """
        try:
            # 等待0.5秒，确保界面有足够的时间切换
            logger.info("等待0.5秒确保界面切换")
            time.sleep(0.5)
            
            # 首先检测炼狱选择完毕图片
            purgatory_done_result = self.detect_template(purgatory_done_path)
            
            if purgatory_done_result['detected']:
                # 获取炼狱选择完毕的位置
                purgatory_done_position = purgatory_done_result['position']
                purgatory_done_confidence = purgatory_done_result['confidence']
                
                logger.info(f"检测到炼狱选择完毕界面，置信度: {purgatory_done_confidence:.2f}，位置: {purgatory_done_position}")
                
                # 执行第一次点击炼狱选择完毕
                click_result = self.click_at_position(purgatory_done_position)
                if not click_result['success']:
                    logger.error(f"第一次点击炼狱选择完毕失败: {click_result['message']}")
                    return click_result
                
                # 等待1秒
                logger.info("等待1秒执行防错操作")
                time.sleep(1)
                
                # 执行第二次点击炼狱选择完毕
                second_click_result = self.click_at_position(purgatory_done_position)
                if not second_click_result['success']:
                    logger.error(f"第二次点击炼狱选择完毕失败: {second_click_result['message']}")
                    return second_click_result
                
                return {'success': True, 'message': '执行了两次点击炼狱选择完毕操作'}
            else:
                logger.info("未检测到炼狱选择完毕界面，尝试检测炼狱选择界面")
                
                # 检测炼狱选择图片
                purgatory_select_result = self.detect_template(purgatory_select_path)
                
                if not purgatory_select_result['detected']:
                    logger.info("未检测到炼狱选择界面")
                    return {'success': True, 'message': '未检测到炼狱选择界面'}
                
                # 获取炼狱选择的位置
                purgatory_select_position = purgatory_select_result['position']
                purgatory_select_confidence = purgatory_select_result['confidence']
                
                logger.info(f"检测到炼狱选择界面，置信度: {purgatory_select_confidence:.2f}，位置: {purgatory_select_position}")
                
                # 执行第一次点击炼狱选择
                click_result = self.click_at_position(purgatory_select_position)
                if not click_result['success']:
                    logger.error(f"第一次点击炼狱选择失败: {click_result['message']}")
                    return click_result
                
                # 等待1秒
                logger.info("等待1秒执行防错操作")
                time.sleep(1)
                
                # 执行第二次点击炼狱选择
                second_click_result = self.click_at_position(purgatory_select_position)
                if not second_click_result['success']:
                    logger.error(f"第二次点击炼狱选择失败: {second_click_result['message']}")
                    return second_click_result
                
                return {'success': True, 'message': '执行了两次点击炼狱选择操作'}
        
        except Exception as e:
            logger.error(f"处理炼狱选择界面失败: {str(e)}")
            return {'success': False, 'message': f'处理炼狱选择界面失败: {str(e)}'}
    
    def handle_start_and_challenge(self, start_button_path, challenge_tip_path, no_tip_today_path, confirm_start_path):
        """
        处理开始按钮和挑战提示界面
        参数: start_button_path - 开始按钮模板图片路径
              challenge_tip_path - 挑战提示模板图片路径
              no_tip_today_path - 今日不再提示模板图片路径
              confirm_start_path - 确认开启模板图片路径
        返回: dict - 处理结果
        """
        try:
            # 首先检测开始按钮图片
            start_button_result = self.detect_template(start_button_path)
            
            if start_button_result['detected']:
                # 获取开始按钮的位置
                start_button_position = start_button_result['position']
                start_button_confidence = start_button_result['confidence']
                
                logger.info(f"检测到开始按钮，置信度: {start_button_confidence:.2f}，位置: {start_button_position}")
                
                # 执行第一次点击开始按钮
                click_result = self.click_at_position(start_button_position)
                if not click_result['success']:
                    logger.error(f"第一次点击开始按钮失败: {click_result['message']}")
                    return click_result
                
                # 等待1秒
                logger.info("等待1秒检查开始按钮是否仍然存在")
                time.sleep(1)
                
                # 再次检测开始按钮
                second_start_button_detection = self.detect_template(start_button_path)
                
                if second_start_button_detection['detected']:
                    logger.info("开始按钮仍然存在，执行第二次点击")
                    # 执行第二次点击开始按钮
                    second_click_result = self.click_at_position(start_button_position)
                    if not second_click_result['success']:
                        logger.error(f"第二次点击开始按钮失败: {second_click_result['message']}")
                        return second_click_result
                else:
                    logger.info("开始按钮已消失，无需重复点击")
            else:
                logger.info("未检测到开始按钮")
            
            # 等待0.75秒，确保挑战提示有足够的时间弹出
            logger.info("等待0.75秒检查是否弹出挑战提示")
            time.sleep(0.75)
            
            # 检测是否弹出挑战提示
            challenge_tip_result = self.detect_template(challenge_tip_path, threshold=0.75)
            
            if challenge_tip_result['detected']:
                logger.info("检测到挑战提示界面")
                
                # 检测今日不再提示图片
                no_tip_today_result = self.detect_template(no_tip_today_path)
                
                if no_tip_today_result['detected']:
                    # 获取今日不再提示的位置
                    no_tip_today_position = no_tip_today_result['position']
                    no_tip_today_confidence = no_tip_today_result['confidence']
                    
                    logger.info(f"检测到今日不再提示，置信度: {no_tip_today_confidence:.2f}，位置: {no_tip_today_position}")
                    
                    # 执行一次点击今日不再提示
                    click_result = self.click_at_position(no_tip_today_position)
                    if not click_result['success']:
                        logger.error(f"点击今日不再提示失败: {click_result['message']}")
                        return click_result
                    
                    # 等待0.5秒确保操作生效
                    logger.info("等待0.5秒确保操作生效")
                    time.sleep(0.5)
                else:
                    logger.info("未检测到今日不再提示")
                
                # 检测确认开启图片
                confirm_start_result = self.detect_template(confirm_start_path)
                
                if confirm_start_result['detected']:
                    # 获取确认开启的位置
                    confirm_start_position = confirm_start_result['position']
                    confirm_start_confidence = confirm_start_result['confidence']
                    
                    logger.info(f"检测到确认开启，置信度: {confirm_start_confidence:.2f}，位置: {confirm_start_position}")
                    
                    # 执行第一次点击确认开启
                    click_result = self.click_at_position(confirm_start_position)
                    if not click_result['success']:
                        logger.error(f"第一次点击确认开启失败: {click_result['message']}")
                        return click_result
                    
                    # 等待1秒
                    logger.info("等待1秒检查确认开启是否仍然存在")
                    time.sleep(1)
                    
                    # 再次检测确认开启
                    second_confirm_start_detection = self.detect_template(confirm_start_path)
                    
                    if second_confirm_start_detection['detected']:
                        logger.info("确认开启仍然存在，执行第二次点击")
                        # 执行第二次点击确认开启
                        second_click_result = self.click_at_position(confirm_start_position)
                        if not second_click_result['success']:
                            logger.error(f"第二次点击确认开启失败: {second_click_result['message']}")
                            return second_click_result
                    else:
                        logger.info("确认开启已消失，无需重复点击")
                else:
                    logger.error("未检测到确认开启")
                    return {'success': False, 'message': '未检测到确认开启'}
                
                return {'success': True, 'message': '执行了挑战提示处理操作'}
            else:
                logger.info("未检测到挑战提示界面")
                return {'success': True, 'message': '未检测到挑战提示界面'}
        
        except Exception as e:
            logger.error(f"处理开始按钮和挑战提示界面失败: {str(e)}")
            return {'success': False, 'message': f'处理开始按钮和挑战提示界面失败: {str(e)}'}
    
    def handle_enter_game_and_plane_switch(self, enter_game_path, plane_switch_path, plane_switch_success_path):
        """
        处理进入游戏和平面切换界面
        参数: enter_game_path - 进入游戏模板图片路径
              plane_switch_path - 平面切换模板图片路径
              plane_switch_success_path - 平面切换成功模板图片路径
        返回: dict - 处理结果
        """
        try:
            check_count = 0
            
            # 每隔0.5秒检测一次进入游戏图片，直到检测到为止
            while self.is_running:
                check_count += 1
                logger.info(f"第 {check_count} 次检测进入游戏界面")
                
                # 检测跳过开局动画图片
                skip_intro_path = str(Path(__file__).parent / "data" / "images" / "跳过开局动画.png")
                skip_intro_result = self.detect_template(skip_intro_path)
                
                if skip_intro_result['detected']:
                    logger.info("检测到跳过开局动画界面")
                    
                    # 获取窗口区域，计算中心位置
                    window_rect = self.window_manager.get_window_rect()
                    if not window_rect:
                        logger.error("无法获取窗口区域")
                        return {'success': False, 'message': '无法获取窗口区域'}
                    
                    # 计算窗口中心位置
                    window_center_x = window_rect[0] + (window_rect[2] // 2)
                    window_center_y = window_rect[1] + (window_rect[3] // 2)
                    center_position = (window_center_x, window_center_y)
                    
                    logger.info(f"长按窗口中心位置 ({window_center_x}, {window_center_y}) 三秒钟")
                    
                    # 移动鼠标到窗口中心
                    pyautogui.moveTo(window_center_x, window_center_y, duration=0.2)
                    
                    # 执行长按操作，持续3秒
                    pyautogui.mouseDown(window_center_x, window_center_y)
                    time.sleep(3)
                    pyautogui.mouseUp(window_center_x, window_center_y)
                    
                    logger.info("长按操作完成")
                    
                    # 等待1秒后继续检测
                    time.sleep(1)
                    continue
                
                # 检测进入游戏图片
                enter_game_result = self.detect_template(enter_game_path)
                
                if enter_game_result['detected']:
                    logger.info("检测到进入游戏界面")
                    
                    # 增加四秒钟延时
                    logger.info("等待四秒钟再执行后续操作")
                    time.sleep(4)
                    
                    # 检测平面切换图片
                    plane_switch_result = self.detect_template(plane_switch_path)
                    
                    if not plane_switch_result['detected']:
                        logger.error("未检测到平面切换按钮")
                        return {'success': False, 'message': '未检测到平面切换按钮'}
                    
                    # 获取平面切换的位置
                    plane_switch_position = plane_switch_result['position']
                    plane_switch_confidence = plane_switch_result['confidence']
                    
                    logger.info(f"检测到平面切换按钮，置信度: {plane_switch_confidence:.2f}，位置: {plane_switch_position}")
                    
                    # 执行第一次点击平面切换
                    click_result = self.click_at_position(plane_switch_position)
                    if not click_result['success']:
                        logger.error(f"第一次点击平面切换失败: {click_result['message']}")
                        return click_result
                    
                    # 等待0.5秒
                    logger.info("等待0.5秒检查平面切换是否成功")
                    time.sleep(0.5)
                    
                    # 检测平面切换成功图片
                    plane_switch_success_result = self.detect_template(plane_switch_success_path)
                    
                    if not plane_switch_success_result['detected']:
                        logger.info("未检测到平面切换成功，执行第二次点击平面切换")
                        # 执行第二次点击平面切换
                        second_click_result = self.click_at_position(plane_switch_position)
                        if not second_click_result['success']:
                            logger.error(f"第二次点击平面切换失败: {second_click_result['message']}")
                            return second_click_result
                        
                        return {'success': True, 'message': '执行了两次点击平面切换操作'}
                    else:
                        logger.info("平面切换成功")
                        
                        # 检测并点击商场入口
                        mall_entry_path = str(Path(__file__).parent / "data" / "images" / "商场入口.png")
                        mall_entry_result = self.detect_template(mall_entry_path)
                        
                        if mall_entry_result['detected']:
                            # 获取商场入口的位置
                            mall_entry_position = mall_entry_result['position']
                            mall_entry_confidence = mall_entry_result['confidence']
                            
                            logger.info(f"检测到商场入口，置信度: {mall_entry_confidence:.2f}，位置: {mall_entry_position}")
                            
                            # 执行点击商场入口
                            click_result = self.click_at_position(mall_entry_position)
                            if not click_result['success']:
                                logger.error(f"点击商场入口失败: {click_result['message']}")
                                return click_result
                            
                            logger.info("已点击商场入口")
                            
                            # 处理商场操作
                            mall_result = self.handle_mall_operations()
                            if not mall_result['success']:
                                logger.error(f"处理商场操作失败: {mall_result['message']}")
                                return mall_result
                            
                            return {'success': True, 'message': '执行了一次点击平面切换操作并处理了商场操作'}
                        else:
                            logger.info("未检测到商场入口")
                            return {'success': True, 'message': '执行了一次点击平面切换操作'}
                else:
                    logger.info("未检测到进入游戏界面，0.5秒后再次检测")
                    time.sleep(0.5)
        
        except Exception as e:
            logger.error(f"处理进入游戏和平面切换界面失败: {str(e)}")
            return {'success': False, 'message': f'处理进入游戏和平面切换界面失败: {str(e)}'}

    def handle_mall_operations(self):
        """
        处理商场操作
        返回: dict - 处理结果
        """
        try:
            # 检测进入商场成功图片
            enter_mall_success_path = str(Path(__file__).parent / "data" / "images" / "进入商场成功.png")
            mall_entry_path = str(Path(__file__).parent / "data" / "images" / "商场入口.png")
            
            # 简化商场操作逻辑，已成功点击商场入口后直接跳过检测
            logger.info("已成功点击商场入口，开始处理商场内操作")
            
            # 等待一段时间确保界面切换
            time.sleep(2)
            
            # 直接继续后续操作，不再检测进入商场成功界面
            logger.info("跳过进入商场成功界面检测，直接执行后续操作")
            
            # 要识别的四个图片
            target_images = [
                "自修复磁暴塔.png",
                "防空导弹.png",
                "修理站.png",
                "破坏者.png"
            ]
            
            # 已找到的图片
            found_images = set()
            
            # 下拉区域路径
            pull_down_path = str(Path(__file__).parent / "data" / "images" / "下拉区域.png")
            
            # 下拉操作计数器和方向
            pull_count = 0
            pull_direction = "up"  # 初始方向为向上（修改为第一次上拉）
            
            # 循环直到找到所有四个图片
            while self.is_running and len(found_images) < len(target_images):
                logger.info(f"当前已找到 {len(found_images)} 个目标，还需找到 {len(target_images) - len(found_images)} 个")
                
                # 按顺序检测每个目标图片
                for image_name in target_images:
                    if image_name in found_images:
                        continue
                    
                    # 构建图片路径
                    image_path = str(Path(__file__).parent / "data" / "images" / image_name)
                    
                    # 检测图片
                    image_result = self.detect_template(image_path)
                    
                    if image_result['detected']:
                        logger.info(f"检测到 {image_name}")
                        
                        # 获取图片位置
                        image_position = image_result['position']
                        
                        # 执行单击装备区域中间
                        self.click_at_position(image_position)
                        time.sleep(0.5)
                        
                        # 点击装备.png
                        equipment_path = str(Path(__file__).parent / "data" / "images" / "装备.png")
                        equipment_result = self.detect_template(equipment_path)
                        if equipment_result['detected']:
                            logger.info("检测到装备按钮，执行点击操作")
                            equipment_position = equipment_result['position']
                            self.click_at_position(equipment_position)
                        else:
                            logger.warning("未检测到装备按钮")
                        
                        # 将该图片添加到已找到集合
                        found_images.add(image_name)
                    
                    # 每次识别间隔0.5秒
                    time.sleep(0.5)
                
                # 如果还有未找到的图片，执行下拉操作
                if len(found_images) < len(target_images):
                    logger.info(f"还有未找到的图片，执行{'向下' if pull_direction == 'down' else '向上'}拖动操作")
                    
                    # 检测下拉区域
                    pull_down_result = self.detect_template(pull_down_path)
                    
                    if not pull_down_result['detected']:
                        logger.error("未检测到下拉区域")
                        return {'success': False, 'message': '未检测到下拉区域'}
                    
                    # 获取下拉区域位置
                    pull_down_position = pull_down_result['position']
                    
                    # 计算移动的目标位置
                    move_distance = 150  # 移动的距离
                    if pull_direction == "down":
                        target_position = (pull_down_position[0], pull_down_position[1] + move_distance)
                        logger.info(f"在下拉区域 ({pull_down_position[0]}, {pull_down_position[1]}) 向下拖动 {move_distance} 像素")
                    else:
                        target_position = (pull_down_position[0], pull_down_position[1] - move_distance)
                        logger.info(f"在下拉区域 ({pull_down_position[0]}, {pull_down_position[1]}) 向上拖动 {move_distance} 像素")
                    
                    # 移动鼠标到下拉区域
                    pyautogui.moveTo(pull_down_position[0], pull_down_position[1], duration=0.2)
                    
                    # 按下左击，移动，松开左击
                    pyautogui.mouseDown()
                    pyautogui.moveTo(target_position[0], target_position[1], duration=0.5)
                    pyautogui.mouseUp()
                    
                    # 等待0.8秒后继续检测，为识别留出时间
                    time.sleep(0.8)
                    
                    # 更新下拉计数器和方向
                    pull_count += 1
                    if pull_count >= 5:
                        # 切换方向
                        if pull_direction == "down":
                            pull_direction = "up"
                        else:
                            pull_direction = "down"
                        pull_count = 0
                        logger.info(f"切换拖动方向为{'向下' if pull_direction == 'down' else '向上'}")
            
            logger.info("已找到所有四个目标图片")
            
            # 购买确认操作的下拉计数器和方向
            confirm_pull_count = 0
            confirm_pull_direction = "up"  # 初始方向为向上（修改为第一次上拉）
            
            # 处理购买确认操作
            # 1. 处理购买确认破坏者
            confirm_destroyer_path = str(Path(__file__).parent / "data" / "images" / "购买确认破坏者.png")
            confirm_destroyer_result = self.detect_template(confirm_destroyer_path)
            
            if confirm_destroyer_result['detected']:
                logger.info("检测到购买确认破坏者")
                
                # 寻找破坏者.png
                destroyer_path = str(Path(__file__).parent / "data" / "images" / "破坏者.png")
                destroyer_result = self.detect_template(destroyer_path)
                
                if destroyer_result['detected']:
                    logger.info("检测到破坏者，执行单击操作后点击装备按钮")
                    destroyer_position = destroyer_result['position']
                    
                    # 执行单击装备区域中间
                    self.click_at_position(destroyer_position)
                    time.sleep(0.5)
                    
                    # 点击装备.png
                    equipment_path = str(Path(__file__).parent / "data" / "images" / "装备.png")
                    equipment_result = self.detect_template(equipment_path)
                    if equipment_result['detected']:
                        logger.info("检测到装备按钮，执行点击操作")
                        equipment_position = equipment_result['position']
                        self.click_at_position(equipment_position)
                    else:
                        logger.warning("未检测到装备按钮")
                else:
                    logger.warning("未检测到破坏者")
            else:
                logger.info("未检测到购买确认破坏者，跳过处理")
            
            # 重置下拉计数器和方向
            confirm_pull_count = 0
            confirm_pull_direction = "up"  # 修改为向上
            
            # 2. 处理购买确认修理站
            confirm_repair_path = str(Path(__file__).parent / "data" / "images" / "购买确认修理站.png")
            confirm_repair_result = self.detect_template(confirm_repair_path)
            
            if confirm_repair_result['detected']:
                logger.info("检测到购买确认修理站")
                
                # 寻找修理站.png
                repair_path = str(Path(__file__).parent / "data" / "images" / "修理站.png")
                repair_result = self.detect_template(repair_path)
                
                if repair_result['detected']:
                    logger.info("检测到修理站，执行单击操作后点击装备按钮")
                    repair_position = repair_result['position']
                    
                    # 执行单击装备区域中间
                    self.click_at_position(repair_position)
                    time.sleep(0.5)
                    
                    # 点击装备.png
                    equipment_path = str(Path(__file__).parent / "data" / "images" / "装备.png")
                    equipment_result = self.detect_template(equipment_path)
                    if equipment_result['detected']:
                        logger.info("检测到装备按钮，执行点击操作")
                        equipment_position = equipment_result['position']
                        self.click_at_position(equipment_position)
                    else:
                        logger.warning("未检测到装备按钮")
                else:
                    logger.warning("未检测到修理站")
            else:
                logger.info("未检测到购买确认修理站，跳过处理")
            
            # 重置下拉计数器和方向
            confirm_pull_count = 0
            confirm_pull_direction = "up"  # 修改为向上
            
            # 3. 处理购买确认防空导弹
            confirm_air_defense_path = str(Path(__file__).parent / "data" / "images" / "购买确认防空导弹.png")
            confirm_air_defense_result = self.detect_template(confirm_air_defense_path)
            
            if confirm_air_defense_result['detected']:
                logger.info("检测到购买确认防空导弹")
                
                # 寻找防空导弹.png
                air_defense_path = str(Path(__file__).parent / "data" / "images" / "防空导弹.png")
                air_defense_result = self.detect_template(air_defense_path)
                
                if air_defense_result['detected']:
                    logger.info("检测到防空导弹，执行单击操作后点击装备按钮")
                    air_defense_position = air_defense_result['position']
                    
                    # 执行单击装备区域中间
                    self.click_at_position(air_defense_position)
                    time.sleep(0.5)
                    
                    # 点击装备.png
                    equipment_path = str(Path(__file__).parent / "data" / "images" / "装备.png")
                    equipment_result = self.detect_template(equipment_path)
                    if equipment_result['detected']:
                        logger.info("检测到装备按钮，执行点击操作")
                        equipment_position = equipment_result['position']
                        self.click_at_position(equipment_position)
                    else:
                        logger.warning("未检测到装备按钮")
                else:
                    logger.warning("未检测到防空导弹")
            else:
                logger.info("未检测到购买确认防空导弹，跳过处理")
            
            # 重置下拉计数器和方向
            confirm_pull_count = 0
            confirm_pull_direction = "up"  # 修改为向上
            
            # 4. 处理购买确认自修复
            confirm_self_repair_path = str(Path(__file__).parent / "data" / "images" / "购买确认自修复.png")
            confirm_self_repair_result = self.detect_template(confirm_self_repair_path)
            
            if confirm_self_repair_result['detected']:
                logger.info("检测到购买确认自修复")
                
                # 寻找自修复磁暴塔.png
                self_repair_path = str(Path(__file__).parent / "data" / "images" / "自修复磁暴塔.png")
                self_repair_result = self.detect_template(self_repair_path)
                
                if self_repair_result['detected']:
                    logger.info("检测到自修复磁暴塔，执行单击操作后点击装备按钮")
                    self_repair_position = self_repair_result['position']
                    
                    # 执行单击装备区域中间
                    self.click_at_position(self_repair_position)
                    time.sleep(0.5)
                    
                    # 点击装备.png
                    equipment_path = str(Path(__file__).parent / "data" / "images" / "装备.png")
                    equipment_result = self.detect_template(equipment_path)
                    if equipment_result['detected']:
                        logger.info("检测到装备按钮，执行点击操作")
                        equipment_position = equipment_result['position']
                        self.click_at_position(equipment_position)
                    else:
                        logger.warning("未检测到装备按钮")
                else:
                    logger.warning("未检测到自修复磁暴塔")
            else:
                logger.info("未检测到购买确认自修复，跳过处理")
            
            logger.info("商场操作完成")
            
            # 间隔0.5秒点击退出商场.png
            time.sleep(0.5)
            exit_mall_path = str(Path(__file__).parent / "data" / "images" / "退出商场.png")
            exit_mall_result = self.detect_template(exit_mall_path)
            
            if exit_mall_result['detected']:
                logger.info("检测到退出商场按钮，执行点击操作")
                exit_mall_position = exit_mall_result['position']
                
                # 执行第一次点击
                self.click_at_position(exit_mall_position)
                
                # 防错机制：检测是否仍然在商场内
                enter_mall_success_path = str(Path(__file__).parent / "data" / "images" / "进入商场成功.png")
                enter_mall_result = self.detect_template(enter_mall_success_path)
                
                if enter_mall_result['detected']:
                    logger.warning("仍然在商场内，再次点击退出商场按钮")
                    self.click_at_position(exit_mall_position)
                
                # 延时0.5秒后检测是否有退出地图.png
                time.sleep(0.5)
                exit_map_path = str(Path(__file__).parent / "data" / "images" / "退出地图.png")
                exit_map_result = self.detect_template(exit_map_path)
                
                if exit_map_result['detected']:
                    logger.info("检测到退出地图按钮，执行点击操作")
                    exit_map_position = exit_map_result['position']
                    self.click_at_position(exit_map_position)
                else:
                    logger.info("未检测到退出地图按钮，跳过这一步")
            else:
                logger.warning("未检测到退出商场按钮")
            
            # 商场操作完成后延时0.5秒
            logger.info("商场操作完成，等待0.5秒")
            time.sleep(0.5)
            
            # 点击退出平面.png
            logger.info("点击退出平面.png")
            exit_plane_path = str(Path(__file__).parent / "data" / "images" / "退出平面.png")
            exit_plane_result = self.detect_template(exit_plane_path)
            
            if exit_plane_result['detected']:
                logger.info("检测到退出平面按钮，执行点击操作")
                exit_plane_position = exit_plane_result['position']
                self.click_at_position(exit_plane_position)
            else:
                logger.warning("未检测到退出平面按钮，跳过这一步")
            
            # 延时一秒钟启动角色移动.Q脚本
            from src.core.script_manager import ScriptManager
            
            logger.info("延时一秒钟启动角色移动.Q脚本")
            time.sleep(1)
            
            # 创建ScriptManager实例并运行角色移动脚本
            script_manager = ScriptManager()
            logger.info("启动角色移动.Q脚本")
            result = script_manager.run_script("角色移动")
            logger.info(f"角色移动脚本执行结果: {result}")
            
            # 延时0.5秒后启动第一关.Q脚本
            logger.info("延时0.5秒启动第一关.Q脚本")
            time.sleep(0.5)
            
            logger.info("启动第一关.Q脚本")
            result_first_level = script_manager.run_script("第一关")
            logger.info(f"第一关脚本执行结果: {result_first_level}")
            
            # 开始持续检测"波次01完成"图片
            logger.info("开始持续检测\"波次01完成\"图片")
            wave_complete_image = PROJECT_ROOT / "data" / "images" / "波次01完成.png"
            
            detection_count = 0
            max_attempts = 600  # 最多尝试600次，约10分钟
            detection_interval = 1  # 检测间隔1秒
            
            while detection_count < max_attempts:
                try:
                    # 检测"波次01完成"图片
                    detection_result = self.detect_template(str(wave_complete_image))
                    detection_count += 1
                    
                    if detection_result['detected']:
                        logger.info(f"检测到\"波次01完成\"图片，置信度: {detection_result['confidence']}")
                        logger.info("启动第二关.Q脚本")
                        result_second_level = script_manager.run_script("第二关")
                        logger.info(f"第二关脚本执行结果: {result_second_level}")
                        
                        # 第二关脚本执行完成后，调用角色移动2.Q脚本
                        logger.info("第二关脚本执行完成，开始启动角色移动2.Q脚本")
                        
                        try:
                            # 列出所有加载的脚本，验证角色移动2脚本是否被加载
                            loaded_scripts = script_manager.list_scripts()
                            logger.info(f"已加载的脚本: {loaded_scripts}")
                            
                            if "角色移动2" in loaded_scripts:
                                logger.info("角色移动2脚本已成功加载")
                            else:
                                logger.warning("角色移动2脚本未加载，可能是文件不存在或格式错误")
                            
                            # 延时1秒，准备启动角色移动2.Q脚本
                            logger.info("延时1秒后启动角色移动2.Q脚本")
                            time.sleep(1)
                            
                            # 执行角色移动2.Q脚本
                            logger.info("启动角色移动2.Q脚本")
                            result_character_movement = script_manager.run_script("角色移动2")
                            logger.info(f"角色移动2脚本执行结果: {result_character_movement}")
                            
                            # 分析执行结果
                            if result_character_movement.get('success'):
                                logger.info("角色移动2脚本执行成功")
                            else:
                                logger.error(f"角色移动2脚本执行失败: {result_character_movement.get('message', '未知错误')}")
                        except Exception as e:
                            logger.error(f"执行角色移动2脚本时发生错误: {str(e)}")
                            result_character_movement = {'success': False, 'message': f'执行失败: {str(e)}'}
                        
                        # 开始持续检测"波次02完成"图片
                        logger.info("开始持续检测\"波次02完成\"图片")
                        wave_complete_image_02 = PROJECT_ROOT / "data" / "images" / "波次02完成.png"
                        
                        detection_count_02 = 0
                        max_attempts_02 = 1200  # 最多尝试1200次，约10分钟
                        detection_interval_02 = 0.5  # 检测间隔0.5秒
                        
                        while detection_count_02 < max_attempts_02:
                            try:
                                # 检测"波次02完成"图片
                                detection_result_02 = self.detect_template(str(wave_complete_image_02))
                                detection_count_02 += 1
                                
                                if detection_result_02['detected']:
                                    logger.info(f"检测到\"波次02完成\"图片，置信度: {detection_result_02['confidence']}")
                                    logger.info("准备启动第三关.Q脚本")
                                    
                                    try:
                                        # 列出所有加载的脚本，验证第三关脚本是否被加载
                                        loaded_scripts = script_manager.list_scripts()
                                        logger.info(f"已加载的脚本: {loaded_scripts}")
                                        
                                        if "第三关" in loaded_scripts:
                                            logger.info("第三关脚本已成功加载")
                                        else:
                                            logger.warning("第三关脚本未加载，可能是文件不存在或格式错误")
                                        
                                        # 延时1秒，模拟 test_third_level_call.py 中的调用前等待
                                        logger.info("延时1秒后启动第三关.Q脚本")
                                        time.sleep(1)
                                        
                                        # 执行第三关.Q脚本
                                        logger.info("启动第三关.Q脚本")
                                        result_third_level = script_manager.run_script("第三关")
                                        logger.info(f"第三关脚本执行结果: {result_third_level}")
                                        
                                        # 分析执行结果
                                        if result_third_level.get('success'):
                                            logger.info("第三关脚本执行成功")
                                        else:
                                            logger.error(f"第三关脚本执行失败: {result_third_level.get('message', '未知错误')}")
                                    except Exception as e:
                                        logger.error(f"执行第三关脚本时发生错误: {str(e)}")
                                        result_third_level = {'success': False, 'message': f'执行失败: {str(e)}'}
                                    
                                    # 第三关脚本执行完成后，检测商场升级入口
                                    logger.info("第三关脚本执行完成，开始检测商场升级入口")
                                    
                                    # 延时60秒
                                    logger.info("延时60秒后检测商场升级入口")
                                    time.sleep(60)
                                    
                                    # 检测商场升级入口.png
                                    mall_upgrade_entry_path = PROJECT_ROOT / "data" / "images" / "商场升级入口.png"
                                    mall_upgrade_entry_result = self.detect_template(str(mall_upgrade_entry_path))
                                    
                                    if mall_upgrade_entry_result['detected']:
                                        logger.info(f"检测到商场升级入口，置信度: {mall_upgrade_entry_result['confidence']}")
                                        
                                        # 点击商场升级入口
                                        mall_upgrade_entry_position = mall_upgrade_entry_result['position']
                                        click_result = self.click_at_position(mall_upgrade_entry_position)
                                        if click_result['success']:
                                            logger.info("已点击商场升级入口")
                                        else:
                                            logger.error(f"点击商场升级入口失败: {click_result['message']}")
                                        
                                        # 延时1秒
                                        time.sleep(1)
                                        
                                        # 检测防空火箭升级.png
                                        air_defense_upgrade_path = PROJECT_ROOT / "data" / "images" / "防空火箭升级.png"
                                        air_defense_upgrade_result = self.detect_template(str(air_defense_upgrade_path))
                                        
                                        if air_defense_upgrade_result['detected']:
                                            logger.info(f"检测到防空火箭升级，置信度: {air_defense_upgrade_result['confidence']}")
                                            
                                            # 点击防空火箭升级
                                            air_defense_upgrade_position = air_defense_upgrade_result['position']
                                            click_result = self.click_at_position(air_defense_upgrade_position)
                                            if click_result['success']:
                                                logger.info("已点击防空火箭升级")
                                            else:
                                                logger.error(f"点击防空火箭升级失败: {click_result['message']}")
                                        else:
                                            logger.info("未检测到防空火箭升级，跳过此步骤")
                                        
                                        # 点击退出商场.png
                                        exit_mall_path = PROJECT_ROOT / "data" / "images" / "退出商场.png"
                                        exit_mall_result = self.detect_template(str(exit_mall_path))
                                        
                                        if exit_mall_result['detected']:
                                            logger.info(f"检测到退出商场按钮，置信度: {exit_mall_result['confidence']}")
                                            
                                            # 点击退出商场
                                            exit_mall_position = exit_mall_result['position']
                                            click_result = self.click_at_position(exit_mall_position)
                                            if click_result['success']:
                                                logger.info("已点击退出商场")
                                            else:
                                                logger.error(f"点击退出商场失败: {click_result['message']}")
                                        else:
                                            logger.error("未检测到退出商场按钮")
                                    else:
                                        logger.info("未检测到商场升级入口，跳过商场操作")
                                    
                                    # 开始持续检测"波次03完成"图片
                                    logger.info("开始持续检测\"波次03完成\"图片")
                                    wave_complete_image_03 = PROJECT_ROOT / "data" / "images" / "波次03完成.png"
                                    
                                    detection_count_03 = 0
                                    max_attempts_03 = 1200  # 最多尝试1200次，约10分钟
                                    detection_interval_03 = 0.5  # 检测间隔0.5秒
                                    
                                    while detection_count_03 < max_attempts_03:
                                        try:
                                            # 检测"波次03完成"图片
                                            detection_result_03 = self.detect_template(str(wave_complete_image_03))
                                            detection_count_03 += 1
                                            
                                            if detection_result_03['detected']:
                                                logger.info(f"检测到\"波次03完成\"图片，置信度: {detection_result_03['confidence']}")
                                                
                                                # 识别"返回平面判断.png"，如果存在则点击"返回平面.png"
                                                logger.info("识别'返回平面判断.png'，如果存在则点击'返回平面.png'")
                                                return_plane_judge_image = PROJECT_ROOT / "data" / "images" / "返回平面判断.png"
                                                return_plane_image = PROJECT_ROOT / "data" / "images" / "返回平面.png"
                                                
                                                # 检测"返回平面判断.png"
                                                return_plane_judge_result = self.detect_template(str(return_plane_judge_image))
                                                
                                                if return_plane_judge_result['detected']:
                                                    logger.info(f"检测到'返回平面判断'图片，置信度: {return_plane_judge_result['confidence']}")
                                                    # 检测"返回平面.png"
                                                    return_plane_result = self.detect_template(str(return_plane_image))
                                                    
                                                    if return_plane_result['detected']:
                                                        logger.info(f"检测到'返回平面'图片，置信度: {return_plane_result['confidence']}")
                                                        # 点击"返回平面.png"
                                                        return_plane_position = return_plane_result['position']
                                                        click_result = self.click_at_position(return_plane_position)
                                                        logger.info(f"点击返回平面结果: {click_result['message']}")
                                                    else:
                                                        logger.info("未检测到'返回平面'图片，跳过点击操作")
                                                else:
                                                    logger.info("未检测到'返回平面判断'图片，跳过这一步")
                                                
                                                # 启动第四关.Q脚本
                                                logger.info("启动第四关.Q脚本")
                                                result_fourth_level = script_manager.run_script("第四关")
                                                logger.info(f"第四关脚本执行结果: {result_fourth_level}")
                                                
                                                # 延时1秒后识别并点按"结束准备时间.png"
                                                logger.info("延时1秒后识别并点按'结束准备时间.png'")
                                                time.sleep(1)
                                                
                                                # 识别"结束准备时间.png"图片
                                                end_prep_time_image = PROJECT_ROOT / "data" / "images" / "结束准备时间.png"
                                                end_prep_time_result = self.detect_template(str(end_prep_time_image))
                                                
                                                if end_prep_time_result['detected']:
                                                    logger.info(f"检测到'结束准备时间'图片，置信度: {end_prep_time_result['confidence']}")
                                                    # 点按该图片
                                                    end_prep_time_position = end_prep_time_result['position']
                                                    click_result = self.click_at_position(end_prep_time_position)
                                                    logger.info(f"点按结束准备时间结果: {click_result['message']}")
                                                else:
                                                    logger.info("未检测到'结束准备时间'图片，跳过点按操作")
                                                
                                                # 开始持续检测"波次04完成"图片
                                                logger.info("开始持续检测\"波次04完成\"图片")
                                                wave_complete_image_04 = PROJECT_ROOT / "data" / "images" / "波次04完成.png"
                                                
                                                detection_count_04 = 0
                                                max_attempts_04 = 1200  # 最多尝试1200次，约10分钟
                                                detection_interval_04 = 0.5  # 检测间隔0.5秒
                                                
                                                while detection_count_04 < max_attempts_04:
                                                    try:
                                                        # 检测"波次04完成"图片
                                                        detection_result_04 = self.detect_template(str(wave_complete_image_04))
                                                        detection_count_04 += 1
                                                        
                                                        if detection_result_04['detected']:
                                                            logger.info(f"检测到\"波次04完成\"图片，置信度: {detection_result_04['confidence']}")
                                                            logger.info("启动第五关.Q脚本")
                                                            result_fifth_level = script_manager.run_script("第五关")
                                                            logger.info(f"第五关脚本执行结果: {result_fifth_level}")
                                                            
                                                            # 开始持续检测"波次05完成"图片
                                                            logger.info("开始持续检测\"波次05完成\"图片")
                                                            wave_complete_image_05 = PROJECT_ROOT / "data" / "images" / "波次05完成.png"
                                                            
                                                            detection_count_05 = 0
                                                            max_attempts_05 = 600  # 最多尝试600次，约10分钟
                                                            detection_interval_05 = 1  # 检测间隔1秒
                                                            
                                                            while detection_count_05 < max_attempts_05:
                                                                try:
                                                                    # 检测"波次05完成"图片
                                                                    detection_result_05 = self.detect_template(str(wave_complete_image_05))
                                                                    detection_count_05 += 1
                                                                    
                                                                    if detection_result_05['detected']:
                                                                        logger.info(f"检测到\"波次05完成\"图片，置信度: {detection_result_05['confidence']}")
                                                                        logger.info("启动六七八.Q脚本")
                                                                        result_six_seven_eight_level = script_manager.run_script("六七八")
                                                                        logger.info(f"六七八脚本执行结果: {result_six_seven_eight_level}")
                                                                        
                                                                        # 开始持续检测"BOSS"图片
                                                                        logger.info("开始持续检测\"BOSS\"图片")
                                                                        boss_image = PROJECT_ROOT / "data" / "images" / "BOSS.png"
                                                                        
                                                                        detection_count_boss = 0
                                                                        max_attempts_boss = 1200  # 最多尝试1200次，约10分钟
                                                                        detection_interval_boss = 0.5  # 检测间隔0.5秒
                                                                        
                                                                        while detection_count_boss < max_attempts_boss:
                                                                            try:
                                                                                # 检测"BOSS"图片
                                                                                detection_result_boss = self.detect_template(str(boss_image))
                                                                                detection_count_boss += 1
                                                                                
                                                                                if detection_result_boss['detected']:
                                                                                    logger.info(f"检测到\"BOSS\"图片，置信度: {detection_result_boss['confidence']}")
                                                                                    logger.info("启动BOSS.Q脚本")
                                                                                    result_boss_level = script_manager.run_script("BOSS")
                                                                                    logger.info(f"BOSS脚本执行结果: {result_boss_level}")
                                                                                    break
                                                                                else:
                                                                                    if detection_count_boss % 10 == 0:
                                                                                        logger.info(f"第 {detection_count_boss} 次检测: 未检测到\"BOSS\"图片")
                                                                                    time.sleep(detection_interval_boss)
                                                                                    
                                                                            except Exception as e:
                                                                                logger.error(f"检测\"BOSS\"图片时出错: {str(e)}")
                                                                                time.sleep(detection_interval_boss)
                                                                        
                                                                        if detection_count_boss >= max_attempts_boss:
                                                                            logger.warning("达到最大检测次数，未检测到\"BOSS\"图片，停止检测")
                                                                        
                                                                        # 开始持续检测"胜利"图片
                                                                        logger.info("开始持续检测\"胜利\"图片")
                                                                        victory_image = PROJECT_ROOT / "data" / "images" / "胜利.png"
                                                                        
                                                                        detection_count_victory = 0
                                                                        max_attempts_victory = 600  # 最多尝试600次，约10分钟
                                                                        detection_interval_victory = 1  # 检测间隔1秒
                                                                        
                                                                        while detection_count_victory < max_attempts_victory:
                                                                            try:
                                                                                # 检测"胜利"图片
                                                                                detection_result_victory = self.detect_template(str(victory_image))
                                                                                detection_count_victory += 1
                                                                                
                                                                                if detection_result_victory['detected']:
                                                                                    logger.info(f"检测到\"胜利\"图片，置信度: {detection_result_victory['confidence']}")
                                                                                    logger.info("点击区域中间偏下位置")
                                                                                    
                                                                                    # 获取窗口区域，计算中间偏下位置
                                                                                    window_rect = self.window_manager.get_window_rect()
                                                                                    if window_rect:
                                                                                        # 计算中间偏下位置
                                                                                        center_x = window_rect[0] + (window_rect[2] // 2)
                                                                                        center_y = window_rect[1] + (window_rect[3] // 2) + (window_rect[3] // 4)  # 中间偏下
                                                                                        self.click_at_position((center_x, center_y))
                                                                                    
                                                                                    # 开始持续检测"结算1"图片
                                                                                    logger.info("开始持续检测\"结算1\"图片")
                                                                                    settlement1_image = PROJECT_ROOT / "data" / "images" / "结算1.png"
                                                                                    
                                                                                    detection_count_settlement1 = 0
                                                                                    max_attempts_settlement1 = 600  # 最多尝试600次，约10分钟
                                                                                    detection_interval_settlement1 = 1  # 检测间隔1秒
                                                                                    
                                                                                    while detection_count_settlement1 < max_attempts_settlement1:
                                                                                        try:
                                                                                            # 检测"结算1"图片
                                                                                            detection_result_settlement1 = self.detect_template(str(settlement1_image))
                                                                                            detection_count_settlement1 += 1
                                                                                            
                                                                                            if detection_result_settlement1['detected']:
                                                                                                logger.info(f"检测到\"结算1\"图片，置信度: {detection_result_settlement1['confidence']}")
                                                                                                logger.info("点击\"结算1\"图片")
                                                                                                
                                                                                                # 点击结算1图片位置
                                                                                                settlement1_position = detection_result_settlement1['position']
                                                                                                self.click_at_position(settlement1_position)
                                                                                                
                                                                                                # 开始持续检测"结算2"图片
                                                                                                logger.info("开始持续检测\"结算2\"图片")
                                                                                                settlement2_image = PROJECT_ROOT / "data" / "images" / "结算2.png"
                                                                                                
                                                                                                detection_count_settlement2 = 0
                                                                                                max_attempts_settlement2 = 600  # 最多尝试600次，约10分钟
                                                                                                detection_interval_settlement2 = 1  # 检测间隔1秒
                                                                                                
                                                                                                while detection_count_settlement2 < max_attempts_settlement2:
                                                                                                    try:
                                                                                                        # 检测"结算2"图片
                                                                                                        detection_result_settlement2 = self.detect_template(str(settlement2_image))
                                                                                                        detection_count_settlement2 += 1
                                                                                                        
                                                                                                        if detection_result_settlement2['detected']:
                                                                                                            logger.info(f"检测到\"结算2\"图片，置信度: {detection_result_settlement2['confidence']}")
                                                                                                            logger.info("点击\"结算2\"图片")
                                                                                                            
                                                                                                            # 点击结算2图片位置
                                                                                                            settlement2_position = detection_result_settlement2['position']
                                                                                                            self.click_at_position(settlement2_position)
                                                                                                            
                                                                                                            # 开始持续检测"开始按钮"图片
                                                                                                            logger.info("开始持续检测\"开始按钮\"图片")
                                                                                                            start_button_image = PROJECT_ROOT / "data" / "images" / "开始按钮.png"
                                                                                                            
                                                                                                            detection_count_start_button = 0
                                                                                                            max_attempts_start_button = 600  # 最多尝试600次，约10分钟
                                                                                                            detection_interval_start_button = 1  # 检测间隔1秒
                                                                                                            
                                                                                                            while detection_count_start_button < max_attempts_start_button:
                                                                                                                try:
                                                                                                                    # 检测"开始按钮"图片
                                                                                                                    detection_result_start_button = self.detect_template(str(start_button_image))
                                                                                                                    detection_count_start_button += 1
                                                                                                                    
                                                                                                                    if detection_result_start_button['detected']:
                                                                                                                        logger.info(f"检测到\"开始按钮\"图片，置信度: {detection_result_start_button['confidence']}")
                                                                                                                        logger.info("程序结束进程")
                                                                                                                        
                                                                                                                        # 调用stop_execution方法结束进程
                                                                                                                        self.stop_execution()
                                                                                                                        return {'success': True, 'message': '程序已完成所有操作并结束进程'}
                                                                                                                    else:
                                                                                                                        if detection_count_start_button % 10 == 0:
                                                                                                                            logger.info(f"第 {detection_count_start_button} 次检测: 未检测到\"开始按钮\"图片")
                                                                                                                        time.sleep(detection_interval_start_button)
                                                                                                                        
                                                                                                                except Exception as e:
                                                                                                                    logger.error(f"检测\"开始按钮\"图片时出错: {str(e)}")
                                                                                                                    time.sleep(detection_interval_start_button)
                                                                                                            
                                                                                                            if detection_count_start_button >= max_attempts_start_button:
                                                                                                                logger.warning("达到最大检测次数，未检测到\"开始按钮\"图片，停止检测")
                                                                                                            
                                                                                                            break
                                                                                                        else:
                                                                                                            if detection_count_settlement2 % 10 == 0:
                                                                                                                logger.info(f"第 {detection_count_settlement2} 次检测: 未检测到\"结算2\"图片")
                                                                                                            time.sleep(detection_interval_settlement2)
                                                                                                    
                                                                                                    except Exception as e:
                                                                                                        logger.error(f"检测\"结算2\"图片时出错: {str(e)}")
                                                                                                        time.sleep(detection_interval_settlement2)
                                                                                                
                                                                                                if detection_count_settlement2 >= max_attempts_settlement2:
                                                                                                    logger.warning("达到最大检测次数，未检测到\"结算2\"图片，停止检测")
                                                                                                
                                                                                                break
                                                                                        except Exception as e:
                                                                                            logger.error(f'检测"结算1"图片时出错: {str(e)}')
                                                                                            time.sleep(detection_interval_settlement1)
                                                                                        
                                                                                        if not detection_result_settlement1['detected']:
                                                                                            if detection_count_settlement1 % 10 == 0:
                                                                                                logger.info(f'第 {detection_count_settlement1} 次检测: 未检测到"结算1"图片')
                                                                                            time.sleep(detection_interval_settlement1)
                                                                                    
                                                                                    if detection_count_settlement1 >= max_attempts_settlement1:
                                                                                        logger.warning("达到最大检测次数，未检测到\"结算1\"图片，停止检测")
                                                                                    
                                                                                    break
                                                                                else:
                                                                                    if detection_count_victory % 10 == 0:
                                                                                        logger.info(f"第 {detection_count_victory} 次检测: 未检测到\"胜利\"图片")
                                                                                    time.sleep(detection_interval_victory)
                                                                                    
                                                                            except Exception as e:
                                                                                logger.error(f"检测\"胜利\"图片时出错: {str(e)}")
                                                                                time.sleep(detection_interval_victory)
                                                                        
                                                                        if detection_count_victory >= max_attempts_victory:
                                                                            logger.warning("达到最大检测次数，未检测到\"胜利\"图片，停止检测")
                                                                        
                                                                        break
                                                                    else:
                                                                        if detection_count_05 % 10 == 0:
                                                                            logger.info(f"第 {detection_count_05} 次检测: 未检测到\"波次05完成\"图片")
                                                                        time.sleep(detection_interval_05)
                                                                        
                                                                except Exception as e:
                                                                    logger.error(f"检测\"波次05完成\"图片时出错: {str(e)}")
                                                                    time.sleep(detection_interval_05)
                                                            
                                                            if detection_count_05 >= max_attempts_05:
                                                                logger.warning("达到最大检测次数，未检测到\"波次05完成\"图片，停止检测")
                                                        else:
                                                            if detection_count_04 % 10 == 0:
                                                                logger.info(f"第 {detection_count_04} 次检测: 未检测到\"波次04完成\"图片")
                                                            time.sleep(detection_interval_04)
                                                            
                                                    except Exception as e:
                                                        logger.error(f"检测\"波次04完成\"图片时出错: {str(e)}")
                                                        time.sleep(detection_interval_04)
                                                
                                                if detection_count_04 >= max_attempts_04:
                                                    logger.warning("达到最大检测次数，未检测到\"波次04完成\"图片，停止检测")
                                                
                                                break
                                            else:
                                                if detection_count_03 % 10 == 0:
                                                    logger.info(f"第 {detection_count_03} 次检测: 未检测到\"波次03完成\"图片")
                                                time.sleep(detection_interval_03)
                                                
                                        except Exception as e:
                                            logger.error(f"检测\"波次03完成\"图片时出错: {str(e)}")
                                            time.sleep(detection_interval_03)
                                    
                                    if detection_count_03 >= max_attempts_03:
                                        logger.warning("达到最大检测次数，未检测到\"波次03完成\"图片，停止检测")
                                    
                                    break
                                else:
                                    if detection_count_02 % 10 == 0:
                                        logger.info(f"第 {detection_count_02} 次检测: 未检测到\"波次02完成\"图片")
                                    time.sleep(detection_interval_02)
                                    
                            except Exception as e:
                                logger.error(f"检测\"波次02完成\"图片时出错: {str(e)}")
                                time.sleep(detection_interval_02)
                        
                        if detection_count_02 >= max_attempts_02:
                            logger.warning("达到最大检测次数，未检测到\"波次02完成\"图片，停止检测")
                        
                        break
                    else:
                        if detection_count % 10 == 0:
                            logger.info(f"第 {detection_count} 次检测: 未检测到\"波次01完成\"图片")
                        time.sleep(detection_interval)
                        
                except Exception as e:
                    logger.error(f"检测\"波次01完成\"图片时出错: {str(e)}")
                    time.sleep(detection_interval)
            
            if detection_count >= max_attempts:
                logger.warning("达到最大检测次数，未检测到\"波次01完成\"图片，停止检测")
            
            return {'success': True, 'message': '商场操作完成，已退出商场并点击退出平面按钮，且已启动角色移动脚本、第一关脚本、第二关脚本、第三关脚本、第四关脚本、第五关脚本、六七八脚本、BOSS脚本，并添加了胜利后处理逻辑'}
        
        except Exception as e:
            logger.error(f"处理商场操作失败: {str(e)}")
            return {'success': False, 'message': f'处理商场操作失败: {str(e)}'}

    def start_afk_detection(self):
        """
        开始检测挂机提示弹窗
        """
        logger.info("开始检测挂机提示弹窗")
        self.afk_detection_running = True
        self.afk_detection_thread = threading.Thread(target=self._detect_afk_popup, daemon=True)
        self.afk_detection_thread.start()
        return {'success': True, 'message': '挂机提示检测已启动'}
    
    def stop_afk_detection(self):
        """
        停止检测挂机提示弹窗
        """
        logger.info("停止检测挂机提示弹窗")
        self.afk_detection_running = False
        if self.afk_detection_thread:
            self.afk_detection_thread.join(timeout=2)
        return {'success': True, 'message': '挂机提示检测已停止'}
    
    def _detect_afk_popup(self):
        """
        持续检测挂机提示弹窗的后台线程函数
        """
        afk_popup_image = PROJECT_ROOT / "data" / "images" / "挂机提示.png"
        return_game_image = PROJECT_ROOT / "data" / "images" / "返回游戏.png"
        
        logger.info("挂机提示检测线程已启动")
        
        while self.afk_detection_running:
            try:
                # 检测挂机提示弹窗
                afk_result = self.detect_template(str(afk_popup_image))
                
                if afk_result['detected']:
                    logger.info(f"检测到挂机提示弹窗，置信度: {afk_result['confidence']}")
                    # 检测返回游戏按钮
                    return_game_result = self.detect_template(str(return_game_image))
                    
                    if return_game_result['detected']:
                        logger.info(f"检测到返回游戏按钮，置信度: {return_game_result['confidence']}")
                        # 点击返回游戏按钮
                        return_game_position = return_game_result['position']
                        click_result = self.click_at_position(return_game_position)
                        logger.info(f"点击返回游戏按钮结果: {click_result['message']}")
                    else:
                        logger.warning("未检测到返回游戏按钮")
                
                # 休眠后继续检测，避免CPU占用过高
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"检测挂机提示弹窗时出错: {str(e)}")
                # 出错后短暂休眠，避免无限循环报错
                time.sleep(1)
        
        logger.info("挂机提示检测线程已停止")
    
    def stop_execution(self):
        """
        停止执行
        """
        logger.info("停止执行")
        self.is_running = False
        self.afk_detection_running = False
        
        if self.afk_detection_thread:
            try:
                self.afk_detection_thread.join(timeout=2)
            except Exception as e:
                logger.error(f"等待挂机检测线程结束失败: {str(e)}")
        
        # 结束所有相关进程
        try:
            import os
            import psutil
            
            # 获取当前进程
            current_process = psutil.Process(os.getpid())
            
            # 获取当前进程的所有子进程
            children = current_process.children(recursive=True)
            
            # 结束所有子进程
            for child in children:
                try:
                    logger.info(f"结束子进程: {child.pid}")
                    child.terminate()
                    # 等待进程终止
                    child.wait(timeout=2)
                except Exception as e:
                    logger.error(f"结束子进程 {child.pid} 失败: {str(e)}")
            
            # 查找并结束与本项目相关的其他进程
            logger.info("查找并结束与项目相关的其他进程")
            
            # 查找所有Python进程，检查是否与本项目相关
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe' or proc.info['name'] == 'pythonw.exe':
                        cmdline = proc.info.get('cmdline', [])
                        # 检查命令行中是否包含本项目的路径或__pycache__
                        if cmdline:
                            cmdline_str = ' '.join(cmdline)
                            if '视觉脚本' in cmdline_str and '__pycache__' in cmdline_str:
                                logger.info(f"发现与项目相关的__pycache__进程: {proc.info['pid']}")
                                proc.terminate()
                                proc.wait(timeout=2)
                except Exception as e:
                    logger.error(f"检查进程 {proc.info.get('pid', 'unknown')} 失败: {str(e)}")
            
            # 结束所有相关进程后，确保清理所有资源
            logger.info("所有相关进程已结束")
        except ImportError as e:
            logger.warning(f"无法导入psutil库，可能无法结束所有子进程: {str(e)}")
        except Exception as e:
            logger.error(f"结束进程失败: {str(e)}")
        
        return {'success': True, 'message': '执行已停止，所有相关进程已结束'}


# 创建全局执行器实例
fzr_executor = FZRExecutor()


def get_executor():
    """
    获取执行器实例
    返回: FZRExecutor - 执行器实例
    """
    return fzr_executor


def main():
    """
    主函数，用于直接运行测试
    """
    logger.info("运行FZRzx主执行程序测试")
    
    # 设置测试参数
    fzr_executor.set_target_window("FZR塔防")
    fzr_executor.set_loop_count(1)
    
    # 开始执行
    result = fzr_executor.start_execution()
    logger.info(f"执行结果: {result}")
    print(f"执行结果: {result}")


if __name__ == "__main__":
    main()
