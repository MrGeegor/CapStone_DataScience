# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                        options=[
                                            {'label': 'All Sites', 'value': 'ALL'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                        ],
                                        value='ALL',
                                        placeholder='Select a Launch Site',
                                        searchable=True
                                        ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                html.Div(dcc.RangeSlider(min=0, 
                                    max=10000, 
                                    step=1000, 
                                    value=[min_payload, max_payload],
                                    id='payload-slider')),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        success_counts = filtered_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(success_counts, values='class', 
            names='Launch Site', 
            title='Total Successful Launches Across Sites')
        return fig
    else:
        site_df=filtered_df[filtered_df['Launch Site'] == entered_site]
        success_fail_df= site_df['class'].value_counts().reset_index()
        success_fail_df.columns = ["Outcome", "Count"]
        success_fail_df['Outcome'] = success_fail_df['Outcome'].replace({1: "Success", 0:"Failure"})
        fig = px.pie(success_fail_df, 
            values = 'Count', 
            names = 'Outcome', 
            title=f'Success vs Failure at {entered_site}') 
        return fig 
        
        # return the outcomes piechart for a selected site


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'), 
                Input(component_id='site-dropdown', component_property='value'),
                Input(component_id='payload-slider', component_property='value'))
def produce_scatter(entered_site, entered_payload): 
    low, high = entered_payload 
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site != 'ALL': 
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    fig = px.scatter(filtered_df, 
        x='Payload Mass (kg)', 
        y= 'class', 
        color="Booster Version Category", 
        symbol = 'Launch Site',
        title='Correlation between Payload and Launch Success')


    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
