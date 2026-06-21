import cv2
import mediapipe as mp
import math
import time


class HandTracker:

    def __init__(self):

        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        RunningMode = mp.tasks.vision.RunningMode


        options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path="hand_landmarker.task"
            ),

            # Track both hands
            num_hands=2,

            # VIDEO MODE 🔥
            running_mode=RunningMode.VIDEO,

            # Higher confidence
            min_hand_detection_confidence=0.8,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7
        )


        self.landmarker = (
            HandLandmarker.create_from_options(
                options
            )
        )


        # Video timestamps
        self.frame_timestamp = 0


        # FPS
        self.prev_time = 0


        # Landmark smoothing
        self.previous_landmarks = {}

        # 0 = no smoothing
        # 1 = extremely slow
        self.smoothing = 0.6


    def get_frame(self, frame):

        frame = cv2.flip(frame, 1)


        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )


        # VIDEO mode requires timestamps
        self.frame_timestamp += 33


        result = self.landmarker.detect_for_video(
            mp_image,
            self.frame_timestamp
        )


        hands_data = []

        h, w, _ = frame.shape


        if result.hand_landmarks:


            for i, hand in enumerate(result.hand_landmarks):


                handedness = (
                    result.handedness[i][0]
                    .category_name
                )


                # Fix mirrored camera
                if handedness == "Left":
                    handedness = "Right"
                else:
                    handedness = "Left"


                landmarks = []


                for idx, point in enumerate(hand):

                    x = int(point.x * w)
                    y = int(point.y * h)


                    # ==================
                    # Landmark smoothing
                    # ==================

                    key = f"{handedness}_{idx}"


                    if key in self.previous_landmarks:

                        old_x, old_y = (
                            self.previous_landmarks[key]
                        )


                        x = int(
                            old_x * self.smoothing +
                            x * (1 - self.smoothing)
                        )

                        y = int(
                            old_y * self.smoothing +
                            y * (1 - self.smoothing)
                        )


                    self.previous_landmarks[key] = (
                        x,
                        y
                    )


                    landmarks.append(
                        (idx, x, y)
                    )


                    cv2.circle(
                        frame,
                        (x, y),
                        4,
                        (0, 255, 0),
                        -1
                    )


                # Label hand
                cv2.putText(
                    frame,
                    handedness,
                    (
                        landmarks[0][1],
                        landmarks[0][2] - 20
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 0),
                    2
                )


                hands_data.append(
                    {
                        "hand": handedness,
                        "landmarks": landmarks
                    }
                )


        # ==================
        # FPS Counter
        # ==================

        current = time.time()


        if self.prev_time:
            fps = int(
                1 / (current - self.prev_time)
            )
        else:
            fps = 0


        self.prev_time = current


        cv2.putText(
            frame,
            f"FPS: {fps}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )


        return frame, hands_data


    def distance(self, p1, p2, landmarks):

        if len(landmarks) < 21:
            return 0


        x1 = landmarks[p1][1]
        y1 = landmarks[p1][2]

        x2 = landmarks[p2][1]
        y2 = landmarks[p2][2]


        return math.hypot(
            x2 - x1,
            y2 - y1
        )


    def fingers_up(self, landmarks, hand):

        if len(landmarks) < 21:
            return [0, 0, 0, 0, 0]


        fingers = []


        # Thumb depends on hand
        if hand == "Right":

            fingers.append(
                1 if landmarks[4][1] > landmarks[3][1]
                else 0
            )

        else:

            fingers.append(
                1 if landmarks[4][1] < landmarks[3][1]
                else 0
            )


        # Other fingers
        tips = [8, 12, 16, 20]
        joints = [6, 10, 14, 18]


        for tip, joint in zip(
            tips,
            joints
        ):

            fingers.append(
                1 if landmarks[tip][2] < landmarks[joint][2]
                else 0
            )


        return fingers


    def close(self):

        self.landmarker.close()