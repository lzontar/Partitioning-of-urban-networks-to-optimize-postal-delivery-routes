import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import os



def CONTROLS():
    filenames = list(filter(lambda x: x.endswith('.net'), os.listdir('data/graphs/')))
    nets = [
        {'label': x.replace('.net', '').replace('-', ' ').upper(), 'value': x}
        for x in filenames
    ]
    return html.Div(children=[
        html.Div('Time series for clustering', className="ds-control-label"),
        dcc.Dropdown(
            id='dropdown_nets',
            options=nets,
            value='pungert.net',
            multi=False
        ),
    ], className="ds-sidebar border-right")


def CONTENT():
    return html.Div(children=[
        dcc.Graph(id='city_graph')
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
