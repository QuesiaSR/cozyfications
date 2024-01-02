class CozyException(Exception):
    def __init__(self, message):
        self.args = message


class TwitchChannelNotFound(CozyException):
    def __init__(self):
        super().__init__("Channel not found.")


class TwitchChannelAlreadySelected(CozyException):
    def __init__(self):
        super().__init__("Channel already selected.")


class TwitchChannelNotSelected(CozyException):
    def __init__(self):
        super().__init__("Channel not selected.")
