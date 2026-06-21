import json
import customtkinter as ctk

from config_manager import ConfigManager


class SettingsWindow(ctk.CTk):

    def __init__(self):

        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("GCDA V4 Settings")
        self.geometry("700x650")

        self.config_manager = ConfigManager()

        self.options = [
            "PLAY_PAUSE",
            "NEXT_TRACK",
            "PREVIOUS_TRACK",
            "LEFT_CLICK",
            "RIGHT_CLICK",
            "MOVE_MOUSE",
            "VOLUME_UP",
            "VOLUME_DOWN",
            "BRIGHTNESS_UP",
            "BRIGHTNESS_DOWN",
            "OPEN_NOTEPAD",
            "OPEN_CALCULATOR",
            "EXIT",
            "TOGGLE_SLEEP",
            "NONE"
        ]

        self.dropdowns = {}

        title = ctk.CTkLabel(
            self,
            text="GCDA Gesture Settings",
            font=("Arial", 26, "bold")
        )
        title.pack(pady=15)


        self.scroll = ctk.CTkScrollableFrame(
            self,
            width=620,
            height=420
        )
        self.scroll.pack(padx=10, pady=10)


        self.build_settings()


        self.status = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 14)
        )
        self.status.pack(pady=10)


        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)


        ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            width=180,
            height=40
        ).pack(
            side="left",
            padx=10
        )


        ctk.CTkButton(
            button_frame,
            text="Reset Default",
            command=self.reset_default,
            width=180,
            height=40
        ).pack(
            side="left",
            padx=10
        )


        self.check_conflicts()


    # ==========================
    # Build gesture rows
    # ==========================
    def build_settings(self):

        for widget in self.scroll.winfo_children():
            widget.destroy()

        self.dropdowns.clear()

        for gesture, action in self.config_manager.get_all().items():

            row = ctk.CTkFrame(self.scroll)

            row.pack(
                fill="x",
                padx=10,
                pady=6
            )


            label = ctk.CTkLabel(
                row,
                text=gesture,
                width=250,
                anchor="w"
            )

            label.pack(
                side="left",
                padx=15
            )


            dropdown = ctk.CTkOptionMenu(
                row,
                values=self.options,
                command=lambda value: self.check_conflicts()
            )


            # Store original theme color
            dropdown.default_color = dropdown.cget("fg_color")


            dropdown.set(action)


            dropdown.pack(
                side="right",
                padx=15
            )


            self.dropdowns[gesture] = dropdown


    # ==========================
    # Save settings
    # ==========================

    def save_settings(self):

        for gesture, dropdown in self.dropdowns.items():

            self.config_manager.set_action(
                gesture,
                dropdown.get()
            )


        self.config_manager.save()


        conflicts = self.get_conflict_count()


        if conflicts == 0:

            self.status.configure(
                text="✓ Settings saved successfully",
                text_color="light green"
            )

        else:

            self.status.configure(
                text=f"⚠ Saved with {conflicts} conflicting controls",
                text_color="orange"
            )


    # ==========================
    # Reset to default
    # ==========================

    def reset_default(self):

        with open(
            "default_config.json",
            "r"
        ) as file:

            defaults = json.load(file)


        self.config_manager.config = defaults


        self.config_manager.save()


        self.build_settings()


        self.check_conflicts()


        self.status.configure(
            text="✓ Restored default controls",
            text_color="light green"
        )


    # ==========================
    # Count conflicts
    # ==========================

    def get_conflict_count(self):

        actions = {}


        for dropdown in self.dropdowns.values():

            action = dropdown.get()

            actions[action] = actions.get(action, 0) + 1


        conflicts = 0


        for count in actions.values():

            if count > 1:

                conflicts += 1


        return conflicts


    # ==========================
    # Highlight conflicts
    # ==========================

    def check_conflicts(self):

        actions = {}


        # Reset colors
        for dropdown in self.dropdowns.values():

            dropdown.configure(
                fg_color=dropdown.default_color
            )


        # Group same actions
        for dropdown in self.dropdowns.values():

            action = dropdown.get()


            if action not in actions:

                actions[action] = []


            actions[action].append(dropdown)


        # Highlight duplicates
        for group in actions.values():

            if len(group) > 1:

                for dropdown in group:

                    dropdown.configure(
                        fg_color="#B03030"
                    )


        conflicts = self.get_conflict_count()


        if conflicts == 0:

            self.status.configure(
                text="✓ No conflicting controls",
                text_color="light green"
            )

        else:

            self.status.configure(
                text=f"⚠ {conflicts} conflicting action(s) detected",
                text_color="red"
            )


if __name__ == "__main__":

    app = SettingsWindow()

    app.mainloop()