

class Node:
    def __init__(self, values):
        self.label = values["label"]
        self.position = values["position"]
        self.connected_nodes = values["connected_nodes"]
        if "transceiver" in values:
            self.transceiver = values["transceiver"]
        else:
            self.transceiver = "fixed-rate"
        self.successive = {}

    def getLabel(self):
        return self.label
    def getTransceiverMode(self):
        return self.transceiver
    def setTransceiverMode(self, mode):
        self.transceiver = mode


    def propagate(self, signal):
        nextNode = signal.nextHop()
        if nextNode is None:
            return
        for nodes in self.connected_nodes:
            if nodes == nextNode:
                self.successive[nextNode].propagate(signal)
                break


    def probe(self, path, pathLenght, signal):          #usato pre creare la weightened table
        if len(path) == 0:
            return
        nextNode = path.pop(0)
        for nodes in self.connected_nodes:
            if nodes == nextNode:
                self.successive[nextNode].probe(path, pathLenght, signal)
                break
        return
