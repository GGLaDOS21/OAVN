from Network import Network
from Connection import Connection
import random

import matplotlib.pyplot as plt



class Main:
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
    sum = 0
    n = 0
    for conn in connList:
        if conn.getBitRate() != 0:
            sum += conn.getBitRate()
            n += 1
            plotList2.append(conn.getBitRate())
    plt.figure(2)
    plt.hist(plotList2, bins= 25)
    print ("Media: ")
    print (sum / n)
    plt.show()
