import numpy as np
import plotly.express as px
import time
import uuid
import dash_uploader as du

from dash import Dash, dcc, html, State, callback_context
from pyimzml.ImzMLParser import ImzMLParser, getionimage

def get_contour_plot(data_df):
    print('contour start')
    start = time.time()
    data_df.sort_values(by='mz', inplace=True)
    contour_df = data_df.groupby(['mz', 'mobility'], as_index=False).aggregate(sum)
    contour_df = contour_df[contour_df['intensity'] >= (np.max(contour_df['intensity']) * 0.0002)]
    contour_df = contour_df.round({'mz': 4, 'mobility': 3})
    print('contour df time flag: ' + str((time.time() - start)))
    start = time.time()
    global contour_plot
    contour_plot = px.density_contour(data_frame=contour_df, x='mz', y='mobility',
                                      marginal_x='histogram', marginal_y='histogram', histfunc='sum',
                                      nbinsx=20000, nbinsy=len(set(contour_df['mobility'])) // 2)
    print('contour plot time flag: ' + str((time.time() - start)))

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

def get_ion_image(data, mass=0, mass_tol=0, ook0=0, ook0_tol=0):
    start = time.time()
    ion_image = getionimage(data,
                            mz_value=float(mass),
                            mz_tol=float(mass_tol),
                            mob_value=float(ook0),
                            mob_tol=float(ook0_tol))

    ion_image_plot = px.imshow(ion_image, color_continuous_scale='viridis')
    print('get_ion_image time flag: ' + str((time.time() - start)))

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

def update_ion_image(n_clicks, mass, mass_tol, ook0, ook0_tol):
    changed_id = [i['prop_id'] for i in callback_context.triggered][0]

    if 'update' in changed_id:
        global DATA
        print('Updating Ion Image')
        return get_ion_image(DATA,
                             mass=mass,
                             mass_tol=mass_tol,
                             ook0=ook0,
                             ook0_tol=ook0_tol)

def get_upload_component(id):
    return du.Upload(
        id=id,
        max_file_size=1800,  # 1800 Mb
        filetypes=['imzML', 'ibd'],
        upload_id=uuid.uuid1(),  # Unique session id
    )                             

def removeConsecutiveDuplicates(s):
    if len(s) < 2:
        return s
    if s[0] != s[1]:
        return s[0]+removeConsecutiveDuplicates(s[1:])
    return removeConsecutiveDuplicates(s[1:])