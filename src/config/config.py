import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"

# 模型目录
MODELS_DIR = PROJECT_ROOT / "src" / "models"

# 脚本目录
SCRIPTS_DIR = PROJECT_ROOT / "src" / "scripts"

# 按键精灵脚本目录
Q_SCRIPTS_DIR = PROJECT_ROOT / "关卡脚本"

# 日志目录
LOGS_DIR = PROJECT_ROOT / "logs"

# 确保目录存在
for dir_path in [DATA_DIR, MODELS_DIR, SCRIPTS_DIR, Q_SCRIPTS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 窗口配置
WINDOW_TITLE = "手机投屏"

# YOLO模型配置
YOLO_MODEL_PATH = MODELS_DIR / "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.5

# 脚本配置
SCRIPT_TIMEOUT = 30  # 脚本执行超时时间（秒）

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 测试模式
TEST_MODE = False
