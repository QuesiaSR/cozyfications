class CozyException(Exception):
    def __init__(self, message):
        pass

class TwitchChannelNotFound(CozyException): pass
class TwitchChannelAlreadySelected(CozyException): pass
class TwitchChannelNotSelected(CozyException): pass
