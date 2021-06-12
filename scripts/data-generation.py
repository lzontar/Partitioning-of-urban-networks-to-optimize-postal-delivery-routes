import pandas as pd
import xml.etree.cElementTree as ET
import networkx as nx
import math

import requests
from pyvis.network import Network


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

obcina = 'Škofja Loka'
obcina_filename = obcina \
    .replace(' ', '-') \
    .lower() \
    .replace('č', 'c') \
    .replace('š', 's') \
    .replace('ž', 'z')

generate_graph = False
zgeneriraj_csv = False

if zgeneriraj_csv:
    # To izvedemo le prvič, da se zgenerira Excel datoteka
    # ulice_vse = pd.read_csv('data/UL_VSE.csv', encoding='utf-8', delimiter=';')
    # ulice_vse.to_excel('data/ulice.xlsx')

    ulice = pd.read_excel('data/e-prostor/ulice.xlsx')
    obcine = pd.read_excel('data/e-prostor/obcine.xlsx')
    hisne_stevilke = pd.read_excel('data/e-prostor/hisne-stevilke.xlsx')

    # Vzamemo le željeno občino
    obcine = obcine[obcine['OB_UIME'] == obcina]

    # Združimo tabele skupaj, da dobimo vse naslove iz občine
    ulice_obcina = pd.merge(obcine, ulice, how="inner", on=["OB_MID"])
    naslovi_obcina = pd.merge(ulice_obcina, hisne_stevilke, how="inner", on=["UL_MID"])['']

    # Shranimo dataframe v excel
    naslovi_obcina.to_excel(f'data/e-prostor/{obcina_filename}.xlsx')

if generate_graph:
    naslovi_obcina = pd.read_excel(f'data/e-prostor/{obcina_filename}.xlsx')
    reported_by_gov = list(zip(naslovi_obcina['OB_UIME'], naslovi_obcina['LABELA'], naslovi_obcina['UL_UIME']))

    # reported_by_gov = dict()
    # for row in naslovi_obcina.iterrows():
    #     if row['OB_UIME'] not in reported_by_gov.keys():
    #         reported_by_gov['OB_UIME'] = []
    #     if row['UL_IME'] not in reported_by_gov[row['OB_IME']].keys():
    #         reported_by_gov[row['OB_UIME']][row['UL_IME']] = []
    #
    #     reported_by_gov[row['OB_UIME']][row['UL_IME']].append(naslovi_obcina['LABELA'])

    node_tree = ET.parse(f'data/osm/{obcina_filename}/{obcina_filename}-nodes.osm')
    root = node_tree.getroot()
    nodes = root.findall('node')

    graph = nx.Graph()

    for node in nodes:
        # Read data from node and check if it represents a house
        tags = list(filter(lambda x:
                           x.get('k') == 'addr:housenumber'
                           or x.get('k') == 'addr:street',
                           node.findall("tag")))

        if tags:
            node_ = {
                'id': node.get('id'),
                'lat': float(node.get('lat')),
                'lon': float(node.get('lon')),
                'obcina': obcina
            }

            for tag in tags:
                if tag.get('k') == 'addr:housenumber':
                    node_['hisna_st'] = tag.get('v')
                if tag.get('k') == 'addr:street':
                    node_['ulica'] = tag.get('v')
                if tag.get('k') == 'addr:city':
                    node_['obcina'] = tag.get('v')

            # Add node to graph
            if 'ulica' in node_.keys() and 'hisna_st' in node_.keys() and 'obcina' in node_.keys():
                if (node_['obcina'], node_['hisna_st'].upper(), node_['ulica']) in reported_by_gov:
                    graph.add_node(node_['id'],
                                   lat=str(node_['lat']),
                                   lon=str(node_['lon']),
                                   obcina=node_['obcina'],
                                   hisna_st=node_['hisna_st'],
                                   ulica=node_['ulica'],
                                   node_type='address')

    node_tree = ET.parse(f'data/osm/{obcina_filename}/{obcina_filename}-crossroads.osm')
    root = node_tree.getroot()
    nodes = root.findall('node')

    crossroads = [node.get('id') for node in nodes]

    for node in nodes:
        # Read data from node
        graph.add_node(node.get('id'),
                       lat=str(float(node.get('lat'))),
                       lon=str(float(node.get('lon'))),
                       node_type='crossroad')

    for node_1 in graph.nodes:
        if graph.nodes[node_1]['node_type'] == 'address':
            min_distance = None
            min_node_1 = None
            min_node_2 = None
            for node_2 in graph.nodes:
                if graph.nodes[node_2]['node_type'] == 'crossroad' and node_1 != node_2:
                    distance = geo_distance(float(graph.nodes[node_1]['lon']), float(graph.nodes[node_1]['lat']), float(graph.nodes[node_2]['lon']), float(graph.nodes[node_2]['lat']))
                    if min_distance is None or min_distance > distance:
                        min_distance = distance
                        min_node_1 = node_1
                        min_node_2 = node_2

            graph.add_edge(min_node_1, min_node_2, geo_dist=str(min_distance))

    way_tree = ET.parse(f'data/osm/{obcina_filename}/{obcina_filename}-ways.osm')
    root = way_tree.getroot()
    ways = root.findall('way')

    node_tree = ET.parse(f'data/osm/{obcina_filename}/{obcina_filename}-crossroads.osm')
    root = node_tree.getroot()
    nodes = root.findall('node')

    crossroads = set([node.get('id') for node in nodes])

    for way in ways:
        crs_in_way = list(filter(lambda x: x in crossroads, [nd.get('ref') for nd in way.findall('nd')]))
        if len(crs_in_way) > 1:
            edges = list(zip(crs_in_way, crs_in_way[1:]))
            # Calculate the duration of travel between crossroads and add it as attribute (weight)
            graph.add_edges_from(edges)


    # We take only the biggest component.
    graph = nx.subgraph(graph, list(nx.connected_components(graph))[0])
    nx.write_pajek(graph, f'data/graphs/{obcina_filename}.net')

graph = nx.read_pajek(f'data/graphs/{obcina_filename}.net')
net = Network(notebook=True)
net.from_nx(graph)
net.barnes_hut()
net.show("plot.html")

# graph = nx.read_pajek(f'data/graphs/{obcina_filename}.net')
# naslovi_obcina = pd.read_excel(f'data/e-prostor/{obcina_filename}.xlsx')
#
# available_addresses = list(filter(lambda x: x is not None, [(graph.nodes[node]['obcina'], graph.nodes[node]['hisna_st'], graph.nodes[node]['ulica']) if graph.nodes[node]['node_type'] == 'address' else None for node in graph.nodes]))
# reported_by_gov = list(zip(naslovi_obcina['OB_UIME'], naslovi_obcina['LABELA'], naslovi_obcina['UL_UIME']))
#
# missing = []
#
# for address1 in reported_by_gov:
#     not_in_addresses = True
#     for address2 in available_addresses:
#         if address1[0] == address2[0] and str(address1[1]).upper() == str(address2[1]).upper() and address1[2] == address2[2]:
#             not_in_addresses = False
#     if not_in_addresses:
#         missing.append(address1)
# print(f'Number of missing addresses: {len(missing)}')
# API_KEY = 'fa1549b5-21e1-4082-9ab7-a915315f0df5'
# data = {'username':'Olivia','password':'123'}
#
# r = requests.post(f'https://graphhopper.com/api/1/matrix?key={API_KEY}', data=data)

