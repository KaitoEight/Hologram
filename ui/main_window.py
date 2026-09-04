"""
ui/main_window.py
-----------------
Cửa sổ chính (Main Application Window) kết nối tất cả các phân hệ:
1. UI Control Panel Sidebar (Quản lý hình học, cm, màu sắc).
2. OpenGL 3D Render Canvas (Pitch Black Hologram viewport).
3. Live Camera Preview (MediaPipe 21 Hand Landmarks & Touchless Pinch interaction).
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QStatusBar, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from graphics.gl_widget import HologramGLWidget
from ui.control_panel import ControlPanelWidget
from ui.camera_widget import CameraPreviewWidget
from vision.camera_thread import CameraThread


class HologramMainWindow(QMainWindow):
    """Cửa sổ ứng dụng 3D Hologram với MediaPipe Touchless Interaction."""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hologram 3D Generator & MediaPipe Touchless Control")
        self.resize(1366, 768)

        # Style sheet tổng thể cho ứng dụng
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0c10;
            }
            QStatusBar {
                background-color: #12141c;
                color: #00f0ff;
                font-weight: bold;
                border-top: 1px solid #2a2e3d;
            }
            QScrollArea {
                border: none;
                background-color: #12141c;
            }
        """)

        # Khởi tạo các Widget phân hệ chính
        self.gl_widget = HologramGLWidget(self)
        self.control_panel = ControlPanelWidget(self)
        self.camera_widget = CameraPreviewWidget(self)

        # QThread thu webcam & nhận diện bàn tay
        self.camera_thread = CameraThread(camera_source="http://192.168.1.28:4747/video", parent=self)

        self._setup_layout()
        self._connect_signals()

        # Khởi chạy Thread Webcam
        self.camera_thread.start()

    def _setup_layout(self):
        """Thiết lập bố cục giao diện (Splitter Layout)."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # ScrollArea chứa Bảng điều khiển thông số bên trái
        scroll_control = QScrollArea()
        scroll_control.setWidgetResizable(True)
        scroll_control.setWidget(self.control_panel)
        scroll_control.setMinimumWidth(340)
        scroll_control.setMaximumWidth(380)

        # Sidebar bên phải chứa Camera Preview Widget
        right_sidebar = QWidget()
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.addWidget(self.camera_widget)
        right_layout.addStretch()
        right_sidebar.setMinimumWidth(340)
        right_sidebar.setMaximumWidth(360)

        # Main Splitter phân chia (Left Controls | Center OpenGL | Right Webcam)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(scroll_control)
        splitter.addWidget(self.gl_widget)
        splitter.addWidget(right_sidebar)

        # Tỷ lệ kích thước mặc định: Controls (20%), OpenGL (60%), Camera (20%)
        splitter.setSizes([340, 700, 340])

        main_layout.addWidget(splitter)

        # Thanh trạng thái Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.lbl_status_info = QLabel("✨ Hologram Engine Active | Nền Đen Tuyền Pitch Black (#000000) Ready")
        self.status_bar.addWidget(self.lbl_status_info)

    def _connect_signals(self):
        """Tích hợp các tín hiệu (Signals & Slots) giữa các phân hệ."""
        # 1. Từ Control Panel tới OpenGL Widget
        self.control_panel.shape_changed.connect(self.gl_widget.set_shape)
        self.control_panel.dimension_changed.connect(self._on_dimension_changed)
        self.control_panel.scale_factor_changed.connect(self.gl_widget.set_scale_factor)
        self.control_panel.color_changed.connect(self.gl_widget.set_color)
        self.control_panel.wireframe_changed.connect(self.gl_widget.set_wireframe)
        self.control_panel.view_mode_changed.connect(self._on_view_mode_changed)
        self.control_panel.auto_rotate_changed.connect(lambda enable: setattr(self.gl_widget, 'auto_rotate', enable))
        self.control_panel.sensitivity_changed.connect(lambda sens: setattr(self.camera_thread.tracker, 'sensitivity', sens))
        self.control_panel.camera_source_changed.connect(self.camera_thread.set_camera_source)

        # 2. Từ Camera Thread tới Camera Widget & OpenGL Widget (Xử lý tương tác cử chỉ Pinch)
        self.camera_thread.frame_processed.connect(self._on_camera_frame_processed)
        self.camera_thread.camera_error.connect(self._on_camera_error)
        self.camera_thread.camera_connected.connect(lambda msg: self.lbl_status_info.setText(f"✨ {msg}"))

    def _on_dimension_changed(self, size_cm: float, height_cm: float):
        """Cập nhật kích thước thực tế cho đối tượng 3D hiện tại."""
        geom = self.gl_widget.get_current_geometry()
        
        if hasattr(geom, 'side_length_cm'):
            geom.side_length_cm = size_cm
        if hasattr(geom, 'base_size_cm'):
            geom.base_size_cm = size_cm
        if hasattr(geom, 'radius_cm'):
            geom.radius_cm = size_cm
        if hasattr(geom, 'height_cm'):
            geom.height_cm = height_cm
        if hasattr(geom, 'major_radius_cm'):
            geom.major_radius_cm = size_cm
            geom.minor_radius_cm = size_cm * 0.3

        self.gl_widget.update()

    def _on_view_mode_changed(self, mode: str):
        """Thay đổi chế độ xem Single View vs 4-View Hologram Pyramid."""
        self.gl_widget.view_mode = mode
        self.gl_widget.update()
        
        mode_str = "4-View Pyramid Hologram Cross" if mode == 'pyramid' else "Single 3D Preview"
        self.lbl_status_info.setText(f"🖥️ Đã chuyển chế độ: {mode_str}")

    def _on_camera_frame_processed(self, frame: np.ndarray, gesture_data: dict):
        """Slot nhận khung hình webcam & dữ liệu tương tác bàn tay từ QThread."""
        # 1. Cập nhật giao diện camera preview widget
        self.camera_widget.update_frame(frame, gesture_data)

        # 2. Nếu đang cử chỉ ZOOM PINCH (Ngón cái + Ngón giữa) -> Phóng to / Thu nhỏ
        if gesture_data.get('is_zoom_pinching', False):
            delta_zoom = gesture_data.get('delta_zoom', 0.0)
            if abs(delta_zoom) > 0.001:
                self.gl_widget.update_zoom(delta_zoom)

        # 3. Nếu đang cử chỉ ROTATE PINCH (Ngón cái + Ngón trỏ) -> Xoay Yaw & Pitch
        elif gesture_data.get('is_pinching', False):
            delta_yaw = gesture_data.get('delta_yaw', 0.0)
            delta_pitch = gesture_data.get('delta_pitch', 0.0)

            if abs(delta_yaw) > 0.001 or abs(delta_pitch) > 0.001:
                self.gl_widget.update_rotation(delta_yaw, delta_pitch)

    def _on_camera_error(self, err_msg: str):
        """Xử lý sự cố kết nối Webcam."""
        self.lbl_status_info.setText(f"⚠️ {err_msg}")

    def closeEvent(self, event):
        """Dừng Thread camera an toàn khi đóng ứng dụng."""
        self.camera_thread.stop()
        event.accept()
