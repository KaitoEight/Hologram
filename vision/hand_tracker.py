"""
vision/hand_tracker.py
----------------------
Phân hệ thị giác máy tính & nhận diện cử chỉ bàn tay dùng MediaPipe.

Nhiệm vụ:
1. Trích xuất 21 điểm đặc trưng (Landmarks) của bàn tay từ webcam frame.
2. Tính khoảng cách giữa đầu ngón cái (Landmark 4) và ngón trỏ (Landmark 8) để xác định cử chỉ Pinch ("Nắm") -> XoayXoay.
3. Tính khoảng cách giữa đầu ngón cái (Landmark 4) và ngón giữa (Landmark 12) để xác định cử chỉ Zoom Pinch -> Phóng to/Thu nhỏ.
4. Tính toán độ dời bàn tay (dx, dy) khi đang Pinch để sinh ra góc xoay Yaw & Pitch.
5. Cơ chế Khóa Góc Xoay (Pinch-to-Rotate Lock): Nhả tay ra -> Dừng xoay. Kéo tay về không bị xoay ngược.
"""

import math
import numpy as np
import cv2
import mediapipe as mp


class HandTracker:
    """Bộ xử lý nhận diện bàn tay & phát hiện cử chỉ Pinch (Rotate + Zoom)."""
    def __init__(self, pinch_threshold: float = 0.06, sensitivity: float = 250.0):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Ngưỡng phát hiện cử chỉ Chụm tay (Pinch)
        self.pinch_threshold = pinch_threshold
        self.sensitivity = sensitivity

        # Trạng thái cử chỉ XoayXoay (Thumb + Index Finger)
        self.is_pinching = False
        self.last_pinch_pos = None  # (x, y) chuẩn hóa

        # Trạng thái cử chỉ Zoom (Thumb + Middle Finger)
        self.is_zoom_pinching = False
        self.last_zoom_pos = None  # (x, y) chuẩn hóa

        # Smoothing filter cho xoay
        self.smooth_alpha = 0.4  # Hệ số lọc thông thấp Low-pass
        self.current_delta_yaw = 0.0
        self.current_delta_pitch = 0.0

        # Smoothing filter cho zoom
        self.current_delta_zoom = 0.0

    def process_frame(self, frame_bgr: np.ndarray):
        """
        Xử lý khung hình từ webcam.
        Trả về:
        - frame_annotated: Ảnh đã vẽ 21 landmarks + chỉ số cử chỉ.
        - gesture_data: Dictionary chứa thông tin cử chỉ.
        """
        h, w, _ = frame_bgr.shape
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        gesture_data = {
            'hand_detected': False,
            'is_pinching': False,
            'is_zoom_pinching': False,
            'delta_yaw': 0.0,
            'delta_pitch': 0.0,
            'delta_zoom': 0.0,
            'pinch_distance': 0.0,
            'zoom_pinch_distance': 0.0,
            'landmarks': None
        }

        if results.multi_hand_landmarks:
            gesture_data['hand_detected'] = True
            hand_landmarks = results.multi_hand_landmarks[0]
            gesture_data['landmarks'] = hand_landmarks

            # Vẽ 21 Landmarks lên hình ảnh preview
            self.mp_drawing.draw_landmarks(
                frame_bgr,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )

            # Lấy tọa độ Landmark 4 (Thumb Tip), Landmark 8 (Index Tip), Landmark 12 (Middle Tip)
            thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            # Tọa độ pixel thực tế
            t_x, t_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            i_x, i_y = int(index_tip.x * w), int(index_tip.y * h)
            m_x, m_y = int(middle_tip.x * w), int(middle_tip.y * h)

            # --- CỬ CHỈ 1: PINCH XOAY (Ngón cái + Ngón trỏ) ---
            dist_rotate = math.sqrt(
                (thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2
            )
            gesture_data['pinch_distance'] = dist_rotate

            # Điểm trung tâm giữa Ngón cái & Ngón trỏ
            mid_rot_x = (thumb_tip.x + index_tip.x) / 2.0
            mid_rot_y = (thumb_tip.y + index_tip.y) / 2.0

            # --- CỬ CHỈ 2: PINCH ZOOM (Ngón cái + Ngón giữa) ---
            dist_zoom = math.sqrt(
                (thumb_tip.x - middle_tip.x) ** 2 + (thumb_tip.y - middle_tip.y) ** 2
            )
            gesture_data['zoom_pinch_distance'] = dist_zoom

            # Điểm trung tâm giữa Ngón cái & Ngón giữa
            mid_zoom_x = (thumb_tip.x + middle_tip.x) / 2.0
            mid_zoom_y = (thumb_tip.y + middle_tip.y) / 2.0

            # ============================================================
            # Ưu tiên: Nếu cả 2 cử chỉ cùng active, ưu tiên ZOOM
            # ============================================================

            rotate_active = dist_rotate < self.pinch_threshold
            zoom_active = dist_zoom < self.pinch_threshold

            # --- XỬ LÝ CỬ CHỈ ZOOM (ƯU TIÊN CAO) ---
            if zoom_active:
                current_is_zoom = True

                # Vẽ đường Zoom màu Cyan neon
                cv2.line(frame_bgr, (t_x, t_y), (m_x, m_y), (255, 255, 0), 4)
                cv2.circle(frame_bgr, (int(mid_zoom_x * w), int(mid_zoom_y * h)), 10, (255, 255, 0), -1)

                if not self.is_zoom_pinching:
                    # Bắt đầu Zoom mới
                    self.last_zoom_pos = (mid_zoom_x, mid_zoom_y)
                    self.is_zoom_pinching = True
                else:
                    # Đang Zoom: di chuyển lên = phóng to, xuống = thu nhỏ
                    if self.last_zoom_pos is not None:
                        lx, ly = self.last_zoom_pos
                        diff_y = mid_zoom_y - ly

                        # dy âm (kéo tay lên trên) -> Phóng to (zoom in, delta > 0)
                        # dy dương (kéo tay xuống dưới) -> Thu nhỏ (zoom out, delta < 0)
                        raw_delta_zoom = -diff_y * self.sensitivity * 0.8

                        # Áp dụng bộ lọc làm mượt Low-pass Filter
                        self.current_delta_zoom = (
                            self.smooth_alpha * raw_delta_zoom +
                            (1 - self.smooth_alpha) * self.current_delta_zoom
                        )
                        gesture_data['delta_zoom'] = self.current_delta_zoom

                        self.last_zoom_pos = (mid_zoom_x, mid_zoom_y)

                gesture_data['is_zoom_pinching'] = True

                # Reset rotate state khi zoom active
                self.is_pinching = False
                self.last_pinch_pos = None
                self.current_delta_yaw = 0.0
                self.current_delta_pitch = 0.0

                # Hiển thị trạng thái Zoom trên preview
                zoom_dir = "ZOOM IN" if gesture_data['delta_zoom'] > 0.5 else ("ZOOM OUT" if gesture_data['delta_zoom'] < -0.5 else "ZOOM HOLD")
                cv2.putText(frame_bgr, "ZOOM: " + zoom_dir, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            # --- XỬ LÝ CỬ CHỈ XOAY (Thumb + Index) ---
            elif rotate_active:
                # Báo hiệu đường nối màu xanh neon lá tươi nếu đang Pinch
                cv2.line(frame_bgr, (t_x, t_y), (i_x, i_y), (0, 255, 0), 4)
                cv2.circle(frame_bgr, (int(mid_rot_x * w), int(mid_rot_y * h)), 8, (0, 255, 0), -1)

                if not self.is_pinching:
                    # Mới bắt đầu Pinch -> Lưu vị trí gốc ban đầu
                    self.last_pinch_pos = (mid_rot_x, mid_rot_y)
                    self.is_pinching = True
                else:
                    # Đang tiếp tục Pinch -> Tính độ dời delta
                    if self.last_pinch_pos is not None:
                        lx, ly = self.last_pinch_pos
                        diff_x = mid_rot_x - lx
                        diff_y = mid_rot_y - ly

                        # dx dương (kéo tay sang phải) -> Xoay Yaw dương
                        # dy dương (kéo tay xuống dưới) -> Xoay Pitch dương
                        raw_delta_yaw = diff_x * self.sensitivity
                        raw_delta_pitch = diff_y * self.sensitivity

                        # Áp dụng bộ lọc làm mượt Low-pass Filter
                        self.current_delta_yaw = (self.smooth_alpha * raw_delta_yaw +
                                                  (1 - self.smooth_alpha) * self.current_delta_yaw)
                        self.current_delta_pitch = (self.smooth_alpha * raw_delta_pitch +
                                                    (1 - self.smooth_alpha) * self.current_delta_pitch)

                        gesture_data['delta_yaw'] = self.current_delta_yaw
                        gesture_data['delta_pitch'] = self.current_delta_pitch

                        # Cập nhật vị trí mốc cho frame tiếp theo
                        self.last_pinch_pos = (mid_rot_x, mid_rot_y)

                gesture_data['is_pinching'] = True

                # Reset zoom state khi rotate active
                self.is_zoom_pinching = False
                self.last_zoom_pos = None
                self.current_delta_zoom = 0.0

                # Hiển thị trạng thái Rotate trên preview
                cv2.putText(frame_bgr, "ROTATE: ACTIVE", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            else:
                # Không chụm tay => vẽ đường đỏ chỉ thị Idle
                cv2.line(frame_bgr, (t_x, t_y), (i_x, i_y), (0, 0, 255), 2)
                cv2.line(frame_bgr, (t_x, t_y), (m_x, m_y), (0, 0, 180), 1)

                # Reset tất cả trạng thái
                self.is_pinching = False
                self.last_pinch_pos = None
                self.current_delta_yaw = 0.0
                self.current_delta_pitch = 0.0

                self.is_zoom_pinching = False
                self.last_zoom_pos = None
                self.current_delta_zoom = 0.0

            # Hiển thị thông tin khoảng cách
            info_y = h - 20
            cv2.putText(frame_bgr,
                        "Rotate(T+I): " + "{:.3f}".format(dist_rotate) + " | Zoom(T+M): " + "{:.3f}".format(dist_zoom),
                        (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

        else:
            # Không tìm thấy bàn tay
            self.is_pinching = False
            self.last_pinch_pos = None
            self.current_delta_yaw = 0.0
            self.current_delta_pitch = 0.0

            self.is_zoom_pinching = False
            self.last_zoom_pos = None
            self.current_delta_zoom = 0.0

        return frame_bgr, gesture_data
