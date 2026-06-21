import os


class ActionManager:


    def __init__(self, actions):

        self.actions = actions


        self.action_map = {

            # =====================
            # Mouse
            # =====================

            "LEFT_CLICK":
                self.actions.left_click,

            "RIGHT_CLICK":
                self.actions.right_click,


            # =====================
            # Media
            # =====================

            "PLAY_PAUSE":
                self.actions.play_pause,

            "NEXT_TRACK":
                self.actions.next_track,

            "PREVIOUS_TRACK":
                self.actions.previous_track,


            # =====================
            # Volume
            # =====================

            "VOLUME_UP":
                self.actions.volume_up,

            "VOLUME_DOWN":
                self.actions.volume_down,


            # =====================
            # Brightness
            # =====================

            "BRIGHTNESS_UP":
                self.actions.brightness_up,

            "BRIGHTNESS_DOWN":
                self.actions.brightness_down,


            # =====================
            # Applications
            # =====================

            "OPEN_NOTEPAD":
                lambda: os.system(
                    "notepad"
                ),

            "OPEN_CALCULATOR":
                lambda: os.system(
                    "calc"
                )
        }


    def execute(self, action):

        if action is None:

            return


        command = self.action_map.get(
            action
        )


        if command:

            command()


        else:

            print(
                f"Unknown action: {action}"
            )