# -*- coding: utf-8 -*-
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime
from dateutil.parser import parse

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

import pandas as pd
import requests
import numpy as np

url_1="https://datos.madrid.es/egob/catalogo/300228-21-accidentes-trafico-detalle.csv"
data_1 = pd.read_csv(url_1, sep=";", encoding="latin1")
#data_1.head()
#data_1.dtypes

url_2="https://datos.madrid.es/egob/catalogo/300228-19-accidentes-trafico-detalle.csv"
data_2 = pd.read_csv(url_2, sep=";", encoding="latin1")
data_2.drop(data_2.columns[len(data_2.columns)-1], axis=1, inplace=True)
#data_2.head()
#data_2.dtypes
data_2 = data_2.rename(columns={"RANGO EDAD":"RANGO DE EDAD"})
#Create only one data frame
data_1 = data_1.append(pd.DataFrame(data = data_2), ignore_index=True)
data1 = data_1
data1.dtypes
#import os
#c=pd.read_csv("2020_Accidentalidad.csv", sep=";", encoding="latin1" )
#c.head()
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Changes in dataset ------------------------------------------------------
# Changes in column names
data1 = data1.rename(columns={"NÚMERO":"NUMERO","ESTADO METEREOLÓGICO":"ESTADO.METEREOLOGICO",\
    "TIPO VEHÍCULO":"TIPO.VEHICULO","LESIVIDAD*":"LESIVIDAD","Nº  EXPEDIENTE":"NEXPEDIENTE",\
        "TIPO ACCIDENTE":"TIPO.ACCIDENTE","TIPO PERSONA":"TIPO.PERSONA","RANGO DE EDAD":"RANGO.EDAD"})
list(data1.columns)

#Create column of address
data1 = data1.astype({'NUMERO': 'str'})
data1['ADDRESS'] =data1.apply(lambda x: '.'.join([x['CALLE'],', ',x['NUMERO'],', ','MADRID, SPAIN']),axis=1)
#list(data1.columns)
#data1.head()
#data1.describe()
#print(data1)

#Replaces needed in address
data1['ADDRESS'] = data1['ADDRESS'].str.replace('\.','')
#data1.loc[1,'ADDRESS']
data1['ADDRESS'] = data1['ADDRESS'].str.replace(', -, ',', 0,')
data1['ADDRESS'] = data1['ADDRESS'].str.replace(' NA, ','')

#Replace all the NaN
data1 = data1.fillna('Unknown')
data1 = data1.replace('Se desconoce', 'Unknown')
data1 = data1.replace('DESCONOCIDO', 'Unknown')
#Eliminate all the names ("CALL.", "AV.", etc) that are not supported by geolocation & eliminate double direction.
data1['ADDRESS'] = data1['ADDRESS'].str.replace('.*\\/','')
data1['ADDRESS'] = data1['ADDRESS'].str.replace('.*\\. ','')
data1['ADDRESS'] = data1['ADDRESS'].str.replace('CALL ','')
data1['ADDRESS'] = data1['ADDRESS'].str.replace('AVDA ','')
data1['ADDRESS'] = data1['ADDRESS'].str.replace('GTA ','')
data1['ADDRESS'] = data1['ADDRESS'].str.replace('CTRA ','')
data1['ADDRESS'] = data1['ADDRESS'].str.replace('CALLE ','')

#data1.loc[105,]

#Change levels of injury based on dataset dictionary
data1['INJURY'] ="Mild"
#data1.loc[2,]
#data1.loc[data1.LESIVIDAD==3,'INJURY']
#data1.dtypes
data1.loc[data1.LESIVIDAD==3,'INJURY']= 'Fatal'
data1.loc[data1['LESIVIDAD']==14,'INJURY']= 'Without assistance'
data1.loc[data1.LESIVIDAD==70,'INJURY']= 'Unknown'

#Change type of variables
#data1 = data1.astype({'FECHA': 'float64', 'HORA': 'object'})
data1['FECHA'] = pd.to_datetime(data1['FECHA'],dayfirst=True)
data1['DAY'] = data1['FECHA'].dt.strftime('%A')

#data1['FECHA'] = data1['FECHA'].dt.strftime('%d/%m/%Y')
#data1.dtypes

#Create historical data

#Min data
min_date = data1['FECHA'].min().strftime('%d/%m/%Y')
#min_date
max_date = data1['FECHA'].max().strftime('%d/%m/%Y')
#max_date

#Create data outputs
#Date victims, accidents and fatal victims
data_date = data1.groupby('FECHA')['NEXPEDIENTE'].count()
#data_date.head()
data_date_victims = data1.groupby('FECHA').NEXPEDIENTE.nunique()
#data_date_victims.head()
data_date_fvictims = data1[data1['INJURY'] == 'Fatal'].groupby('FECHA')['NEXPEDIENTE'].count()
#data_date_fvictims.head()

#Data 2020
data = data1[(data1['FECHA'] > '2019-12-31')]
#data.head()
#data

#Types
types = data1['TIPO.ACCIDENTE'].sort_values().unique()
types_dict = [{'label': x, 'value': x} for x in types]

#Levels
levels = data1['INJURY'].sort_values().unique()
levels_dict = [{'label': x, 'value': x} for x in levels]

#Total accidents 2020
total_acc = data.NEXPEDIENTE.nunique()
total_acc_his = data1.NEXPEDIENTE.nunique()

#total_acc
#Total victims
total_vic = data.NEXPEDIENTE.count()
total_vic_his = data.NEXPEDIENTE.count()

#total_vic
#Total fatal victims
total_fvic = data[data['INJURY'] == 'Fatal'].NEXPEDIENTE.count()
#total_fvic

#Total
total_data_acc = data.groupby('TIPO.ACCIDENTE').NEXPEDIENTE.nunique()
total_data_vic = data.groupby('TIPO.ACCIDENTE')['NEXPEDIENTE'].count()
total_data = pd.merge(total_data_acc,total_data_vic, on='TIPO.ACCIDENTE')
total_data = total_data.rename(columns={'NEXPEDIENTE_x':'Accidents','NEXPEDIENTE_y':'Victims'})
#total_data

#Subset by type
fill_data_vic = data.groupby(['TIPO.ACCIDENTE','TIPO.PERSONA'])['NEXPEDIENTE'].count().reset_index()
fill_data_vic.columns = ['Type of accident','Type of victim', 'Total victims']

#Subset by injury level
fill_data_inj = data.groupby(['INJURY','RANGO.EDAD'])['NEXPEDIENTE'].count().reset_index()


# data1.groupby(['TIPO.VEHICULO']).groups.keys()
# data1.groupby('DAY')['NEXPEDIENTE'].count()
# data1.groupby('ESTADO.METEREOLOGICO')['NEXPEDIENTE'].count()
# data1.groupby('ESTADO.METEREOLOGICO').data1['DAY']=='Monday'.count()
# data1[data1['INJURY'] == 'Fatal'].groupby('DAY')['NEXPEDIENTE'].count()
# data1[data1['INJURY'] == 'Fatal'].groupby(['DAY','NEXPEDIENTE']).count()
# data1[data1['INJURY'] == 'Fatal'].groupby('DAY').NEXPEDIENTE.nunique()
# data1.groupby('INJURY')['NEXPEDIENTE'].count()

#Geolocalization function
locations = data[data['INJURY'] == 'Fatal'].ADDRESS
#locations

def geofunction(location):
    url = 'http://nominatim.openstreetmap.org/search/@addr@?format=json&addressdetails=0&limit=1'
    url1 = url.replace('@addr@',location)
    s=[]
    s=requests.get(url1).json()
    if not s:
        result=pd.DataFrame(np.nan, index=[0], columns=['lat', 'lon'])
    else:
        result=pd.DataFrame({'lat':s[0]['lat'], 'lon':s[0]['lon']}, index=[0])
    
    return result

results = pd.DataFrame(columns=['lat','lon'])
for i in range(len(locations)):
    location = locations.values[i].lstrip()
    location1 = location.replace(' ','%20')
    result = geofunction(location1)
    results= results.append(result, ignore_index=True)

#results
#Data frames of detail of fatal victims divided by in there was a geolocation identified or not. 
data_vic = data[data['INJURY'] == 'Fatal']
data_vic = pd.concat([data_vic.reset_index(drop=True), results], axis=1)
list(data_vic.columns)
loc = data_vic.dropna(subset=['lat', 'lon']).reset_index()

data_c = data_vic.dropna(subset=['lat', 'lon']).reset_index()
data_nc = data_vic[pd.isnull(data_vic).any(axis=1)].reset_index()
data_c = data_c[['CALLE','NUMERO','DISTRITO','RANGO.EDAD','TIPO.ACCIDENTE']]
data_nc = data_nc[['CALLE','NUMERO','DISTRITO','RANGO.EDAD','TIPO.ACCIDENTE']]
list(data_nc.columns)
data_nc.columns= ["Street", "Number", "District", "Age", "Type of accident"] # no complete
data_c.columns= ["Street", "Number", "District", "Age", "Type of accident"]# complete cases with geolocation

#Test plots
import plotly.express as px
import plotly.graph_objects as go

#Hover
import dash_table

#Simple plot for total
total_data_pl = total_data.unstack().reset_index()
total_data_pl.columns = ['Variable', 'TIPO.ACCIDENTE', 'Total']



#Tables
#Table map
def tablefunction(dataframe):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(len(dataframe))
        ])
    ])

markdown_text1 = '''
#### About
This is a reporting tool which aims to present some relevant information
about traffic accidents in Madrid. The dataset use is part of the open
data offer from the City town hall. The format in which the datasets are
presented is a compilation of the anual cases, updated every month. 
This app has been made to present the data from 2020 in a direct and 
updated way colleting the data from the website. Additionally, some 
information is presented as a historical look using the unified data
 available from january 2019.

'''
markdown_text2 = '''
The contents of the tabs are:

- Type: information about the total number of accidents per type, number of accidents per district, type of weather and injury level.
- Date: historical information about the number of victims, accidents and fatal victims since january 2019 and the classification per day of occurance.
- Location: location of the occurance of accidents that involve fatal victims in 2020.

For more information about this app you can check: [Open Data Madrid](https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=7c2843010d9c3610VgnVCM2000001f4a900aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default)

Presentation about app.

### Statistics

The data presented is availbale until:
'''
markdown_text3 = '''
Thest:
'''
external_stylesheets = [
{
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config['suppress_callback_exceptions'] = True
# Layout
app.layout = \
    html.Div([
        html.Div([html.H1('Madrid Trafic Accidents 2020',
                style={'textAlign': 'left',
                       'margin': '48px 0',
                       'fontFamily': 'system-ui'})
        ],className= 'product4'),
        dcc.Tabs(id="tabs",
                parent_style={'flex-direction': 'column',
                            '-webkit-flex-direction': 'column',
                            '-ms-flex-direction': 'column',
                            'display': 'flex'},
                children=[
                    dcc.Tab(className="fa fa-binoculars fa-lg",
                            label='      Description',
                            children = [
                                        html.Div([
                                            html.Br(),
                                        ], className="one column"),
                                        html.Div([
                                            html.Div([
                                            dcc.Markdown(markdown_text1)
                                        ], className="six columns"),
                                            html.Div([
                                            html.Br(),
                                            html.Img(id='image', 
                                                src=('https://www.stepsrelocation.com/wp-content/uploads/2019/03/madrid-central-1.jpg)'),
                                                width='40%',
                                                height='50%')
                                        ], className="six columns"),
                                            html.Div([
                                            dcc.Markdown(markdown_text2),
                                            html.H6(max_date),
                                            html.Div([html.H5("Total accidents"),
                                            html.H6(total_acc)], className= 'product'),
                                            html.Div([html.H5("Total victims"),
                                            html.H6(total_vic)], className= 'product2'),
                                            html.Div([html.H5("Total fatal victims"),
                                            html.H6(total_fvic)], className= 'product3')    
                                            ], className="eleven columns")
                                            ],className="eleven columns")
                                        ]),
                    dcc.Tab(className="fa fa-bus-alt fa-lg",
                            label='      Type',
                            children = [
                                        html.Div([
                                            html.Br(),
                                            html.H4("Select type of accident"),
                                            dcc.Checklist(
                                            id="type_selector",
                                            options=types_dict,
                                            value=types
                                        )
                                        ],className="three columns"),
                                        html.Div(children=[ 
                                            html.Br(),
                                            dcc.Tabs(id="tabs2", children=[
                                                dcc.Tab(label='Total', children=[
                                                    html.Div([html.H5("Total number of victims and accidents")], className= 'product4'),
                                                        dcc.Graph(id='fig1'),
                                                        dash_table.DataTable(id='hover-data',
                                                                            columns=[{"name": i, "id": i} for i in fill_data_vic.columns])
                                                ]),
                                                dcc.Tab(label='Accidents per district', children=[
                                                        html.Div([html.H5("Number of accidents per district")], className= 'product4'),
                                                        dcc.Graph(id='fig2'),
                                                        html.Div([html.H5("Number of victims per district")], className= 'product4'),
                                                        dcc.Graph(id='fig3')
                                                ]),
                                                dcc.Tab(label='Weather', children=[
                                                        html.Div([html.H5("Number of accidents based on the weather of the day")], className= 'product4'),
                                                        dcc.Graph(id='fig4'),
                                                        html.Div([html.H5("Number of victims based on the weather of the accident day")], className= 'product4'),
                                                        dcc.Graph(id='fig5')
                                                ]),
                                                dcc.Tab(label='Injury Level', children=[
                                                        html.Div([html.H5("Number of victims based on the level of injury register")], className= 'product4'),
                                                        dcc.Graph(id='fig6'),
                                                        dash_table.DataTable(id='hover-data2',
                                                            columns=[{"name": i, "id": i} for i in fill_data_inj.columns])
                                                ])
                                            ])
                                        ], className="nine columns")
                                    ]),
                    dcc.Tab(className="fa fa-calendar-alt fa-lg",
                            label='      Date',
                            children = [
                                        html.Div([
                                        html.Div([html.H5("Historical statistics since january 2019 until available information")], className= 'product4'),
                                        html.Div([html.H5("Total accidents"),
                                            html.H6(total_acc_his)], className= 'product5'),
                                        html.Div([html.H5("Total victims"),
                                            html.H6(total_vic_his)], className= 'product5'),
                                        dcc.DatePickerRange(
                                            id='my-date-picker-range',
                                            min_date_allowed=data1['FECHA'].min(),
                                            max_date_allowed=data1['FECHA'].max(),
                                            initial_visible_month=data1['FECHA'].min(),
                                            start_date=data1['FECHA'].min(),
                                            end_date=data1['FECHA'].max()
                                        ),
                                        dbc.Button('Update filter', 
                                                            color="primary", 
                                                            className="mr-1",
                                                            id='my-button'),
                                        html.Div(id='output-container-date-picker-range', style={'display': 'none'}),
                                        dcc.Graph(id='fig8'),
                                        html.Div([html.H5("Percentage of historical accidents based on the day that occured and the injury level")], className= 'product4'),
                                        dcc.Checklist(
                                            id="level_selector",
                                            options=levels_dict,
                                            value=levels
                                        ),
                                        dcc.Graph(id='fig7')
                                        ])
                                    ]),
                    dcc.Tab(className="fa fa-map-marked-alt fa-lg",
                            label='      Location',
                            children = [
                                        html.Div([
                                            html.Div([html.H5("Location of accidents which involved fatal victims")], className= 'product4'),
                                            dcc.Graph(
                                                id='graph9',
                                                figure={
                                                    'data': [{
                                                        'lat': loc.lat, 'lon': loc.lon, 'type': 'scattermapbox',
                                                        'mode':'markers',
                                                        'marker': go.scattermapbox.Marker(
                                                            size=17,
                                                            color='rgb(255, 0, 0)',
                                                            opacity=0.7
                                                        )
                                                    }],
                                                    'layout': {
                                                        'mapbox': {
                                                            'accesstoken': (
                                                                'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3M' +
                                                                'DBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'
                                                            ),
                                                            'center' : go.layout.mapbox.Center(
                                                                                    lat=40.46,
                                                                                    lon=-3.66
                                                                                ),
                                                            'style': "outdoors", 'zoom': 12
                                                        },
                                                        'showlegend' : False,
                                                        'margin': {
                                                            'l': 0, 'r': 0, 'b': 0, 't': 0
                                                        },
                                                    }
                                                }
                                            ),
                                            dbc.Button('Cases that could not be geolocated', 
                                                            color="primary", 
                                                            className="mr-1",
                                                            id='my-button2'),
                                            html.Div(id='table1'),
                                            dbc.Button('Cases geolocated', 
                                                            color="primary", 
                                                            className="mr-1",
                                                            id='my-button3'),
                                            html.Div(id='table2')               
                                        ])
                                    ])
                    ])
])

def filter_dataframe(df, type_selector):
    dff = df[df['TIPO.ACCIDENTE'].isin(type_selector)]
    return dff

@app.callback(
    [Output('fig1', 'figure'),
    Output('fig2', 'figure'),
    Output('fig3', 'figure'),
    Output('fig4', 'figure'),
    Output('fig5', 'figure'),
    Output('fig6', 'figure')],
    [Input('type_selector', 'value')])
def update_figure(type_selector):
    #Total
    fil_df = filter_dataframe(total_data_pl,type_selector)
    figure1 =px.bar(fil_df, x="TIPO.ACCIDENTE", y="Total", color='Variable', barmode='group', labels = {'x' : 'Type of accident'})
    
    #District
    fil_df2 = filter_dataframe(data,type_selector)
        #Plot per ditrict accidents
    district_acc = fil_df2.groupby(['DISTRITO']).NEXPEDIENTE.nunique().reset_index()
    figure2 = go.Figure(data=[go.Bar(x=district_acc['DISTRITO'], y=district_acc['NEXPEDIENTE'])])
        #Plot per district victims by type
    district_vic = fil_df2.groupby(['DISTRITO','TIPO.PERSONA'])['NEXPEDIENTE'].count().reset_index()
    figure3=px.bar(district_vic, x='DISTRITO', y='NEXPEDIENTE', color='TIPO.PERSONA')
    figure3.update_layout(
        xaxis_title="District",
        yaxis_title="Victims",
    )
    #Weather
    #Pie chart weather victims
    weather_vic = fil_df2.groupby('ESTADO.METEREOLOGICO')['NEXPEDIENTE'].count().reset_index()
    figure4 = px.pie(weather_vic, values='NEXPEDIENTE', names='ESTADO.METEREOLOGICO')
    #Pie chart weather accidents
    weather_acc = fil_df2.groupby(['ESTADO.METEREOLOGICO']).NEXPEDIENTE.nunique().reset_index()
    figure5 = px.pie(weather_acc, values='NEXPEDIENTE', names='ESTADO.METEREOLOGICO')

    #Injury
    injury_vic = fil_df2.groupby(['INJURY'])['NEXPEDIENTE'].count().reset_index()
    #Injury level
    figure6 = go.Figure(data=[go.Bar(
                x=injury_vic['INJURY'],
                y=injury_vic['NEXPEDIENTE'],
                text=injury_vic['NEXPEDIENTE'],
                textposition='auto'
            )])
    return figure1, figure2, figure3, figure4, figure5, figure6  


@app.callback(
    Output('hover-data', 'data'),
    [Input('fig1', 'hoverData')])
def display_hover_data(hoverData):
    if hoverData is None or len(hoverData) == 0:
        return []
    type_name = hoverData['points'][0]['x']
    if len(type_name) == 0:
        return []
    fil_df_type = fill_data_vic[fill_data_vic['Type of accident']==type_name]
    return fil_df_type.to_dict("rows")
    #json.dumps(hoverData, indent=2)

@app.callback(
    Output('hover-data2', 'data'),
    [Input('fig6', 'hoverData')])
def display_hover_datat(hoverData):
    if hoverData is None or len(hoverData) == 0:
        return []
    inj_name = hoverData['points'][0]['x']
    if len(inj_name) == 0:
        return []
    fil_df_inj = fill_data_inj[fill_data_inj['INJURY']==inj_name]
    return fil_df_inj.to_dict("rows")

#Date figures
def filter_dataframe2(df, level_selector):
    dff2 = df[df['INJURY'].isin(level_selector)]
    return dff2

@app.callback(
    Output('fig7', 'figure'),
    [Input('level_selector', 'value')])
def update_figure2(level_selector):
    fil_df3 = filter_dataframe2(data1, level_selector)
    days = fil_df3.groupby('DAY').NEXPEDIENTE.nunique().reset_index()
    #Pie chart days accidents
    figure7 = px.pie(days, values='NEXPEDIENTE', names='DAY')
    return figure7

@app.callback(
    Output('output-container-date-picker-range', 'children'),
    [Input('my-button', 'n_clicks')],
    [State('my-date-picker-range', 'start_date'),
     State('my-date-picker-range', 'end_date')])
def update_output(n_clicks,start_date, end_date):
    datast = data1[(data1['FECHA'] >= parse(start_date)) & (data1['FECHA'] <= parse(end_date))].to_json(orient='split', date_format='iso')
    return json.dumps(datast)

@app.callback(
    Output('fig8', 'figure'),
    [Input('output-container-date-picker-range', 'children')]
)
def update_output_graph(data):
    if data is None:
        historical_acc =  data1.groupby('FECHA').NEXPEDIENTE.nunique()
        historical_vic =  data1.groupby('FECHA').NEXPEDIENTE.count()
        historical_fvic = data1[data1['INJURY'] == 'Fatal'].groupby('FECHA').NEXPEDIENTE.count()
        historical_data = pd.merge(historical_acc,historical_vic,how='outer', on='FECHA')
        historical_data = pd.merge(historical_data,historical_fvic, how='outer',on='FECHA').reset_index()
        historical_data.columns = ['Date','Accidents', 'Victims', 'Fatal victims']
        historical_data = historical_data.fillna('0')

        figure81 = go.Figure(data=[go.Bar(
        x=historical_data['Date'],
        y=historical_data['Accidents'],
        name="Accidents",
        marker_color='deepskyblue'),
        go.Bar(x=historical_data.Date,
            y=historical_data['Victims'],
            name="Victims",
            marker_color='dimgray'),
        go.Bar(x=historical_data.Date,
            y=historical_data['Fatal victims'],
            name="Fatal Victims",
            marker_color='green')])

        figure81.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="Last m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6 m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="Year",
                            step="year",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            )
        )
        return figure81
    
    dataset = json.loads(data)
    df = pd.read_json(dataset, orient='split')
    #Historical data
    historical_acc =  df.groupby('FECHA').NEXPEDIENTE.nunique()
    historical_vic =  df.groupby('FECHA').NEXPEDIENTE.count()
    historical_fvic = df[df['INJURY'] == 'Fatal'].groupby('FECHA').NEXPEDIENTE.count()
    historical_data = pd.merge(historical_acc,historical_vic,how='outer', on='FECHA')
    historical_data = pd.merge(historical_data,historical_fvic, how='outer',on='FECHA').reset_index()
    historical_data.columns = ['Date','Accidents', 'Victims', 'Fatal victims']
    historical_data = historical_data.fillna('0')
    #Bar chart historical

    figure8 = go.Figure(data=[go.Bar(
        x=historical_data['Date'],
        y=historical_data['Accidents'],
        name="Accidents",
        marker_color='deepskyblue'),
    go.Bar(x=historical_data.Date,
        y=historical_data['Victims'],
        name="Victims",
        marker_color='dimgray'),
    go.Bar(x=historical_data.Date,
        y=historical_data['Fatal victims'],
        name="Fatal Victims",
        marker_color='green')])

    figure8.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="Last m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6 m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="Year",
                        step="year",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    return figure8

@app.callback(
    Output('table1', 'children'),
    [Input('my-button2', 'n_clicks')]
)
def on_button_click(n):
    if n is None:
        return []
    else:
        return tablefunction(data_nc)

@app.callback(
    Output('table2', 'children'),
    [Input('my-button3', 'n_clicks')]
)
def on_button_click2(n):
    if n is None:
        return []
    else:
        return tablefunction(data_c)

if __name__ == '__main__':
    app.run_server(debug=True)
    
