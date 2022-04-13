import Net
import random

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
        connList.append(Net.Connection(nodesName[n1], nodesName[n2], 0.001))    #signal power = 0.001 W

    network.stream(connList, "latency")
    #plot
    network.stream(connList, "snr")
    #plot


#dict_list = {}
#nodes = net.get_nodes()
#table_data = {}

#dataframe = net.createDataframeFromSignal(0.001)

#net.find_best_snr("A", "C")



















