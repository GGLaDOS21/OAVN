import json
import math
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import re
import sys

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

    def getLabel(self):
        return self.label

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

    def get_nodes_name(self):
        lis = []
        for node in self.nodes:
            lis.append(node)
        return lis


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
    def createDataframeFromSignal(self, signalPower):
        dict_list = {}
        table_data = {}
        for key1 in self.nodes:
            for key2 in self.nodes:
                if (key1 != key2):
                    if(key1 + key2) in dict_list:
                        continue
                    if(key2 + key1) in dict_list:
                        continue
                    dict_list.update({(key1 + key2): self.find_path(key1, key2)})
        for key in dict_list:
            path_list = dict_list[key]
            for path in path_list:
                signal = Signal_information(signalPower,path)
                self.propagate(signal)
                signal_data={"Latency": signal.getLatency(),"Noise": signal.getNoise(),"Signal/Noise(dB)": 10 * math.log10(signal.getPower()/signal.getNoise())}
                l = len(path)
                s = ""
                for n in path:
                    s = s + n
                    l = l-1
                    if l != 0:
                        s = s + "->"
                table_data.update({s: signal_data})
        self.weighted_paths = pd.DataFrame(table_data)
        return self.weighted_paths

    def find_best_snr(self, input_node, output_node):
        reg = re.compile("^" + re.escape(input_node) + ".*" + re.escape(output_node) + "$")
        save = 0.0
        for column in self.weighted_paths:
            if re.search(reg, column) != None:
                if self.weighted_paths[column]["Signal/Noise(dB)"] > save:
                    save = self.weighted_paths[column]["Signal/Noise(dB)"]
        return save

    def find_best_latency(self, input_node, output_node):
        reg = re.compile("^" + re.escape(input_node) + ".*" + re.escape(output_node) + "$")
        save = sys.float_info.max
        for column in self.weighted_paths:
            if re.search(reg, column) != None:
                if self.weighted_paths[column]["Signal/Noise(dB)"] < save:
                    save = self.weighted_paths[column]["Signal/Noise(dB)"]
        return save

    def stream(self, connectionList, label):
        for connection in connectionList:
            self.createDataframeFromSignal(connection.getPower())
            if label == "snr":
                connection.setSnr(self.find_best_snr(connection.getInput(), connection.getOutput()))
                connection.setLatency(self.find_Latency_given_snr(connection.getInput(), connection.getOutput(), connection.getSnr()))
            else:
                connection.setLatency(self.find_best_latency(connection.getInput(), connection.getOutput()))
                connection.setSnr(self.find_snr_given_latency(connection.getInput(), connection.getOutput(), connection.getLatency()))


    def find_snr_given_latency(self, input, output, latency):
        reg = re.compile("^" + re.escape(input) + ".*" + re.escape(output) + "$")
        for column in self.weighted_paths:
            if re.search(reg, column) != None:
                if self.weighted_paths[column]["Latency"] == latency:
                    return self.weighted_paths[column]["Signal/Noise(dB)"]

    def find_Latency_given_snr(self, input, output, snr):
        reg = re.compile("^" + re.escape(input) + ".*" + re.escape(output) + "$")
        for column in self.weighted_paths:
            if re.search(reg, column) != None:
                if self.weighted_paths[column]["Signal/Noise(dB)"] == snr:
                    return self.weighted_paths[column]["Latency"]


class Connection:
    def __init__(self, input_node, output_node, signal_power):
        self.input = input_node
        self.output = output_node
        self.signal_power = signal_power
        self.latency = 0.0
        self.snr = 0.0

    def getPower(self):
        return self.signal_power

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
