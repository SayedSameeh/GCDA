import time


class GestureEngine:

    def __init__(self):

        # =========================
        # System state
        # =========================

        self.active = True

        self.fist_start = None
        self.sleep_hold = 2.0
        self.sleep_progress = 0


        # =========================
        # Left hand state
        # =========================

        self.left = {
            "index_start": None,
            "middle_start": None,
            "index_drag": False,
            "middle_drag": False,
            "index_y": 0,
            "middle_y": 0
        }


        # =========================
        # Right hand state
        # =========================

        self.right = {
            "previous_x": None,
            "last_action": 0
        }


        self.cooldown = 0.7
        self.hold_time = 0.4
        self.drag_threshold = 30


    def detect(self, hand, fingers, tracker, landmarks):

        now = time.time()


        # =========================
        # Global Sleep Gesture
        # =========================

        if fingers == [0,0,0,0,0]:

            if self.fist_start is None:
                self.fist_start = now


            elapsed = now - self.fist_start


            self.sleep_progress = min(
                elapsed / self.sleep_hold,
                1
            )


            if elapsed >= self.sleep_hold:

                self.active = not self.active

                self.fist_start = None
                self.sleep_progress = 0


                return "GLOBAL_SLEEP"


        else:

            self.fist_start = None
            self.sleep_progress = 0


        # Sleeping ignores everything
        if not self.active:
            return "NONE"


        # =========================
        # RIGHT HAND
        # =========================

        if hand == "Right":

            # 👍 Thumb up
            if (
                fingers == [1,0,0,0,0]
                and now - self.right["last_action"]
                > self.cooldown
            ):

                self.right["last_action"] = now

                return "RIGHT_THUMB_UP"


            # 🖕 Middle finger
            if fingers == [0,0,1,0,0]:

                return "RIGHT_MIDDLE_FINGER"


            # Swipe detection
            current_x = landmarks[9][1]


            if self.right["previous_x"] is not None:

                movement = (
                    current_x -
                    self.right["previous_x"]
                )


                if (
                    abs(movement) > 100
                    and now - self.right["last_action"]
                    > self.cooldown
                ):

                    self.right["last_action"] = now

                    self.right["previous_x"] = current_x


                    if movement > 0:

                        return (
                            "RIGHT_SWIPE_RIGHT"
                        )

                    else:

                        return (
                            "RIGHT_SWIPE_LEFT"
                        )


            self.right["previous_x"] = current_x



        # =========================
        # LEFT HAND
        # =========================

        elif hand == "Left":


            index_distance = tracker.distance(
                4, 8, landmarks
            )


            middle_distance = tracker.distance(
                4, 12, landmarks
            )


            # =====================
            # Index pinch
            # =====================

            if index_distance < 35:


                if self.left["index_start"] is None:

                    self.left["index_start"] = now

                    self.left["index_y"] = (
                        landmarks[8][2]
                    )


                elif (
                    now -
                    self.left["index_start"]
                    > self.hold_time
                ):

                    self.left["index_drag"] = True


                    movement = (
                        self.left["index_y"]
                        -
                        landmarks[8][2]
                    )


                    if abs(movement) > self.drag_threshold:


                        self.left["index_y"] = (
                            landmarks[8][2]
                        )


                        if movement > 0:

                            return (
                                "LEFT_INDEX_DRAG_UP"
                            )

                        else:

                            return (
                                "LEFT_INDEX_DRAG_DOWN"
                            )


            else:


                if (
                    self.left["index_start"]
                    and
                    not self.left["index_drag"]
                ):

                    self.left["index_start"] = None

                    return (
                        "LEFT_INDEX_PINCH"
                    )


                self.left["index_start"] = None

                self.left["index_drag"] = False



            # =====================
            # Middle pinch
            # =====================

            if middle_distance < 35:


                if (
                    self.left["middle_start"]
                    is None
                ):

                    self.left["middle_start"] = now

                    self.left["middle_y"] = (
                        landmarks[12][2]
                    )


                elif (
                    now -
                    self.left["middle_start"]
                    > self.hold_time
                ):


                    self.left["middle_drag"] = True


                    movement = (
                        self.left["middle_y"]
                        -
                        landmarks[12][2]
                    )


                    if abs(movement) > self.drag_threshold:


                        self.left["middle_y"] = (
                            landmarks[12][2]
                        )


                        if movement > 0:

                            return (
                                "LEFT_MIDDLE_DRAG_UP"
                            )

                        else:

                            return (
                                "LEFT_MIDDLE_DRAG_DOWN"
                            )


            else:


                if (
                    self.left["middle_start"]
                    and
                    not self.left["middle_drag"]
                ):

                    self.left["middle_start"] = None

                    return (
                        "LEFT_MIDDLE_PINCH"
                    )


                self.left["middle_start"] = None

                self.left["middle_drag"] = False


            # Mouse movement
            if fingers == [0,1,0,0,0]:

                return "LEFT_MOUSE_MOVE"


        return "NONE"