import warnings

from pandas.core.common import SettingWithCopyWarning

from Network import Network
import pandas as pd
import matplotlib.pyplot as plt


class Main:
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)
    connList = []
    M_values = []
    network_usage = []
    matrix_usage = []

    for i in range(1, 35):
        network = Network("nodes.json")
        network.connect()
        nodesName = network.get_nodes_name()

        net_matrix = pd.DataFrame(0, index=nodesName, columns=nodesName)
        M = i
        for na in nodesName:
            for nb in nodesName:
                if na == nb:
                    net_matrix[na][nb] = 0
                else:
                    net_matrix[na][nb] = M * 100

        old_matrix = net_matrix.copy()
        conn_list = network.streamByMatrix(net_matrix, "snr")
        #print(net_matrix)

        perc1 = network.usage()

        tot = 0
        part = 0
        for na in nodesName:
            for nb in nodesName:
                part = part + net_matrix[na][nb]
                tot = tot + old_matrix[na][nb]

        perc2 = (part/tot)*100

        M_values.append(i)
        network_usage.append(perc1)
        matrix_usage.append(perc2)

    fig, ax = plt.subplots()
    ax.plot(M_values, network_usage)
    ax.plot(M_values, matrix_usage)
    plt.show()


    # network.strong_failure("DC")
    # network.traffic_recovery(net_matrix)
    # print(net_matrix)
    # conn_list2 = network.streamByMatrix(net_matrix, "snr")
    # print(net_matrix)
