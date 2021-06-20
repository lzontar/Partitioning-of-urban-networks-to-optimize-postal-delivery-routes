import networkx as nx
import util.lib.TSP as TSP
import numpy as np
import math


def rotate(l, n):
    return l[n:] + l[:n]


def distance_matrix(graph):
    distances = dict(nx.all_pairs_dijkstra_path_length(graph, weight=lambda u, v, d: int(d[0]['duration'])))

    distanceMatrix = np.full((len(graph.nodes), len(graph.nodes)), 0)
    for ix_1, node_1 in enumerate(graph.nodes()):
        for ix_2, node_2 in enumerate(graph.nodes()):
            distanceMatrix[ix_1][ix_2] = distances[node_1][node_2]
    return distanceMatrix


def optimalTraversal(graph, subgraph_nodes, distanceMatrix, verbose=False):
    crossroadList = []
    addressList = []
    for ix, node in enumerate(subgraph_nodes):
        if graph.nodes[node]['node_type'] == "crossroad":
            crossroadList.append(TSP.Address(ix, distanceMatrix))
        elif graph.nodes[node]['node_type'] == "address":
            addressList.append(TSP.Address(ix, distanceMatrix))
    if crossroadList:
        optimalRouteCrs, optimalPrice = TSP.geneticAlgorithm(population=crossroadList, popSize=40, eliteSize=20,
                                                             mutationRate=0.01,
                                                             generations=80, verbose=verbose)
        optimalRoute = []
        for crs in optimalRouteCrs:
            crs_node = list(subgraph_nodes)[crs.id_]
            graph.edges(crs_node)
            subgraph_ids = list(
                map(lambda x: TSP.Address(int(x['id']) - 1, distanceMatrix), filter(lambda x: x['node_type'] != 'crossroad',
                                                                                    [graph.nodes[node] for node in
                                                                                     list(graph.neighbors(crs_node))])))
            subgraph_ids.append(crs)
            if len(subgraph_ids) < 2:
                optimalRoute.append(crs)
                continue

            subgraphOptRoute, subgraphOptPrice = TSP.geneticAlgorithm(population=subgraph_ids, popSize=40, eliteSize=20,
                                                                      mutationRate=0.01,
                                                                      generations=80, verbose=verbose)
            subgraphOptRoute = rotate(subgraphOptRoute, subgraphOptRoute.index(crs))
            optimalRoute.extend(subgraphOptRoute)
            optimalRoute.append(crs)
            optimalPrice += subgraphOptPrice

        optimalRoute.append(optimalRouteCrs[0])
    else:
        subgraph_ids = list(map(lambda x: TSP.Address(int(x['id']) - 1, distanceMatrix), [graph.nodes[node] for node in subgraph_nodes]))
        optimalRoute, optimalPrice = TSP.geneticAlgorithm(population=subgraph_ids, popSize=40, eliteSize=20,
                                                                  mutationRate=0.01,
                                                                  generations=80, verbose=verbose)
    return optimalRoute, optimalPrice


def geo_distance(lon1, lat1, lon2, lat2):
    # Approximate radius of earth in km
    R = 6373.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    return distance