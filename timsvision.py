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
from timsvision.layout import main_app_layout, contour_plot_layout, ion_image_layout
from timsvision.util import get_contour_plot, get_ion_image, get_global_df
from pyimzml.ImzMLParser import ImzMLParser


# relative path for directory where uploaded data is stored
DATA = None
DF = None
UPLOAD_DIR = 'upload'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Use DashProxy instead of Dash to allow for multiple callbacks to the same plot
app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])

app.layout = main_app_layout


@app.callback(Output('contour_block', 'children'),
              Output('ion_image_block', 'children'),
              Input('load', 'n_clicks'),
              State('path', 'value'))
def upload_data(n_clicks, path):
    changed_id = [i['prop_id'] for i in callback_context.triggered][0]

    if 'load' in changed_id:
        #if path.lower().endswith('imzml'):
        if True:
            global DATA
            print('Parsing imzML File')
            #DATA = ImzMLParser(path, include_spectra_metadata='full', include_mobility=True)
            DATA = ImzMLParser('C:\\Users\\bass\\code\\timsvision\\prototype\\20210921_vc_rugose_tims_gordon.imzML',
                               include_spectra_metadata='full', include_mobility=True)
            print('Creating Master DataFrame')
            global DF
            DF = get_global_df(DATA)
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
              State('ook0_tol', 'value'),
              prevent_initial_call=True)
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
              State('ook0_tol', 'value'),
              prevent_initial_call=True)
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


def main():
    app.run_server(debug=False, port=8050)


if __name__ == '__main__':
    main()
