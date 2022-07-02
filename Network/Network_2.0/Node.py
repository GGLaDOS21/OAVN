

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
        if signal.pathUpdate() == self.label:
            nextNode = signal.nextHop()
            if nextNode is None:
                return
            for nodes in self.connected_nodes:
                if nodes == nextNode:
                    opt_power = self.successive[nextNode].get_optimal_power()   #il nodo legge la potenza ottimale della linea
                    signal.setPower(opt_power)                                  #e imposta la potenza del segnale di conseguenza
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