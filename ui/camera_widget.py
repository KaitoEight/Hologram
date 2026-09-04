"""
ui/camera_widget.py
-------------------
Widget hiển thị luồng video từ Webcam kèm chỉ báo nhận diện bàn tay MediaPipe,
khoảng cách Pinch và trạng thái tương tác thời gian thực.
"""

import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt


class CameraPreviewWidget(QFrame):
    """Widget xem trước Webcam & Trạng thái Cử chỉ."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #12141c;
                border: 1px solid #2a2e3d;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Tiêu đề Widget
        self.title_label = QLabel("📹 Live Webcam & Hand Tracker")
        self.title_label.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 13px; border: none;")
        layout.addWidget(self.title_label)

        # Nhãn hiển thị khung hình OpenCV (Image Label)
        self.image_label = QLabel()
        self.image_label.setFixedSize(320, 240)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #333; background-color: #000; border-radius: 4px;")
        layout.addWidget(self.image_label)

        # Nhãn báo trạng thái cử chỉ
        self.status_label = QLabel("Trạng thái: Khởi động Webcam...")
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 12px; border: none;")
        layout.addWidget(self.status_label)

    def update_frame(self, frame_bgr: np.ndarray, gesture_data: dict):
        """Cập nhật ảnh khung hình và hiển thị dữ liệu cử chỉ."""
        # Chuyển đổi BGR OpenCV sang RGB QImage
        h, w, ch = frame_bgr.shape
        bytes_per_line = ch * w
        rgb_image = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        # Scale vừa vặn QLabel 320x240
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

        # Cập nhật nhãn trạng thái cử chỉ (Status Indicator)
        if not gesture_data.get('hand_detected', False):
            self.status_label.setText("🖐️ Chưa phát hiện bàn tay")
            self.status_label.setStyleSheet("color: #ff5555; font-size: 12px; border: none; font-weight: bold;")
        elif gesture_data.get('is_pinching', False):
            dist = gesture_data.get('pinch_distance', 0.0)
            self.status_label.setText(f"✊ ĐANG NẮM (Pinching) | Dist: {dist:.3f}")
            self.status_label.setStyleSheet("color: #00ff66; font-size: 12px; border: none; font-weight: bold;")
        else:
            dist = gesture_data.get('pinch_distance', 0.0)
            self.status_label.setText(f"🖐️ Bàn tay sẵn sàng (Xòe) | Dist: {dist:.3f}")
            self.status_label.setStyleSheet("color: #00e5ff; font-size: 12px; border: none;")
