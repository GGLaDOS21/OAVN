import warnings
from pandas.core.common import SettingWithCopyWarning
from Network import Network
import pandas as pd



class Main:
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)
    connList = []

    network = Network("nodes.json")
    network.connect()
    nodesName = network.get_nodes_name()

    net_matrix = pd.DataFrame(0, index=nodesName, columns=nodesName)
    M = 19
    for na in nodesName:
        for nb in nodesName:
            if na == nb:
                net_matrix[na][nb] = 0
            else:
                net_matrix[na][nb] = M * 100

    old_matrix = net_matrix.copy()
    conn_list = network.streamByMatrix(net_matrix, "snr")
    print(net_matrix)

    network.strong_failureV2()
    network.traffic_recovery(net_matrix)
    print(net_matrix)
    conn_list2 = network.streamByMatrix(net_matrix, "snr")
    print(net_matrix)
