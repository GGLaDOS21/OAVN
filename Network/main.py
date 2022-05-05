import Net
import random
import matplotlib
import matplotlib.pyplot as plt

def getLatencyPlot(network, connList):
    network.stream(connList, "latency")

    plotList1= []
    for conn in connList:
        plotList1.append(conn.getLatency())
    plt.figure(1)
    plt.hist(plotList1, bins= 25)
    plt.show()


def getSnrPlot(network, connList):

    network.stream(connList, "snr")

    plotList2= []
    for conn in connList:
        plotList2.append(conn.getSnr())
    plt.figure(2)
    plt.hist(plotList2, bins= 25)
    plt.show()

class Main:
    network = Net.Network("nodes.json")
    network.connect()
    connList = []
    nodesName = network.get_nodes_name()
    l = len(nodesName)
    for i in range(100):
        n1 = n2 = 0
        while(n1 == n2):
            n1 = random.randint(0, l-1)
            n2 = random.randint(0, l-1)
        connList.append(Net.Connection(nodesName[n1], nodesName[n2], 0.001, 1))    #signal power = 0.001 W

#   getLatencyPlot(network, connList)
#    getSnrPlot(network, connList)






#dict_list = {}
#nodes = net.get_nodes()
#table_data = {}

#dataframe = net.createDataframeFromSignal(0.001)

#net.find_best_snr("A", "C")



















