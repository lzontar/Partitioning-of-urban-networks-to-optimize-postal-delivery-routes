import argparse
import random
from datetime import datetime

import networkx as nx

parser = argparse.ArgumentParser(
    description='Simple script that adds cluster ids to nodes, based on k-means clustering')

parser.add_argument('-n', '--name',
                    type=str,
                    default='tolmin',
                    help='settlement name'
                    )

parser.add_argument('-k',
                    type=int,
                    default=4,
                    help='number of partitions')

parser.add_argument('-v',
                    action='store_true',
                    help='verbose')

if __name__ == '__main__':
    args = parser.parse_args()

    verbose = args.v
    name = args.name

    name = name \
        .replace(' ', '-') \
        .lower() \
        .replace('č', 'c') \
        .replace('š', 's') \
        .replace('ž', 'z')

    g: nx.Graph = nx.read_pajek(f"../data/graphs/with_distances/{name}.net")

    centers = {center: [] for center in random.sample(g.nodes, args.k)}
    distances = dict(nx.all_pairs_dijkstra_path_length(g, weight=lambda u, v, d: int(d[0]['duration'])))

    for i in range(0, 10):
        # for each node, find closest center
        for node in g.nodes:
            closest_center = -1
            closest_distance = float('inf')

            for center in centers:
                distance = distances[center][node]

                if distance < closest_distance:
                    closest_distance = distance
                    closest_center = center

            centers[closest_center].append(node)

        # for each cluster, find new center
        new_centers = {min([(a, sum([distances[a][b] for b in cluster])) for a in cluster], key=lambda x: x[1])[0]: []
                       for cluster in centers.values()}
        if verbose:
            print(f'previous: {centers.keys()}')
            print(f'new     : {new_centers.keys()}')

        # if centers haven't changed, stop early
        if centers.keys() == new_centers.keys():
            for cluster_id, nodes in enumerate(centers.values()):
                for node in nodes:
                    g.nodes[node]['cluster_id'] = str(cluster_id)

            current_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            nx.write_pajek(g, f'../data/graphs/with_communities/{name}-k-means.net')
            if verbose:
                print(f'Graph saved to: ../data/graphs/with_communities/{name}-k-means.net')
            break

        centers = new_centers
