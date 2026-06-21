import json


class ConfigManager:


    def __init__(self):

        self.file = "config.json"

        self.config = {}

        self.load()


    def load(self):

        try:

            with open(
                self.file,
                "r"
            ) as f:

                self.config = json.load(f)


        except FileNotFoundError:

            print(
                "config.json not found"
            )

            self.config = {}


    def get_action(self, gesture):

        return self.config.get(
            gesture,
            None
        )


    def set_action(self, gesture, action):

        self.config[gesture] = action


    def save(self):

        with open(
            self.file,
            "w"
        ) as f:

            json.dump(
                self.config,
                f,
                indent=4
            )


    def get_all(self):

        return self.config