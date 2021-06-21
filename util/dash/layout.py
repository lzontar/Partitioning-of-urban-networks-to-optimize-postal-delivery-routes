import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import os



def CONTROLS():
    filenames = list(filter(lambda x: x.endswith('.net'), os.listdir('data/graphs/')))
    nets = [
        {'label': x.replace('.net', '').replace('-', ' ').upper(), 'value': x.replace('.net', '')}
        for x in filenames
    ]
    return html.Div(children=[
        html.Div('Time series for clustering', className="ds-control-label"),
        dcc.Dropdown(
            id='dropdown_nets',
            options=[{'label': 'TOLMIN', 'value': 'tolmin'}],
            value='tolmin',
            multi=False,
            style={
                'marginTop': '2%'
            }
        ),
        dcc.Dropdown(
            id='dropdown_algs',
            options=[
                {'label': 'K-MEANS', 'value': 'k-means'},
                {'label': 'ASYNC FLUID', 'value': 'async-fluid'},
                {'label': 'AGDL', 'value': 'agdl'},
                {'label': 'GIRVAN NEWMAN', 'value': 'girvan-newman'},
                {'label': 'KCUT WEIGHTED NODES', 'value': 'kcut-weighted-nodes'},
                {'label': 'KCUT EDGE DURATION', 'value': 'kcut-edge-duration'},
                {'label': 'KCUT EDGE DISTANCE', 'value': 'kcut-edge-distance'},
                {'label': 'K-MEANS (EQUIVALENT SAMPLE SIZE)', 'value': 'k-means-size'},
            ],
            value='agdl',
            multi=False,
            style={
                'marginTop': '2%'
            }
        ),
        # html.Div('Average time postman waits for delivery recipient (seconds)', className="ds-control-label-inline"),
        # dcc.Input(id='mu', type="number", value=60,
        #           className='ds-control-input-inline'),
        # html.Div('Standard deviation postman waits for delivery recipient (seconds)', className="ds-control-label-inline"),
        # dcc.Input(id='sigma', type="number", value=120,
        #           className='ds-control-input-inline'),
        dbc.Button(
            id='partition_button',
            n_clicks=0,
            children='Partition',
            color='primary',
            block=True,
            style={
                'marginTop': '2%'
            }
        )
    ], className="ds-sidebar border-right")


def CONTENT():
    return html.Div(children=[
        dcc.Graph(id='city_graph'),
        dcc.Graph(id='partition_graph'),
        html.Div(id='results')
    ], className='ds-content')


def LAYOUT():
    return [
        html.Div(children=[
            dcc.Location(id='url', refresh=False),
            html.Nav(className="nav nav-pills navbar-light bg-light ds-nav border-bottom sticky-top", children=[
                html.H5('Partitioning of urban networks to optimize postal delivery routes',
                        className="ds-nav-title nav-el navbar-brand mr-auto p-2 px-3"),
            ]),
            html.Div(id='page-content', children=[
                CONTROLS(),
                CONTENT()
            ])
        ])
    ]
