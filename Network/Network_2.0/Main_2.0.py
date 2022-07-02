from Network import Network
from Connection import Connection
import random
import matplotlib.pyplot as plt
import pandas as pd

class Main:
    network = Network("nodes.json")
    network.connect()
    connList = []
    nodesName = network.get_nodes_name()
    l = len(nodesName)
    # for i in range(100):
    #     n1 = n2 = 0
    #     while n1 == n2:
    #         n1 = random.randint(0, l-1)
    #         n2 = random.randint(0, l-1)
    #         freq = random.randint(0,9)
    #     connList.append(Connection(nodesName[n1], nodesName[n2], 0.001, freq))    #signal power = 0.001 W

#    network.stream(connList, "latency")

    #plot
#    plotList1= []
#    for conn in connList:
#        plotList1.append(conn.getLatency())
#    plt.figure(1)
#    plt.hist(plotList1, bins= 25)


    #network.stream(connList, "snr")
    #plot


    # plotList2= []
    # for conn in connList:
    #     if conn.getSnr() != 0:
    #         plotList2.append(conn.getSnr())
    # plt.figure(2)
    # plt.hist(plotList2, bins= 25)
    # plt.show()


    # plotList2= []
    # sum = 0
    # n = 0
    # for conn in connList:
    #     if conn.getBitRate() != 0:
    #         sum += conn.getBitRate()
    #         n += 1
    #         plotList2.append(conn.getSnr())
    # plt.figure(2)
    # plt.hist(plotList2, bins= 25)
    # print ("Media: ")
    # print (sum / n)
    # plt.show()

    net_matrix = pd.DataFrame(0, index= nodesName, columns= nodesName)
    for na in nodesName:
        for nb in nodesName:
            net_matrix[na][nb] = random.randint(0,10)*1000
    #print(net_matrix)
    old_matrix = net_matrix.copy()

    conn_list = network.streamByMatrix(net_matrix, "snr")
    comparison = old_matrix.compare(net_matrix)
    print(comparison)













