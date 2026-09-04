"""
vision/camera_thread.py
-----------------------
QThread thu thập dữ liệu Webcam / DroidCam IP Camera bất đồng bộ.

QUAN TRỌNG: Bản OpenCV (pip) trên Windows thường KHÔNG có avdevice,
nên cv2.VideoCapture(url) sẽ THẤT BẠI với mọi URL stream.
Giải pháp: Đọc MJPEG stream trực tiếp qua urllib + cv2.imdecode.

Hỗ trợ:
1. DroidCam / Phone IP Camera qua HTTP MJPEG (urllib fallback).
2. Webcam USB / Laptop vật lý (Index 0, 1, 2...).
3. Chế độ Mô phỏng Cử chỉ Bàn tay Demo.
"""

import os
import sys
import time
import math
import threading
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from vision.hand_tracker import HandTracker

# Tắt log rác của OpenCV C++ VideoIO
os.environ["OPENCV_LOG_LEVEL"] = "FATAL"
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"


class CSuppressStderr:
    """Redirect file descriptor 2 (stderr) cấp C/C++ để ẩn warning OpenCV native."""
    def __enter__(self):
        try:
            self.null_fd = os.open(os.devnull, os.O_RDWR)
            self.save_fd = os.dup(2)
            os.dup2(self.null_fd, 2)
        except Exception:
            self.null_fd = None

    def __exit__(self, *_):
        if self.null_fd is not None:
            try:
                os.dup2(self.save_fd, 2)
                os.close(self.null_fd)
                os.close(self.save_fd)
            except Exception:
                pass


class MjpegStreamReader:
    """
    Đọc luồng MJPEG từ DroidCam / IP Camera qua urllib thay vì cv2.VideoCapture(url).
    Giải pháp cho OpenCV builds thiếu avdevice (pip install opencv-python mặc định).
    """
    def __init__(self, url):
        self.url = url
        self.stream = None
        self.frame = None
        self.running = False
        self._lock = threading.Lock()
        self._thread = None

    def start(self):
        """Mở kết nối HTTP và bắt đầu đọc frames."""
        import urllib.request
        try:
            self.stream = urllib.request.urlopen(self.url, timeout=5)
            self.running = True
            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            return True
        except Exception:
            self.running = False
            return False

    def _read_loop(self):
        """Vòng lặp đọc JPEG frames liên tục từ HTTP MJPEG stream."""
        raw = b""
        while self.running and self.stream:
            try:
                chunk = self.stream.read(8192)
                if not chunk:
                    break
                raw += chunk

                # Tìm JPEG Start-Of-Image (FF D8) và End-Of-Image (FF D9)
                while True:
                    soi = raw.find(b"\xff\xd8")
                    eoi = raw.find(b"\xff\xd9")
                    if soi != -1 and eoi != -1 and eoi > soi:
                        jpg_data = raw[soi:eoi + 2]
                        raw = raw[eoi + 2:]

                        img = cv2.imdecode(
                            np.frombuffer(jpg_data, dtype=np.uint8),
                            cv2.IMREAD_COLOR
                        )
                        if img is not None:
                            with self._lock:
                                self.frame = img
                    else:
                        break
            except Exception:
                break

        self.running = False

    def read(self):
        """Đọc frame mới nhất (thread-safe). Trả về (success, frame)."""
        with self._lock:
            if self.frame is not None:
                return True, self.frame.copy()
        return False, None

    def isOpened(self):
        return self.running

    def release(self):
        self.running = False
        try:
            if self.stream:
                self.stream.close()
        except Exception:
            pass


class CameraThread(QThread):
    """Thread đọc khung hình Webcam / DroidCam IP và chạy nhận diện MediaPipe."""
    
    frame_processed = pyqtSignal(np.ndarray, dict)
    camera_error = pyqtSignal(str)
    camera_connected = pyqtSignal(str)

    def __init__(self, camera_source="http://192.168.1.28:4747/video", parent=None):
        super().__init__(parent)
        self.camera_source = camera_source
        self.force_demo_mode = False
        self.running = False
        self.tracker = HandTracker()

    def set_camera_source(self, source):
        if source == -1 or source == "-1":
            self.force_demo_mode = True
            self.camera_source = -1
        else:
            self.force_demo_mode = False
            self.camera_source = source

    def _open_camera(self, source):
        """Kết nối camera: dùng urllib MJPEG cho URL, cv2 cho webcam index."""
        if isinstance(source, str) and source.startswith("http"):
            return self._open_ip_camera(source)
        elif isinstance(source, int) and source >= 0:
            return self._open_usb_camera(source)
        return None

    def _open_ip_camera(self, url):
        """Kết nối DroidCam / IP Camera bằng urllib MJPEG reader."""
        # Xây dựng danh sách URL thử nghiệm
        endpoints = [url]
        base = url.rsplit("/", 1)[0] if "/" in url[8:] else url
        for path in ["/video", "/mjpegfeed", "/videofeed"]:
            candidate = base + path
            if candidate not in endpoints:
                endpoints.append(candidate)

        for ep in endpoints:
            reader = MjpegStreamReader(ep)
            if reader.start():
                # Chờ tối đa 2 giây để nhận frame đầu tiên
                for _ in range(40):
                    ret, frame = reader.read()
                    if ret and frame is not None:
                        return reader
                    time.sleep(0.05)
                reader.release()

        return None

    def _open_usb_camera(self, index):
        """Kết nối webcam USB/Laptop bằng cv2.VideoCapture."""
        with CSuppressStderr():
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
            for backend in backends:
                try:
                    cap = cv2.VideoCapture(index, backend)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            return cap
                        cap.release()
                except Exception:
                    continue
        return None

    def run(self):
        """Vòng lặp chính của QThread capture video."""
        self.running = True

        while self.running:
            if self.force_demo_mode:
                self.camera_error.emit("✨ Đang chạy Chế độ Mô phỏng Cử chỉ Bàn tay Demo")
                self._run_virtual_hand_demo()
                continue

            cap = self._open_camera(self.camera_source)

            if cap is None:
                src_str = self.camera_source if isinstance(self.camera_source, str) else "Index " + str(self.camera_source)
                self.camera_error.emit("📱 DroidCam/Camera [" + src_str + "]: Chưa kết nối. Mở App DroidCam / tắt DroidCam Client PC!")
                self._show_offline_frame()
                time.sleep(0.5)
                continue

            src_str = "DroidCam IP Phone" if isinstance(self.camera_source, str) else "Webcam " + str(self.camera_source)
            self.camera_connected.emit("📱 ĐÃ KẾT NỐI: " + src_str)
            
            if hasattr(cap, 'set'):
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            while self.running and not self.force_demo_mode and cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None:
                    time.sleep(0.01)
                    continue

                frame = cv2.flip(frame, 1)
                annotated_frame, gesture_data = self.tracker.process_frame(frame)
                self.frame_processed.emit(annotated_frame, gesture_data)

            if cap:
                cap.release()

    def _show_offline_frame(self):
        """Màn hình tĩnh khi DroidCam / Camera chưa kết nối."""
        h, w = 480, 640
        frame = np.zeros((h, w, 3), dtype=np.uint8)

        for y in range(0, h, 40):
            cv2.line(frame, (0, y), (w, y), (15, 18, 25), 1)
        for x in range(0, w, 40):
            cv2.line(frame, (x, 0), (x, h), (15, 18, 25), 1)

        cv2.putText(frame, "DROIDCAM / CAMERA OFFLINE", (120, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 165, 255), 2)

        src_info = self.camera_source if isinstance(self.camera_source, str) else "Camera Index " + str(self.camera_source)
        cv2.putText(frame, "Source: " + str(src_info), (100, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.putText(frame, ">> TAT DroidCam Client PC truoc <<", (120, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 255), 2)
        cv2.putText(frame, "(DroidCam chi cho phep 1 ket noi)", (130, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1)
        cv2.putText(frame, "Or use Left Mouse Drag to rotate 3D", (130, 330),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

        gesture_data = {
            'hand_detected': False, 'is_pinching': False, 'is_zoom_pinching': False,
            'delta_yaw': 0.0, 'delta_pitch': 0.0, 'delta_zoom': 0.0,
            'pinch_distance': 0.0, 'zoom_pinch_distance': 0.0, 'landmarks': None
        }
        self.frame_processed.emit(frame, gesture_data)

    def _run_virtual_hand_demo(self):
        """Chế độ Mô phỏng Cử chỉ Bàn tay 3D."""
        h, w = 480, 640
        start_time = time.time()
        last_x, last_y = 0.5, 0.5
        is_pinching = False

        while self.running and self.force_demo_mode:
            t = time.time() - start_time
            frame = np.zeros((h, w, 3), dtype=np.uint8)

            for y in range(0, h, 40):
                cv2.line(frame, (0, y), (w, y), (20, 24, 35), 1)
            for x in range(0, w, 40):
                cv2.line(frame, (x, 0), (x, h), (20, 24, 35), 1)

            hand_x = 0.5 + 0.25 * math.sin(t * 1.2)
            hand_y = 0.5 + 0.18 * math.cos(t * 1.8)
            cycle = t % 5.0
            should_pinch = (1.0 <= cycle <= 3.8)
            pinch_dist = 0.03 if should_pinch else 0.12

            px, py = int(hand_x * w), int(hand_y * h)
            thumb_x = int((hand_x - pinch_dist * 0.5) * w)
            thumb_y = int((hand_y - pinch_dist * 0.3) * h)
            index_x = int((hand_x + pinch_dist * 0.5) * w)
            index_y = int((hand_y + pinch_dist * 0.3) * h)

            wrist = (px, py + 80)
            cv2.line(frame, wrist, (thumb_x, thumb_y), (255, 200, 0), 2)
            cv2.line(frame, wrist, (index_x, index_y), (255, 200, 0), 2)
            cv2.line(frame, wrist, (px + 30, py - 40), (255, 200, 0), 2)
            cv2.line(frame, wrist, (px + 60, py - 30), (255, 200, 0), 2)
            cv2.line(frame, wrist, (px + 80, py - 10), (255, 200, 0), 2)

            cv2.circle(frame, wrist, 6, (0, 240, 255), -1)
            cv2.circle(frame, (thumb_x, thumb_y), 7, (0, 255, 0) if should_pinch else (0, 0, 255), -1)
            cv2.circle(frame, (index_x, index_y), 7, (0, 255, 0) if should_pinch else (0, 0, 255), -1)

            delta_yaw, delta_pitch = 0.0, 0.0
            if should_pinch:
                cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 3)
                cv2.putText(frame, "STATE: PINCHING (HOLD & ROTATE 3D)", (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
                if not is_pinching:
                    is_pinching = True
                    last_x, last_y = hand_x, hand_y
                else:
                    delta_yaw = (hand_x - last_x) * 250.0
                    delta_pitch = (hand_y - last_y) * 250.0
                    last_x, last_y = hand_x, hand_y
            else:
                cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 0, 255), 1)
                cv2.putText(frame, "STATE: OPEN HAND (PINCH LOCK ACTIVE)", (30, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 200, 255), 2)
                is_pinching = False
                last_x, last_y = hand_x, hand_y

            cv2.putText(frame, "[DEMO MODE] Virtual Hand Simulation", (30, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

            gesture_data = {
                'hand_detected': True, 'is_pinching': is_pinching, 'is_zoom_pinching': False,
                'delta_yaw': delta_yaw, 'delta_pitch': delta_pitch, 'delta_zoom': 0.0,
                'pinch_distance': pinch_dist, 'zoom_pinch_distance': 0.0, 'landmarks': None
            }
            self.frame_processed.emit(frame, gesture_data)
            time.sleep(0.03)

    def stop(self):
        self.running = False
        self.wait()
