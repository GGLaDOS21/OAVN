from Signal_Information import Signal_Information

class LightPath(Signal_Information):
    def __int__(self, signal_power, path, channel):
        super().__init__(signal_power, path)
        self.channel = channel

    def getChannel(self):
        return self.channel