import json
import math
import scipy.special
import scipy.constants as con
import matplotlib.pyplot as plt
import pandas as pd
import re
import sys


#NOTA:   E' stato verificata l'indipendenza completa di snr dal segnale, inoltre, la latenza può essere
#        calcolata separatamente e post-moltiplicansola per la potenza del segnale

class LightPath:
    def __init__(self, signal_power, path, channel):
        self.signal_power = signal_power
        self.noise_power = 0.0
        self.latency = 0.0
        self.channel = channel
        self.path = []
        for p in path:
            self.path.append(p)
        #da lab7, i seguenti sono "signal symbol rate" e ""frequency spacing between 2 consecutive channel"
        #????????????????????'
        self.Rs = 0.0
        self.df = 0.0

    def getLatency(self):
        return self.latency
    def getNoise(self):
        return self.noise_power
    def getPower(self):
        return self.signal_power
    def getChannel(self):
        return self.channel

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
            if(nextNode == None):
                return
            for nodes in self.connected_nodes:
                if nodes == nextNode:
                    self.successive[nextNode].propagate(signal)
                    break
        else:
            return

    def probe(self, path, pathLenght):
        if len(path) == 0:
            return
        nextNode = path[0]
        for nodes in self.connected_nodes:
            if nodes == nextNode:
                self.successive[nextNode].probe(path, pathLenght)
                break
        return



class Line:
    def __init__(self, label, length):
        self.NLI = 0.0
        self.ase = 0.0
        self.label = label
        self.length = length
        self.successive = {}
        self.state = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.n_amplifier = (length // 80) + 2 #un amplificatore ogni 80 km, più quelli agli estremi
        self.gain = 16 #dB
        self.noiseFigure = 3 #dB    -> F

        #attributi fisici della fibra
        self.alpha_dB = pow(0.2, -3)   #dB/m
        self.alpha = self.alpha_dB/(20* math.log10(con.e))
        self.L_eff = 1/self.alpha
        self.beta2_module = pow(2.13, -26)  #(m*Hz^2)^-1
        self.gamma = pow(1.27, -3)  #(m*W)^-1
        self.Rs = pow(32, 9)    #Hz, giga
        self.df = pow(50, 9)    #Hz, giga
        self.Nch = len(self.state)
        self.nu_nli = 16/(23 * con.pi) * math.log10(pow( (con.pi), 2)/2 * (self.beta2_module * pow(self.Rs, 2)) /self.alpha * Nch * (self.Rs /self.df)) * pow(self.gamma, 2) / (4* self.alpha * self.beta2_module) * 1/pow(self.Rs, 3)
        self.ase_Generation()   #l'ase dipende solo dai parametri fisici, quindi è fisso per ogni linea

    def latency_generation(self, signal):
        signal.latencyUpdate(self.length/200000)

    def noise_generation(self, signal):
        # signal.noisePowUpdate(signal.signal_power * self.length * math.pow(10, -9)) vecchia versione

        #nuova versione:
        self.nli_generation(signal.getPower())
        signal.noisePowUpdate(signal.signal_power * self.NLI * self.ase)    #di questo non sono assolutamente sicuro

    def propagate(self, signal):
        self.noise_generation(signal)
        self.latency_generation(signal)
        if self.state[signal.getChannel()] == 1:
            self.state[signal.getChannel()] = 0
        else:
            print("Errore propagazione: canale occupato")
            return
        node = signal.nextHop()
        self.successive[node].propagate(signal)

    def getState(self):
        return self.state

    #def occupy(self):
    #    self.state = 0

    def probe(self, path, pathLenght):
        pathLenght[0] += self.length
        if len(path) == 0:
            return
        nextNode = path.pop(0)
        for nodes in self.successive:
            if nodes == nextNode:
                self.successive[nextNode].probe(path, pathLenght)
                break
        return

    def ase_Generation(self):                                                   #NOTA: il rumore ase (Amplified Spontaneus Emission)  è il risultato dell'amplifiazione della luce nella
        freq = pow(193.414, 12) #Hz, in questo caso teraHertz                   #fibra dall'EDFA; l'amplificatore intrduce contempranemante un guadagno e un rumore
        h = con.h
        Bn = pow(12.5, 9) # noise bandwith, in Hz

        self.ase = self.n_amplifier * (h * freq * Bn * self.noiseFigure * (self.gain - 1))

    def nli_generation(self, power):   #NLI=Non Linear Inteference

        Bn = pow(12.5,9)
        Nspan = self.n_amplifier - 1     #"number of fiber span" -> ovvero il numero di tratti di fibra della linea = numero mplificatori - 1
        self.NLI = pow(power, 3) * nu_nli * Nspan * Bn

    def optimized_launch_power(self):       #NOTA: problema: nelle richieste delle slide, viene detto di chiamare il metodo in propagate di Node; tuttavia, calcolato in questo modo, il launch power
                                            #è indipendente dal nodo o dal segnale specifico da cui è lanciato; non ha dunque senso ricalcolarlo ad ogni propagate
        #                            F                  L                      Gase
        #                           \/                  \/                      \/
        self.opt_pow=pow( (self.noiseFigure * (self.alpha * self.length) * self.ase) / (2 * self.nu_nli), 1/3)

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

    def createWeightenedTable(self):     #ovvero una tabella contenente i valori "assoluti" di latenza e snr;
        dict_list = {}                  # in pratica dipendeono entrambi esclusivamente dalla topologia e dai percorsi disponibili
        table_data = {}                 # meglio ancora, dipendono entrambi esclusivamente dalla lughezza del percorso
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

    def stream(self, connectionList, label):        #nota: la modifica sull'utilizzo del metodo calculate_bit_rate viene delegate ai metodi per trovare snr
                                                    # e latenza, per ragioni di implementazione
        for connection in connectionList:
            if label == "snr":
                self.find_best_snr(connection)
            else:
                self.find_best_latency(connection)



    def pathIsFree(self, searchedPath, freq):

        for columns in self.routeSpace:
            if searchedPath == columns:
                if self.routeSpace[columns][freq] == 1:
                    return True
                else:
                    return False

    def occupy(self, path, freq):
        nodelist = path.split("->")
        #sfrutto la propagate per occupare le linee
        sign = LightPath(1, nodelist, freq)
        self.propagate(sign)

        #per ogni linea del percorso, ogni percorso che sfrutta quel nodo non è più disponibile a quella
        #frequenza

        for i in range(0, len(nodelist)-1):
            reg1 = re.compile(".*" + re.escape(nodelist[i]) + "->" + re.escape(nodelist[i + 1]) + ".*")
            reg2 = re.compile(".*" + re.escape(nodelist[i+1]) + "->" + re.escape(nodelist[i]) + ".*")
            for route in self.routeSpace:
                if re.search(reg1, route) is not None or re.search(reg2, route) is not None:
                    self.routeSpace[route][freq] = 0



    def find_best_snr(self, connection):
        reg = re.compile("^" + re.escape(connection.getInput()) + ".*" + re.escape(connection.getOutput()) + "$")
        save = 0.0
        flag = 0
        for column in self.weighted_paths:
            if re.search(reg, column) is not None:
                if self.weighted_paths[column]["Signal/Noise(dB)"] > save:
                    if self.pathIsFree(column, connection.getFrequency()):
                        save = self.weighted_paths[column]["Signal/Noise(dB)"]
                        best = column
                        flag = 1
        if flag == 0:
            return
        node = connection.getInput()
        mode = self.nodes[node]
        bitRate = self.calculateBitRate(best, mode)
        if bitRate == 0:    #connection rejected
            return
        connection.setBitRate(bitRate)
        self.occupy(best, connection.getFrequency())
        connection.setSnr(save)
        connection.setLatency(self.weighted_paths[best]["Latency"])

    def find_best_latency(self, connection):
        reg = re.compile("^" + re.escape(connection.getInput()) + ".*" + re.escape(connection.getOutput()) + "$")
        save = sys.float_info.max
        flag = 0
        for column in self.weighted_paths:
            if re.search(reg, column) != None:
                if self.weighted_paths[column]["Latency"] < save:
                    if self.pathIsFree(column):
                        saveLat = self.weighted_paths[column]["Latency"]
                        saveSnr = self.weighted_paths[column]["Signal/Noise(dB)"]
                        best = column
                        flag = 1
        if flag == 0:
            return
        mode = connection.getInput().getTransceiverMode()
        bitRate = self.calculateBitRate(best, mode)
        if bitRate == 0:  # connection rejected
            return
        connection.setBitRate(bitRate)
        self.occupy(best, connection.getFrequency())
        connection.setSnr(saveSnr)
        connection.setLatency(saveLat)

    def calculateBitRate(self, lightpath, strategy):
        bitRate = 0
        BER = 0.001
        Rs = 32 * 1000000000     #rate simbolico del light path, in hertz (32 GHz)
        Bn = 12.5 * 1000000000   #larghezza di banda del rumore, in hertz (12.5 GHz)

        c1 = 2 * math.pow(scipy.special.erfcinv(2 * BER), 2) * (Rs / Bn)
        c2 = (14/3) * math.pow(scipy.special.erfcinv( (3/2) * BER), 2) * (Rs / Bn)
        c3 = 10 * math.pow(scipy.special.erfcinv( (8/3) * BER), 2) * (Rs / Bn)

        GSNR = self.weighted_paths[path]["Signal/Noise(dB)"] # ?????

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

class Connection:
    def __init__(self, input_node, output_node, signal_power, frequency):
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