import argparse
import random
from datetime import datetime

import networkx as nx

parser = argparse.ArgumentParser(
    description='Simple script that adds cluster ids to nodes, based on k-means clustering')

parser.add_argument('-p', '--path',
                    type=str,
                    default='../data/graphs/temp/skofja-loka-distances-06-19-2021-12-58-20.net',
                    help='path to the graph file'
                    )

parser.add_argument('-k',
                    type=int,
                    default=4,
                    help='number of partitions')

if __name__ == '__main__':
    args = parser.parse_args()

    g: nx.Graph = nx.read_pajek(args.path)

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

        print(f'previous: {centers.keys()}')
        print(f'new     : {new_centers.keys()}')

        # if centers haven't changed, stop early
        if centers.keys() == new_centers.keys():
            for cluster_id, nodes in enumerate(centers.values()):
                for node in nodes:
                    g.nodes[node]['cluster_id'] = str(cluster_id)

            current_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            nx.write_pajek(g, f'{args.path[:-4]}-kmeans-{current_time}.net')
            print(f'Graph saved to: {args.path[:-4]}-kmeans-{current_time}.net')
            break

        centers = new_centers
