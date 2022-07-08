from Network import Network

class Main:
    network = Network("nodes.json")
    network.connect()
    connList = []
    nodesName = network.get_nodes_name()
    network.draw()
