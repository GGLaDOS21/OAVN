

class Connection:
    def __init__(self, input_node, output_node, signal_power, frequency):
        self.LightPath = None
        self.input = input_node
        self.output = output_node
        self.signal_power = signal_power
        self.latency = 0.0
        self.snr = 0.0
        self.frequency = frequency
        self.bitRate = 0

    def getPower(self):
        return self.signal_power

    def getFrequency(self):
        return self.frequency

    def getInput(self):
        return self.input

    def getOutput(self):
        return self.output

    def setLatency(self, latency):
        self.latency = latency

    def getLatency(self):
        return self.latency

    def setSnr(self, snr):
        self.snr = snr

    def getSnr(self):
        return self.snr

    def setBitRate(self, bitRate):
        self.bitRate = bitRate

    def getBitRate(self):
        return  self.bitRate

    def addLightPath(self, lp):
        self.LightPath = lp

    def getLight(self):
        return self.LightPath