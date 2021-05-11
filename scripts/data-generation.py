import pandas as pd
import xml.etree.cElementTree as ET
import networkx as nx
import math

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

generate_graph = True
zgeneriraj_csv = False

if zgeneriraj_csv:


    # To izvedemo le prvič, da se zgenerira Excel datoteka
    # ulice_vse = pd.read_csv('data/UL_VSE.csv', encoding='utf-8', delimiter=';')
    # ulice_vse.to_excel('data/ulice.xlsx')

    ulice = pd.read_excel('data/ulice.xlsx')
    obcine = pd.read_excel('data/obcine.xlsx')
    hisne_stevilke = pd.read_excel('data/hisne-stevilke.xlsx')

    # Vzamemo le željeno občino
    obcine = obcine[obcine['OB_UIME'] == obcina]

    # Združimo tabele skupaj, da dobimo vse naslove iz občine
    ulice_obcina = pd.merge(obcine, ulice, how="inner", on=["OB_MID"])
    naslovi_obcina = pd.merge(ulice_obcina, hisne_stevilke, how="inner", on=["UL_MID"])['']

    # Shranimo dataframe v excel
    naslovi_obcina.to_excel(f'data/{obcina_filename}.xlsx')

if generate_graph:
    naslovi_obcina = pd.read_excel(f'data/{obcina_filename}.xlsx')

    node_tree = ET.parse(f'data/{obcina_filename}-nodes.osm')
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

            # Add node to graph
            if 'ulica' in node_.keys() and 'hisna_st' in node_.keys():
                graph.add_node(node_['id'],
                               lat=node_['lat'],
                               lon=node_['lon'],
                               obcina=node_['obcina'],
                               hisna_st=node_['hisna_st'],
                               ulica=node_['ulica'],
                               node_type='address')

    node_tree = ET.parse(f'data/{obcina_filename}-crossroads.osm')
    root = node_tree.getroot()
    nodes = root.findall('node')

    for node in nodes:
        # Read data from node
        graph.add_node(node.get('id'),
                       lat=float(node.get('lat')),
                       lon=float(node.get('lon')),
                       node_type='crossroad')


    for node_1 in graph.nodes:
        if graph.nodes[node_1]['node_type'] == 'crossroad':
            min_distance = None
            min_node_1 = None
            min_node_2 = None
            for node_2 in graph.nodes:
                if graph.nodes[node_2]['node_type'] == 'crossroad' and node_1 != node_2:
                    distance = geo_distance(graph.nodes[node_1]['lon'], graph.nodes[node_1]['lat'], graph.nodes[node_2]['lon'], graph.nodes[node_2]['lat'])
                    if min_distance is None or min_distance > distance:
                        min_distance = distance
                        min_node_1 = node_1
                        min_node_2 = node_2

            graph.add_edge(min_node_1, min_node_2, geo_dist=min_distance)

    for node_1 in graph.nodes:
        if graph.nodes[node_1]['node_type'] == 'address':
            min_distance = None
            min_node_1 = None
            min_node_2 = None
            for node_2 in graph.nodes:
                if graph.nodes[node_2]['node_type'] == 'crossroad' and node_1 != node_2:
                    distance = geo_distance(graph.nodes[node_1]['lon'], graph.nodes[node_1]['lat'], graph.nodes[node_2]['lon'], graph.nodes[node_2]['lat'])
                    if min_distance is None or min_distance > distance:
                        min_distance = distance
                        min_node_1 = node_1
                        min_node_2 = node_2

            graph.add_edge(min_node_1, min_node_2, geo_dist=min_distance)


    nx.write_pajek(graph, f'data/{obcina_filename}.net')
