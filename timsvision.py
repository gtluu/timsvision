import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, callback_context
from pyimzml.ImzMLParser import ImzMLParser, getionimage

app = Dash(__name__)

app.layout = html.Div([
    html.Div(html.H1('TIMSvision')),
    html.Div(html.H4('Input imzML File')),
    html.Div([dcc.Input(id='path', placeholder='imzML file', type='text')]),
    html.Div(html.H5('m/z')),
    html.Div([dcc.Input(id='mass', value=0, type='text')]),
    html.Div(html.H5('m/z tolerance')),
    html.Div([dcc.Input(id='mass_tol', value=0, type='text')]),
    html.Div(html.H5('1/k0')),
    html.Div([dcc.Input(id='ook0', value=0, type='text')]),
    html.Div(html.H5('1/k0 tolerance')),
    html.Div([dcc.Input(id='ook0_tol', value=0, type='text')]),
    html.Div(html.H5('')),
    html.Div(html.Button('Update Plots', id='update')),
    html.Div(dcc.Graph(id='image', figure={}, className='row')),
    html.Div(dcc.Graph(id='contour', figure={}, className='row')),
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
        data = ImzMLParser(path, include_spectra_metadata='full', include_mobility=True)
        mz_array = np.zeros(0)
        intensity_array = np.zeros(0)
        mobility_array = np.zeros(0)
        for i in range(0, len(data.coordinates)):
            mzs, ints, mobs = data.getspectrum(i)
            mz_array = np.append(mz_array, mzs)
            intensity_array = np.append(intensity_array, ints)
            mobility_array = np.append(mobility_array, mobs)
        data_df = pd.DataFrame(data={'mz': mz_array,
                                     'intensity': intensity_array,
                                     'mobility': mobility_array})

        contour = data_df.groupby(['mz', 'mobility'], as_index=False).aggregate(sum)
        contour = contour[contour['intensity'] >= (np.max(contour['intensity']) * 0.0002)]
        ion_image = getionimage(data, mz_value=float(mass), mz_tol=float(mass_tol),
                                mob_value=float(ook0), mob_tol=float(ook0_tol))

        contour_plot = px.density_contour(data_frame=contour, x='mz', y='mobility',
                                          marginal_x='histogram', marginal_y='histogram', histfunc='sum',
                                          nbinsx=20000, nbinsy=len(set(contour['mobility'])) // 2)
        ion_image_plot = px.imshow(ion_image, color_continuous_scale='viridis')

        return [contour_plot, ion_image_plot, {'stored_path': path}]


@app.callback(Output(component_id='mass', component_property='value'),
              Output(component_id='ook0', component_property='value'),
              Input('contour', 'clickData'),)
def update_inputs(coords):
    mass = coords['points'][0]['x']
    ook0 = coords['points'][0]['y']
    return [mass, ook0]


if __name__ == '__main__':
    app.run_server(debug=False, port=8050)
