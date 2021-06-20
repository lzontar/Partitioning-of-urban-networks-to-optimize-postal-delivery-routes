import plotly.graph_objects as go
import networkx as nx
import utm
import plotly.express as px
import dash_html_components as html
import numpy as np
import util.lib.helper as help
import math
import pickle


def _updateGraphCity(filename):
    G = nx.read_pajek(f'data/graphs/{filename}.net')
    title = f"{filename.replace('.net', '').replace('-', ' ').upper()} PLOT"
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0, _, _ = utm.from_latlon(float(G.nodes[edge[0]]['lat']), float(G.nodes[edge[0]]['lon']))
        x1, y1, _, _ = utm.from_latlon(float(G.nodes[edge[1]]['lat']), float(G.nodes[edge[1]]['lon']))
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        name='Edges',
        line=dict(width=0.5, color='#888'),
        )

    traces = [edge_trace]
    for ix, type in enumerate(set([G.nodes[node]['node_type'] for node in G.nodes])):
        nodes = list(filter(lambda x: G.nodes[x]['node_type'] == type, G.nodes))
        node_x = []
        node_y = []
        texts = []
        groups = []
        for node in nodes:
            x, y, _, _ = utm.from_latlon(float(G.nodes[node]['lat']), float(G.nodes[node]['lon']))
            node_x.append(x)
            node_y.append(y)
            groups.append(G.nodes[node]['node_type'])
            if G.nodes[node]['node_type'] == 'crossroad':
                texts.append(f'Type: crossroad, <br>Lon:  {round(float(G.nodes[node]["lon"]), 4)}, Lat: {round(float(G.nodes[node]["lat"]), 4)}')
            else:
                texts.append(f'Type: address, <br>City: {G.nodes[node]["obcina"]},<br> Street: {G.nodes[node]["ulica"]} {G.nodes[node]["hisna_st"]}, <br>Lon:  {round(float(G.nodes[node]["lon"]), 4)}, Lat: {round(float(G.nodes[node]["lat"]), 4)}')

        traces.append(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=texts,
            name=type.capitalize(),
            marker=dict(
                color=px.colors.qualitative.Plotly[ix],
                size=10,
                line_width=2)))

    fig = go.Figure(data=traces,
                    layout=go.Layout(
                        title=title,
                        titlefont_size=16,
                        showlegend=True,
                        hovermode='closest',
                        xaxis=dict(showgrid=True, zeroline=True, showticklabels=False),
                        yaxis=dict(showgrid=True, zeroline=True, showticklabels=False))
                    )

    return fig

def _updateGraphPartition(net, alg, mu, sigma):
    G = nx.read_pajek(f'data/graphs/with_communities/{net}-{alg}.net')

    title = f"{net.replace('-', ' ').upper()} PARTITIONING ({alg.replace('-', ' ').upper()})"
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0, _, _ = utm.from_latlon(float(G.nodes[edge[0]]['lat']), float(G.nodes[edge[0]]['lon']))
        x1, y1, _, _ = utm.from_latlon(float(G.nodes[edge[1]]['lat']), float(G.nodes[edge[1]]['lon']))
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        name='Edges',
        line=dict(width=0.5, color='#888'),
        )

    traces = [edge_trace]
    cluster_enumerator = list(enumerate(set([G.nodes[node]['cluster_id'] for node in G.nodes])))
    for ix, type in cluster_enumerator:
        nodes = list(filter(lambda x: G.nodes[x]['cluster_id'] == type, G.nodes))
        node_x = []
        node_y = []
        texts = []
        groups = []
        for node in nodes:
            x, y, _, _ = utm.from_latlon(float(G.nodes[node]['lat']), float(G.nodes[node]['lon']))
            node_x.append(x)
            node_y.append(y)
            groups.append(G.nodes[node]['cluster_id'])
            if G.nodes[node]['node_type'] == 'crossroad':
                texts.append(f'Type: crossroad, <br>Lon:  {round(float(G.nodes[node]["lon"]), 4)}, Lat: {round(float(G.nodes[node]["lat"]), 4)}')
            else:
                texts.append(f'Type: address, <br>City: {G.nodes[node]["obcina"]},<br> Street: {G.nodes[node]["ulica"]} {G.nodes[node]["hisna_st"]}, <br>Lon:  {round(float(G.nodes[node]["lon"]), 4)}, Lat: {round(float(G.nodes[node]["lat"]), 4)}')

        traces.append(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=texts,
            name=type.capitalize(),
            marker=dict(
                color=px.colors.qualitative.Plotly[ix],
                size=10,
                line_width=2)))

    fig = go.Figure(data=traces,
                    layout=go.Layout(
                        title=title,
                        titlefont_size=16,
                        showlegend=True,
                        hovermode='closest',
                        xaxis=dict(showgrid=True, zeroline=True, showticklabels=False),
                        yaxis=dict(showgrid=True, zeroline=True, showticklabels=False))
                    )

    cached_file = f"cache/{net}-{alg}-{mu}-{sigma}.pickle"

    try:
        with open(cached_file, "rb") as cached:
            children = pickle.load(cached)
    except IOError:

        children = [html.H5('Partition traversal results')]
        for ix, type in cluster_enumerator:
            subgraph_nodes = list(filter(lambda x: G.nodes[x]['cluster_id'] == type, G.nodes))
            distanceMatrix = help.distance_matrix(G)
            optimalRoute, optimalPrice = help.optimalTraversal(G, subgraph_nodes, distanceMatrix)

            optimalPriceRecWait = sum(np.random.normal(mu, sigma, len(subgraph_nodes)))

            hoursOpt = math.floor(optimalPrice / 3600)
            hoursRecWait = math.floor(optimalPriceRecWait / 3600)
            minOpt = math.floor((optimalPrice - hoursOpt * 3600) / 60)
            minRecWait = math.floor((optimalPriceRecWait - hoursRecWait * 3600) / 60)
            secondsOpt = round(optimalPrice - 3600 * hoursOpt - 60 * minOpt, 2)
            secondsRecWait = round(optimalPriceRecWait - 3600 * hoursRecWait - 60 * minRecWait, 2)

            children.append(html.Div(children=[
                html.Div(f"Partition {type}:"),
                html.Ul(children=[
                            html.Li(f"number of houses: {len(list(filter(lambda x: x['node_type'] == 'address', [G.nodes[node] for node in subgraph_nodes])))},"),
                            html.Li(f"duration driving: {hoursOpt} h {minOpt} min {secondsOpt} sec"),
                            html.Li(f"duration waiting for recipient: {hoursRecWait} h {minRecWait} min {secondsRecWait} sec"),
                        ])
            ]))

            with open(cached_file, "wb") as out:
                pickle.dump(children, out)

    return fig, children
