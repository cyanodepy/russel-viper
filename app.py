import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import dash_leaflet as dl

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Load data from the correct sheet in the Excel file
data_path = '/russelviper.xlsx'
data = pd.read_excel(data_path, sheet_name=1)

# Correct column names based on the printed output
death_sighting_col = 'Death/Sighting'
lat_col = 'Lat'
long_col = 'Long'
district_col = 'District'
date_col = 'Date'
upazila_col = 'Upazila'


# Create markers for deaths and sightings
def generate_markers(data, lat_col, long_col, death_sighting_col):
    markers = []
    for _, row in data.iterrows():
        if row[death_sighting_col].lower() == 'death':
            marker = dl.Marker(position=[row[lat_col], row[long_col]], children=dl.Tooltip('Death'),
                               icon=dict(iconUrl='/assets/red_marker.png', iconSize=[12, 12], iconAnchor=[6, 6]))
        else:
            marker = dl.Marker(position=[row[lat_col], row[long_col]], children=dl.Tooltip('Sighting'),
                               icon=dict(iconUrl='/assets/yellow_marker.png', iconSize=[12, 12], iconAnchor=[6, 6]))
        markers.append(marker)
    return markers


# Generate markers
markers = generate_markers(data, lat_col, long_col, death_sighting_col)


# Create a bar chart of deaths and sightings per district
def create_bar_chart(data, district_col, death_sighting_col):
    df_counts = data.groupby([district_col, death_sighting_col]).size().reset_index(name='count')
    fig = px.bar(df_counts, x=district_col, y='count', color=death_sighting_col, barmode='group',
                 labels={district_col: 'District', 'count': 'Count', death_sighting_col: 'Type'})
    return fig


# Create a line chart of deaths and sightings per year
def create_yearly_line_chart(data, date_col, death_sighting_col):
    data['Year'] = pd.to_datetime(data[date_col]).dt.year
    df_counts = data.groupby(['Year', death_sighting_col]).size().reset_index(name='count')
    fig = px.line(df_counts, x='Year', y='count', color=death_sighting_col,
                  labels={'Year': 'Year', 'count': 'Count', death_sighting_col: 'Type'})
    return fig


# Create a line chart of deaths and sightings per month
def create_monthly_line_chart(data, date_col, death_sighting_col):
    data['Month'] = pd.to_datetime(data[date_col]).dt.to_period('M')
    df_counts = data.groupby(['Month', death_sighting_col]).size().reset_index(name='count')
    df_counts['Month'] = df_counts['Month'].astype(str)
    fig = px.line(df_counts, x='Month', y='count', color=death_sighting_col,
                  labels={'Month': 'Month', 'count': 'Count', death_sighting_col: 'Type'})
    return fig


# Create a pie chart of district-wise deaths
def create_pie_chart(data, district_col, death_sighting_col):
    df_deaths = data[data[death_sighting_col].str.lower() == 'death']
    df_counts = df_deaths[district_col].value_counts().reset_index(name='count')
    df_counts.columns = [district_col, 'count']
    fig = px.pie(df_counts, values='count', names=district_col, title='District-wise Deaths')
    return fig


# Generate the initial charts
bar_chart = create_bar_chart(data, district_col, death_sighting_col)
yearly_line_chart = create_yearly_line_chart(data, date_col, death_sighting_col)
monthly_line_chart = create_monthly_line_chart(data, date_col, death_sighting_col)
pie_chart = create_pie_chart(data, district_col, death_sighting_col)

# Create the layout of the app
app.layout = html.Div(
    style={'height': '100vh', 'width': '100vw'},  # Set full height and width for the container
    children=[
        # Title bar with dropdown filters
        html.Div(
            style={'height': '10%', 'width': '100%', 'backgroundColor': '#58b9a2', 'display': 'flex',
                   'alignItems': 'center'},
            children=[
                html.H1('Russells Viper Sighting and Death Data', style={'textAlign': 'center', 'margin': 'auto'}),
                dcc.Dropdown(
                    id='district-dropdown',
                    options=[{'label': district, 'value': district} for district in data[district_col].unique()],
                    placeholder='Select District',
                    style={'width': '40%', 'marginLeft': '10%'}
                ),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': year, 'value': year} for year in data['Year'].unique()],
                    placeholder='Select Year',
                    style={'width': '40%', 'marginLeft': '10%'}
                )
            ]
        ),
        # Gap
        html.Div(
            style={'height': '0.5%'}
        ),
        # Main content row
        html.Div(
            style={'height': '89.5%', 'width': '100%', 'backgroundColor': '#c4e6de', 'display': 'flex'},
            children=[
                # Map section
                html.Div(
                    style={'width': '40%', 'height': '100%'},
                    children=[
                        dl.Map(center=[23.6850, 90.3563], zoom=7, style={'height': '100%', 'width': '100%'},
                               children=[
                                   dl.TileLayer(),
                                   dl.LayerGroup(id='marker-layer', children=markers)
                               ])
                    ]
                ),
                # Other components section
                html.Div(
                    style={'width': '60%', 'height': '100%', 'backgroundColor': '#c4e6de', 'display': 'flex',
                           'flexWrap': 'wrap'},
                    children=[
                        # Top left
                        html.Div(
                            style={'width': '50%', 'height': '50%', 'backgroundColor': 'lightgray'},
                            children=[
                                dcc.Graph(id='bar-chart', figure=bar_chart)
                            ]
                        ),
                        # Top right
                        html.Div(
                            style={'width': '50%', 'height': '50%', 'backgroundColor': '#c4e6de'},
                            children=[
                                dcc.Graph(id='yearly-line-chart', figure=yearly_line_chart)
                            ]
                        ),
                        # Bottom left
                        html.Div(
                            style={'width': '50%', 'height': '50%', 'backgroundColor': 'lightgray'},
                            children=[
                                dcc.Graph(id='monthly-line-chart', figure=monthly_line_chart)
                            ]
                        ),
                        # Bottom right
                        html.Div(
                            style={'width': '50%', 'height': '50%', 'backgroundColor': 'lightgray'},
                            children=[
                                dcc.Graph(id='pie-chart', figure=pie_chart)
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


# Callback to update charts and markers based on dropdown filters
@app.callback(
    [Output('marker-layer', 'children'),
     Output('bar-chart', 'figure'),
     Output('yearly-line-chart', 'figure'),
     Output('monthly-line-chart', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('district-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_charts(selected_district, selected_year):
    filtered_data = data.copy()

    if selected_district:
        filtered_data = filtered_data[filtered_data[district_col] == selected_district]
    if selected_year:
        filtered_data = filtered_data[filtered_data['Year'] == selected_year]

    # Update markers
    markers = generate_markers(filtered_data, lat_col, long_col, death_sighting_col)

    # Update charts
    bar_chart = create_bar_chart(filtered_data, district_col, death_sighting_col)
    yearly_line_chart = create_yearly_line_chart(filtered_data, date_col, death_sighting_col)
    monthly_line_chart = create_monthly_line_chart(filtered_data, date_col, death_sighting_col)
    pie_chart = create_pie_chart(filtered_data, district_col, death_sighting_col)

    return markers, bar_chart, yearly_line_chart, monthly_line_chart, pie_chart


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
