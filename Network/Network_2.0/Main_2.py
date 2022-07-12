from Network import Network
from Connection import Connection
import random
import matplotlib.pyplot as plt
import warnings

class Main:
    warnings.simplefilter(action='ignore', category=FutureWarning)
    network = Network("nodes.json")
    network.connect()
    connList = []
    nodesName = network.get_nodes_name()
    l = len(nodesName)
    for i in range(100):
        n1 = n2 = 0
        while n1 == n2:
            n1 = random.randint(0, l - 1)
            n2 = random.randint(0, l - 1)
        connList.append(Connection(nodesName[n1], nodesName[n2], 0.001))  # signal power = 0.001 W

    network.stream(connList, "latency")
                                                   #plot latency
    sum=0
    plotList1= []
    for conn in connList:
        plotList1.append(round(conn.getLatency(),1))
        sum=sum + conn.getLatency()
    fig, ax = plt.subplots()
    ax.hist(plotList1, linewidth=0.5, edgecolor="white")
    plt.show()
    print("latenza media: ")
    print(float((sum/len(connList))))
