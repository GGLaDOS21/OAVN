from Network import Network
from Connection import Connection
import random
import warnings
import math



class Main:
    warnings.simplefilter(action='ignore', category=FutureWarning)
    network = Network("nodes.json")
    network.connect()
    connList = []
    nodesName = network.get_nodes_name()
    # network.draw()
    l = len(nodesName)
    for i in range(100):
        n1 = n2 = 0
        while n1 == n2:
            n1 = random.randint(0, l - 1)
            n2 = random.randint(0, l - 1)
        connList.append(Connection(nodesName[n1], nodesName[n2], 0.001))  # signal power = 0.001 W

                                            #plot bitrate transceiver method
    network.stream(connList, "snr")
    plotList2= []
    capacity = 0
    sum = 0
    n = 0
    for conn in connList:
        if conn.getGSNR() != 0:

            sum += 10* math.log10(conn.getGSNR())
            n += 1
        if conn.getBitRate() != 0:
            capacity += conn.getBitRate()


    print ("GSNR Medio: ")
    print (sum / n)
    print ("Capacità: ")
    print (capacity)

