# 🔮 3D Hologram Pyramid Generator & Touchless Gesture Control

> **Hệ thống sinh hình học không gian 3D & Trình chiếu Kim tự tháp Hologram 4 mặt kết hợp Điều khiển Cử chỉ Không chạm (Touchless Interaction) thời gian thực với MediaPipe và OpenGL.**

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![OpenGL](https://img.shields.io/badge/Graphics-PyOpenGL-red.svg)](https://pyopengl.sourceforge.net/)
[![MediaPipe](https://img.shields.io/badge/Vision-MediaPipe-orange.svg)](https://developers.google.com/mediapipe)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-brightgreen.svg)](https://opencv.org/)

---

## 📖 Giới thiệu Dự án

Dự án này là giải pháp toàn diện phục vụ cho **thiết bị chiếu Kim tự tháp Hologram 4 mặt (4-Face Hologram Pyramid)**:
1. **Phân hệ Đồ họa 3D (OpenGL Engine)**: Sinh các khối hình học chuẩn (Cube, Pyramid, Sphere, Cylinder, Torus), hỗ trợ cấu hình kích thước thực tế bằng cm, độ trong suốt (Alpha Blending), chiếu sáng Phong Lighting, và chế độ 4 Viewport chữ thập chuẩn Hologram (Cross Layout) trên nền **Đen Tuyền Tuyệt Đối (`#000000` Pitch Black)**.
2. **Phân hệ Thị giác Máy tính (Computer Vision & AI)**: Nhận diện 21 điểm đốt ngón tay bằng Google MediaPipe, xử lý cử chỉ chụm ngón tay không chạm để **xoay 3D (Rotate)** và **phóng to / thu nhỏ (Zoom)** mô hình mượt mà không cần chạm vào chuột hay bàn phím.
3. **Phân hệ Giao diện (PyQt6 UI)**: Bảng điều khiển màu tối phong cách Cyberpunk, cho phép đổi màu, chỉnh kích cỡ cm, độ trong suốt, chọn nguồn camera (Webcam USB, DroidCam WiFi IP qua điện thoại, hoặc Chế độ Mô phỏng Demo).

---

## ✨ Tính năng Nổi bật

| Phân hệ | Tính năng chính |
|:---|:---|
| 📐 **Hình học 3D** | Khối Lập phương (Cube), Hình chóp tứ giác (Pyramid), Khối cầu (Sphere), Hình trụ (Cylinder), Hình xuyến (Torus). Nhập kích thước cm thực tế. |
| 🔮 **Chiếu Hologram** | Chế độ **4-View Pyramid Cross** (4 góc nhìn đối xứng quanh tâm màn hình, xoay đúng chuẩn quang học lăng kính kim tự tháp) và **Single View** (Góc nhìn đơn). |
| 🖐️ **Điều khiển Không chạm** | • 👌 **Chụm Ngón cái + Ngón trỏ (Pinch Rotate)**: Xoay Yaw & Pitch.<br>• 🤏 **Chụm Ngón cái + Ngón giữa (Zoom Pinch)**: Kéo lên/xuống để Phóng to / Thu nhỏ.<br>• 🔒 **Pinch Lock**: Thả tay ra giữ nguyên góc xoay, không bị trôi vật thể. |
| 🎨 **Tùy biến Thẩm mỹ** | Bảng chọn màu RGBA, thanh chỉnh độ trong suốt (Alpha Blending), chế độ khung dây (Wireframe), tự động xoay (Auto Rotate). |
| 📱 **Nguồn Camera Linh hoạt**| Webcam USB/Laptop, DroidCam IP WiFi (Smartphone), hoặc Chế độ Mô phỏng Bàn tay Ảo (Virtual Hand Simulator) khi không có camera. |
| 🖱️ **Dự phòng Chuột** | Kéo chuột trái để xoay, lăn con lăn chuột để Zoom bất kỳ lúc nào. |

---

## 🖐️ Hướng dẫn Cử chỉ Bàn tay (Touchless Gestures)

Ứng dụng nhận diện bàn tay thời gian thực qua Camera:

```
        [NGÓN TRỎ]        [NGÓN GIỮA]
            (8)               (12)
             \                 /
              \   👌 XOAY     /   🤏 ZOOM
               \             /
              (4) [NGÓN CÁI]
```

* **👌 Cử chỉ Xoay 3D (Rotate)**:
  * Chụm **Đầu ngón cái (Landmark 4)** và **Đầu ngón trỏ (Landmark 8)** lại với nhau (đường nối hiển thị **Màu Xanh Lá 🟢**).
  * Di chuyển bàn tay sang Trái / Phải để xoay quanh trục thẳng đứng (**Yaw**).
  * Di chuyển bàn tay Lên / Xuống để nghiêng vật thể (**Pitch**).
  * **Thả ngón tay ra**: Vật thể giữ nguyên vị trí, bạn có thể đưa tay về vị trí khác mà không sợ vật thể xoay ngược.
* **🤏 Cử chỉ Phóng to / Thu nhỏ (Zoom)**:
  * Chụm **Đầu ngón cái (Landmark 4)** và **Đầu ngón giữa (Landmark 12)** lại với nhau (đường nối hiển thị **Màu Vàng / Cyan 🟡**).
  * Di chuyển tay **Lên trên**: Phóng to (Zoom In).
  * Di chuyển tay **Xuống dưới**: Thu nhỏ (Zoom Out).

---

## 🏗️ Cấu trúc Thư mục Dự án

```text
Hologram/
├── graphics/               # Phân hệ Đồ họa 3D & OpenGL
│   ├── geometry.py         # Lớp định nghĩa đỉnh, pháp tuyến, mặt của các khối 3D (cm)
│   ├── gl_widget.py        # QOpenGLWidget quản lý 4-view pyramid & single view
│   └── lighting.py         # Thiết lập ánh sáng Phong Lighting cho Hologram
├── ui/                     # Phân hệ Giao diện Người dùng PyQt6
│   ├── main_window.py      # Cửa sổ chính tích hợp Splitter (Controls | OpenGL | Preview)
│   ├── control_panel.py    # Sidebar chỉnh tham số hình học, màu sắc, camera
│   └── camera_widget.py    # Khung hiển thị webcam kèm 21 Hand Landmarks
├── vision/                 # Phân hệ Thị giác Máy tính & Nhận diện Bàn tay
│   ├── camera_thread.py    # QThread đọc camera nền (hỗ trợ DroidCam MJPEG stream)
│   └── hand_tracker.py     # MediaPipe Hand Tracking, nhận diện Pinch Rotate & Zoom
├── requirements.txt        # Danh sách thư viện phụ thuộc
├── main.py                 # Điểm khởi chạy ứng dụng (Main Entry Point)
└── README.md               # Tài liệu hướng dẫn cài đặt & sử dụng
```

---

## ⚙️ Yêu cầu Hệ thống (Prerequisites)

* **Hệ điều hành**: Windows 10/11, macOS, hoặc Linux.
* **Python**: Khuyến nghị phiên bản **Python 3.8 đến 3.10** (để đảm bảo tương thích tốt nhất với `mediapipe` và `PyQt6`).
* **Camera**: Webcam tích hợp trên Laptop, Webcam USB, hoặc Smartphone có cài ứng dụng **DroidCam** qua WiFi.

---

## 🚀 Hướng dẫn Cài đặt Chi tiết (Step-by-step Setup)

### Bước 1: Clone kho mã nguồn từ GitHub

Mở Terminal (hoặc PowerShell / Command Prompt) và chạy lệnh:

```bash
git clone https://github.com/KaitoEight/Hologram.git
cd Hologram
```

---

### Bước 2: Tạo và Kích hoạt Môi trường Ảo (Khuyến nghị)

Nên sử dụng môi trường ảo (`venv`) để tránh xung đột thư viện:

* **Trên Windows (PowerShell / CMD)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

* **Trên macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

---

### Bước 3: Cài đặt các Thư viện Phụ thuộc

Cài đặt toàn bộ dependencies thông qua file `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Ghi chú danh sách thư viện:**
> * `PyQt6`: Bộ công cụ giao diện người dùng hiện đại.
> * `PyOpenGL`: Thư viện dựng hình 3D OpenGL.
> * `opencv-python`: Thu nhận và xử lý luồng khung hình video.
> * `mediapipe`: Nhận diện 21 điểm mốc bàn tay thời gian thực của Google.
> * `numpy`: Tính toán ma trận và đại số tuyến tính.

---

### Bước 4: Khởi chạy Ứng dụng

Chạy lệnh:

```bash
python main.py
```

Cửa sổ ứng dụng sẽ xuất hiện với 3 phần chính:
1. **Cột trái**: Bảng điều khiển thông số hình học, màu sắc, chế độ hiển thị, nguồn camera.
2. **Khu vực giữa**: Khung chiếu 3D Hologram nền đen Pitch Black.
3. **Cột phải**: Màn hình Camera Preview thời gian thực với khung xương bàn tay MediaPipe.

---

## 📱 Hướng dẫn Kết nối DroidCam (Dùng Điện thoại làm Webcam)

Nếu bạn không có webcam rời hoặc muốn camera chất lượng cao từ điện thoại:

1. **Cài đặt DroidCam** trên điện thoại (Android qua Google Play Store hoặc iOS qua App Store).
2. Kết nối điện thoại và máy tính vào **CÙNG MỘT MẠNG WIFI**.
3. Mở App DroidCam trên điện thoại, bạn sẽ thấy thông tin:
   * **WiFi IP**: ví dụ `192.168.1.28` (hoặc IP tương ứng của mạng nhà bạn).
   * **DroidCam Port**: mặc định là `4747`.
4. **LƯU Ý QUAN TRỌNG**: 
   * **KHÔNG CẦN / TẮT** phần mềm *DroidCam Client trên PC* (vì DroidCam điện thoại chỉ cho phép một kết nối duy nhất tại một thời điểm; nếu app PC đang kết nối, ứng dụng Python sẽ báo `DroidCam is Busy`).
5. Trong ứng dụng Hologram:
   * Chọn mục **Nguồn Camera**: Chọn **📱 DroidCam IP**.
   * Nhập địa chỉ: `http://<IP_DIEN_THOAI>:4747/video` (hoặc bấm nút gán nhanh nếu dùng IP mặc định).
   * Nhấn **Kết nối / Đổi Camera**.

---

## 🛠️ Chế độ Mô phỏng Demo (Khi không có Camera)

Nếu bạn chưa có camera hoặc muốn test nhanh tính năng chiếu Hologram:
* Trong bảng điều khiển bên trái, ở mục **Nguồn Camera**, chọn **✨ Demo (Mô phỏng Bàn tay)**.
* Hệ thống sẽ kích hoạt một bàn tay ảo tự động thực hiện cử chỉ Chụm ngón (Pinch) và xoay vật thể 3D để bạn kiểm tra khả năng hiển thị Hologram.
* Bạn cũng có thể dùng **Chuột trái** để xoay và **Con lăn chuột** để Phóng to/Thu nhỏ trực tiếp trên màn hình 3D.

---

## ❓ Khắc phục Sự cố Thường gặp (Troubleshooting & FAQs)

<details>
<summary><b>1. Lỗi: OpenCV should be configured with libavdevice to open a camera device</b></summary>

* **Nguyên nhân**: Bản `opencv-python` mặc định trên Windows khi dùng hàm `cv2.VideoCapture("http://...")` không tích hợp sẵn backend ffmpeg avdevice.
* **Đã xử lý**: Mã nguồn trong `vision/camera_thread.py` đã được tích hợp bộ đọc `MjpegStreamReader` trực tiếp qua thư viện chuẩn `urllib`, tự động giải mã các frame JPEG từ DroidCam mà không phụ thuộc vào `avdevice`.
</details>

<details>
<summary><b>2. DroidCam báo lỗi kết nối hoặc "DroidCam is Busy"</b></summary>

* Đảm bảo máy tính và điện thoại cùng kết nối vào 1 mạng WiFi (cùng dải IP, ví dụ `192.168.1.x`).
* Kiểm tra xem trên máy tính có đang mở cửa sổ **DroidCam Client** không. Nếu có, hãy nhấn **Stop** và đóng hoàn toàn DroidCam Client trên PC.
</details>

<details>
<summary><b>3. Làm sao để chiếu lên tháp mica Hologram?</b></summary>

* Chuyển chế độ hiển thị sang **4-View Pyramid Hologram Cross**.
* Đặt thiết bị hiển thị (màn hình, máy tính bảng hoặc laptop lật ngược) nằm ngang song song mặt bàn.
* Đặt đỉnh nhọn của Kim tự tháp Hologram mica 4 mặt vào chính giữa tâm màn hình.
* Tắt bớt đèn phòng để ánh sáng phản xạ từ 4 góc chiếu lên các mặt kính mica tạo cảm giác vật thể lơ lửng trong không gian 3D.
</details>

---

## 📜 Giấy phép & Tác giả

* **Repository**: [https://github.com/KaitoEight/Hologram.git](https://github.com/KaitoEight/Hologram.git)
* **Author**: Senior Software Engineer & Computer Graphics Developer
* **License**: Dự án mở phục vụ mục đích nghiên cứu, học tập và chế tạo thiết bị Hologram tương tác không chạm.
