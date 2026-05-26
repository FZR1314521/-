import time
import logging
from src.config.config import LOG_LEVEL, LOG_FORMAT, LOGS_DIR
from src.core.window_manager import WindowManager
from src.core.yolo_detector import YoloDetector
from src.core.screenshot import ScreenshotManager
from src.core.script_manager import ScriptManager

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOGS_DIR / "main.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FZRDefense:
    def __init__(self):
        self.window_manager = WindowManager()
        self.yolo_detector = YoloDetector()
        self.screenshot_manager = ScreenshotManager()
        self.script_manager = ScriptManager()
        self.running = False
    
    def start(self):
        """
        启动自动化脚本
        """
        logger.info("启动FZR塔防自动化脚本")
        self.running = True
        
        while self.running:
            try:
                # 检查窗口
                if not self.window_manager.find_window():
                    logger.warning("未找到目标窗口")
                    time.sleep(2)
                    continue
                
                # 激活窗口
                self.window_manager.activate_window()
                
                # 获取窗口区域
                window_rect = self.window_manager.get_window_rect()
                if not window_rect:
                    logger.warning("获取窗口区域失败")
                    time.sleep(2)
                    continue
                
                # 目标检测（使用优化后的方法）
                import time
                start_time = time.time()
                detections = self.yolo_detector.detect_from_window(window_rect)
                end_time = time.time()
                detection_time = end_time - start_time
                
                # 记录检测时间
                logger.info(f"检测时间: {detection_time:.3f}秒, 检测到 {len(detections)} 个目标")
                
                # 处理检测结果
                self.process_detections(detections)
                
                # 等待
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                logger.info("用户中断脚本")
                self.stop()
            except Exception as e:
                logger.error(f"脚本运行失败: {str(e)}")
                time.sleep(2)
    
    def process_detections(self, detections):
        """
        处理检测结果
        参数: detections - 检测结果列表
        """
        for detection in detections:
            class_name = detection['class_name']
            bbox = detection['bbox']
            
            logger.info(f"检测到目标: {class_name}, 位置: {bbox}")
            
            # 根据检测到的目标调用相应的脚本
            script_name = self.get_script_for_detection(class_name)
            if script_name:
                params = {
                    'class_name': class_name,
                    'bbox': bbox,
                    'timestamp': time.time()
                }
                result = self.script_manager.run_script(script_name, params)
                logger.info(f"脚本执行结果: {result}")
    
    def get_script_for_detection(self, class_name):
        """
        根据检测到的目标获取对应的脚本
        参数: class_name - 目标类别名称
        返回: str - 脚本名称
        """
        # 这里根据实际情况映射类别到脚本
        script_mapping = {
            # 'target_class': 'script_name'
        }
        return script_mapping.get(class_name)
    
    def stop(self):
        """
        停止自动化脚本
        """
        logger.info("停止FZR塔防自动化脚本")
        self.running = False


def main():
    """
    主函数
    """
    fzr_defense = FZRDefense()
    try:
        fzr_defense.start()
    except KeyboardInterrupt:
        fzr_defense.stop()


if __name__ == "__main__":
    main()
