# Data608 Module 4
# Gabriel Santos 
# Date: 03-15-2023

import pandas as pd
import numpy as np
import string as s
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

#In this module we’ll be looking at data from the New York City tree census:
#https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh
#This data is collected by volunteers across the city, and is meant to catalog information about every single tree in the city.

#Build a dash app for a arborist studying the health of various tree species (as defined by the variable ‘spc_common’) across each borough (defined by the variable ‘borough’). This arborist would like to answer the following two questions for each species and in each borough:

#1. What proportion of trees are in good, fair, or poor health according to the ‘health’ variable ?
#2. Are stewards (steward activity measured by the ‘steward’ variable) having an impact on the health of trees?

#Please see the accompanying notebook for an introduction and some notes on the Socrata API.

url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json'
trees = pd.read_json(url)
trees.head(10)


#Looks good, but lets take a look at the shape of this data:

trees.shape


#If we wanted the next 5, we would use this url:
    
nextfive_url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=5&$offset=5'
nextfive_trees = pd.read_json(nextfive_url)
nextfive_trees

url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=5&$offset=' + str(0) + '&$select=count(tree_id)').replace(' ', '%20')
trees = pd.read_json(url)
count = pd.read_json(url)
print(count)

#Think about the shape you want your data to be in before querying it. Using `SoQL` is a good way to avoid the limits of the API. For example, using the below query I can easily obtain the count of each species of tree in the Bronx:

   
boro = 'Bronx'
soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,count(tree_id)' +\
        '&$where=boroname=\'Bronx\'' +\
        '&$group=spc_common').replace(' ', '%20')
soql_trees = pd.read_json(soql_url)

soql_trees


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

tree_query = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=boroname,health,steward,spc_common,count(tree_id)' +\
        '&$group=boroname,spc_common,steward,health').replace(' ', '%20')

trees = pd.read_json(tree_query)


tree_totals = trees.groupby(['boroname','spc_common','steward'])['count_tree_id'].sum()
tree_totals = tree_totals.reset_index(drop=False)
tree_totals.columns = ['boroname', 'common_name', 'steward','total_in_boro']

tree_total_health = trees.groupby(['boroname', 'spc_common', 'health','steward'])['count_tree_id'].sum()
tree_total_health = tree_total_health.reset_index(drop=False)
tree_total_health.columns = ['boroname', 'common_name', 'health','steward','total_by_health']

tree_df = pd.merge(tree_total_health, tree_totals, on=['boroname', 'common_name', 'steward'])

tree_df['ratio']=tree_df['total_by_health']/tree_df['total_in_boro']

df=tree_df


boro_ind = df['boroname'].unique()
tree_ind = df['common_name'].unique()
health_ind = df['health'].unique()
steward_ind = df['steward'].unique()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.Div([

        html.Label(["Choose Boro:  ", html.Div([
            dcc.Dropdown(
                id='boro_dropdown',
                options=[{'label': i, 'value': i} for i in boro_ind],
                value='boroname'
            )
        ],
        style={'width': '25%', 'display': 'inline-block'})]),

        html.Label(["Choose steward number:  ", html.Div([
            dcc.Dropdown(
                id='steward_dropdown',
                options=[{'label': i, 'value': i} for i in steward_ind],
                value='steward'
            )
        ],style={'width': '25%', 'display': 'inline-block'})
    ])]),
	
    dcc.Graph(id='graph-by-boro'),
    
    html.Div([
        dcc.Markdown("""
            Answer 1: In the graph we can see the proportion of the trees are in good, fair,
                   or poor health according to the ‘health’ variable. We can see that in both Borough the proportion of trees.
                   good health is the highest.
                  
            Answer 2: In the graph we can see the impact of stewards on the health of the trees. According to the graph
                   I consider that the stewards do not have an impact on the health of the trees. We can see that in cases that do not.
                   There are stewards, the proportion of trees with good health is high.

            The graph shows the relationship of the health of the trees with the total number of trees by the selected Boro (ratio), and
            steward amount filters the graph to a number of stewards per tree species.
              
            The color and sizes of the dots relate to the ratio of total number of trees types in each health category divided 
            by the total number of the same tree type in the boro.
                
              """)    
           ])
    
])

                     
                     
@app.callback(
    Output('graph-by-boro', 'figure'),
    [Input('boro_dropdown', 'value'),
     Input('steward_dropdown', 'value')])
def update_graph(selected_boro, selected_steward):
    filtered_df = df[df.boroname == selected_boro]
    filtered_df = filtered_df[filtered_df.steward == selected_steward]

    fig = px.scatter(filtered_df, x='total_in_boro', y='health', 
                     size='ratio', color = 'ratio', hover_name='common_name', 
                     log_x=True, size_max=50)

    fig.update_layout(margin={'l': 45, 'b': 45, 't': 10, 'r': 0}, hovermode='closest')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)

                     
                     

