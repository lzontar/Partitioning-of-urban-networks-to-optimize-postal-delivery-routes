import networkx as nx
import util.lib.helper as help

graph = nx.read_pajek(f'data/graphs/temp/pungert-distances-06-19-2021-14-02-38.net')

print(help.optimalTraversal(graph, verbose=True))
