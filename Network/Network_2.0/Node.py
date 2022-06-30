

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

    #TO_DO: provare a impostare la potenza di ingresso della linea = alla optimized launch power
    def propagate(self, signal):
        if signal.pathUpdate() == self.label:
            nextNode = signal.nextHop()
            if(nextNode == None):
                return
            for nodes in self.connected_nodes:
                if nodes == nextNode:
                    self.successive[nextNode].propagate(signal)
                    break
        else:
            return

    def probe(self, path, pathLenght):          #usato pre creare la weightened table
        if len(path) == 0:
            return
        nextNode = path[0]
        for nodes in self.connected_nodes:
            if nodes == nextNode:
                self.successive[nextNode].probe(path, pathLenght)
                break
        return