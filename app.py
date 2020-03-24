# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

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

#Total accidents 2020
total_acc = data.NEXPEDIENTE.nunique()
#total_acc
#Total victims
total_vic = data.NEXPEDIENTE.count()
#total_vic
#Total fatal victims
total_fvic = data[data['INJURY'] == 'Fatal'].NEXPEDIENTE.count()
#total_fvic

#Weather
weather_vic = data.groupby('ESTADO.METEREOLOGICO')['NEXPEDIENTE'].count().reset_index()
weather_acc = data.groupby(['ESTADO.METEREOLOGICO']).NEXPEDIENTE.nunique().reset_index()

#Injury
injury_vic = data.groupby(['INJURY'])['NEXPEDIENTE'].count().reset_index()
injury_acc = data.groupby(['TIPO.ACCIDENTE','INJURY']).NEXPEDIENTE.nunique()

#District
district_acc = data.groupby(['DISTRITO']).NEXPEDIENTE.nunique().reset_index()
district_type = data.groupby(['DISTRITO','TIPO.PERSONA'])['NEXPEDIENTE'].count().reset_index()

#Total
total_data_acc = data.groupby('TIPO.ACCIDENTE').NEXPEDIENTE.nunique()
total_data_vic = data.groupby('TIPO.ACCIDENTE')['NEXPEDIENTE'].count()
total_data = pd.merge(total_data_acc,total_data_vic, on='TIPO.ACCIDENTE')
total_data = total_data.rename(columns={'NEXPEDIENTE_x':'Accidents','NEXPEDIENTE_y':'Victims'})
#total_data

#Historical data
days = data1.groupby('DAY').NEXPEDIENTE.nunique().reset_index()
historical_acc =  data1.groupby('FECHA').NEXPEDIENTE.nunique()
historical_vic =  data1.groupby('FECHA').NEXPEDIENTE.count()
historical_fvic = data1[data1['INJURY'] == 'Fatal'].groupby('FECHA').NEXPEDIENTE.count()
historical_data = pd.merge(historical_acc,historical_vic,how='outer', on='FECHA')
historical_data = pd.merge(historical_data,historical_fvic, how='outer',on='FECHA').reset_index()
historical_data.columns = ['Date','Accidents', 'Victims', 'Fatal victims']
historical_data = historical_data.fillna('0')

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

#Simple plot for total
#import seaborn as sns
total_data_pl = total_data.unstack().reset_index()
total_data_pl.columns = ['Variable', 'Type of accident', 'Total']
#fig1 = sns.barplot(y="Type of accident", hue="Variable", x="Total", data=total_data_pl)
#plt.show()

fig1=px.bar(total_data_pl, x="Type of accident", y="Total", color='Variable', barmode='group')

#Plot per district
fig2=px.bar(district_type, x='DISTRITO', y='NEXPEDIENTE', color='TIPO.PERSONA')
fig2.update_layout(
    xaxis_title="District",
    yaxis_title="Victims",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="#7f7f7f"
    )
)
#Pie chart weather victims
fig3 = px.pie(weather_vic, values='NEXPEDIENTE', names='ESTADO.METEREOLOGICO')

#Pie chart weather accidents
fig4 = px.pie(weather_acc, values='NEXPEDIENTE', names='ESTADO.METEREOLOGICO')

#Injury level
fig5 = go.Figure(data=[go.Bar(
            x=injury_vic['INJURY'],
            y=injury_vic['NEXPEDIENTE'],
            text=injury_vic['NEXPEDIENTE'],
            textposition='auto'
        )])

#Pie chart days accidents
fig6 = px.pie(days, values='NEXPEDIENTE', names='DAY')

#Bar chart historical
fig7 = go.Figure()
fig7.add_trace(go.Bar(x=historical_data.Date, y=historical_data['Accidents'], name="Accidents",
                         marker_color='deepskyblue'))
fig7.add_trace(go.Bar(x=historical_data.Date, y=historical_data['Victims'], name="Victims",
                         marker_color='dimgray'))
fig7.add_trace(go.Bar(x=historical_data.Date, y=historical_data['Fatal victims'], name="Fatal Victims",
                         marker_color='green'))
fig7.update_layout(
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

#Accidents per district
#import plotly.express as px
#fig = px.bar(district_acc, x='DISTRITO', y='NEXPEDIENTE')
#fig.show()



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Checklist(
        id="type_selector",
        options=types_dict,
        value=types
    ),  
    dcc.Graph(figure=fig1),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                go.Bar(x=district_acc['DISTRITO'], y=district_acc['NEXPEDIENTE'])
            ],
            'layout': {
                'title': 'Dash Data Visualization',
            }
        }
    ),
    dcc.Graph(figure=fig2),
    dcc.Graph(figure=fig3),
    dcc.Graph(figure=fig4),
    dcc.Graph(figure=fig5),
    dcc.Graph(figure=fig6),
    dcc.Graph(figure=fig7),
    tablefunction(data_nc),
    tablefunction(data_c)   
])

if __name__ == '__main__':
    app.run_server(debug=True)