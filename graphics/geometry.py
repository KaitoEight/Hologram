"""
graphics/geometry.py
-------------------
Module chứa các lớp tạo hình học 3D (Cube, Pyramid, Sphere, Cylinder, Torus)
cho ứng dụng Hologram 3D.

Mỗi đối tượng hình học hỗ trợ:
- Tính toán tọa độ đỉnh (vertices), vector pháp tuyến (normals), chỉ số mặt (indices).
- Quy đổi thông số kích thước thực tế (cm) thành tỷ lệ không gian 3D (World Units).
- Render bằng PyOpenGL (dùng OpenGL Immediate Mode / Display List hoặc Vertex Arrays).
"""

import math
from OpenGL.GL import *


class Geometry3D:
    """Lớp cơ sở cho tất cả các đối tượng hình học 3D."""
    def __init__(self):
        self.scale_factor = 0.2  # 1 cm = 0.2 units trong OpenGL coordinate system
        self.color = (0.0, 0.9, 1.0)  # RGB (Cyan Hologram mặc định)
        self.alpha = 0.95  # Độ trong suốt (0.0 - 1.0)
        self.wireframe = False  # Chế độ khung dây
        self.enable_lighting = True

    def set_color(self, r: float, g: float, b: float, a: float = 1.0):
        """Cấu hình màu sắc và độ trong suốt."""
        self.color = (r, g, b)
        self.alpha = a

    def apply_material(self):
        """Thiết lập thông số vật liệu và màu sắc trong môi trường OpenGL."""
        r, g, b = self.color
        a = self.alpha
        
        # Thiết lập màu tô sắc (Color) khi vẽ
        glColor4f(r, g, b, a)

        # Cấu hình thuộc tính phản xạ ánh sáng (Phong Material Properties)
        ambient = [r * 0.4, g * 0.4, b * 0.4, a]
        diffuse = [r * 0.9, g * 0.9, b * 0.9, a]
        specular = [1.0, 1.0, 1.0, a]
        shininess = 64.0

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

    def draw(self):
        """Phương thức vẽ ảo - các lớp con ghi đè triển khai cụ thể."""
        pass


class CubeGeometry(Geometry3D):
    """
    Hình Lập Phương (Cube).
    Thông số:
    - side_length_cm: Chiều dài cạnh tính bằng cm.
    """
    def __init__(self, side_length_cm: float = 10.0):
        super().__init__()
        self.side_length_cm = side_length_cm

    def draw(self):
        """Vẽ khối lập phương 3D với 6 mặt và vector pháp tuyến chuẩn."""
        self.apply_material()
        
        # Chuyển đổi kích thước cm -> world unit (bán kính một nửa chiều dài)
        s = (self.side_length_cm * self.scale_factor) / 2.0

        # Định nghĩa 6 mặt của hình lập phương (Normal Vector + 4 Vertices)
        faces = [
            # Mặt trước (+Z)
            ((0.0, 0.0, 1.0), [(-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)]),
            # Mặt sau (-Z)
            ((0.0, 0.0, -1.0), [(-s, -s, -s), (-s, s, -s), (s, s, -s), (s, -s, -s)]),
            # Mặt trên (+Y)
            ((0.0, 1.0, 0.0), [(-s, s, -s), (-s, s, s), (s, s, s), (s, s, -s)]),
            # Mặt dưới (-Y)
            ((0.0, -1.0, 0.0), [(-s, -s, -s), (s, -s, -s), (s, -s, s), (-s, -s, s)]),
            # Mặt phải (+X)
            ((1.0, 0.0, 0.0), [(s, -s, -s), (s, s, -s), (s, s, s), (s, -s, s)]),
            # Mặt trái (-X)
            ((-1.0, 0.0, 0.0), [(-s, -s, -s), (-s, -s, s), (-s, s, s), (-s, s, -s)]),
        ]

        mode = GL_LINE_LOOP if self.wireframe else GL_QUADS

        for normal, verts in faces:
            glBegin(mode)
            glNormal3fv(normal)
            for v in verts:
                glVertex3fv(v)
            glEnd()


class PyramidGeometry(Geometry3D):
    """
    Hình Chóp 4 Mặt (Pyramid).
    Thông số:
    - base_size_cm: Kích thước cạnh đáy (cm).
    - height_cm: Chiều cao hình chóp (cm).
    """
    def __init__(self, base_size_cm: float = 10.0, height_cm: float = 12.0):
        super().__init__()
        self.base_size_cm = base_size_cm
        self.height_cm = height_cm

    def draw(self):
        """Vẽ hình chóp 3D với đáy hình vuông và 4 mặt bên hình tam giác."""
        self.apply_material()

        b = (self.base_size_cm * self.scale_factor) / 2.0
        h = (self.height_cm * self.scale_factor) / 2.0
        top = (0.0, h, 0.0)

        # 4 đỉnh đáy
        p1 = (-b, -h, b)
        p2 = (b, -h, b)
        p3 = (b, -h, -b)
        p4 = (-b, -h, -b)

        # Hàm tính vector pháp tuyến chuẩn cho mặt tam giác (cross product)
        def calc_normal(v1, v2, v3):
            ax, ay, az = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
            bx, by, bz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
            nx = ay * bz - az * by
            ny = az * bx - ax * bz
            nz = ax * by - ay * bx
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            if length > 0:
                return (nx/length, ny/length, nz/length)
            return (0.0, 1.0, 0.0)

        mode = GL_LINE_LOOP if self.wireframe else GL_TRIANGLES

        # Vẽ 4 mặt bên
        side_faces = [
            (top, p1, p2),
            (top, p2, p3),
            (top, p3, p4),
            (top, p4, p1)
        ]

        for v1, v2, v3 in side_faces:
            n = calc_normal(v1, v2, v3)
            glBegin(mode)
            glNormal3fv(n)
            glVertex3fv(v1)
            glVertex3fv(v2)
            glVertex3fv(v3)
            glEnd()

        # Vẽ mặt đáy
        glBegin(GL_LINE_LOOP if self.wireframe else GL_QUADS)
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3fv(p1)
        glVertex3fv(p4)
        glVertex3fv(p3)
        glVertex3fv(p2)
        glEnd()


class SphereGeometry(Geometry3D):
    """
    Khối Cầu 3D (Sphere).
    Thông số:
    - radius_cm: Bán kính khối cầu (cm).
    - slices, stacks: Độ phân giải đường vĩ tuyến & kinh tuyến.
    """
    def __init__(self, radius_cm: float = 6.0, slices: int = 32, stacks: int = 32):
        super().__init__()
        self.radius_cm = radius_cm
        self.slices = slices
        self.stacks = stacks

    def draw(self):
        """Vẽ khối cầu với các mặt tứ giác nhỏ theo kinh vĩ độ."""
        self.apply_material()
        r = self.radius_cm * self.scale_factor

        for i in range(self.stacks):
            lat0 = math.pi * (-0.5 + float(i) / self.stacks)
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)

            lat1 = math.pi * (-0.5 + float(i + 1) / self.stacks)
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)

            glBegin(GL_LINE_LOOP if self.wireframe else GL_QUAD_STRIP)
            for j in range(self.slices + 1):
                lng = 2 * math.pi * float(j) / self.slices
                x = math.cos(lng)
                y = math.sin(lng)

                # Điểm 1 trên vòng vĩ tuyến lat0
                nx0, ny0, nz0 = x * zr0, y * zr0, z0
                glNormal3f(nx0, ny0, nz0)
                glVertex3f(x * zr0 * r, y * zr0 * r, z0 * r)

                # Điểm 2 trên vòng vĩ tuyến lat1
                nx1, ny1, nz1 = x * zr1, y * zr1, z1
                glNormal3f(nx1, ny1, nz1)
                glVertex3f(x * zr1 * r, y * zr1 * r, z1 * r)
            glEnd()


class CylinderGeometry(Geometry3D):
    """
    Hình Trụ 3D (Cylinder).
    Thông số:
    - radius_cm: Bán kính mặt đáy (cm).
    - height_cm: Chiều cao hình trụ (cm).
    - slices: Độ phân giải vòng tròn.
    """
    def __init__(self, radius_cm: float = 5.0, height_cm: float = 10.0, slices: int = 32):
        super().__init__()
        self.radius_cm = radius_cm
        self.height_cm = height_cm
        self.slices = slices

    def draw(self):
        """Vẽ hình trụ với thân trụ và 2 nắp hình tròn."""
        self.apply_material()
        r = self.radius_cm * self.scale_factor
        h2 = (self.height_cm * self.scale_factor) / 2.0

        # Thân hình trụ (Quad Strip)
        glBegin(GL_LINE_LOOP if self.wireframe else GL_QUAD_STRIP)
        for i in range(self.slices + 1):
            angle = 2.0 * math.pi * i / self.slices
            x = math.cos(angle)
            z = math.sin(angle)

            glNormal3f(x, 0.0, z)
            glVertex3f(x * r, h2, z * r)
            glVertex3f(x * r, -h2, z * r)
        glEnd()

        # Nắp trên (+Y)
        glBegin(GL_LINE_LOOP if self.wireframe else GL_TRIANGLE_FAN)
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, h2, 0.0)
        for i in range(self.slices + 1):
            angle = 2.0 * math.pi * i / self.slices
            glVertex3f(math.cos(angle) * r, h2, math.sin(angle) * r)
        glEnd()

        # Nắp dưới (-Y)
        glBegin(GL_LINE_LOOP if self.wireframe else GL_TRIANGLE_FAN)
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(0.0, -h2, 0.0)
        for i in range(self.slices + 1):
            angle = -2.0 * math.pi * i / self.slices
            glVertex3f(math.cos(angle) * r, -h2, math.sin(angle) * r)
        glEnd()


class TorusGeometry(Geometry3D):
    """
    Khối Xuyến / Bánh Xe 3D (Torus).
    Thông số:
    - major_radius_cm: Bán kính lớn (từ tâm tới lõi vòng) (cm).
    - minor_radius_cm: Bán kính ống nhỏ (cm).
    """
    def __init__(self, major_radius_cm: float = 6.0, minor_radius_cm: float = 2.0, num_major: int = 32, num_minor: int = 16):
        super().__init__()
        self.major_radius_cm = major_radius_cm
        self.minor_radius_cm = minor_radius_cm
        self.num_major = num_major
        self.num_minor = num_minor

    def draw(self):
        """Vẽ hình xuyến (Torus)."""
        self.apply_material()
        R = self.major_radius_cm * self.scale_factor
        r = self.minor_radius_cm * self.scale_factor

        for i in range(self.num_major):
            u0 = i * 2.0 * math.pi / self.num_major
            u1 = (i + 1) * 2.0 * math.pi / self.num_major

            glBegin(GL_LINE_LOOP if self.wireframe else GL_QUAD_STRIP)
            for j in range(self.num_minor + 1):
                v = j * 2.0 * math.pi / self.num_minor
                cos_v = math.cos(v)
                sin_v = math.sin(v)

                for u in (u0, u1):
                    cos_u = math.cos(u)
                    sin_u = math.sin(u)

                    x = (R + r * cos_v) * cos_u
                    y = r * sin_v
                    z = (R + r * cos_v) * sin_u

                    nx = cos_v * cos_u
                    ny = sin_v
                    nz = cos_v * sin_u

                    glNormal3f(nx, ny, nz)
                    glVertex3f(x, y, z)
            glEnd()
