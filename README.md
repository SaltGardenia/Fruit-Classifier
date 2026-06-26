# 🍎 Fruit Classifier

基于 CNN 卷积神经网络的水果分类检测系统，提供 PyQt5 图形界面。

## 🎯 功能

- 上传或拖拽水果图片进行识别
- 支持 5 类水果分类：**Apple** 🍎、**Banana** 🍌、**Mango** 🥭、**Orange** 🍊、**Pineapple** 🍍
- 显示识别结果与置信度
- 展示各类别概率分布柱状图

## 📂 项目结构

```
Fruit-Classifier/
├── fruit_gui.py          # PyQt5 图形界面主程序
├── requirements.txt      # Python 依赖
├── README.md
├── Data/
│   ├── train/            # 训练集
│   │   ├── Apple/
│   │   ├── Banana/
│   │   ├── Mango/
│   │   ├── Orange/
│   │   └── Pineapple/
│   └── test/             # 测试集
│       ├── Apple/
│       ├── Banana/
│       ├── Mango/
│       ├── Orange/
│       └── Pineapple/
├── Model/
│   └── model.h5          # 训练好的 CNN 模型
└── Notebook/
    └── main.ipynb        # 模型训练 Notebook
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行 GUI

```bash
python fruit_gui.py
```

或者使用 conda 环境：

```bash
conda activate fruit
python fruit_gui.py
```

### 3. 使用方法

1. 点击 **「选择图片」** 或直接将图片拖拽到虚线框内
2. 点击 **「开始检测」** 进行识别
3. 右侧面板显示识别结果与各类别概率
4. 点击 **「重置」** 清空并重新开始

## 🧠 模型

CNN 模型结构：
- 3 个卷积块（Conv2D + MaxPooling2D）
- 2 个全连接层 + Dropout 正则化
- Softmax 输出 5 类概率

输入尺寸：`128 × 128 × 3`（RGB 图像）
