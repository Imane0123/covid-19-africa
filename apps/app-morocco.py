# -*- coding: utf-8 -*-
# TODO share data between callbacks: see  https://dash.plotly.com/sharing-data-between-callbacks
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq             as daq
from dash.dependencies import Output, Input, State

import plotly.graph_objs as go
import numpy as np
from pandas import read_csv
import pandas as pd
from datetime import datetime as dt
import datetime

from utilities import load_country_map
from utilities import load_country_patients
from utilities import compute_barycenters
from utilities import plotly_country_map
from utilities import plotly_country_n_patients
from utilities import select_by_date

# ...
COUNTRY = 'Morocco'
# ...

# ...
app = dash.Dash(__name__)
# ...

# ...
namespace = {}
namespace['contours'] = load_country_map(COUNTRY)
namespace['patients'] = load_country_patients(COUNTRY)

provinces = list(namespace['contours'].keys())

d_barycenters = compute_barycenters(namespace['contours'])
# ...

# =================================================================
app.layout = html.Div([
    html.H2('COVID-19'),
    #
    html.Div(className='Container', children=[
        html.Div(className='seven columns', children=[
            html.Div([dcc.Graph(id="map")]),
        ]),
        #
        html.Div(className='four columns', children=[
            #
            html.Div([
                html.Label('Province'),
                dcc.Dropdown(id="province",
                             options=[{'label':name, 'value':name}
                                      for name in provinces],
                             value=[],
                             multi=True),
            ]),
            html.Label('Period'),
            html.Div([
                dcc.DatePickerRange(id='date-picker-range',
                                    start_date=dt(2020, 3, 2),
                                    end_date=datetime.date.today()),
#                                    end_date_placeholder_text='Select a date!',
            ]),
            html.Div([
                html.Div([dcc.Graph(id="graph")]),
            ]),
        ]),
    ])
])

# =================================================================
@app.callback(
    Output("map", "figure"),
    [Input("province", "value"),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_map(provinces, start_date, end_date):

    # ...
    # TODO we should use dash storage
    date_key = 'confirmed_date'

    df = select_by_date(namespace['patients'], date_key, start_date, end_date)
    # ...

    traces = []

    # ...
    if 'contours' in list(namespace.keys()):
        d_contours = namespace['contours']
        for province, contour in d_contours.items():
            highlighted = province in provinces
            traces += plotly_country_map(province, contour,
                                         highlighted=highlighted)
    # ...

    # ...
    traces += plotly_country_n_patients(d_barycenters, df)
    # ...

    # ...
    showlegend = False
    layout = go.Layout( xaxis=dict(showticklabels=False,
                                   showgrid=False,
                                   zeroline=False),
                        yaxis=dict(scaleanchor="x",
                                   scaleratio=1,
                                   autorange='reversed',
                                   showticklabels=False,
                                   showgrid=False,
                                   showline=False,
                                   zeroline=False),
                        showlegend=showlegend,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                      )
    # ...

    return {'data': traces, 'layout': layout}

# =================================================================
@app.callback(
    Output("graph", "figure"),
    [Input("province", "value"),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(provinces, start_date, end_date):

    traces = []

    # ...
    layout = go.Layout( xaxis=dict(showticklabels=True,
                                   showgrid=False,
                                   zeroline=False),
                        yaxis=dict(scaleanchor="x",
                                   scaleratio=1,
                                   showticklabels=True,
                                   showgrid=True,
                                   showline=True,
                                   zeroline=True),
                        showlegend=True,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                      )
    # ...

    if len(provinces) == 0:
        return {'data': traces, 'layout': layout}

    # ...
    # TODO we should use dash storage
    date_key = 'confirmed_date'

    df = select_by_date(namespace['patients'], date_key, start_date, end_date)
    # ...

    # ...
    df0 =  pd.DataFrame([0, 0], index=pd.to_datetime([start_date, end_date]))

    for province in provinces:
        _df = df[df['province'] == province]

        dt_series = _df[date_key].value_counts()
        dt_series = dt_series.append(df0)

        dt_series.sort_index(inplace=True)
        dt_series = dt_series.asfreq('D')
        dt_series = dt_series.fillna(0)
        dt_series = dt_series.cumsum()

        dates = dt_series.axes[0]
        days = dates.day
        months = dates.month
        dates = ['{d}/{m}'.format(d=d, m=m) for d,m in zip(days, months)]

        values = dt_series.values[:,0]

        line_marker = dict(width=2)

        trace = go.Scatter(
            x=dates,
            y=values,
            mode = 'lines',
            name=province,
            line=line_marker,
        )

        traces.append(trace)
    # ...

    return {'data': traces, 'layout': layout}



###########################################################
if __name__ == '__main__':

    app.run_server(debug=True)
