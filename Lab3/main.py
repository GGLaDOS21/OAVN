import json
import math
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

class Signal_information:
    def __init__(self, signal_power, path):
        self.signal_power = signal_power
        self.noise_power = 0.0
        self.latency = 0.0
        self.path = []
        for p in path:
            self.path.append(p)
    def getLatency(self):
        return self.latency
    def getNoise(self):
        return self.noise_power
    def getPower(self):
        return self.signal_power

    def sigPowUpdate(self, increment):
        self.signal_power += increment

    def noisePowUpdate(self, increment):
        self.noise_power += increment

    def latencyUpdate(self, increment):
        self.latency += increment

    def pathUpdate(self):
        return self.path.pop(0)

    def nextHop(self):
        if(len(self.path) == 0):
            return None
        return self.path[0]

class Node:
    def __init__(self, values):
        self.label = values["label"]
        self.position = values["position"]
        self.connected_nodes = values["connected_nodes"]
        self.successive = {}

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

class Line:
    def __init__(self, label, length):
        self.label = label
        self.length = length
        self.successive = {}

    def latency_generation(self, signal):
        signal.latencyUpdate(self.length/200000)

    def noise_generation(self, signal):
        signal.noisePowUpdate(signal.signal_power * self.length * math.pow(10, -9))

    def propagate(self, signal):
        self.noise_generation(signal)
        self.latency_generation(signal)
        node = signal.nextHop()
        self.successive[node].propagate(signal)


class Network:
    def __init__(self, filename):
        self.nodes = {}
        self.lines = {}
        with open(filename, "r") as file:
            dict = json.load(file)

        for node in dict:
            dict[node].update({"label": node})
            n = Node(dict[node])
            self.nodes.update({node: n})

        for node in self.nodes:
            for conn in self.nodes[node].connected_nodes:
                if((node + conn) in self.lines):
                    continue
                if((conn + node) in self.lines):
                    continue
                label = node + conn
                node1 = self.nodes[node]
                node2 = self.nodes[conn]
                dist = math.sqrt(math.pow(node1.position[0] - node2.position[0], 2) + math.pow(node1.position[1] - node2.position[1], 2))
                ln = Line(label, dist)
                self.lines.update({label: ln})

    def get_nodes(self):
        return self.nodes

    def connect(self):
        for key in self.nodes:
            node = self.nodes[key]
            for conn in node.connected_nodes:
                lbl = key + conn
                if(lbl in self.lines):
                    line = self.lines[lbl]
                else:
                    lbl = conn + key
                    line = self.lines[lbl]
                node.successive.update({conn: line})
                line.successive.update({conn: self.nodes[conn]})
                line.successive.update({key: node})

    def find_path(self, nA, nB):
        nodeA = self.nodes[nA]
        nodeB = self.nodes[nB]

        listaR = []
        listaP = []
        self.pathRec(listaR, listaP, nodeA, nodeB)
        return listaR

    def pathRec(self, listaR, listaP, nodeA, nodeB):
        listaP.append(nodeA.label)
        for node in nodeA.connected_nodes:
            if node in listaP:                 #evita il backtrack
                continue
            if node == nodeB.label:            #se abbiamo trovato la fine
                listaP.append(node)
                listaR.append(listaP.copy())
                listaP.remove(node)
            else:
                newnode = self.nodes[node]
                self.pathRec(listaR, listaP, newnode, nodeB)
        listaP.remove(nodeA.label)

    def propagate(self, signal):
        startNode = signal.nextHop()
        self.nodes[startNode].propagate(signal)
        #verificare: il segnale dovrebbe contenere tutte le informazioni di intyerferenza

    def draw(self):
        for key in self.nodes:
            node = self.nodes[key]
            plt.plot(node.position[0], node.position[1], marker="o", markersize=10, markerfacecolor="white")
            plt.annotate(key,(node.position[0], node.position[1]))
        for key in self.nodes:
            node = self.nodes[key]
            for conn in node.connected_nodes:
                node2 = self.nodes[conn]
                plt.plot((node.position[0], node2.position[0]),(node.position[1], node2.position[1]), linestyle= '-', linewidth= 2)




net = Network("nodes.json")
net.connect()
#net.draw()
#plt.show()
dict_list = {}
nodes = net.get_nodes()
table_data = {}
for key1 in nodes:
    for key2 in nodes:
        if (key1 != key2):
            if(key1 + key2) in dict_list:
                continue
            if(key2 + key1) in dict_list:
                continue
            dict_list.update({(key1 + key2): net.find_path(key1, key2)})
for key in dict_list:
    path_list = dict_list[key]
    for path in path_list:
        signal = Signal_information(1*math.pow(10,-3),path)
        net.propagate(signal)
        signal_data={"Latency": signal.getLatency(),"Noise": signal.getNoise(),"Signal/Noise(dB)": 10 * math.log10(signal.getPower()/signal.getNoise())}
        table_data.update({key: signal_data})
dataframe = pd.DataFrame(table_data)

print(dataframe)


















