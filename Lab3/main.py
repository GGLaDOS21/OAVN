import json
import math

class Signal_information:
    def __init__(self, signal_power, path):
        self.signal_power = signal_power
        self.noise_power = 0.0
        self.latency = 0.0
        self.path = []
        for p in path:
            self.path.append(p)

    def sigPowUpdate(self, increment):
        self.signal_power += increment

    def noisePowUpdate(self, increment):
        self.noise_power += increment

    def latencyUpdate(self, increment):
        self.latency += increment

    def pathUpdate(self):
        return self.path.pop(0)

    def nextHop(self):
        return self.path[0]

class Node:
    def __init__(self, values):
        self.label = values["label"]
        self.position = values["position"]
        self.connected_nodes = values["connected_nodes"]
        self.successive = {}

    def propagate(self, signal):
        if signal.pathUpdate == self.label:
            nextNode = signal.nextHop
            for nodes in self.connected_nodes:
                if nodes == nextNode:
                    self.successive[nextNode].propagate
        else:
            print("Error during propagation")

class Line:
    def __init__(self, label, length):
        self.label = label
        self.length = length
        self.successive = {}

    def latency_generation(self, signal):
        signal.latencyUpdate(signal, self.length/200000)

    def noise_generation(self, signal):
        signal.noisePowUpdate(signal.signal_power * self.length * 10^(-9))

    def propagate(self, signal):
        self.noise_generation(signal)
        self.latency_generation(signal)
        node = signal.nextHop()
        self.successive[node].propagate


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
                label = node + conn
                node1 = self.nodes[node]
                node2 = self.nodes[conn]
                dist = math.sqrt(math.pow(node1.position[0] - node2.position[0], 2) + math.pow(node1.position[1] - node2.position[1], 2))
                ln = Line(label, dist)
                self.lines.update({label: ln})


net = Network("nodes.json")
