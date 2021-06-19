import networkx as nx
import util.lib.TSP as TSP
import numpy as np


def optimalTraversal(graph, verbose=False):
    # graph = nx.read_pajek(f'../data/graphs/temp/tolmin-distances-06-19-2021-14-08-18.net')
    distances = dict(nx.all_pairs_dijkstra_path_length(graph, weight=lambda u, v, d: int(d[0]['duration'])))

    crossroadList = list(filter(lambda x: x[1] == 'crossroad',
                                (map(lambda x: (x[0], graph.nodes[x[1]]['node_type']), enumerate(graph.nodes)))))

    distanceMatrix = np.full((len(graph.nodes), len(graph.nodes)), 0)
    for ix_1, node_1 in enumerate(graph.nodes()):
        for ix_2, node_2 in enumerate(graph.nodes()):
            distanceMatrix[ix_1][ix_2] = distances[node_1][node_2]

    crossroadList = []
    addressList = []
    for ix, node in enumerate(graph.nodes):
        if graph.nodes[node]['node_type'] == "crossroad":
            crossroadList.append(TSP.Address(ix, distanceMatrix))
        elif graph.nodes[node]['node_type'] == "address":
            addressList.append(TSP.Address(ix, distanceMatrix))

    optimalRouteCrs, optimalPrice = TSP.geneticAlgorithm(population=crossroadList, popSize=100, eliteSize=20, mutationRate=0.01,
                                                generations=200, verbose=verbose)
    optimalRoute = []
    for crs in optimalRouteCrs:
        print(crs.id_ + 1)

    return optimalPrice
