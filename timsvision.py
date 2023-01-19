import os
import numpy as np
import pandas as pd
import plotly.express as px
import time
import sqlite3 as sq
from dash import Dash, dcc, html, Input, Output, State, callback_context
from pyimzml.ImzMLParser import ImzMLParser, getionimage

app = Dash(__name__)

app.layout = html.Div([
    html.Div(children=[
        html.Img(src='assets/timsvision_logo_mini.png', alt='TIMSvision Logo', width="375")
    ], style={'display': 'flex', 'justifyContent': 'center', 'padding': '25px'}, className='row'),

#shifit down
    html.Div(children=[
        html.Div(children=[
            html.H4('Input imzML File:'),
        ], style={'width': '250px', 'display': 'flex', 'justifyContent': 'center', 'font-family': 'Times New Roman', 'font-size': '20px', 'width': '1440px', 'height': '25px', 'position':'relative', 'top':'-35px'}),
        html.Div(children=[
            dcc.Input(id='path', placeholder='imzML File', type='text')
        ], style={'display': 'flex', 'justifyContent': 'center', 'width': '100%', 'padding' : '10px'})
    ], className='row'),

#blue border #0047AB
    html.Div(children=[
        html.Div(children=[
            html.H5('m/z:'),
        ], style={'display': 'inline-block', 'position':'relative', 'top':'90px','font-family': 'Times New Roman', 'font-size': '20px', 'padding-left': '120px'}),
        html.Div(children=[
            dcc.Input(id='mass', value=0, type='text'),
        ], style={'position':'relative', 'top':'65px', 'width': '150px','font-family': 'Times New Roman', 'font-size': '20px', 'padding-left': '120px', 'border-color': '#0047AB'}),
        html.Div(children=[
            html.H5('m/z Tolerance:'),
        ], style={'position':'relative', 'top':'60px', 'display': 'inline-block','font-family': 'Times New Roman', 'font-size': '20px', 'padding-left': '120px'}),
        html.Div(children=[
            dcc.Input(id='mass_tol', value=0, type='text'),
        ], style={'position':'relative', 'top':'35px', 'width': '150px','font-family': 'Times New Roman', 'font-size': '20px', 'padding-left': '120px'}),
        html.Div(children=[
            html.H5('1/K0:'),
        ], style={'position':'relative', 'top':'30px', 'display': 'inline-block','font-family': 'Times New Roman', 'font-size': '20px', 'padding-left': '120px'}),
        html.Div(children=[
            dcc.Input(id='ook0', value=0, type='text'),
        ], style={'position':'relative', 'top':'5px', 'width': '150px','font-family': 'Times New Roman', 'font-size': '20px', 'padding-left': '120px'}),
        html.Div(children=[
            html.H5('1/K0 Tolerance:'),
        ], style={'position':'relative', 'top':'0px', 'display': 'inline-block', 'font-family': 'Times New Roman', 'font-size': '20px', 'padding-left': '120px'}),
        html.Div(children=[
            dcc.Input(id='ook0_tol', value=0, type='text'),
        ], style={'position':'relative', 'top':'-25px', 'width': '150px','font-family': 'Times New Roman', 'font-size': '20px', 'padding-left': '120px'}),
        html.Div(children=[
            html.Div(html.Button('Update Plots', id='update')),
        ], style={'border-radius': '20px', 'display': 'inline-block', 'margin-right': '9vw', 'font-family': 'Times New Roman', 'font-size': '25px', 'position':'relative', 'top':'-10px', 'padding-left': '140px'}),
        html.Div(children=[
            dcc.Graph(id='image', figure={})
        ], style={'border': '1px solid black','display': 'inline-block', 'vertical-align': 'top', 'position':'relative', 'top':'-350px'})
    ], className='row'),

#label table, center second table
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id='contour', figure={}),
        ], style = {'border': '1px solid black', 'position':'relative', 'top':'-250px', 'width': '1250px', 'margin-right': '10vw'})
    ], className='row'),

    dcc.Store(id='stored_path')
], style={'font-family': 'Lucida Sans Unicode'})


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
        current = time.time()

        data = ImzMLParser(path, include_spectra_metadata='full', include_mobility=True)
        print("1st time flag", (time.time()-current))
        current = time.time()
        mz_array = np.zeros(0)
        intensity_array = np.zeros(0)
        mobility_array = np.zeros(0)
###       totalTime = time.time()
###       print("Time in seconds since the epoch:", totalTime)
        for i in range(0, len(data.coordinates)):
            startLoopTime = time.time()
            mzs, ints, mobs = data.getspectrum(i)
            mz_array = np.append(mz_array, mzs) #1
            intensity_array = np.append(intensity_array, ints)  #2
            mobility_array = np.append(mobility_array, mobs) #3

        print('loop time flag: ' + str((time.time() - start)))
            #timestamp
        endLoopTime = time.time()
        print('loop: ' + str(endLoopTime-startLoopTime))

            #timestamp
            endLoopTime = time.time()
            print('loop: ' + str(endLoopTime-startLoopTime))

        #print('total' + totalTime)
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

        print(contour_plot)
        print('contour time flag: ' + str((time.time() - start)))

        start = time.time()
        ion_image_plot = px.imshow(ion_image, color_continuous_scale='viridis')
        print('ion time flag: ' + str((time.time() - start)))

        startIon = time.time()
        ion_image_plot = px.imshow(ion_image, color_continuous_scale='viridis')
        #timestamp
        endiontime = time.time()
        print('ion: ' + str(startIon-endiontime))

        startIon = time.time()
        ion_image_plot = px.imshow(ion_image, color_continuous_scale='viridis')
        #timestamp
        endiontime = time.time()
        print('ion: ' + str(startIon-endiontime))
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
