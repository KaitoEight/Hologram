"""
ui/control_panel.py
-------------------
Bảng điều khiển các thông số của ứng dụng 3D Hologram:
- Chọn loại hình học 3D.
- Nhập thông số thực tế tính bằng cm (chiều dài cạnh, bán kính, chiều cao).
- Tỷ lệ quy đổi (Scale factor).
- Màu sắc, độ trong suốt (Alpha slider), chế độ wireframe.
- Chọn chế độ hiển thị 1 View vs 4-View Pyramid Hologram Cross.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QComboBox,
    QDoubleSpinBox, QSlider, QCheckBox, QPushButton, QColorDialog, QRadioButton, QButtonGroup, QLineEdit
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal, Qt


class ControlPanelWidget(QWidget):
    """Bảng điều khiển thông số thiết lập Hologram."""

    shape_changed = pyqtSignal(str)
    dimension_changed = pyqtSignal(float, float)  # (size_cm, height_cm)
    scale_factor_changed = pyqtSignal(float)
    color_changed = pyqtSignal(float, float, float, float)  # (r, g, b, a)
    wireframe_changed = pyqtSignal(bool)
    view_mode_changed = pyqtSignal(str)  # 'single' hoặc 'pyramid'
    auto_rotate_changed = pyqtSignal(bool)
    sensitivity_changed = pyqtSignal(float)
    camera_source_changed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_r = 0.0
        self.current_g = 0.9
        self.current_b = 1.0
        self.current_a = 0.95

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # Apply dark aesthetic stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #12141c;
                color: #e0e6ed;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #2a2e3d;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                font-size: 13px;
                color: #00f0ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                font-size: 12px;
                color: #c0c6d0;
            }
            QComboBox, QDoubleSpinBox {
                background-color: #1b1e2b;
                border: 1px solid #33384a;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QPushButton {
                background-color: #1e2436;
                border: 1px solid #3a4259;
                border-radius: 4px;
                padding: 6px 12px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2b334d;
                border-color: #00f0ff;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #1b1e2b;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #00f0ff;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
            QCheckBox, QRadioButton {
                font-size: 12px;
            }
        """)

        # -------------------------------------------------------------
        # 1. Chọn loại Hình học (3D Geometries)
        # -------------------------------------------------------------
        group_shape = QGroupBox("🔷 1. Chọn khối hình 3D (3D Geometry)")
        layout_shape = QVBoxLayout()

        self.combo_shape = QComboBox()
        self.combo_shape.addItem("📦 Hình Lập Phương (Cube)", "cube")
        self.combo_shape.addItem("🔺 Hình Chóp (Pyramid)", "pyramid")
        self.combo_shape.addItem("⚽ Khối Cầu (Sphere)", "sphere")
        self.combo_shape.addItem("🛢️ Hình Trụ (Cylinder)", "cylinder")
        self.combo_shape.addItem("🍩 Hình Xuyến (Torus)", "torus")
        self.combo_shape.currentIndexChanged.connect(self._on_shape_changed)
        layout_shape.addWidget(self.combo_shape)

        group_shape.setLayout(layout_shape)
        layout.addWidget(group_shape)

        # -------------------------------------------------------------
        # 2. Nhập thông số thực tế (Kích thước cm)
        # -------------------------------------------------------------
        group_dim = QGroupBox("📏 2. Thông số kích thước thực tế (cm)")
        layout_dim = QVBoxLayout()

        # Cạnh / Bán kính (cm)
        h_size = QHBoxLayout()
        self.lbl_size = QLabel("Cạnh / Bán kính (x cm):")
        self.spin_size = QDoubleSpinBox()
        self.spin_size.setRange(1.0, 50.0)
        self.spin_size.setValue(10.0)
        self.spin_size.setSingleStep(0.5)
        self.spin_size.setSuffix(" cm")
        self.spin_size.valueChanged.connect(self._on_dimension_changed)
        h_size.addWidget(self.lbl_size)
        h_size.addWidget(self.spin_size)
        layout_dim.addLayout(h_size)

        # Chiều cao (cm) (dành cho Chóp & Trụ)
        h_height = QHBoxLayout()
        self.lbl_height = QLabel("Chiều cao (y cm):")
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setRange(1.0, 50.0)
        self.spin_height.setValue(12.0)
        self.spin_height.setSingleStep(0.5)
        self.spin_height.setSuffix(" cm")
        self.spin_height.valueChanged.connect(self._on_dimension_changed)
        h_height.addWidget(self.lbl_height)
        h_height.addWidget(self.spin_height)
        layout_dim.addLayout(h_height)

        # Tỷ lệ quy đổi Scale (1 cm = N units)
        h_scale = QHBoxLayout()
        h_scale.addWidget(QLabel("Tỷ lệ Scale (cm ➜ 3D Units):"))
        self.slider_scale = QSlider(Qt.Orientation.Horizontal)
        self.slider_scale.setRange(5, 50)  # 0.05 đến 0.50
        self.slider_scale.setValue(20)      # Mặc định 0.20
        self.slider_scale.valueChanged.connect(self._on_scale_slider_changed)
        self.lbl_scale_val = QLabel("0.20")
        h_scale.addWidget(self.slider_scale)
        h_scale.addWidget(self.lbl_scale_val)
        layout_dim.addLayout(h_scale)

        group_dim.setLayout(layout_dim)
        layout.addWidget(group_dim)

        # -------------------------------------------------------------
        # 3. Màu sắc & Độ trong suốt (Material & Transparency)
        # -------------------------------------------------------------
        group_mat = QGroupBox("🎨 3. Màu sắc & Độ trong suốt (Alpha)")
        layout_mat = QVBoxLayout()

        # Nút chọn màu Custom
        h_color = QHBoxLayout()
        self.btn_color_picker = QPushButton("🎨 Chọn Màu (Color Picker)")
        self.btn_color_picker.clicked.connect(self._open_color_dialog)
        
        self.lbl_color_swatch = QLabel()
        self.lbl_color_swatch.setFixedSize(30, 24)
        self.lbl_color_swatch.setStyleSheet("background-color: #00e5ff; border-radius: 4px; border: 1px solid #fff;")
        
        h_color.addWidget(self.btn_color_picker)
        h_color.addWidget(self.lbl_color_swatch)
        layout_mat.addLayout(h_color)

        # Bảng màu Preset Hologram Nổi bật
        lbl_preset = QLabel("Bảng màu Hologram Preset:")
        layout_mat.addWidget(lbl_preset)
        
        h_presets = QHBoxLayout()
        presets = [
            ("Cyan", "#00f0ff", (0.0, 0.94, 1.0)),
            ("Neon Green", "#00ff66", (0.0, 1.0, 0.4)),
            ("Gold", "#ffcc00", (1.0, 0.8, 0.0)),
            ("Magenta", "#ff007f", (1.0, 0.0, 0.5)),
            ("Ice Blue", "#70b5ff", (0.44, 0.71, 1.0)),
            ("White", "#ffffff", (1.0, 1.0, 1.0))
        ]
        for name, hex_code, (r, g, b) in presets:
            btn_p = QPushButton()
            btn_p.setToolTip(name)
            btn_p.setStyleSheet(f"background-color: {hex_code}; border-radius: 4px; border: 1px solid #444; max-width: 28px; max-height: 24px;")
            btn_p.clicked.connect(lambda checked, red=r, green=g, blue=b, hx=hex_code: self._set_preset_color(red, green, blue, hx))
            h_presets.addWidget(btn_p)
        layout_mat.addLayout(h_presets)

        # Alpha Transparency Slider
        h_alpha = QHBoxLayout()
        h_alpha.addWidget(QLabel("Độ trong suốt (Alpha):"))
        self.slider_alpha = QSlider(Qt.Orientation.Horizontal)
        self.slider_alpha.setRange(10, 100)
        self.slider_alpha.setValue(95)
        self.slider_alpha.valueChanged.connect(self._on_alpha_changed)
        self.lbl_alpha_val = QLabel("95%")
        h_alpha.addWidget(self.slider_alpha)
        h_alpha.addWidget(self.lbl_alpha_val)
        layout_mat.addLayout(h_alpha)

        # Wireframe Checkbox
        self.chk_wireframe = QCheckBox("Chế độ Khung dây (Wireframe)")
        self.chk_wireframe.toggled.connect(self.wireframe_changed.emit)
        layout_mat.addWidget(self.chk_wireframe)

        group_mat.setLayout(layout_mat)
        layout.addWidget(group_mat)

        # -------------------------------------------------------------
        # 4. Chế độ hiển thị Hologram & Tự động xoay
        # -------------------------------------------------------------
        group_view = QGroupBox("🖥️ 4. Định dạng Hiển thị Hologram")
        layout_view = QVBoxLayout()

        self.btn_group_view = QButtonGroup(self)
        self.radio_4view = QRadioButton("✨ 4-View Pyramid Cross (Hologram 4 mặt)")
        self.radio_4view.setChecked(True)
        self.radio_single = QRadioButton("👁️ Single View (Xem thử 1 góc nhìn)")
        
        self.btn_group_view.addButton(self.radio_4view, 1)
        self.btn_group_view.addButton(self.radio_single, 2)
        self.btn_group_view.idToggled.connect(self._on_view_mode_toggled)

        layout_view.addWidget(self.radio_4view)
        layout_view.addWidget(self.radio_single)

        # Auto rotate
        self.chk_auto_rotate = QCheckBox("🔄 Tự động xoay 360°")
        self.chk_auto_rotate.toggled.connect(self.auto_rotate_changed.emit)
        layout_view.addWidget(self.chk_auto_rotate)

        # Hand Gesture Sensitivity
        h_sens = QHBoxLayout()
        h_sens.addWidget(QLabel("Độ nhạy cử chỉ tay:"))
        self.slider_sens = QSlider(Qt.Orientation.Horizontal)
        self.slider_sens.setRange(100, 500)
        self.slider_sens.setValue(250)
        self.slider_sens.valueChanged.connect(lambda v: self.sensitivity_changed.emit(float(v)))
        h_sens.addWidget(self.slider_sens)
        layout_view.addLayout(h_sens)

        group_view.setLayout(layout_view)
        layout.addWidget(group_view)

        # -------------------------------------------------------------
        # 5. Cấu hình Camera & DroidCam / IP Stream
        # -------------------------------------------------------------
        group_cam = QGroupBox("📱 5. Thấu kính Camera & DroidCam Phone")
        layout_cam = QVBoxLayout()

        self.combo_camera = QComboBox()
        self.combo_camera.addItem("📱 DroidCam / Phone IP Camera", "droidcam")
        self.combo_camera.addItem("📷 Camera 0 (Laptop/USB Webcam)", 0)
        self.combo_camera.addItem("📷 Camera 1", 1)
        self.combo_camera.addItem("📷 Camera 2", 2)
        self.combo_camera.addItem("✨ Mô phỏng Cử chỉ Bàn tay (Virtual Demo)", -1)
        self.combo_camera.currentIndexChanged.connect(self._on_camera_source_changed)

        layout_cam.addWidget(self.combo_camera)

        # DroidCam IP URL Input Widget Group
        self.widget_droidcam_input = QWidget()
        layout_droid = QVBoxLayout(self.widget_droidcam_input)
        layout_droid.setContentsMargins(0, 4, 0, 0)

        lbl_url = QLabel("Đường dẫn DroidCam / IP Stream URL:")
        lbl_url.setStyleSheet("font-size: 11px; color: #00e5ff;")
        layout_droid.addWidget(lbl_url)

        self.edit_droidcam_url = QLineEdit()
        self.edit_droidcam_url.setText("http://192.168.1.28:4747/video")
        self.edit_droidcam_url.setPlaceholderText("http://192.168.1.28:4747/video")
        self.edit_droidcam_url.setStyleSheet("background-color: #1b1e2b; border: 1px solid #00e5ff; border-radius: 4px; padding: 4px; color: #ffffff;")
        layout_droid.addWidget(self.edit_droidcam_url)

        h_btn_droid = QHBoxLayout()
        self.btn_connect_droidcam = QPushButton("🔌 Kết nối DroidCam")
        self.btn_connect_droidcam.setStyleSheet("background-color: #0088cc; color: #ffffff; font-weight: bold;")
        self.btn_connect_droidcam.clicked.connect(self._on_connect_droidcam_clicked)
        
        self.btn_preset_wifi = QPushButton("WiFi (192.168.1.28)")
        self.btn_preset_wifi.setStyleSheet("font-size: 11px; padding: 4px;")
        self.btn_preset_wifi.clicked.connect(lambda: self.edit_droidcam_url.setText("http://192.168.1.28:4747/video"))

        self.btn_preset_local = QPushButton("Local (127.0.0.1)")
        self.btn_preset_local.setStyleSheet("font-size: 11px; padding: 4px;")
        self.btn_preset_local.clicked.connect(lambda: self.edit_droidcam_url.setText("http://127.0.0.1:4747/mjpegfeed"))

        h_btn_droid.addWidget(self.btn_connect_droidcam)
        h_btn_droid.addWidget(self.btn_preset_wifi)
        h_btn_droid.addWidget(self.btn_preset_local)
        layout_droid.addLayout(h_btn_droid)

        layout_cam.addWidget(self.widget_droidcam_input)

        lbl_hint = QLabel("💡 Mẹo DroidCam: Mở App DroidCam trên điện thoại & PC. Nhập IP rồi nhấn 'Kết nối DroidCam'.")
        lbl_hint.setWordWrap(True)
        lbl_hint.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        layout_cam.addWidget(lbl_hint)

        group_cam.setLayout(layout_cam)
        layout.addWidget(group_cam)

        layout.addStretch()

    def _on_shape_changed(self, index: int):
        shape_key = self.combo_shape.currentData()
        self.shape_changed.emit(shape_key)

    def _on_dimension_changed(self):
        size = self.spin_size.value()
        height = self.spin_height.value()
        self.dimension_changed.emit(size, height)

    def _on_scale_slider_changed(self, value: int):
        factor = value / 100.0
        self.lbl_scale_val.setText(f"{factor:.2f}")
        self.scale_factor_changed.emit(factor)

    def _open_color_dialog(self):
        initial_color = QColor(int(self.current_r * 255), int(self.current_g * 255), int(self.current_b * 255))
        color = QColorDialog.getColor(initial_color, self, "Chọn màu vật thể Hologram")
        if color.isValid():
            self.current_r = color.redF()
            self.current_g = color.greenF()
            self.current_b = color.blueF()
            self.lbl_color_swatch.setStyleSheet(f"background-color: {color.name()}; border-radius: 4px; border: 1px solid #fff;")
            self.color_changed.emit(self.current_r, self.current_g, self.current_b, self.current_a)

    def _set_preset_color(self, r: float, g: float, b: float, hex_code: str):
        self.current_r = r
        self.current_g = g
        self.current_b = b
        self.lbl_color_swatch.setStyleSheet(f"background-color: {hex_code}; border-radius: 4px; border: 1px solid #fff;")
        self.color_changed.emit(self.current_r, self.current_g, self.current_b, self.current_a)

    def _on_alpha_changed(self, value: int):
        self.current_a = value / 100.0
        self.lbl_alpha_val.setText(f"{value}%")
        self.color_changed.emit(self.current_r, self.current_g, self.current_b, self.current_a)

    def _on_view_mode_toggled(self, id_val: int, checked: bool):
        if checked:
            mode = 'pyramid' if id_val == 1 else 'single'
            self.view_mode_changed.emit(mode)

    def _on_camera_source_changed(self, index: int):
        data = self.combo_camera.currentData()
        if data == "droidcam":
            self.widget_droidcam_input.setVisible(True)
            url = self.edit_droidcam_url.text().strip()
            if url:
                self.camera_source_changed.emit(url)
        else:
            self.widget_droidcam_input.setVisible(False)
            self.camera_source_changed.emit(data)

    def _on_connect_droidcam_clicked(self):
        url = self.edit_droidcam_url.text().strip()
        if url:
            self.camera_source_changed.emit(url)
