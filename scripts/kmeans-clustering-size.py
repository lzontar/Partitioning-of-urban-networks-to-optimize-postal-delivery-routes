import argparse
import random
import math
from pprint import pprint
from datetime import datetime
from typing import Dict, Set

import networkx as nx

parser = argparse.ArgumentParser(
    description='Simple script that adds cluster ids to nodes, based on k-means clustering')

parser.add_argument('-n', '--name',
                    type=str,
                    default='tolmin',
                    help='settlement name'
                    )

parser.add_argument('-i', '--iterations',
                    type=int,
                    default=100,
                    help='max number of iterations'
                    )

parser.add_argument('-p', '--path',
                    type=str,
                    default='../data/graphs/with_distances/tolmin.net',
                    help='path to the graph file'
                    )

parser.add_argument('-k',
                    type=int,
                    default=4,
                    help='number of partitions')


def minmax(it):
    minimum = maximum = None
    for val in it:
        if minimum is None or val < minimum:
            minimum = val
        if maximum is None or val > maximum:
            maximum = val
    return minimum, maximum


def minmax_diff(it):
    return abs(minmax(it)[0] - minmax(it)[1])


if __name__ == '__main__':
    args = parser.parse_args()

    g: nx.Graph = nx.read_pajek(args.path)

    nodes = {}
    centers = {center: [] for center in random.sample(g.nodes, args.k)}
    distances = dict(nx.all_pairs_dijkstra_path_length(g, weight=lambda u, v, d: int(d[0]['duration'])))

    # 1. compute the desired cluster size
    max_cluster_size = math.ceil(g.number_of_nodes() / args.k)

    # 2. Initialise means, preferably with k-means
    for i in range(0, 100):
        # for each node, find closest center
        for node in g.nodes:
            closest_center = -1
            closest_distance = float('inf')

            for center in centers:
                distance = distances[center][node]

                if distance < closest_distance:
                    closest_distance = distance
                    closest_center = center

            nodes[node] = closest_center
            centers[closest_center].append(node)

        # for each cluster, find new center
        new_centers = {min([(a, sum([distances[a][b] for b in cluster])) for a in cluster], key=lambda x: x[1])[0]: []
                       for cluster in centers.values()}

        print(f'previous: {centers.keys()}')
        print(f'new     : {new_centers.keys()}')

        # if centers haven't changed, stop early
        if centers.keys() == new_centers.keys():
            break

        centers = new_centers

    # 3. Order points by the distance to their nearest cluster minus distance to the farthest cluster
    sorted_nodes = sorted(list(g.nodes), key=lambda x: minmax_diff([distances[x][center] for center in centers]))

    # 4. In the proposed approach the points are ordered by their distance to the closest center minus
    # the distance to the farthest cluster. Each point is assigned to the best cluster in this order.
    # If the best cluster is full, the second best is chosen, etc.
    centers = {center: [] for center in centers}
    for node in sorted_nodes:
        sorted_centers = sorted([(center, distances[node][center]) for center in centers], key=lambda x: x[1])

        for center in sorted_centers:
            if len(centers[center[0]]) < max_cluster_size:
                centers[center[0]].append(node)
                nodes[node] = center[0]
                break

    # Iteration
    for i in range(0, args.iterations):
        # 1. Compute current cluster means
        new_centers: Dict[str, Set] = {
            min([(a, sum([distances[a][b] for b in cluster])) for a in cluster], key=lambda x: x[1])[0]: set(cluster)
            for cluster in centers.values()}

        for new_center, cluster in new_centers.items():
            for node in cluster:
                nodes[node] = new_center

        centers = new_centers

        # 2. For each object, compute the distances to the cluster means
        # 3. Sort elements based on the delta of the current assignment and the best possible alternate assignment.
        temp = []
        for node in g.nodes:
            current_assignment = distances[node][nodes[node]]
            best_assignment = min(distances[node][center] for center in centers.keys())
            temp.append((node, abs(current_assignment - best_assignment)))

        sorted_nodes = sorted(temp, key=lambda x: x[1])

        active = 0
        transfers: Dict[str, Set] = {center: set() for center in new_centers}

        # 4. For each element by priority:
        for node, diff in sorted_nodes:

            moved = False
            current_center = nodes[node]

            # 1. For each other cluster, by element gain, unless already moved:
            for center in new_centers.keys():
                gain = distances[node][current_center] - distances[node][center]

                if current_center == center:
                    continue

                # 1. If there is an element wanting to leave the other cluster and
                # this swap yields an improvement, swap the two elements
                if len(transfers[center]) > 0:
                    # calculate gain for each node in transfer list of the target cluster
                    tmp = [(transfer_node, distances[transfer_node][center] - distances[transfer_node][current_center])
                           for transfer_node in
                           transfers[center]]
                    # get transfer node with biggest gain
                    tmp = max(tmp, key=lambda x: x[1])

                    if gain + tmp[1] > 0:
                        active += 2
                        moved = True

                        new_centers[current_center].remove(node)
                        new_centers[center].add(node)
                        nodes[node] = center

                        new_centers[center].remove(tmp[0])
                        new_centers[current_center].add(tmp[0])
                        nodes[tmp[0]] = current_center

                        transfers[center].remove(tmp[0])
                        break

                elif len(new_centers[center]) < max_cluster_size:
                    active += 1
                    moved = True

                    new_centers[center].add(node)
                    nodes[node] = center
                    break

            if not moved:
                transfers[current_center].add(node)

    for cluster_id, nodes in enumerate(centers.values()):
        print(len(nodes))
        for node in nodes:
            g.nodes[node]['cluster_id'] = str(cluster_id)

    current_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    nx.write_pajek(g, f'../data/graphs/with_communities/{args.name}-k-means-size.net')
