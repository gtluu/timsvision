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
from plotly_resampler.figure_resampler import FigureResampler
from pyimzml.ImzMLParser import getionimage
from timsvision.layout import *
import seaborn as sns


def import_bruker():
    pass


def get_contour_plot(data_df):
    print('Contour Plot')
    contour_plot = px.density_contour(data_frame=data_df, x='m/z', y='1/K0',
                                      marginal_x='histogram', marginal_y='histogram', histfunc='sum',
                                      nbinsx=len(set(data_df['m/z'])),
                                      nbinsy=len(set(data_df['1/K0'])),
                                      hover_data={'m/z': ':.4f',
                                                  '1/K0': ':.3f'})
    # default_n_shown_samples=1000000)
    contour_plot.update_layout(xaxis_tickformat='d',
                               yaxis_tickformat='~e')
    return contour_plot_layout(contour_plot), contour_plot


def get_global_df(data):
    rows = []
    for i in range(0, len(data.coordinates)):
    #for i in range(0, 1):
        mzs, ints, mobs = data.getspectrum(i)
        rows.append(pd.DataFrame({'m/z': mzs,
                                  'Intensity': ints,
                                  '1/K0': mobs}))
    data_df = pd.concat(rows)
    data_df = data_df.round({'m/z': 4, '1/K0': 3})
    data_df = data_df.groupby(['m/z', '1/K0'], as_index=False).aggregate(sum)
    #data_df = data_df[data_df['Intensity'] >= (np.max(data_df['Intensity']) * 0.0001)]
    print(data_df)
    return data_df
