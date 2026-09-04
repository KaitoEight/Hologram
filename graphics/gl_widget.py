"""
graphics/gl_widget.py
---------------------
QOpenGLWidget chuyên dụng hiển thị không gian 3D Hologram.
Hỗ trợ 2 chế độ hiển thị:
1. Single View: Xem thử 1 camera góc nhìn trực diện.
2. 4-View Hologram Pyramid: Chia thành 4 viewport tạo hình chữ thập (Cross Layout)
   được thiết kế chuẩn cho thiết bị chiếu Kim tự tháp Hologram 4 mặt.

Đặc tính quan trọng:
- Background mặc định: Pitch Black (#000000).
- Alpha Blending: Hỗ trợ vật thể bán trong suốt.
- Nhận giá trị Pitch & Yaw từ cử chỉ MediaPipe thời gian thực.
"""

from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMouseEvent, QWheelEvent
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt

from graphics.geometry import (
    CubeGeometry, PyramidGeometry, SphereGeometry, CylinderGeometry, TorusGeometry
)
from graphics.lighting import setup_hologram_lighting


class HologramGLWidget(QOpenGLWidget):
    """OpenGL Render Widget cho màn hình chiếu Hologram."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Chế độ hiển thị: 'single' (1 góc nhìn) hoặc 'pyramid' (4 góc nhìn chữ thập)
        self.view_mode = 'pyramid'

        # Danh sách các khối hình 3D khởi tạo sẵn
        self.geometries = {
            'cube': CubeGeometry(side_length_cm=10.0),
            'pyramid': PyramidGeometry(base_size_cm=10.0, height_cm=12.0),
            'sphere': SphereGeometry(radius_cm=6.0),
            'cylinder': CylinderGeometry(radius_cm=5.0, height_cm=10.0),
            'torus': TorusGeometry(major_radius_cm=6.0, minor_radius_cm=2.0)
        }
        self.current_shape_key = 'cube'

        # Góc xoay của vật thể (Pitch: quanh trục X, Yaw: quanh trục Y, Roll: quanh trục Z)
        self.pitch = 15.0
        self.yaw = 30.0
        self.roll = 0.0

        # Xoay tự động (Auto-rotation toggle)
        self.auto_rotate = False
        self.auto_rotate_speed = 0.8

        # Khoảng cách Camera tới vật thể (Zoom)
        self.camera_distance = 6.0
        self.camera_distance_min = 1.5
        self.camera_distance_max = 25.0
        self.zoom_sensitivity = 0.02  # Tốc độ zoom từ cử chỉ bàn tay

        # Mouse interaction backup
        self.last_mouse_pos = None

        # Timer cập nhật frame (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def set_shape(self, shape_key: str):
        """Thay đổi loại hình học đang hiển thị."""
        if shape_key in self.geometries:
            self.current_shape_key = shape_key
            self.update()

    def get_current_geometry(self):
        return self.geometries[self.current_shape_key]

    def set_color(self, r: float, g: float, b: float, a: float = 1.0):
        """Cấu hình màu sắc và độ trong suốt cho tất cả hình học."""
        for geom in self.geometries.values():
            geom.set_color(r, g, b, a)
        self.update()

    def set_wireframe(self, enable: bool):
        """Bật/tắt chế độ vẽ khung dây (Wireframe)."""
        for geom in self.geometries.values():
            geom.wireframe = enable
        self.update()

    def set_scale_factor(self, factor: float):
        """Cấu hình tỷ lệ cm -> World Unit (1 cm = N units)."""
        for geom in self.geometries.values():
            geom.scale_factor = factor
        self.update()

    def update_rotation(self, delta_yaw: float, delta_pitch: float):
        """Cập nhật góc xoay nhận được từ MediaPipe hand tracking."""
        self.yaw += delta_yaw
        self.pitch += delta_pitch
        
        # Giới hạn góc Pitch để tránh xoay ngược lộn đầu quá đà nếu muốn (-90 đến 90 deg)
        self.pitch = max(-89.0, min(89.0, self.pitch))
        self.update()

    def update_zoom(self, delta_zoom: float):
        """
        Cập nhật zoom (phóng to/thu nhỏ) nhận từ cử chỉ Ngón cái + Ngón giữa.
        delta_zoom > 0: Phóng to (camera lại gần vật thể).
        delta_zoom < 0: Thu nhỏ (camera ra xa vật thể).
        """
        self.camera_distance -= delta_zoom * self.zoom_sensitivity
        self.camera_distance = max(self.camera_distance_min, min(self.camera_distance_max, self.camera_distance))
        self.update()

    def update_frame(self):
        """Vòng lặp timer cập nhật tự động xoay nếu bật Auto Rotate."""
        if self.auto_rotate:
            self.yaw = (self.yaw + self.auto_rotate_speed) % 360.0
            self.update()

    def initializeGL(self):
        """Khởi tạo môi trường OpenGL."""
        # BẮT BUỘC: Clear background là màu Đen Tuyền (Pitch Black #000000)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Bật Depth Buffer cho hình thể 3D
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Bật Alpha Blending cho độ trong suốt
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Bật Smooth Shading
        glShadeModel(GL_SMOOTH)

        # Cấu hình ánh sáng Phong
        setup_hologram_lighting()

    def resizeGL(self, width: int, height: int):
        """Xử lý thay đổi kích thước cửa sổ."""
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)

    def paintGL(self):
        """Vẽ khung hình OpenGL."""
        # Xóa màn hình với màu Đen tuyền Pitch Black
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        w = self.width()
        h = self.height()

        if self.view_mode == 'single':
            self._render_single_view(w, h)
        else:
            self._render_4view_pyramid(w, h)

    def _render_single_view(self, width: int, height: int):
        """Vẽ 1 camera trực diện giữa màn hình (Preview Mode)."""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 0.0, self.camera_distance,
                  0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0)

        # Thực hiện biến đổi hình học & xoay vật thể
        glPushMatrix()
        glRotatef(self.pitch, 1.0, 0.0, 0.0)
        glRotatef(self.yaw, 0.0, 1.0, 0.0)
        glRotatef(self.roll, 0.0, 0.0, 1.0)

        current_geom = self.geometries[self.current_shape_key]
        current_geom.draw()
        glPopMatrix()

    def _render_4view_pyramid(self, width: int, height: int):
        """
        Vẽ 4 góc nhìn chuẩn cho Kim Tự Tháp Hologram 4 mặt (Cross Pyramid Layout).
        Sắp xếp 4 viewport tạo hình chữ thập (Top, Bottom, Left, Right)
        xung quanh tâm màn hình.
        """
        size = min(width, height) // 3  # Kích thước mỗi viewport
        cx = width // 2
        cy = height // 2

        # 4 Vùng hiển thị Viewport xung quanh tâm:
        # 1. Viewport Dưới (Bottom View): Nhìn từ phía trước (Front)
        vp_bottom = (cx - size // 2, cy - size * 3 // 2, size, size)
        
        # 2. Viewport Trên (Top View): Nhìn từ phía sau (Back) & Xoay ngược 180 độ
        vp_top = (cx - size // 2, cy + size // 2, size, size)
        
        # 3. Viewport Trái (Left View): Nhìn từ bên trái & Xoay -90 độ
        vp_left = (cx - size * 3 // 2, cy - size // 2, size, size)

        # 4. Viewport Phải (Right View): Nhìn từ bên phải & Xoay +90 độ
        vp_right = (cx + size // 2, cy - size // 2, size, size)

        views = [
            # (Viewport Rect, Screen Rotation Z, Extra Camera Yaw)
            (vp_bottom, 0.0, 0.0),       # Mặt dưới: Giữ nguyên
            (vp_top, 180.0, 180.0),      # Mặt trên: Xoay 180° để ánh chiếu đúng kính
            (vp_left, -90.0, 90.0),      # Mặt trái: Xoay -90°
            (vp_right, 90.0, -90.0)      # Mặt phải: Xoay +90°
        ]

        current_geom = self.geometries[self.current_shape_key]

        for (vx, vy, vw, vh), z_rot, cam_yaw_offset in views:
            glViewport(vx, vy, vw, vh)
            
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, 1.0, 0.1, 100.0)

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            gluLookAt(0.0, 0.0, self.camera_distance,
                      0.0, 0.0, 0.0,
                      0.0, 1.0, 0.0)

            glPushMatrix()
            # Xoay mặt phẳng hiển thị theo góc tương ứng của 4 mặt kim tự tháp
            glRotatef(z_rot, 0.0, 0.0, 1.0)
            
            # Áp dụng góc xoay tương tác người dùng (Pitch & Yaw)
            glRotatef(self.pitch, 1.0, 0.0, 0.0)
            glRotatef(self.yaw + cam_yaw_offset, 0.0, 1.0, 0.0)

            current_geom.draw()
            glPopMatrix()

    # Thao tác Chuột dự phòng (Mouse Drag to Rotate)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.last_mouse_pos is not None:
            pos = event.position()
            dx = pos.x() - self.last_mouse_pos.x()
            dy = pos.y() - self.last_mouse_pos.y()
            
            self.yaw += dx * 0.5
            self.pitch += dy * 0.5
            self.pitch = max(-89.0, min(89.0, self.pitch))
            
            self.last_mouse_pos = pos
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.last_mouse_pos = None

    def wheelEvent(self, event: QWheelEvent):
        """Zoom bằng cuộn chuột (Mouse Scroll Wheel)."""
        delta = event.angleDelta().y()
        # Cuộn lên = phóng to (camera lại gần), cuộn xuống = thu nhỏ
        self.camera_distance -= delta * 0.005
        self.camera_distance = max(self.camera_distance_min, min(self.camera_distance_max, self.camera_distance))
        self.update()
