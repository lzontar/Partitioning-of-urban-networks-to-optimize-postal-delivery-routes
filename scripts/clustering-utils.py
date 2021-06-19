import argparse
import random

import networkx as nx
from networkx.algorithms import community
from cdlib import algorithms, viz
import metis

parser = argparse.ArgumentParser(
    description='Simple script that adds cluster ids to nodes, based on k-means clustering')

parser.add_argument('-p', '--path',
                    type=str,
                    default='../data/graphs/tolmin.net',
                    help='path to the graph file'
                    )

parser.add_argument('-k',
                    type=int,
                    default=4,
                    help='number of partitions')

if __name__ == '__main__':
    args = parser.parse_args()

    g: nx.Graph = nx.read_pajek(args.path)
    k: int = args.k

    # ==================================================
    #   METIS GRAPH PARTITIONING
    #   https://metis.readthedocs.io/en/latest/
    # ==================================================
    crossroad_graph = nx.Graph()
    for node in g.nodes():
        if(g.nodes[node]["node_type"] == "crossroad"):
            crossroad_graph.add_node(node)
            crossroad_graph.nodes[node]['num_of_houses'] = 0
    
    for edge in g.edges():
        node1 = edge[0]
        node2 = edge[1]
        if(node1 in crossroad_graph.nodes() and node2 in crossroad_graph.nodes()):
            crossroad_graph.add_edge(node1, node2)
        elif(node1 in crossroad_graph.nodes() and node2 not in crossroad_graph.nodes()):
            crossroad_graph.nodes[node1]['num_of_houses'] = crossroad_graph.nodes[node1]['num_of_houses'] + 1
        elif(node2 in crossroad_graph.nodes() and node1 not in crossroad_graph.nodes()):
            crossroad_graph.nodes[node2]['num_of_houses'] = crossroad_graph.nodes[node2]['num_of_houses'] + 1

    crossroad_graph.graph['node_weight_attr'] = 'num_of_houses' 
    (cut, parts) = metis.part_graph(crossroad_graph, k)
    for i, part in enumerate(parts):
        crossroad_graph.nodes[list(crossroad_graph.nodes)[i]]['metis_partition_id'] = str(part)
    
    for edge in g.edges():
        node1 = edge[0]
        node2 = edge[1]
        if(node1 in crossroad_graph and node2 not in crossroad_graph):
            crossroad_graph.add_node(node2)
            crossroad_graph.nodes[node2]['metis_partition_id'] = crossroad_graph.nodes[node1]['metis_partition_id']
            crossroad_graph.add_edge(node1, node2)
        elif(node2 in crossroad_graph and node1 not in crossroad_graph):
            crossroad_graph.add_node(node1)
            crossroad_graph.nodes[node1]['metis_partition_id'] = crossroad_graph.nodes[node2]['metis_partition_id']
            crossroad_graph.add_edge(node1, node2)

    for n in crossroad_graph.nodes():
        g.nodes[n]['metis_partition_id'] = str(crossroad_graph.nodes[n]['metis_partition_id'])
    nx.write_pajek(g, f'{args.path[:-4]}-metis.net')

    # ==================================================
    #   GIRVAN NEWMAN COMMUNITY DETECTION
    #   https://cdlib.readthedocs.io/en/0.2.0/reference/cd_algorithms/algs/cdlib.algorithms.girvan_newman.html#cdlib.algorithms.girvan_newman
    # ==================================================
    g: nx.Graph = nx.read_pajek(args.path)
    coms = algorithms.girvan_newman(g, level=k-1)

    for i in coms.to_node_community_map():
        g.nodes[i]['girvan_newman_cluster_id'] = str(coms.to_node_community_map()[i][0])

    nx.write_pajek(g, f'{args.path[:-4]}-girvan_newman.net')

    # ==================================================
    #   GRAPH-BASED AGGLOMERATIVE ALGORITHM
    #   https://cdlib.readthedocs.io/en/0.2.0/reference/cd_algorithms/algs/cdlib.algorithms.agdl.html#cdlib.algorithms.agdl
    # ==================================================
    g: nx.Graph = nx.read_pajek(args.path)
    coms = algorithms.agdl(g, k, 10)

    for i in coms.to_node_community_map():
        g.nodes[i]['agdl_cluster_id'] = str(coms.to_node_community_map()[i][0])

    nx.write_pajek(g, f'{args.path[:-4]}-agdl.net')

    # ==================================================
    #   FLUID COMMUNITY DETECTION
    #   https://cdlib.readthedocs.io/en/0.2.0/reference/cd_algorithms/algs/cdlib.algorithms.async_fluid.html#cdlib.algorithms.async_fluid
    # ==================================================
    g: nx.Graph = nx.read_pajek(args.path)
    coms = algorithms.async_fluid(g, k)

    for i in coms.to_node_community_map():
        g.nodes[i]['async_fluid_cluster_id'] = str(coms.to_node_community_map()[i][0])

    nx.write_pajek(g, f'{args.path[:-4]}-async_fluid.net')