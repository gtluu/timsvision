import os
import numpy as np
import pandas as pd
import plotly.express as px
import time
import sqlite3 as sq
import base64
from dash import Dash, dcc, html, State, callback_context
from dash_extensions.enrich import Input, Output, DashProxy, MultiplexerTransform
import dash_bootstrap_components as dbc
from pyimzml.ImzMLParser import ImzMLParser, getionimage


# relative path for directory where uploaded data is stored
DATA = None
DF = None
UPLOAD_DIR = 'upload'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Use DashProxy instead of Dash to allow for multiple callbacks to the same plot
app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])

app.layout = html.Div(
    [
        # logo element
        html.Div(
            children=[
                html.Img(
                    src='assets/timsvision_logo_mini.png',
                    alt='TIMSvision Logo',
                    width="375"
                )
            ],
            style={
                'display': 'flex',
                'justifyContent': 'center',
                'padding': '25px'},
            className='row'
        ),

        # upload element
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H4('Input imzML File:'),
                    ],
                    style={
                        'width': '1440px',
                        'height': '25px',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'font-family': 'Arial',
                        'font-size': '20px',
                        'position': 'relative',
                        'top': '-35px'
                    }
                ),
                html.Div(
                    children=[
                        dcc.Input(
                            id='path',
                            placeholder='imzML File',
                            type='text'
                        )
                    ],
                    style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'width': '100%',
                        'padding': '10px'
                    }
                ),
                html.Div(
                    children=[
                        html.Button(
                            'Load',
                            id='load'
                        )
                    ],
                    style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'width': '100%',
                        'padding': '10px'
                    }
                )
            ],
            className='row',
        ),

        # ion image ui elements
        html.Div(
            id='ion_image_block',
            className='row'
        ),

        html.Div(
            id='contour_block',
            className='row'
        ),
    ],
    style={
        'font-family': 'Lucida Sans Unicode'
    }
)


def get_contour_plot(data_df):
    print('Contour Groupby')
    contour_df = data_df.groupby(['mz', 'mobility'], as_index=False).aggregate(sum)
    print('Contour Subset')
    contour_df = contour_df[contour_df['intensity'] >= (np.max(contour_df['intensity']) * 0.0002)]

    print('Contour Plot')
    contour_plot = px.density_contour(data_frame=contour_df, x='mz', y='mobility',
                                      marginal_x='histogram', marginal_y='histogram', histfunc='sum',
                                      nbinsx=20000, nbinsy=len(set(contour_df['mobility'])) // 2)

    children = [
       html.Div(
           dcc.Graph(
               id='contour',
               figure=contour_plot
           ),
           style={
               'border': '1px solid black',
               'position': 'relative',
               'top': '-250px',
               'width': '1250px',
               'margin-right': '10vw'
           }
       )
    ]

    return children


def get_ion_image(data, mass=0.0, mass_tol=0.0, ook0=0.0, ook0_tol=0.0, blank=False):
    if not blank:
        print('Not Blank')
        ion_image = getionimage(data,
                                mz_value=float(mass),
                                mz_tol=float(mass_tol),
                                mob_value=float(ook0),
                                mob_tol=float(ook0_tol))
        ion_image_plot = px.imshow(ion_image, color_continuous_scale='viridis')
    elif blank:
        print('Blank')
        ion_image_plot = px.imshow(np.zeros((2, 2)), color_continuous_scale='viridis')

    children = [
        html.Div(
            children=[
                html.H5('m/z:'),
            ],
            style={
                'display': 'inline-block',
                'position': 'relative',
                'top': '90px',
                'font-family': 'Arial',
                'font-size': '20px',
                'padding-left': '120px'
            }
        ),
        html.Div(
            children=[
                dcc.Input(
                    id='mass',
                    value=mass,
                    type='text'
                ),
            ],
            style={'position': 'relative',
                   'top': '65px',
                   'width': '150px',
                   'font-family': 'Arial',
                   'font-size': '20px',
                   'padding-left': '120px',
                   'border-color': '#0047AB'
                   }
        ),
        html.Div(
            children=[
                html.H5('m/z Tolerance:'),
            ],
            style={
                'position': 'relative',
                'top': '60px',
                'display': 'inline-block',
                'font-family': 'Arial',
                'font-size': '20px',
                'padding-left': '120px'
            }
        ),
        html.Div(
            children=[
                dcc.Input(
                    id='mass_tol',
                    value=mass_tol,
                    type='text'
                ),
            ],
            style={'position': 'relative',
                   'top': '35px',
                   'width': '150px',
                   'font-family': 'Arial',
                   'font-size': '20px',
                   'padding-left': '120px'}),
        html.Div(
            children=[
                html.H5('1/K0:'),
            ],
            style={
                'position': 'relative',
                'top': '30px',
                'display': 'inline-block',
                'font-family': 'Arial',
                'font-size': '20px',
                'padding-left': '120px'
            }
        ),
        html.Div(
            children=[
                dcc.Input(
                    id='ook0',
                    value=ook0,
                    type='text'
                ),
            ],
            style={
                'position': 'relative',
                'top': '5px',
                'width': '150px',
                'font-family': 'Arial',
                'font-size': '20px',
                'padding-left': '120px'
            }
        ),
        html.Div(
            children=[
                html.H5('1/K0 Tolerance:'),
            ],
            style={
                'position': 'relative',
                'top': '0px',
                'display': 'inline-block',
                'font-family': 'Arial',
                'font-size': '20px',
                'padding-left': '120px'
            }
        ),
        html.Div(
            children=[
                dcc.Input(
                    id='ook0_tol',
                    value=ook0_tol,
                    type='text'
                ),
            ],
            style={
                'position': 'relative',
                'top': '-25px',
                'width': '150px',
                'font-family': 'Arial',
                'font-size': '20px',
                'padding-left': '120px'
            }
        ),
        html.Div(
            children=[
                html.Div(
                    html.Button(
                        'Update Ion Image',
                        id='update'
                    )
                ),
            ],
            style={
                'border-radius': '20px',
                'display': 'inline-block',
                'margin-right': '9vw',
                'font-family': 'Arial',
                'font-size': '25px',
                'position': 'relative',
                'top': '-10px',
                'padding-left': '140px'
            }
        ),
        html.Div(
            id='ion_image',
            children=[
                dcc.Graph(
                    id='image',
                    figure=ion_image_plot
                )
            ],
            style={
                'border': '1px solid black',
                'display': 'inline-block',
                'vertical-align': 'top',
                'position': 'relative',
                'top': '-350px'
            }
        )
    ]

    return children


@app.callback(Output('contour_block', 'children'),
              Output('ion_image_block', 'children'),
              Input('load', 'n_clicks'),
              State('path', 'value'))
def upload_data(n_clicks, path):
    changed_id = [i['prop_id'] for i in callback_context.triggered][0]

    if 'load' in changed_id:
        if path.lower().endswith('imzml'):
            global DATA
            print('Parsing imzML File')
            DATA = ImzMLParser(path, include_spectra_metadata='full', include_mobility=True)
            print('Creating Master DataFrame')
            rows = []
            for i in range(0, len(DATA.coordinates)):
                mzs, ints, mobs = DATA.getspectrum(i)
                rows.append(pd.DataFrame({'mz': mzs,
                                          'intensity': ints,
                                          'mobility': mobs}))
                #for mz, intensity, mob in zip(mzs.tolist(), ints.tolist(), mobs.tolist()):
                #    rows.append({'mz': mz,
                #                 'intensity': intensity,
                #                 'mobility': mob})
            global DF
            #DF = pd.DataFrame(data=rows)
            DF = pd.concat(rows)
            print('Getting Contour Plot')
            contour_child = get_contour_plot(DF)
            print('Getting Overall Ion Image')
            ion_image_child = get_ion_image(DATA, mass_tol=0.05, ook0_tol=0.05, blank=True)
            return [contour_child, ion_image_child]


@app.callback(Output('ion_image_block', 'children'),
              Input('update', 'n_clicks'),
              State('mass', 'value'),
              State('mass_tol', 'value'),
              State('ook0', 'value'),
              State('ook0_tol', 'value'))
def update_ion_image(n_clicks, mass, mass_tol, ook0, ook0_tol):
    changed_id = [i['prop_id'] for i in callback_context.triggered][0]

    if 'update' in changed_id:
        if n_clicks is not None:
            global DATA
            print('Updating Ion Image')
            return get_ion_image(DATA,
                                 mass=mass,
                                 mass_tol=mass_tol,
                                 ook0=ook0,
                                 ook0_tol=ook0_tol)


@app.callback(Output('ion_image_block', 'children'),
              Input('contour', 'clickData'),
              State('mass_tol', 'value'),
              State('ook0_tol', 'value'))
def update_ion_image_from_contour(coords, mass_tol, ook0_tol):
    global DATA
    print('Updating Ion Image from Heatmap')
    mass = coords['points'][0]['x']
    ook0 = coords['points'][0]['y']
    return get_ion_image(DATA,
                         mass=mass,
                         mass_tol=mass_tol,
                         ook0=ook0,
                         ook0_tol=ook0_tol)


if __name__ == '__main__':
    app.run_server(debug=False, port=8050)
