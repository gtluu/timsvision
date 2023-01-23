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
            dcc.Upload(
                id='upload',
                children=html.Div(
                    [
                        'Drag and Drop or ',
                        html.A('Select mzML Files')
                    ]
                ),
                style={
                    'width': '97%',
                    'height': '100px',
                    'lineHeight': '100px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '20px'
                },
                multiple=True
            )
        ),

        html.Div(
            id='plots',
            [
                # ion image ui elements
                html.Div(
                    id='ion_image_block',
                    children=[
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
                                    value=0,
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
                                    value=0,
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
                                    value=0,
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
                                    value=0,
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
                                        'Update Plots',
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
                                dcc.Graph(id='image', figure={})
                            ],
                            style={
                                'border': '1px solid black',
                                'display': 'inline-block',
                                'vertical-align': 'top',
                                'position': 'relative',
                                'top': '-350px'
                            }
                        )
                    ],
                    className='row'
                ),

                html.Div(
                    id='contour_block',
                    children=[
                        html.Div(
                            children=[
                                dcc.Graph(id='contour', figure={}),
                            ],
                            style={
                                'border': '1px solid black',
                                'position': 'relative',
                                'top': '-250px',
                                'width': '1250px',
                                'margin-right': '10vw'
                            }
                        )
                    ],
                    className='row'
                )
            ]
        ),
        dcc.Store(id='stored_path')
    ],
    style={
        'font-family': 'Lucida Sans Unicode'
    }
)


@app.callback(Output('plots', 'children'),
              Input('upload', 'contents'),
              State('upload', 'filename'))
def upload_data(list_of_contents, list_of_filenames):
    if list_of_contents is not None:
        for contents, filename in zip(list_of_contents, list_of_filenames):
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)


@app.callback(Output(component_id='contour', component_property='figure'),
              Output(component_id='image', component_property='figure'),
              Output(component_id='stored_path', component_property='data'),
              Input(component_id='update', component_property='n_clicks'),
              State(component_id='path', component_property='value'),
              State(component_id='mass', component_property='value'),
              State(component_id='mass_tol', component_property='value'),
              State(component_id='ook0', component_property='value'),
              State(component_id='ook0_tol', component_property='value'),)
def load_data(n_clicks, path, mass, mass_tol, ook0, ook0_tol):
    changed_id = [i['prop_id'] for i in callback_context.triggered][0]

    if 'update' in changed_id:
        start = time.time()
        data = ImzMLParser(path, include_spectra_metadata='full', include_mobility=True)
        print('upload time flag: ' + str((time.time() - start)))
        mz_array = np.zeros(0)
        intensity_array = np.zeros(0)
        mobility_array = np.zeros(0)

        start = time.time()
        data = ImzMLParser(path, include_spectra_metadata='full', include_mobility=True)
        print('loop time flag: ' + str((time.time() - start)))
        current = time.time()
        mz_array = np.zeros(0)
        intensity_array = np.zeros(0)
        mobility_array = np.zeros(0)
        for i in range(0, len(data.coordinates)):
            startLoopTime = time.time()
            mzs, ints, mobs = data.getspectrum(i)
            mz_array = np.append(mz_array, mzs) #1
            intensity_array = np.append(intensity_array, ints)  #2
            mobility_array = np.append(mobility_array, mobs) #3
        print('loop time flag: ' + str((time.time() - start)))

        data_df = pd.DataFrame(data={'mz': mz_array,
                                     'intensity': intensity_array,
                                     'mobility': mobility_array})

        start = time.time()
        contour = data_df.groupby(['mz', 'mobility'], as_index=False).aggregate(sum)
        contour = contour[contour['intensity'] >= (np.max(contour['intensity']) * 0.0002)]

        ion_image = getionimage(data, mz_value=float(mass), mz_tol=float(mass_tol),
                                mob_value=float(ook0), mob_tol=float(ook0_tol))
        print('ion time flag: ' + str((time.time() - start)))

        conn = sq.connect('{}.sqlite'.format('timsvisions_extension'))
        data_df.to_sql('timsvisions_extension', conn, if_exists='replace', index=False) 
        conn.close() 

        ion_image = getionimage(data, mz_value=float(mass), mz_tol=float(mass_tol), mob_value=float(ook0), mob_tol=float(ook0_tol))

        start = time.time()
        contour_plot = px.density_contour(data_frame=contour, x='mz', y='mobility',
                                          marginal_x='histogram', marginal_y='histogram', histfunc='sum',
                                          nbinsx=20000, nbinsy=len(set(contour['mobility'])) // 2)
        print('contour time flag: ' + str((time.time() - start)))

        start = time.time()
        ion_image_plot = px.imshow(ion_image, color_continuous_scale='viridis')
        print('ion time flag: ' + str((time.time() - start)))

        return [contour_plot, ion_image_plot, {'stored_path': path}]


@app.callback(Output(component_id='mass', component_property='value'),
              Output(component_id='ook0', component_property='value'),
              Input('contour', 'clickData'),)
def update_inputs(coords):
    mass = coords['points'][0]['x']
    ook0 = coords['points'][0]['y']
    return [mass, ook0]


if __name__ == '__main__':
    app.run_server(debug=False, port=8051)
