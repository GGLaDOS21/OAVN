


class Signal_Information: #AKA lightpath
    def __init__(self, signal_power, path):
        self.signal_power = signal_power
        self.noise_power = 0.0
        self.latency = 0.0
        self.path = []
        self.channel = None
        self.pos = 0

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
    def getRs(self):
        return self.Rs
    def setRS(self,rs):
        self.Rs = rs
    def setCnannel(self, channel):
        self.channel = channel
    def getChannel(self):
        return self.channel
    def setPower(self, power):
        self.signal_power = power

    def noisePowUpdate(self, increment):
        self.noise_power += increment

    def latencyUpdate(self, increment):
        self.latency += increment



    def nextHop(self):
        if len(self.path) == self.pos:
            return None
        ret = self.pos
        self.pos = self.pos + 1
        return self.path[ret]

    def nextNode(self):     #chiamato solo dalla propagate in line
        return self.path[self.pos-1]

    def getPath(self):
        return self.path

    def getPath_with_arrow(self):
        s= ""
        for i in range(0, len(self.path)):
            s = s+self.path[i]
            if i != (len(self.path)-1):
                s = s + "->"
        return s
