"""
Fruit Classifier GUI - PyQt5
基于训练好的CNN模型，通过PyQt5实现水果图片分类检测
"""

import sys
import os
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QFrame,
    QMessageBox, QSizePolicy, QTextBrowser,
)
from PyQt5.QtGui import QPixmap, QFont, QImage, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt
from tensorflow import keras


# =============================================================================
# 样式常量
# =============================================================================

FONT_FAMILY = "Microsoft YaHei UI"

STYLE_DROP_ZONE = """
    QLabel {
        border: 3px dashed #c0c0c0;
        border-radius: 14px;
        background-color: #f5f6fa;
        color: #95a5a6;
        font-size: 15px;
    }
"""

STYLE_DROP_ZONE_HOVER = """
    QLabel {
        border: 3px dashed #27ae60;
        border-radius: 14px;
        background-color: #eafaf1;
        color: #27ae60;
        font-size: 15px;
    }
"""

STYLE_DROP_ZONE_ACTIVE = """
    QLabel {
        border: 3px solid #3498db;
        border-radius: 14px;
        background-color: #ffffff;
    }
"""

STYLE_BTN_BLUE = """
    QPushButton {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        padding: 9px 18px;
    }
    QPushButton:hover {
        background-color: #2e86c1;
    }
    QPushButton:pressed {
        background-color: #2874a6;
    }
"""

STYLE_BTN_GREEN = """
    QPushButton {
        background-color: #27ae60;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        padding: 9px 18px;
    }
    QPushButton:hover {
        background-color: #229954;
    }
    QPushButton:pressed {
        background-color: #1e8449;
    }
    QPushButton:disabled {
        background-color: #d5dbdb;
        color: #aab7b8;
    }
"""

STYLE_BTN_RED = """
    QPushButton {
        background-color: #e74c3c;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        padding: 9px 18px;
    }
    QPushButton:hover {
        background-color: #d63031;
    }
    QPushButton:pressed {
        background-color: #c0392b;
    }
"""

STYLE_RESULT_FRAME = """
    QFrame {
        background-color: #fef9e7;
        border: 2px solid #f9e79f;
        border-radius: 14px;
        padding: 16px;
    }
"""

STYLE_RESULT_TITLE = """
    color: #2c3e50;
    padding-bottom: 4px;
"""

STYLE_SEPARATOR = """
    QFrame {
        border: none;
        border-top: 2px solid #f9e79f;
    }
"""

STYLE_PLACEHOLDER = """
    color: #95a5a6;
    font-size: 14px;
"""


# =============================================================================
# 可拖放图片的标签
# =============================================================================

class DropableLabel(QLabel):
    """支持拖放图片的QLabel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(360, 340)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(STYLE_DROP_ZONE)
        self._show_placeholder()

    def _show_placeholder(self):
        self.setText("📁 拖放图片到这里\n或点击下方按钮选择")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(STYLE_DROP_ZONE_HOVER)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(STYLE_DROP_ZONE if not self.pixmap() else STYLE_DROP_ZONE_ACTIVE)

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.parent().load_image(file_path)
                break
        self.setStyleSheet(STYLE_DROP_ZONE if not self.pixmap() else STYLE_DROP_ZONE_ACTIVE)


# =============================================================================
# 概率柱状图生成
# =============================================================================

def render_probability_bars(predictions, labels, pred_class):
    """生成概率柱状图的 HTML"""
    rows = ""
    for i, name in labels.items():
        prob = float(predictions[0][i]) * 100
        bar_pct = max(prob, 1.5)
        is_pred = i == pred_class
        bar_color = "#27ae60" if is_pred else "#bdc3c7"
        name_color = "#2c3e50" if is_pred else "#7f8c8d"
        name_bold = "font-weight: bold;" if is_pred else ""

        rows += (
            f'<div style="display: flex; align-items: center; margin: 5px 0;">'
            f'  <span style="width: 80px; font-size: 13px; '
            f'color: {name_color}; {name_bold}">{name}</span>'
            f'  <div style="flex: 1; background-color: #eaecee; border-radius: 5px; '
            f'height: 20px; overflow: hidden;">'
            f'    <div style="width: {bar_pct}%; background-color: {bar_color}; '
            f'height: 20px; border-radius: 5px; '
            f'text-align: right; line-height: 20px; padding-right: 5px; '
            f'font-size: 11px; color: white; font-weight: bold;">'
            f'{prob:.1f}%</div>'
            f'  </div>'
            f'</div>'
        )

    return f'<div style="font-family: {FONT_FAMILY}, sans-serif;">{rows}</div>'


# =============================================================================
# 主窗口
# =============================================================================

class FruitClassifierGUI(QWidget):
    """水果分类器主窗口"""

    def __init__(self):
        super().__init__()
        self.image_path = None
        self.model = None
        self.labels = {0: "Apple", 1: "Banana", 2: "Mango", 3: "Orange", 4: "Pineapple"}
        self.label_emoji = {
            "Apple": "🍎",
            "Banana": "🍌",
            "Mango": "🥭",
            "Orange": "🍊",
            "Pineapple": "🍍",
        }
        self.init_ui()
        self.load_model()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🍎 水果分类检测系统")
        self.setMinimumSize(860, 640)
        self.resize(1300, 850)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #ffffff;
                font-family: '{FONT_FAMILY}', 'Segoe UI', Arial, sans-serif;
            }}
        """)

        # ===== 主垂直布局 =====
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 18, 28, 0)
        main_layout.setSpacing(0)

        # ---------- 标题区域 ----------
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = QLabel("🍎  水果分类检测器")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(FONT_FAMILY, 22, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title_layout.addWidget(title)

        subtitle = QLabel("Apple  🍎  ·  Banana  🍌  ·  Mango  🥭  ·  Orange  🍊  ·  Pineapple  🍍")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont(FONT_FAMILY, 11))
        subtitle.setStyleSheet("color: #95a5a6; margin-bottom: 4px;")
        title_layout.addWidget(subtitle)

        main_layout.addLayout(title_layout)

        # ---------- 间距 ----------
        main_layout.addSpacing(10)

        # ---------- 中间主体（左图 + 右结果） ----------
        center_layout = QHBoxLayout()
        center_layout.setSpacing(22)

        # -- 左侧：图片 + 按钮 --
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)

        self.image_label = DropableLabel(self)
        left_layout.addWidget(self.image_label, stretch=1)

        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.select_btn = QPushButton("📂  选择图片")
        self.select_btn.setMinimumHeight(44)
        self.select_btn.setCursor(Qt.PointingHandCursor)
        self.select_btn.setStyleSheet(STYLE_BTN_BLUE)
        self.select_btn.clicked.connect(self.select_image)
        btn_layout.addWidget(self.select_btn)

        self.classify_btn = QPushButton("🔍  开始检测")
        self.classify_btn.setMinimumHeight(44)
        self.classify_btn.setCursor(Qt.PointingHandCursor)
        self.classify_btn.setEnabled(False)
        self.classify_btn.setStyleSheet(STYLE_BTN_GREEN)
        self.classify_btn.clicked.connect(self.classify_image)
        btn_layout.addWidget(self.classify_btn)

        self.reset_btn = QPushButton("🔄  重置")
        self.reset_btn.setMinimumHeight(44)
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.setStyleSheet(STYLE_BTN_RED)
        self.reset_btn.clicked.connect(self.reset_ui)
        btn_layout.addWidget(self.reset_btn)

        left_layout.addLayout(btn_layout)
        center_layout.addLayout(left_layout, stretch=5)

        # -- 右侧：检测结果 --
        self.result_frame = QFrame()
        self.result_frame.setFrameShape(QFrame.StyledPanel)
        self.result_frame.setStyleSheet(STYLE_RESULT_FRAME)
        self.result_frame.setMinimumWidth(320)
        self.result_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setContentsMargins(10, 6, 10, 6)
        result_layout.setSpacing(8)

        # 结果标题
        self.result_title = QLabel("📊  检测结果")
        self.result_title.setAlignment(Qt.AlignCenter)
        self.result_title.setFont(QFont(FONT_FAMILY, 16, QFont.Bold))
        self.result_title.setStyleSheet(STYLE_RESULT_TITLE)
        result_layout.addWidget(self.result_title)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(STYLE_SEPARATOR)
        sep.setFixedHeight(4)
        result_layout.addWidget(sep)

        # 结果内容（QTextBrowser 正确支持复杂 HTML 高度计算）
        self.result_text = QTextBrowser()
        self.result_text.setAlignment(Qt.AlignCenter)
        self.result_text.setFont(QFont(FONT_FAMILY, 13))
        self.result_text.setStyleSheet(STYLE_PLACEHOLDER + """
            QTextBrowser {
                background-color: transparent;
                border: none;
            }
        """)
        self.result_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_text.setOpenExternalLinks(False)
        self.result_text.setPlainText("请先选择水果图片\n然后点击「开始检测」")
        result_layout.addWidget(self.result_text, stretch=1)

        center_layout.addWidget(self.result_frame, stretch=4)
        main_layout.addLayout(center_layout, stretch=1)

        # ---------- 底部状态栏 ----------
        self.status_label = QLabel("⏳  正在加载模型 ...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(32)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border-top: 1px solid #eaecee;
                color: #27ae60;
                font-size: 12px;
                padding: 6px 0;
            }
        """)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    # ------------------------------------------------------------------
    # 模型加载
    # ------------------------------------------------------------------

    def load_model(self):
        """加载训练好的模型"""
        model_path = os.path.join(os.path.dirname(__file__), "Model", "model.h5")
        try:
            self.model = keras.models.load_model(model_path)
            self.status_label.setText("✅  模型加载成功  ·  就绪")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #f0faf0;
                    border-top: 1px solid #d5f5e3;
                    color: #27ae60;
                    font-size: 12px;
                    padding: 6px 0;
                }
            """)
        except Exception as e:
            self.status_label.setText(f"❌  模型加载失败: {str(e)}")
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #fdedec;
                    border-top: 1px solid #f5b7b1;
                    color: #e74c3c;
                    font-size: 12px;
                    padding: 6px 0;
                }
            """)

    # ------------------------------------------------------------------
    # 选择 / 加载图片
    # ------------------------------------------------------------------

    def select_image(self):
        """打开文件对话框选择图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择水果图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif)"
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """加载并显示图片"""
        try:
            pil_img = Image.open(file_path).convert("RGB")
            data = pil_img.tobytes("raw", "RGB")
            qimage = QImage(data, pil_img.width, pil_img.height,
                            pil_img.width * 3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
        except Exception:
            pixmap = QPixmap(file_path)

        if pixmap.isNull():
            self.image_path = None
            QMessageBox.warning(self, "图片加载失败", f"无法加载图片:\n{file_path}")
            return

        self.image_path = file_path

        # 根据标签当前可用尺寸等比例缩放
        avail_w = self.image_label.width() - 12
        avail_h = self.image_label.height() - 12
        scaled = pixmap.scaled(
            max(avail_w, 200), max(avail_h, 200),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        self.image_label.setStyleSheet(STYLE_DROP_ZONE_ACTIVE)

        self.classify_btn.setEnabled(True)
        self._show_result_placeholder("👆  点击「开始检测」识别水果")

    # ------------------------------------------------------------------
    # 分类检测
    # ------------------------------------------------------------------

    def classify_image(self):
        """执行分类检测"""
        if self.model is None:
            QMessageBox.critical(self, "错误", "模型未加载，无法进行分类！")
            return

        if not self.image_path:
            return

        try:
            # 预处理
            img = Image.open(self.image_path).convert("RGB")
            img_resized = img.resize((128, 128))
            img_array = np.array(img_resized, dtype=np.float32) / 255.0

            # 预测
            predictions = self.model.predict(img_array[np.newaxis, ...], verbose=0)
            pred_class = int(np.argmax(predictions[0]))
            confidence = float(np.max(predictions[0])) * 100
            fruit_name = self.labels[pred_class]
            emoji = self.label_emoji.get(fruit_name, "")

            # 更新标题
            self.result_title.setText("🎯  检测结果")

            # 结果 HTML
            result_html = (
                f'<div style="text-align: center; font-family: {FONT_FAMILY}, sans-serif;">'
                f'  <div style="font-size: 48px; line-height: 1.2;">{emoji}</div>'
                f'  <div style="font-size: 24px; font-weight: bold; color: #2c3e50; '
                f'margin: 4px 0 2px 0;">{fruit_name}</div>'
                f'  <div style="font-size: 16px; color: #27ae60; font-weight: bold; '
                f'margin-bottom: 6px;">置信度  {confidence:.2f}%</div>'
                f'  <hr style="border: none; border-top: 2px solid #f9e79f; '
                f'margin: 8px 0;">'
                f'  <div style="font-size: 13px; color: #7f8c8d; margin-bottom: 4px;">'
                f'各类别概率分布</div>'
                f'{render_probability_bars(predictions, self.labels, pred_class)}'
                f'</div>'
            )

            self.result_text.setHtml(result_html)

        except Exception as e:
            QMessageBox.warning(self, "检测失败", f"图片处理出错:\n{str(e)}")

    # ------------------------------------------------------------------
    # 重置
    # ------------------------------------------------------------------

    def reset_ui(self):
        """重置界面"""
        self.image_path = None
        self.classify_btn.setEnabled(False)
        self.image_label.setPixmap(QPixmap())
        self.image_label.setStyleSheet(STYLE_DROP_ZONE)
        self.image_label._show_placeholder()
        self.result_title.setText("📊  检测结果")
        self._show_result_placeholder("请先选择水果图片\n然后点击「开始检测」")

    def _show_result_placeholder(self, text):
        """将结果区域设为纯文本占位"""
        self.result_text.setPlainText(text)
        self.result_text.setAlignment(Qt.AlignCenter)


# =============================================================================
# 入口
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont(FONT_FAMILY, 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    window = FruitClassifierGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
