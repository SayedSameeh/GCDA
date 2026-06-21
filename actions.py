import pyautogui
import keyboard
import screen_brightness_control as sbc
import time

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)


class SystemActions:

    def __init__(self):

        # =====================
        # Mouse Settings
        # =====================

        pyautogui.FAILSAFE = False

        self.screen_width, self.screen_height = (
            pyautogui.size()
        )

        self.prev_x = 0
        self.prev_y = 0

        self.smoothing = 0.25


        # =====================
        # Volume Setup
        # =====================

        device = AudioUtilities.GetSpeakers()

        interface = device.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        self.volume = cast(
            interface,
            POINTER(IAudioEndpointVolume)
        )


        self.min_volume, self.max_volume = (
            self.volume.GetVolumeRange()[:2]
        )


        self.last_volume_change = 0
        self.volume_cooldown = 0.03


        # =====================
        # Brightness Setup
        # =====================

        self.last_brightness_change = 0
        self.brightness_cooldown = 0.03


    # ==================================
    # Mouse Controls
    # ==================================

    def move_mouse(
        self,
        x,
        y,
        cam_width,
        cam_height
    ):

        target_x = (
            x / cam_width
        ) * self.screen_width


        target_y = (
            y / cam_height
        ) * self.screen_height


        smooth_x = (
            self.prev_x +
            (target_x - self.prev_x)
            * self.smoothing
        )


        smooth_y = (
            self.prev_y +
            (target_y - self.prev_y)
            * self.smoothing
        )


        pyautogui.moveTo(
            smooth_x,
            smooth_y,
            duration=0
        )


        self.prev_x = smooth_x
        self.prev_y = smooth_y


    def left_click(self):

        pyautogui.click()


    def right_click(self):

        pyautogui.rightClick()


    def scroll(self, amount):

        pyautogui.scroll(amount)


    # ==================================
    # Media Controls
    # ==================================

    def play_pause(self):

        keyboard.send(
            "play/pause media"
        )


    def next_track(self):

        keyboard.send(
            "next track"
        )


    def previous_track(self):

        keyboard.send(
            "previous track"
        )


    # ==================================
    # Volume Controls
    # ==================================

    def volume_up(self):

        current_time = time.time()


        if (
            current_time -
            self.last_volume_change
            <
            self.volume_cooldown
        ):
            return


        current_volume = (
            self.volume.GetMasterVolumeLevel()
        )


        new_volume = min(
            current_volume + 1.5,
            self.max_volume
        )


        self.volume.SetMasterVolumeLevel(
            new_volume,
            None
        )


        self.last_volume_change = current_time


    def volume_down(self):

        current_time = time.time()


        if (
            current_time -
            self.last_volume_change
            <
            self.volume_cooldown
        ):
            return


        current_volume = (
            self.volume.GetMasterVolumeLevel()
        )


        new_volume = max(
            current_volume - 1.5,
            self.min_volume
        )


        self.volume.SetMasterVolumeLevel(
            new_volume,
            None
        )


        self.last_volume_change = current_time


    # ==================================
    # Brightness Controls
    # ==================================

    def brightness_up(self):

        current_time = time.time()


        if (
            current_time -
            self.last_brightness_change
            <
            self.brightness_cooldown
        ):
            return


        current = sbc.get_brightness()[0]


        sbc.set_brightness(
            min(
                current + 3,
                100
            )
        )


        self.last_brightness_change = (
            current_time
        )


    def brightness_down(self):

        current_time = time.time()


        if (
            current_time -
            self.last_brightness_change
            <
            self.brightness_cooldown
        ):
            return


        current = sbc.get_brightness()[0]


        sbc.set_brightness(
            max(
                current - 3,
                0
            )
        )


        self.last_brightness_change = (
            current_time
        )
        