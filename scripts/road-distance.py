import argparse
import json
import os
import time
from datetime import datetime

import networkx as nx
import requests
from dotenv import load_dotenv

load_dotenv()

HERE_API_KEY = ''
HERE_ROUTES_URL = 'https://router.hereapi.com/v8/routes'

parser = argparse.ArgumentParser(
    description='Simple script that adds road distance (meters) and duration (seconds) to edges')
parser.add_argument('-p', '--path',
                    type=str,
                    default='../data/graphs/skofja-loka.net',
                    help='path to the graph file'
                    )


def create_request(origin: str, destination: str) -> tuple:
    r = requests.get(HERE_ROUTES_URL, params={
        'apiKey': HERE_API_KEY,
        'origin': origin,
        'destination': destination,
        'transportMode': 'car',
        'return': 'summary'
    })

    result = json.loads(r.text)
    if r.status_code != 200:
        raise RuntimeError(f'Error when making a request: {result["error_description"]}')

    tmp = result['routes'][0]['sections'][0]['summary']
    return tmp['duration'], tmp['length']


if __name__ == '__main__':
    args = parser.parse_args()

    HERE_API_KEY = os.getenv('HERE_API_KEY')
    if HERE_API_KEY is None:
        raise RuntimeError('HERE_API_KEY environment variable is not set!')

    g: nx.Graph = nx.read_pajek(args.path)
    number_of_edges = g.number_of_edges()

    start_time = time.time()
    for index, edge in enumerate(g.edges):
        from_node = edge[0]
        to_node = edge[1]

        from_latitude = g.nodes[from_node]['lat']
        from_longitude = g.nodes[from_node]['lon']

        to_latitude = g.nodes[to_node]['lat']
        to_longitude = g.nodes[to_node]['lon']

        duration, distance = create_request(f'{from_latitude},{from_longitude}', f'{to_latitude},{to_longitude}')
        edge = g.edges[edge]
        edge['duration'] = str(duration)
        edge['distance'] = str(distance)

        os.system('cls')
        print(f'{index} / {number_of_edges}')

    print(f'Total time: {(time.time() - start_time) / 60:.2f} min')
    current_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
    nx.write_pajek(g, f'{args.path}-distances-{current_time}')
    print(f'Graph saved to: {args.path}-distances-{current_time}')
