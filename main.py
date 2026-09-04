"""
main.py
-------
Điểm khởi chạy ứng dụng (Main Entry Point) cho Phần mềm Trình chiếu 3D Hologram 
kết hợp Tương tác Không chạm MediaPipe.

Tác giả: Senior Software Engineer & Computer Graphics Expert
Dự án: Hologram 4-Side Pyramid Renderer & Touchless Gesture Control
"""

import sys
import os

# Tắt log cảnh báo rác của OpenCV C++ VideoIO
os.environ["OPENCV_LOG_LEVEL"] = "FATAL"
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

# Thêm thư mục hiện tại vào sys.path để import các module local
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import HologramMainWindow


def main():
    """Khởi tạo và khởi chạy ứng dụng Hologram 3D."""
    # Khởi tạo QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("3D Hologram Generator & MediaPipe Touchless Control")
    app.setOrganizationName("Hologram Computer Graphics")

    # Thiết lập giao diện màu tối chuẩn (Dark Theme)
    window = HologramMainWindow()
    window.show()

    # Vòng lặp sự kiện chính của ứng dụng PyQt6
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
