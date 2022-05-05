import NewNet_prova
import random
import matplotlib.pyplot as plt

class Main:
    network = NewNet_prova.Network("nodes.json")
    network.connect()
    connList = []
    nodesName = network.get_nodes_name()
    l = len(nodesName)
    for i in range(10):
        n1 = n2 = 0
        while(n1 == n2):
            n1 = random.randint(0, l-1)
            n2 = random.randint(0, l-1)
            freq = random.randint(0,9)
        connList.append(NewNet_prova.Connection(nodesName[n1], nodesName[n2], 0.001, 2))    #signal power = 0.001 W

#    network.stream(connList, "latency")

    #plot
#    plotList1= []
#    for conn in connList:
#        plotList1.append(conn.getLatency())
#    plt.figure(1)
#    plt.hist(plotList1, bins= 25)


    network.stream(connList, "snr")
    #plot


    plotList2= []
    for conn in connList:
        plotList2.append(conn.getSnr())
    plt.figure(2)
    plt.hist(plotList2, bins= 25)
    plt.show()


#dict_list = {}
#nodes = net.get_nodes()
#table_data = {}

#dataframe = net.createDataframeFromSignal(0.001)

#net.find_best_snr("A", "C")









