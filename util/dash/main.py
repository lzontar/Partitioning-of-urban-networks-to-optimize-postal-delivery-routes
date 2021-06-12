import plotly.graph_objects as go
import networkx as nx
import utm
import plotly.express as px


def _updateGraphViz(filename):
    G = nx.read_pajek(f'data/graphs/{filename}')
    title = f"{filename.replace('.net', '').replace('-', ' ').upper()} PLOT"
    edge_x = []
    edge_y = []
    # texts = []
    for edge in G.edges():
        x0, y0, _, _ = utm.from_latlon(float(G.nodes[edge[0]]['lat']), float(G.nodes[edge[0]]['lon']))
        x1, y1, _, _ = utm.from_latlon(float(G.nodes[edge[1]]['lat']), float(G.nodes[edge[1]]['lon']))
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

        edge_data = G.get_edge_data(edge[0], edge[1])[0]
        # texts.append(f"""
        # Geo. dist.: {"nan" if 'geo_dist' not in edge_data.keys() else edge_data['geo_dist']}
        # """)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        # hoverinfo='text',
        # text=texts,
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
