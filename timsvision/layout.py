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


main_app_layout = html.Div(
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
                        dcc.Input(
                            id='path',
                            placeholder='imzML File Path',
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


def contour_plot_layout(contour_plot):
    return [
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


def ion_image_layout(mass, mass_tol, ook0, ook0_tol, ion_image_plot):
    return [
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

