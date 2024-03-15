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
from timsvision.layout import *
from pyimzml.ImzMLParser import getionimage


def import_bruker():
    pass


def get_contour_plot(data_df):
    print('Contour Plot')
    contour_plot = px.density_contour(data_frame=data_df, x='mz', y='mobility',
                                      marginal_x='histogram', marginal_y='histogram', histfunc='sum',
                                      nbinsx=20000, nbinsy=len(set(data_df['mobility'])) // 2)

    return contour_plot_layout(contour_plot)


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

    return ion_image_layout(mass, mass_tol, ook0, ook0_tol, ion_image_plot)


def get_global_df(list_of_spectra):
    rows = []
    for i in list_of_spectra:
        rows.append(pd.DataFrame({'mz': i.mz_array,
                                  'intensity': i.intensity_array,
                                  'mobility': i.mobility_array}))
    data_df = pd.concat(rows)
    #data_df = data_df.round({'mz': 4, 'mobility': 3})
    data_df = data_df.groupby(['mz', 'mobility'], as_index=False).aggregate(sum)
    #data_df = data_df[data_df['intensity'] >= (np.max(data_df['intensity']) * 0.0001)]
    print(data_df)
    return data_df
