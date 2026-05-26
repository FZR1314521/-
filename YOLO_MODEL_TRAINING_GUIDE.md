# YOLO模型训练指南

本指南将帮助您为FZR塔防项目训练自定义的YOLO模型，用于识别游戏中的特定目标。

## 目录

1. [环境准备](#环境准备)
2. [数据准备](#数据准备)
3. [模型训练](#模型训练)
4. [模型评估](#模型评估)
5. [模型导出](#模型导出)
6. [模型使用](#模型使用)
7. [性能优化](#性能优化)

## 环境准备

### 安装依赖

```bash
# 安装ultralytics库
pip install ultralytics

# 安装其他依赖
pip install opencv-python numpy matplotlib
```

### 下载预训练模型

YOLOv8提供了多个预训练模型，您可以根据需要选择：

- `yolov8n.pt` - 最小、最快的模型
- `yolov8s.pt` - 小型模型
- `yolov8m.pt` - 中型模型
- `yolov8l.pt` - 大型模型
- `yolov8x.pt` - 最大、最准确的模型

对于实时检测，建议使用 `yolov8n.pt` 或 `yolov8s.pt`。

## 数据准备

### 1. 收集数据

1. **截图收集**：在游戏中截取包含目标的截图
2. **标注**：使用标注工具（如LabelImg、Roboflow等）对目标进行标注

### 2. 数据标注格式

YOLO使用以下标注格式：

```
<class_id> <center_x> <center_y> <width> <height>
```

其中：
- `<class_id>` - 目标类别ID
- `<center_x>`, `<center_y>` - 目标中心点坐标（归一化到0-1）
- `<width>`, `<height>` - 目标宽高（归一化到0-1）

### 3. 数据集结构

创建以下目录结构：

```
dataset/
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
└── data.yaml
```

### 4. 配置文件

创建 `data.yaml` 配置文件：

```yaml
train: dataset/images/train/
val: dataset/images/val/

nc: 2  # 类别数量
names: ['enemy', 'tower']  # 类别名称
```

## 模型训练

### 基本训练命令

```bash
# 使用yolov8n预训练模型训练
yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=100 imgsz=640 batch=16

# 使用yolov8s预训练模型训练
yolo detect train data=dataset/data.yaml model=yolov8s.pt epochs=100 imgsz=640 batch=16
```

### 训练参数说明

- `epochs` - 训练轮数，建议设置为50-200
- `imgsz` - 输入图像大小，建议设置为640
- `batch` - 批次大小，根据GPU内存调整
- `patience` - 早停耐心值，默认10
- `optimizer` - 优化器，可选SGD、Adam、AdamW等
- `lr0` - 初始学习率

### 高级训练命令

```bash
# 自定义训练参数
yolo detect train \
    data=dataset/data.yaml \
    model=yolov8n.pt \
    epochs=100 \
    imgsz=640 \
    batch=16 \
    patience=20 \
    optimizer=AdamW \
    lr0=0.001 \
    save_period=10 \
    project=training_results \
    name=fzr_defense
```

## 模型评估

训练完成后，您可以评估模型的性能：

```bash
# 评估模型
yolo detect val data=dataset/data.yaml model=training_results/fzr_defense/weights/best.pt
```

### 评估指标

- **mAP@0.5** - IoU=0.5时的平均精度
- **mAP@0.5:0.95** - IoU从0.5到0.95的平均精度
- **precision** - 精确率
- **recall** - 召回率

## 模型导出

训练完成后，导出模型为PyTorch格式：

```bash
# 导出模型
yolo export model=training_results/fzr_defense/weights/best.pt format=pt
```

导出的模型将保存在 `training_results/fzr_defense/weights/` 目录中。

## 模型使用

### 在项目中使用自定义模型

1. **复制模型文件**：将导出的模型文件复制到 `src/models/` 目录

2. **修改配置**：在 `src/config/config.py` 中修改模型路径：

```python
# 修改为您的自定义模型路径
YOLO_MODEL_PATH = MODELS_DIR / "best.pt"
```

3. **更新类别名称**：确保您的模型能够正确识别类别名称

### 测试模型

使用 `tests/test_yolo_performance.py` 脚本测试模型性能：

```bash
python tests/test_yolo_performance.py
```

## 性能优化

### 模型优化

1. **模型量化**：减少模型精度以提高速度

```bash
# 导出为INT8量化模型
yolo export model=best.pt format=onnx int8
```

2. **模型剪枝**：减少模型大小和计算量

3. **模型蒸馏**：使用大型模型的知识来训练小型模型

### 推理优化

1. **减少输入大小**：降低 `input_size` 参数
2. **减少最大检测数量**：降低 `max_det` 参数
3. **使用GPU**：如果有GPU，设置 `device='cuda'`
4. **批量推理**：如果需要处理多个图像，使用批量推理

### 实际应用中的优化

1. **目标区域限制**：只在游戏中的特定区域进行检测
2. **检测频率**：根据游戏节奏调整检测频率
3. **缓存机制**：缓存检测结果，避免重复检测
4. **多线程处理**：使用多线程同时处理检测和键鼠操作

## 常见问题

### 数据标注问题

- **标注不准确**：确保标注框准确包围目标
- **类别不平衡**：确保每个类别的样本数量相对平衡
- **标注格式错误**：确保标注格式符合YOLO要求

### 训练问题

- **过拟合**：增加数据增强，减少模型复杂度
- **欠拟合**：增加训练轮数，使用更复杂的模型
- **训练崩溃**：检查数据格式，调整批次大小

### 推理问题

- **检测速度慢**：使用更小的模型，优化推理参数
- **检测准确率低**：增加训练数据，调整模型参数
- **误检率高**：提高置信度阈值，增加负样本

## 示例配置

### 快速训练配置

```bash
# 适合快速迭代的训练配置
yolo detect train \
    data=dataset/data.yaml \
    model=yolov8n.pt \
    epochs=50 \
    imgsz=480 \
    batch=32 \
    name=fzr_defense_fast
```

### 高精度训练配置

```bash
# 适合追求高精度的训练配置
yolo detect train \
    data=dataset/data.yaml \
    model=yolov8s.pt \
    epochs=200 \
    imgsz=640 \
    batch=16 \
    patience=30 \
    name=fzr_defense_accurate
```

## 总结

通过本指南，您应该能够：

1. 准备用于训练的数据集
2. 训练自定义的YOLO模型
3. 评估模型性能
4. 导出和使用训练好的模型
5. 优化模型性能以满足实时检测需求

训练好的模型将能够在游戏中实时识别特定目标，并触发相应的键鼠操作，为FZR塔防游戏提供自动化支持。

## 参考资源

- [Ultralytics YOLOv8文档](https://docs.ultralytics.com/)
- [YOLOv8 GitHub仓库](https://github.com/ultralytics/ultralytics)
- [LabelImg标注工具](https://github.com/HumanSignal/labelImg)
- [Roboflow数据标注平台](https://roboflow.com/)
