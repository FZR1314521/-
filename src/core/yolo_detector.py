from ultralytics import YOLO
import cv2
import numpy as np
from src.config.config import YOLO_MODEL_PATH, CONFIDENCE_THRESHOLD

class YoloDetector:
    def __init__(self, model_path=YOLO_MODEL_PATH, confidence_threshold=CONFIDENCE_THRESHOLD):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.screenshot_manager = None
        # 性能优化参数
        self.input_size = 480  # 输入图像大小，减小以提高速度
        self.max_det = 5  # 最大检测目标数量，减少以提高速度
        self.device = 'cpu'  # 设备选择，'cpu'或'cuda'
        self.fp16 = False  # 是否使用半精度推理
        self.agnostic_nms = True  # 是否使用类别无关的NMS
        
        # 初始化截图管理器
        from src.core.screenshot import ScreenshotManager
        self.screenshot_manager = ScreenshotManager()
        
        # 预加载模型
        self.load_model()
    
    def load_model(self):
        """
        加载YOLO模型
        返回: bool - 是否加载成功
        """
        try:
            self.model = YOLO(self.model_path)
            return True
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            return False
    
    def detect(self, image):
        """
        在图像中检测目标
        参数: image - 输入图像
        返回: list - 检测结果列表
        """
        if not self.model:
            if not self.load_model():
                return []
        
        try:
            # 使用性能优化参数执行检测
            results = self.model(
                image, 
                conf=self.confidence_threshold,
                imgsz=self.input_size,
                max_det=self.max_det,
                device=self.device,
                fp16=self.fp16,
                agnostic_nms=self.agnostic_nms
            )
            
            detections = []
            
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    class_id = box.cls[0].item()
                    class_name = result.names[int(class_id)]
                    
                    detections.append({
                        'class_id': int(class_id),
                        'class_name': class_name,
                        'confidence': confidence,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })
            
            return detections
        except Exception as e:
            print(f"检测失败: {str(e)}")
            return []
    
    def detect_from_window(self, window_rect):
        """
        从窗口区域检测目标
        参数: window_rect - 窗口矩形区域 (left, top, width, height)
        返回: list - 检测结果列表
        """
        if not window_rect:
            return []
        
        try:
            # 截图窗口区域
            image = self.screenshot_manager.capture_window(window_rect)
            if image is None:
                return []
            
            # 执行检测
            return self.detect(image)
        except Exception as e:
            print(f"窗口检测失败: {str(e)}")
            return []
    
    def benchmark(self, window_rect, iterations=5):
        """
        测试检测速度
        参数: window_rect - 窗口矩形区域
              iterations - 测试次数
        返回: dict - 性能测试结果
        """
        import time
        
        if not window_rect:
            return {'success': False, 'message': '窗口区域无效'}
        
        try:
            times = []
            total_detections = 0
            
            for i in range(iterations):
                start_time = time.time()
                detections = self.detect_from_window(window_rect)
                end_time = time.time()
                
                elapsed = end_time - start_time
                times.append(elapsed)
                total_detections += len(detections)
                
                print(f"迭代 {i+1}/{iterations}: {elapsed:.3f}秒, 检测到 {len(detections)} 个目标")
            
            # 计算统计信息
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            return {
                'success': True,
                'average_time': avg_time,
                'minimum_time': min_time,
                'maximum_time': max_time,
                'total_detections': total_detections,
                'within_threshold': avg_time < 0.5,
                'message': f'平均检测时间: {avg_time:.3f}秒, 是否在0.5秒内: {avg_time < 0.5}'
            }
        except Exception as e:
            return {'success': False, 'message': f'测试失败: {str(e)}'}
