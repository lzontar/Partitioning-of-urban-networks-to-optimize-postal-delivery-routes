import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

from util.dash.layout import *

import dash

from util.dash.main import _updateGraphCity, _updateGraphPartition

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    {
        'href': 'https://use.fontawesome.com/releases/v5.15.3/css/all.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-SZXxX4whJ79/gErwcOYf+zWLeJdY/qpuqC4cAa9rOGUstPomtqpuNWT9wdPEn2fk',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash("INA", external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div(LAYOUT())


@app.callback(
    Output(component_id='city_graph', component_property='figure'),
    Input(component_id='dropdown_nets', component_property='value'),
)
def updateGraphCity(dropdown_net):
    return _updateGraphCity(dropdown_net)

@app.callback(
    Output(component_id='partition_graph', component_property='figure'),
    Input(component_id='partition_button', component_property='n_clicks'),
    [
        State(component_id='dropdown_nets', component_property='value')
    ]
)
def updateGraphPartition(partition_button, net):
    return _updateGraphPartition(net)


if __name__ == '__main__':
    app.run_server(port='3010')
