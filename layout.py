from methods import *
from dash import html, dcc

inital_layout = [
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

                # #drag and drop uploader
                # html.Div(
                # [
                #     get_upload_component(id='dash-uploader'), #ash-uploader
                #     html.Div(id='callback-output'),
                # ],
                # style={  # wrapper div style
                #     'textAlign': 'center',
                #     'justifyContent': 'center',
                #     'width': '400px',
                #     #'height': '50px',
                #     'padding': '10px',
                #     'display': 'inline-block'
                # }),

                html.Div(
                    children=[
                        dcc.Input(
                            id='path1',
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
            style={
            'textAlign': 'center',
            },
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
    ]