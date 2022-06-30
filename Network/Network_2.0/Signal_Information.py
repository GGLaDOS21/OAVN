


class Signal_Information:
    def __init__(self, signal_power, path):
        self.signal_power = signal_power
        self.noise_power = 0.0
        self.latency = 0.0
        self.path = []
        for p in path:
            self.path.append(p)
        self.Rs = 0.0   #signal symbol rate
        self.df = 0.0   #frequency spacing between 2 consecutive channel

    def getLatency(self):
        return self.latency
    def getNoise(self):
        return self.noise_power
    def getPower(self):
        return self.signal_power
    def getChannel(self):
        return self.channel

    def sigPowUpdate(self, increment):
        self.signal_power += increment

    def noisePowUpdate(self, increment):
        self.noise_power += increment

    def latencyUpdate(self, increment):
        self.latency += increment

    def pathUpdate(self):
        return self.path.pop(0)

    def nextHop(self):
        if len(self.path) == 0:
            return None
        return self.path[0]
