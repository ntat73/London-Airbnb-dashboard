import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

#Loading and prepare data
weekdays_df = pd.read_csv('https://zenodo.org/records/4446043/files/london_weekdays.csv')
weekdays_df['Day Type'] = 'Weekday'
weekends_df = pd.read_csv('https://zenodo.org/records/4446043/files/london_weekends.csv')
weekends_df ['Day Type']= 'Weekend'

df = pd.concat([weekdays_df, weekends_df], ignore_index= True)
df.rename(columns={'realSum': 'Price',
                  'guest_satisfaction_overall': 'Satisfaction',
                  'cleanliness_rating': 'Cleanliness',
                  'room_type': 'Room Type',
                  'host_is_superhost': 'Superhost status',
                  'dist': 'City Distance'}, inplace = True)

#Initializing dash app:
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
#App layout
app.layout = dbc.Container([
    
    #Title:
    html.Div([
        html.H1('Airbnb London - Distance and Pricing Insights Dashboard ',
                className = 'text-center mb4',
                style ={'color': 'white', 'background-color':'#20283E', 'padding':'10px','border-radius': '5px'})]),    
    
    #Overview:
    dbc.Row ([
        dbc.Col(dbc.Card([
            dbc.CardBody([
            html.H5('Total Listings', className="text-center", style={'font-weight': 'bold'}),
            html.H2(id='total_listings', className="text-center", style={'color': '#AC3E31', 'font-weight': 'bold'})
            ])
        ], className ='shadow - sm'), width = 3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Average Price", className="text-center", style={'font-weight': 'bold'}),
                html.H2(id="average_price", className="text-center", style={'color': '#AC3E31', 'font-weight': 'bold'})
            ])
        ], className="shadow-sm"), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Average Satisfaction", className="text-center", style={'font-weight': 'bold'}),
                html.H2(id="avg_satisfaction", className="text-center", style={'color': '#AC3E31', 'font-weight': 'bold'})
            ])
        ], className="shadow-sm"), width=3),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Avg Distance to City Center", className="text-center", style={'font-weight': 'bold'}),
                html.H2(id="avg_distance", className="text-center", style={'color': '#AC3E31', 'font-weight': 'bold'})
            ])
        ], className="shadow-sm"), width=3)
    ], className="mb-4", style={'background-color': '#DADADA', 'padding': '20px', 'border-radius': '5px'}),
    
    #Filter:
    dbc.Row([
        dbc.Col(html.Div([
            html.H5('Room Type', style = {'font-weight': 'bold', 'color' : 'white'}),
            dcc.Dropdown(id='room_type_filter', options=[{'label': room, 'value': room} for room in df['Room Type'].unique()], placeholder="Select Room Type")
            ]), width=3),
        
        dbc.Col(html.Div([
            html.H5("Price Range", style={'font-weight': 'bold', 'color' : 'white'}),
            dcc.RangeSlider(id='price_filter',
                            min=0, max=2500, 
                            step=50,
                            marks={0: '0', 500: '500', 1000: '1000', 1500: '1500', 2000: '2000', 2500: 'High'},
                            value=[0, 2500])
        ]), width=3),
        
        dbc.Col(html.Div([
            html.H5("Distance Range", style={'font-weight': 'bold', 'color' : 'white'}),
            dcc.RangeSlider(id='distance_filter',
                            min=0, max=20,
                            step=1,
                            marks={0: 'Near', 5: '5 km', 10: '10 km', 15: '15 km', 20: '20'},
                            value=[0, 20])
            ]), width=3),

        dbc.Col(html.Div([
            html.H5("Satisfaction Tiers", style={'font-weight': 'bold', 'color' : 'white'}),
            dcc.RangeSlider(id='satisfaction_filter',
                            min=0, max=100, step=1,
                            marks={0: 'Low',75: 'Medium', 100: 'High'},
                            value=[0, 100])
            ]), width=3),

        dbc.Col(html.Div([
            html.H5("Day Type", style={'font-weight': 'bold', 'color' : 'white'}),
            dcc.Dropdown(id='day_type_filter',
                         options=[{'label': 'Weekday', 'value': 'Weekday'},
                                  {'label': 'Weekend', 'value': 'Weekend'}],
                         placeholder="Select Day Type")
        ]), width=3),
    ], className="mb-4", style={'background-color': '#20283E', 'padding': '20px', 'border-radius': '5px'}),

# Graphs Section
    dbc.Row([
        dbc.Col(dcc.Graph(id='room_type_pie_chart'), width=6),
        dbc.Col(dcc.Graph(id='revenue_bar_chart'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='price_heat_map'), width=8),
        dbc.Col(dcc.Graph(id='price_vs_city_distance'), width=4)
    ]),
    dbc.Row([dbc.Col(dcc.Graph(id='distance_vs_satisfaction'), width=12)])
], fluid=True)
#App call back:
@app.callback(
    [
        Output('total_listings', 'children'),
        Output('average_price', 'children'),
        Output('avg_satisfaction', 'children'),
        Output('avg_distance', 'children'),
        Output('room_type_pie_chart', 'figure'),
        Output('revenue_bar_chart', 'figure'),
        Output('price_heat_map', 'figure'),
        Output('price_vs_city_distance', 'figure'),
        Output('distance_vs_satisfaction', 'figure')
    ],
    [
        Input('room_type_filter', 'value'),
        Input('price_filter', 'value'),
        Input('distance_filter', 'value'),
        Input('satisfaction_filter', 'value'),
        Input('day_type_filter', 'value')
    ]
)
def update_dashboard(room_type, price_range, distance_range, satisfaction_range, day_type):
    # Filter data based on input:
    filtered_df = df.copy()

    if room_type:
        filtered_df = filtered_df[filtered_df['Room Type'] == room_type]

    filtered_df = filtered_df[
        (filtered_df['Price'] >= price_range[0]) &
        (filtered_df['Price'] <= price_range[1])
    ]
    filtered_df = filtered_df[
        (filtered_df['City Distance'] >= distance_range[0]) &
        (filtered_df['City Distance'] <= distance_range[1])
    ]
    filtered_df = filtered_df[
        (filtered_df['Satisfaction'] >= satisfaction_range[0]) &
        (filtered_df['Satisfaction'] <= satisfaction_range[1])
    ]
    if day_type:
        filtered_df = filtered_df[filtered_df['Day Type'] == day_type]

    # Overview Metrics
    total_listings = len(filtered_df)
    average_price = f"{filtered_df['Price'].mean():.2f} EUR"
    avg_satisfaction = f"{filtered_df['Satisfaction'].mean():.2f}"
    avg_distance = f"{filtered_df['City Distance'].mean():.2f} km"

    # Graphs
    room_type_pie = px.pie(filtered_df, names='Room Type', title="Room Type Distribution")
    
    revenue_bar = px.bar(filtered_df.groupby('Room Type')['Price'].sum().reset_index(),
                         x='Room Type', y='Price', title="Revenue by Room Type")
    revenue_bar.update_layout(yaxis_title="Total Revenue (EUR)")
    
    heat_map = px.density_mapbox(filtered_df, lat='lat', lon='lng', z='Price', radius=10,
                                 center=dict(lat=df['lat'].mean(), lon=df['lng'].mean()),
                                 mapbox_style="carto-positron", title="Geographic Price Distribution")
    
    price_vs_distance = px.line(filtered_df.groupby('City Distance')['Price'].mean().reset_index(),
                                x='City Distance', y='Price', title="Average Price vs City Distance")
    
    distance_vs_satisfaction = px.scatter(filtered_df, x='City Distance', y='Satisfaction',
                                          trendline='ols', title="Distance vs Guest Satisfaction",
                                          labels={'City Distance': 'Distance (km)', 'Satisfaction': 'Satisfaction'},
                                          color_discrete_sequence=['#488A99'])
    distance_vs_satisfaction.update_traces(
        line=dict(color='#AC3E31'),  # Change trendline color to red
        selector=dict(mode='lines'))

    return total_listings, average_price, avg_satisfaction, avg_distance, room_type_pie, revenue_bar, heat_map, price_vs_distance, distance_vs_satisfaction
# Run the App
if __name__ == "__main__":
    app.run_server(debug=True, port = 8051)