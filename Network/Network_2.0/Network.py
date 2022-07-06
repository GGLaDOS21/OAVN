import pandas as pd
import matplotlib.pyplot as plt
import re
import sys
import scipy.special
import json
import math
import time
from Signal_Information import Signal_Information
from Node import Node
from Line import Line
import random
from Connection import Connection


class Network:
    def __init__(self, filename):
        self.routeSpace = None
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
                if ((node + conn) in self.lines):
                    continue
                label = node + conn
                node1 = self.nodes[node]
                node2 = self.nodes[conn]
                dist = math.sqrt(
                    math.pow(node1.position[0] - node2.position[0], 2) + math.pow(node1.position[1] - node2.position[1],
                                                                                  2))
                ln = Line(label, dist, node1, node2)
                self.lines.update({label: ln})
        self.logger = pd.DataFrame()
        #self.logger = pd.DataFrame(index=["epoch time", "path", "channel ID", "bit rate"])

    def get_nodes(self):
        return self.nodes

    def get_nodes_name(self):
        lis = []
        for node in self.nodes:
            lis.append(node)
        return lis

    def connect(self):  # aggiungo momentaneamente la creazione delle due tabelle qui
        for key in self.nodes:
            node = self.nodes[key]
            for conn in node.connected_nodes:
                lbl = key + conn
                if lbl in self.lines:
                    line = self.lines[lbl]
                    node.successive.update({conn: line})
        self.createRouteSpace()
        self.createWeightenedTable()
        a=6

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
            if node in listaP:  # evita il backtrack
                continue
            if node == nodeB.label:  # se abbiamo trovato la fine
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

    def draw(self):
        for key in self.nodes:
            node = self.nodes[key]
            plt.plot(node.position[0], node.position[1], marker="o", markersize=10, markerfacecolor="white")
            plt.annotate(key, (node.position[0], node.position[1]))
        for key in self.nodes:
            node = self.nodes[key]
            for conn in node.connected_nodes:
                node2 = self.nodes[conn]
                plt.plot((node.position[0], node2.position[0]), (node.position[1], node2.position[1]), linestyle='-',
                         linewidth=2)

    def createRouteSpace(self):
        dict_list = {}
        for key1 in self.nodes:
            for key2 in self.nodes:
                if key1 != key2:
                    if (key1 + key2) in dict_list:
                        continue
                    dict_list.update({(key1 + key2): self.find_path(key1, key2)})
        table_data = {}
        for key in dict_list:
            path_list = dict_list[key]
            for path in path_list:
                l = len(path)
                s = ""
                for n in path:
                    s = s + n
                    l = l - 1
                    if l != 0:
                        s = s + "->"
                table_data.update({s: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]})
        self.routeSpace = pd.DataFrame(table_data)

    def createWeightenedTable(self):            # ovvero una tabella contenente i valori "assoluti" di latenza e snr;
        dict_list = {}
        table_data = {}
        for key1 in self.nodes:
            for key2 in self.nodes:
                if key1 != key2:
                    if (key1 + key2) in dict_list:
                        continue
                    dict_list.update({(key1 + key2): self.find_path(key1, key2)})
        for key in dict_list:
            path_list = dict_list[key]
            for path in path_list:
                name = path.copy()
                pathLenght = []  # trucco stupido perchè pyton considera i float immutabili, le lliste no
                pathLenght.append(0.0)
                probe_signal = Signal_Information(0.001, path)
                self.probe(path, pathLenght, probe_signal)
                signal_data = {"Latency": pathLenght[0] / 200000, "Noise": math.pow(10, -9) * pathLenght[0], "Signal/Noise(dB)": 90 - 10 * math.log10(pathLenght[0])}
                #signal_data = {"Latency": probe_signal.getLatency(), "Noise": probe_signal.getNoise(), "Signal/Noise(dB)": 10*math.log(0.001/probe_signal.getNoise())}
                l = len(name)
                s = ""
                for n in name:
                    s = s + n
                    l = l - 1
                    if l != 0:
                        s = s + "->"
                table_data.update({s: signal_data})
        self.weighted_paths = pd.DataFrame(table_data)

    def probe(self, path, pathLenght, signal):
        node = path.pop(0)
        self.nodes[node].probe(path, pathLenght, signal)

    def stream(self, connectionList, label):
        for connection in connectionList:
            if label == "snr":
                best = self.find_best_snr(connection.getInput(),connection.getOutput())
            else:
                best = self.find_best_latency(connection.getInput(),connection.getOutput())
            if best is not None:
                ch = self.findFreeChannel(best)
                sign = Signal_Information(connection.getPower(), best.split("->"))
                sign.setRS(self.get_Rs(best))
                sign.setCnannel(ch)
                connection.addLightPath(sign)
                self.propagate(sign)
                bitrate = self.calculateBitRate(sign, self.nodes[connection.getInput()].getTransceiverMode())
                if bitrate != 0:
                    connection.setBitRate(bitrate)
                    connection.setSnr(self.weighted_paths[best]["Signal/Noise(dB)"])
                    connection.setLatency(self.weighted_paths[best]["Latency"])
                    self.occupy(best, connection.getFrequency())
                # self.update_logger(connection)
                else:
                    print("Connessione rifiutata")

    def get_Rs(self, path):
        nodeList = path.split("->")
        for i in range(0, len(nodeList) - 1):
            if (nodeList[i] + nodeList[i + 1]) in self.lines:
                Rs = self.lines[nodeList[i] + nodeList[i + 1]].getRs()
            elif (nodeList[i + 1] + nodeList[i]) in self.lines:
                Rs = self.lines[nodeList[i + 1] + nodeList[i]].getRs()
        return Rs

    def pathIsFree(self, searchedPath):

        for columns in self.routeSpace:
            if searchedPath == columns:
                for i in range(0,9):
                    if self.routeSpace[columns][i] == 1:
                        return True
        return False

    def findFreeChannel(self, path):

        for columns in self.routeSpace:
            if path == columns:
                for i in range(0,9):
                    if self.routeSpace[columns][i] == 1:
                        return i


    def occupy(self, path, freq):
        nodelist = path.split("->")
        # per ogni linea del percorso, ogni percorso che sfrutta quella linea non è più disponibile a quella
        # frequenza, e il canale della linea deve risultare occupato

        for i in range(0, len(nodelist) - 1):
            reg = re.compile(".*" + re.escape(nodelist[i]) + "->" + re.escape(nodelist[i + 1]) + ".*")
            for route in self.routeSpace:
                if re.search(reg, route) is not None:
                    self.routeSpace[route][freq] = 0
            for name in self.lines:
                line = self.lines[name]
                if line.getLabel() == (nodelist[i] + nodelist[i + 1]):
                    line.occupy_state(freq)
                    break

    def find_best_snr(self, input, output):
        reg = re.compile("^" + re.escape(input) + ".*" + re.escape(output) + "$")
        save = 0.0
        flag = 0
        for column in self.weighted_paths:
            if re.search(reg, column) is not None:
                if self.weighted_paths[column]["Signal/Noise(dB)"] > save:
                    if self.pathIsFree(column):
                        save = self.weighted_paths[column]["Signal/Noise(dB)"]
                        best = column
                        flag = 1
        if flag == 0:
            return None
        return best

    def find_best_latency(self, input, output):
        reg = re.compile("^" + re.escape(input) + ".*" + re.escape(output) + "$")
        save = sys.float_info.max
        flag = 0
        for column in self.weighted_paths:
            if re.search(reg, column) is not None:
                if self.weighted_paths[column]["Latency"] < save:
                    if self.pathIsFree(column):
                        best = column
                        flag = 1
        if flag == 0:
            return None
        return best

    def calculateBitRate(self, lp, strategy):
        bitRate = 0
        BER = 0.001
        Rs = lp.getRs()  # 32 * 1000000000     #rate simbolico del light path, in hertz (32 GHz)
        Bn = 12.5 * 1000000000  # larghezza di banda del rumore, in hertz (12.5 GHz)

        t1 = 2 * math.pow(scipy.special.erfcinv(2 * BER), 2) * (Rs / Bn)
        t2 = (14 / 3) * math.pow(scipy.special.erfcinv((3 / 2) * BER), 2) * (Rs / Bn)
        t3 = 10 * math.pow(scipy.special.erfcinv((8 / 3) * BER), 2) * (Rs / Bn)

        GSNR = self.calculateGSNR(lp)

        if strategy == "shannon":
            bitRate = 2 * Rs * math.log(1 + GSNR * (Rs / Bn), 2)
        elif strategy == "flex-rate":
            if GSNR < t1:
                bitRate = 0
            elif t1 <= GSNR < t2:
                bitRate = 100
            elif t2 <= GSNR < t3:
                bitRate = 200
            else:
                bitRate = 400
        else:  # default: fixed-rate
            if GSNR >= t1:
                bitRate = 100
            else:
                bitRate = 0

        return bitRate

    def calculateGSNR(self, lp):

        GSNR = 0.001 / lp.getNoise()
        return GSNR

    def streamByMatrix(self, matrix, label):  # come per stream, serve una label che specifichi il metodo di selezione
        node_name_list = []
        M = 1
        conn_list = []
        for n in self.nodes:
            node_name_list.append(n)
        l = len(self.nodes)
        Bn = 12.5 * 1000000000  # larghezza di banda del rumore, in hertz (12.5 GHz)
        tentativi = 0
        flag = 1
        while flag == 1:
            n1 = n2 = 0
            while n1 == n2:
                n1 = random.randint(0, l - 1)
                n2 = random.randint(0, l - 1)
            if matrix[node_name_list[n1]][node_name_list[n2]] != 0:
                if label == "snr":
                    best = self.find_best_snr(node_name_list[n1], node_name_list[n2])
                else:
                    best = self.find_best_latency(node_name_list[n1], node_name_list[n2])
                if best is not None:
                    ch = self.findFreeChannel(best)
                    sign = Signal_Information(0.001, best.split("->"))
                    connection = Connection(node_name_list[n1], node_name_list[n2], 0.001)
                    sign.setRS(self.get_Rs(best))
                    sign.setCnannel(ch)
                    connection.addLightPath(sign)
                    self.propagate(sign)
                    bitrate = self.calculateBitRate(sign, self.nodes[connection.getInput()].getTransceiverMode())
                    if bitrate != 0:
                        connection.setBitRate(bitrate)
                        connection.setSnr(self.weighted_paths[best]["Signal/Noise(dB)"])
                        connection.setLatency(self.weighted_paths[best]["Latency"])
                        self.occupy(best, connection.getFrequency())
                        self.update_logger(connection)
                        tentativi = 0
                        if bitrate >= matrix[node_name_list[n1]][node_name_list[n2]]:
                            matrix[node_name_list[n1]][node_name_list[n2]] = 0
                        else:
                            matrix[node_name_list[n1]][node_name_list[n2]] = matrix[node_name_list[n1]][node_name_list[n2]] - bitrate

                        conn_list.append(connection)
                    else:           #obbero se la connessione onn andava bene per il bitrae
                        tentativi = tentativi + 1
                else:               # ovvero se best non è stato trovato (percorso non disponibile)
                    tentativi = tentativi + 1
            else:                   # ovvero se è stata estratta una coppia tra i quali non c'è più disponibilità
                tentativi = tentativi + 1
            if tentativi == 100:
                self.check_availability_and_fill_matrix( matrix, node_name_list, conn_list)
                print("Rete satura")
                flag = 0
        return conn_list

    def check_availability_and_fill_matrix(self, matrix, node_list, conn_list):
        l = len(node_list)
        for i in range(0, l - 1):
            for j in range(0, l - 1):
                if matrix[node_list[i]][node_list[j]] > 0:
                    path = self.findRemainingPath(node_list[i], node_list[j])
                    if path is not None:
                        ch = self.findFreeChannel(path)
                        sign = Signal_Information(0.001, path.split("->"))
                        connection = Connection(node_list[i], node_list[j], 0.001)
                        sign.setRS(self.get_Rs(path))
                        sign.setCnannel(ch)
                        connection.addLightPath(sign)
                        self.propagate(sign)
                        bitrate = self.calculateBitRate(sign, self.nodes[connection.getInput()].getTransceiverMode())
                        if bitrate != 0:
                            connection.setBitRate(bitrate)
                            connection.setSnr(self.weighted_paths[path]["Signal/Noise(dB)"])
                            connection.setLatency(self.weighted_paths[path]["Latency"])
                            self.occupy(path, connection.getFrequency())
                            self.update_logger(connection)
                            if bitrate >= matrix[node_list[i]][node_list[j]]:
                                matrix[node_list[i]][node_list[j]] = 0
                            else:
                                matrix[node_list[i]][node_list[j]] = matrix[node_list[i]][node_list[j]] - bitrate

                            conn_list.append(connection)

    def findRemainingPath(self, n1, n2):
        reg = re.compile("^" + re.escape(n1) + ".*" + re.escape(n2) + "$")
        for column in self.routeSpace:
            if re.search(reg, column) is not None:
                for i in range(0,9):
                    if self.routeSpace[column][i] == 1:
                        return column
        return None


    def update_logger(self, conn):
        t = time.time_ns()%10000000000000
        newrow= {"epoch time": t, "path": conn.getLight().getPath_with_arrow(), "channel ID": int(conn.getFrequency()), "bit rate": conn.getBitRate()}
        self.logger = self.logger.append(newrow, ignore_index=True)


    def strong_failure(self, label):
        self.lines[label].setOutOfOrder()
        node = list(label)
        reg = re.compile(".*" + re.escape(node[0]) + "->" + re.escape(node[1]) + ".*")
        for route in self.routeSpace:
            if re.search(reg, route) is not None:
                for freq in range(0, 9):
                    self.routeSpace[route][freq] = 0

    def traffic_recovery(self, matrix):
        # dovrei valutare ogni log nel logger, verificare se è possibile spostare
        # la connessione sulle linee funzionanti
        non_operative_lines = []
        for l in self.lines:
            if self.lines[l].getServiceStatus() == 0:
                non_operative_lines.append(l)
        for index, row in self.logger.iterrows():
            for line in non_operative_lines:
                reg = re.compile(".*" + re.escape(self.lines[line].getInNode().getLabel()) + "->" + re.escape(self.lines[line].getOutNode().getLabel()) + ".*")
                if re.search(reg, row["path"]) is not None:
                    path = row["path"].split("->")
                    startNode=path[0]
                    endNode=path[len(path)-1]
                    matrix[startNode][endNode] = matrix[startNode][endNode] + row["bit rate"]
                    for i in range(0,len(path)-1):
                        self.lines[path[i] + path[i+1]].resetChannel(row["channel ID"])
        self.check_lines_out_of_order()




    def check_lines_out_of_order(self):
        for l in self.lines:
            if self.lines[l].getServiceStatus() == 0:
                self.lines[l].no_ch_avail()


