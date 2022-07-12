from Network import Network
from Connection import Connection
import random
import matplotlib.pyplot as plt
import numpy as np
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

        # plot snr
    network.stream(connList, "snr")

    sum2 = 0
    n = 0
    plotList2 = []
    for conn in connList:
        if conn.getSnr() != 0:
            plotList2.append(10 * np.log(conn.getSnr()))
            sum2 = sum2 + 10 * np.log(conn.getSnr())
            n = n + 1
    fig, ax = plt.subplots()
    ax.hist(plotList2, linewidth=0.5, edgecolor="white")
    plt.show()
    print("snr media: ")
    print(float((sum2 / n)))
