"""
graphics/lighting.py
-------------------
Module quản lý hệ thống chiếu sáng Phong (Phong Lighting Engine)
cho môi trường 3D Hologram nền đen tuyền.
"""

from OpenGL.GL import *


def setup_hologram_lighting():
    """
    Cấu hình hệ thống ánh sáng 3D tối ưu cho hiển thị Hologram:
    - Nền Pitch Black (#000000).
    - Ambient light vừa đủ.
    - Directional Lights chiếu từ các phía để vật thể 3D sáng lấp lánh và nổi bật.
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)  # Tự động chuẩn hóa vector pháp tuyến khi scale

    # Đèn chính 0 (Directional Light chiếu từ phía trên - trước mặt)
    light0_position = [2.0, 4.0, 5.0, 0.0]  # w = 0.0 là directional light
    light0_ambient = [0.2, 0.2, 0.25, 1.0]
    light0_diffuse = [0.9, 0.9, 1.0, 1.0]
    light0_specular = [1.0, 1.0, 1.0, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)

    # Đèn phụ 1 (Rim Light chiếu ngược từ phía sau - dưới)
    light1_position = [-3.0, -3.0, -4.0, 0.0]
    light1_diffuse = [0.4, 0.4, 0.6, 1.0]

    glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
