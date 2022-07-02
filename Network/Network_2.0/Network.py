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
        self.logger = pd.DataFrame(index=["epoch time", "path", "channel ID", "bit rate"])

    def get_nodes(self):
        return self.nodes

    def get_nodes_name(self):
        lis = []
        for node in self.nodes:
            lis.append(node)
        return lis


    def connect(self):      #aggiungo momentaneamente la creazione delle due tabelle qui
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
        self.createRouteSpace()
        self.createWeightenedTable()

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

    #TODO: implementare dijkstra
    def createRouteSpace(self):
        dict_list = {}
        for key1 in self.nodes:
            for key2 in self.nodes:
                if (key1 != key2):
                    if(key1 + key2) in dict_list:
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

    def createWeightenedTable(self):        #ovvero una tabella contenente i valori "assoluti" di latenza e snr;
        dict_list = {}                      #in pratica dipendeono entrambi esclusivamente dalla topologia e dai percorsi disponibili
        table_data = {}                     #meglio ancora, dipendono entrambi esclusivamente dalla lughezza del percorso
        for key1 in self.nodes:
            for key2 in self.nodes:
                if (key1 != key2):
                    if (key1 + key2) in dict_list:
                        continue
                    dict_list.update({(key1 + key2): self.find_path(key1, key2)})
        for key in dict_list:
            path_list = dict_list[key]
            for path in path_list:
                name = path.copy()
                pathLenght = []     #trucco stupido perchè pyton considera i float immutabili, le lliste no
                pathLenght.append(0.0)
                self.probe(path, pathLenght)
                signal_data = {"Latency": pathLenght[0]/200000, "Noise": math.pow(10, -9)*pathLenght[0], "Signal/Noise(dB)": 90 - 10* math.log10(pathLenght[0])}
                l = len(name)
                s = ""
                for n in name:
                    s = s + n
                    l = l - 1
                    if l != 0:
                        s = s + "->"
                table_data.update({s: signal_data})
        self.weighted_paths = pd.DataFrame(table_data)


    def probe(self, path, pathLenght):
        node = path.pop(0)
        self.nodes[node].probe(path, pathLenght)

    def stream(self, connectionList, label):
        for connection in connectionList:
            if label == "snr":
                best = self.find_best_snr(connection.getInput(), connection.getOutput(), connection.getFrequency())
            else:
                best = self.find_best_latency(connection.getInput(), connection.getOutput(), connection.getFrequency())
            if best is not None:
                sign = Signal_Information(connection.getPower(), best.split("->"), connection.getFrequency())
                connection.addLightPath(sign)
                self.propagate(sign)
                bitrate = self.calculateBitRate(sign, self.nodes[connection.getInput()].getTransceiverMode())
                if bitrate != 0:
                    connection.setBitRate(bitrate)
                    connection.setSnr(self.weighted_paths[best]["Signal/Noise(dB)"])
                    connection.setLatency(self.weighted_paths[best]["Latency"])
                    self.occupy(best, connection.getFrequency())
                    self.update_logger(connection)
                else:
                    print("Connessione rifiutata")

    def pathIsFree(self, searchedPath, freq):

        for columns in self.routeSpace:
            if searchedPath == columns:
                if self.routeSpace[columns][freq] == 1:
                    return True
                else:
                    return False

    def occupy(self, path, freq):
        nodelist = path.split("->")
        #per ogni linea del percorso, ogni percorso che sfrutta quella linea non è più disponibile a quella
        #frequenza, e il canale della linea deve risultare occupato

        for i in range(0, len(nodelist)-1):
            reg1 = re.compile(".*" + re.escape(nodelist[i]) + "->" + re.escape(nodelist[i + 1]) + ".*")
            reg2 = re.compile(".*" + re.escape(nodelist[i+1]) + "->" + re.escape(nodelist[i]) + ".*")
            for route in self.routeSpace:
                if re.search(reg1, route) is not None or re.search(reg2, route) is not None:
                    self.routeSpace[route][freq] = 0
            for name in self.lines:
                line= self.lines[name]
                if line.getLabel() == (nodelist[i] + nodelist[i+1]) or line.getLabel() == (nodelist[i+1] + nodelist[i]):
                    line.occupy_state(freq)
                    break





    def find_best_snr(self, input, output, frequency):
        reg = re.compile("^" + re.escape(input) + ".*" + re.escape(output) + "$")
        save = 0.0
        flag = 0
        for column in self.weighted_paths:
            if re.search(reg, column) is not None:
                if self.weighted_paths[column]["Signal/Noise(dB)"] > save:
                    if self.pathIsFree(column, frequency):
                        save = self.weighted_paths[column]["Signal/Noise(dB)"]
                        best = column
                        flag = 1
        if flag == 0:
            return None
        return best

    def find_best_latency(self, input, output, frequency):
        reg = re.compile("^" + re.escape(input) + ".*" + re.escape(output) + "$")
        save = sys.float_info.max
        flag = 0
        for column in self.weighted_paths:
            if re.search(reg, column) is not None:
                if self.weighted_paths[column]["Latency"] < save:
                    if self.pathIsFree(column, frequency):
                        best = column
                        flag = 1
        if flag == 0:
            return None
        return best

    def calculateBitRate(self, lp, strategy):
        bitRate = 0
        BER = 0.001
        Rs = lp.getRs()     #32 * 1000000000     #rate simbolico del light path, in hertz (32 GHz)
        Bn = 12.5 * 1000000000   #larghezza di banda del rumore, in hertz (12.5 GHz)

        c1 = 2 * math.pow(scipy.special.erfcinv(2 * BER), 2) * (Rs / Bn)
        c2 = (14/3) * math.pow(scipy.special.erfcinv( (3/2) * BER), 2) * (Rs / Bn)
        c3 = 10 * math.pow(scipy.special.erfcinv( (8/3) * BER), 2) * (Rs / Bn)

        GSNR = self.calculateGSNR(lp)

        if strategy == "shannon":
            bitRate = 2 * Rs * math.log( 1 + GSNR * (Rs/Bn) ,2)
        elif strategy == "flex-rate":
            if GSNR < c1:
                bitRate = 0
            elif c1 <= GSNR < c2:
                bitRate = 100
            elif c2 <= GSNR < c3:
                bitRate = 200
            else:
                bitRate = 400
        else:           #default: fixed-rate
            if GSNR >= c1:
                bitRate = 100
            else:
                bitRate = 0

        return bitRate


    def calculateGSNR(self, lp):
        initialPower = lp.getInitialPower()
        GSNR = initialPower / lp.getNoise()
        return GSNR

    def streamByMatrix(self, matrix, label):    #come per stream, serve una label che specifichi il metodo di selezione
        node_name_list = []
        tentativi = 0
        M=1
        conn_list = []
        for n in self.nodes:
            node_name_list.append(n)
        l = len(self.nodes)
        Bn = 12.5 * 1000000000  # larghezza di banda del rumore, in hertz (12.5 GHz)
        while tentativi < 20:
            n1 = n2 = 0
            while n1 == n2:
                n1 = random.randint(0, l-1)
                n2 = random.randint(0, l-1)
            if matrix[node_name_list[n1]][node_name_list[n2]] != 0:
                conn_bit_rate = 100*M
                if matrix[node_name_list[n1]][node_name_list[n2]] >= conn_bit_rate:     #ovvero se c'è ancora disponibilità di traffico tra i due nodi
                    freq = random.randint(0, 9)
                    if label == "snr":
                        best = self.find_best_snr(node_name_list[n1], node_name_list[n2],freq)
                    else:
                        best = self.find_best_latency(node_name_list[n1], node_name_list[n2],freq)
                    if best is not None:
                        sign = Signal_Information(0.001, best.split("->"), freq)
                        connection = Connection(node_name_list[n1], node_name_list[n2], 0.001, freq)
                        connection.addLightPath(sign)
                        self.propagate(sign)
                        bitrate = self.calculateBitRate(sign, self.nodes[connection.getInput()].getTransceiverMode())
                        if bitrate !=0 and bitrate <= conn_bit_rate:    #ipotesi: anche un bitrate inferiore a quello richiesto va bene
                            connection.setBitRate(bitrate)
                            connection.setSnr(self.weighted_paths[best]["Signal/Noise(dB)"])
                            connection.setLatency(self.weighted_paths[best]["Latency"])
                            self.occupy(best, connection.getFrequency())
                            matrix[node_name_list[n1]][node_name_list[n2]] = matrix[node_name_list[n1]][node_name_list[n2]] - bitrate
                            M = M+1
                            tentativi = 0
                            conn_list.append(connection)
                            if self.check_availability(M,matrix,node_name_list) == 0:
                                print("Rete satura")
                                return conn_list
                    else:   #ovvero se best non è stato trovato (percorso non disponibile/frequenza non disponibile)
                        tentativi = tentativi + 1
                else:   #ovvero se è stata estratta una coppia tra i quali non c'è più disponibilità
                    tentativi = tentativi + 1
        print("Tentativi esauriti")
        return conn_list


    def check_availability(self, M, matrix, node_list):
        l=len(node_list)
        for i in range (0, l-1):
            for j in range (0, l-1):
                if matrix[node_list[i]][node_list[j]] > M*100:
                    return 1    #c'è ancora disponibilità
        return 0

    def update_logger(self, conn):
        t= time.time_ns()
        self.logger.append(t, conn.getLight().getPath(), conn.getFrequency(), conn.getBitRate())

    def strong_failure(self, label):
        self.lines[label].setOutOfOrder()
        node=list(label)
        reg1 = re.compile(".*" + re.escape(node[0]) + "->" + re.escape(node[1]) + ".*")
        reg2 = re.compile(".*" + re.escape(node[1]) + "->" + re.escape(node[0]) + ".*")
        for route in self.routeSpace:
            if re.search(reg1, route) is not None or re.search(reg2, route) is not None:
                for freq in range(0,9):
                    self.routeSpace[route][freq] = 0

    def traffic_recovery(self):
        #dovrei valutare ogni log nel logger, verificare se è possibile spostare
        # la connessione sulle linee funzionanti




