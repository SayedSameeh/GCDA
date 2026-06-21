import cv2
import sys

from hand_tracker import HandTracker
from gesture_engine import GestureEngine
from actions import SystemActions

from config_manager import ConfigManager
from action_manager import ActionManager


def draw_hud(frame, engine, last_action):

    overlay = frame.copy()


    cv2.rectangle(
        overlay,
        (10, 10),
        (400, 230),
        (25, 25, 25),
        -1
    )


    cv2.addWeighted(
        overlay,
        0.6,
        frame,
        0.4,
        0,
        frame
    )


    status = (
        "ACTIVE"
        if engine.active
        else "SLEEP"
    )


    color = (
        (0,255,0)
        if engine.active
        else (0,0,255)
    )


    cv2.putText(
        frame,
        "GCDA V4",
        (25, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,0),
        2
    )


    cv2.putText(
        frame,
        f"STATUS: {status}",
        (25, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2
    )


    cv2.putText(
        frame,
        "LEFT : SYSTEM",
        (25, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255,255,255),
        2
    )


    cv2.putText(
        frame,
        "RIGHT: MEDIA",
        (25, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255,255,255),
        2
    )


    cv2.putText(
        frame,
        f"LAST: {last_action}",
        (25, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0,255,255),
        2
    )


    # Sleep progress bar

    if engine.sleep_progress > 0:

        cv2.rectangle(
            frame,
            (25, 205),
            (275, 220),
            (255,255,255),
            2
        )


        fill = int(
            250 * engine.sleep_progress
        )


        cv2.rectangle(
            frame,
            (25, 205),
            (25 + fill, 220),
            (0,200,255),
            -1
        )


def main():

    cap = cv2.VideoCapture(0)

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )


    if not cap.isOpened():

        print("Camera failed.")

        return


    # ==========================
    # Initialize modules
    # ==========================

    tracker = HandTracker()

    gestures = GestureEngine()

    actions = SystemActions()

    config = ConfigManager()

    executor = ActionManager(actions)


    last_action = "NONE"


    print("GCDA V4 ONLINE")


    running = True


    while running:


        success, frame = cap.read()


        if not success:

            break


        frame, hands = tracker.get_frame(frame)


        for hand_data in hands:


            hand = hand_data["hand"]

            landmarks = hand_data["landmarks"]


            fingers = tracker.fingers_up(
                landmarks,
                hand
            )


            gesture = gestures.detect(
                hand,
                fingers,
                tracker,
                landmarks
            )


            if gesture == "NONE":

                continue


            last_action = gesture


            # =========================
            # Mouse is special
            # =========================

            if gesture == "LEFT_MOUSE_MOVE":

                actions.move_mouse(
                    landmarks[8][1],
                    landmarks[8][2],
                    frame.shape[1],
                    frame.shape[0]
                )

                continue


            # =========================
            # Config based actions
            # =========================

            action = config.get_action(
                gesture
            )


            # Exit handling
            if action == "EXIT":

                running = False

                break


            # Execute action
            executor.execute(
                action
            )


        draw_hud(
            frame,
            gestures,
            last_action
        )


        cv2.imshow(
            "GCDA V4",
            frame
        )


        if (
            cv2.waitKey(1)
            & 0xFF
            == ord("q")
        ):

            break


    # ==========================
    # Clean shutdown
    # ==========================

    cap.release()

    tracker.close()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()