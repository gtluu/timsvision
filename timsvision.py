import os
import numpy as np
import pandas as pd
import plotly.express as px
#import plotly.graph_objects as px
import time
import sqlite3 as sq
import base64
from layout import *

import dash_uploader as du
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

# 1) configure the upload folder
du.configure_upload(app, r"C:\tmp\Uploads")

# 2) Use the Upload component
app.layout = html.Div([
    du.Upload(),
])

app.layout = html.Div(
    inital_layout,
    style={
        'font-family': 'Lucida Sans Unicode'
    }
)

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
            rows = {'mz':[], 'intensity':[], 'mobility':[]}
            start = time.time()
            inner_time = 0
            for i in range(0, len(DATA.coordinates)):
                mzs, ints, mobs = DATA.getspectrum(i)
                inner = 0
                inner = time.time()
                for mz, intensity, mob in zip(mzs.tolist(), ints.tolist(), mobs.tolist()):
                    rows['mz'].append(mz)
                    rows['intensity'].append(intensity)
                    rows['mobility'].append(mob)
                    inner_time += time.time() - inner
            print('inner_time: ' + str(inner_time/100000))
            print('outer loop time flag: ' + str((time.time() - start)/100000))
            global DF
            DF = pd.DataFrame(data=rows)
            print('Getting Contour Plot')
            contour_child = get_contour_plot(DF)
            print('Getting Overall Ion Image')
            ion_image_child = get_ion_image(DATA)
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
        global DATA
        print('Updating Ion Image')
        return get_ion_image(DATA,
                             mass=mass,
                             mass_tol=mass_tol,
                             ook0=ook0,
                             ook0_tol=ook0_tol)

@app.callback(Output('mass', 'value'),
              Output('ook0', 'value'),
              Input('contour', 'clickData'),)

def update_inputs(coords):
    print('Updated Coordinates')
    mass = ['points', 0, 'x']
    print(mass)
    ook0 = ['points',0,'y']
    print(ook0)
    return [mass, ook0]

if __name__ == '__main__':
    app.run_server(debug=False, port=8051)