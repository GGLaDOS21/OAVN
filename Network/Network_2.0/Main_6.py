from Network import Network
import pandas as pd



class Main:
    network = Network("nodes.json")
    network.connect()
    connList = []
    nodesName = network.get_nodes_name()
    l = len(nodesName)

    net_matrix = pd.DataFrame(0, index= nodesName, columns= nodesName)
    M=3
    for na in nodesName:
        for nb in nodesName:
            if na == nb:
                net_matrix[na][nb] = 0
            else:
                net_matrix[na][nb] = M*100
    print(net_matrix)
    conn_list = network.streamByMatrix(net_matrix, "snr")
    print(net_matrix)
    network.strong_failure("DC")
    network.traffic_recovery(net_matrix)
    print(net_matrix)
    conn_list2 = network.streamByMatrix(net_matrix, "snr")
    print(net_matrix)
