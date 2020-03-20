# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

import pandas as pd
url_1="https://datos.madrid.es/egob/catalogo/300228-21-accidentes-trafico-detalle.csv"
data_1 = pd.read_csv(url_1, sep=";", encoding="latin1")
data_1.head()
data_1.dtypes

url_2="https://datos.madrid.es/egob/catalogo/300228-19-accidentes-trafico-detalle.csv"
data_2 = pd.read_csv(url_2, sep=";", encoding="latin1")
data_2.drop(data_2.columns[len(data_2.columns)-1], axis=1, inplace=True)
data_2.head()
data_2.dtypes
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
data1 = data1.astype({'FECHA': 'str', 'NUMERO': 'str'})
data1['ADDRESS'] =data1.apply(lambda x: '.'.join([x['CALLE'],', ',x['NUMERO'],', ','MADRID, SPAIN']),axis=1)
list(data1.columns)
data1.head()
data1.describe()
print(data1)

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
data1['FECHA'] = pd.to_datetime(data1['FECHA'])
data1['DAY'] = data1['FECHA'].dt.strftime('%A')

#data1['FECHA'] = data1['FECHA'].dt.strftime('%d/%m/%Y')
data1.dtypes

#Create historical data

#Min data
min_date = data1['FECHA'].min().strftime('%d/%m/%Y')
min_date
max_date = data1['FECHA'].max().strftime('%d/%m/%Y')
max_date

#Create data outputs
#Date victims, accidents and fatal victims
data_date = data1.groupby('FECHA')['NEXPEDIENTE'].count()
data_date.head()
data_date_victims = data1.groupby('FECHA').NEXPEDIENTE.nunique()
data_date_victims.head()
data_date_fvictims = data1[data1['INJURY'] == 'Fatal'].groupby('FECHA')['NEXPEDIENTE'].count()
data_date_fvictims.head()

#Data 2020
data = data1[(data1['FECHA'] > '2019-12-31')]
data.head()
data

#Total accidents 2020
total_acc = data.NEXPEDIENTE.nunique()
total_acc
#Total victims
total_vic = data.NEXPEDIENTE.count()
total_vic
#Total fatal victims
total_fvic = data[data['INJURY'] == 'Fatal'].NEXPEDIENTE.count()
total_fvic

#Weather
weather_vic = data.groupby(['TIPO.ACCIDENTE','ESTADO.METEREOLOGICO'])['NEXPEDIENTE'].count()
weather_acc = data.groupby(['TIPO.ACCIDENTE','ESTADO.METEREOLOGICO']).NEXPEDIENTE.nunique()

#Injury
injury_vic = data.groupby(['TIPO.ACCIDENTE','INJURYO'])['NEXPEDIENTE'].count()
injury_acc = data.groupby(['TIPO.ACCIDENTE','INJURY']).NEXPEDIENTE.nunique()

#District
district_acc = data.groupby(['TIPO.ACCIDENTE','DISTRITO']).NEXPEDIENTE.nunique()
district_type = data.groupby(['TIPO.ACCIDENTE', 'DISTRITO','TIPO.PERSONA'])['NEXPEDIENTE'].count()

#Total
total_data_acc = data.groupby('TIPO.ACCIDENTE').NEXPEDIENTE.nunique()
total_data_vic = data.groupby('TIPO.ACCIDENTE')['NEXPEDIENTE'].count()
total_data = pd.merge(total_data,total_data_vic, on='TIPO.ACCIDENTE')
total_data = total_data.rename(columns={'NEXPEDIENTE_x':'Accidents','NEXPEDIENTE_y':'Victims'})

data1.groupby(['TIPO.VEHICULO']).groups.keys()
data1.groupby('DAY')['NEXPEDIENTE'].count()
data1.groupby('ESTADO.METEREOLOGICO')['NEXPEDIENTE'].count()
data1.groupby('ESTADO.METEREOLOGICO').data1['DAY']=='Monday'.count()
data1[data1['INJURY'] == 'Fatal'].groupby('DAY')['NEXPEDIENTE'].count()
data1[data1['INJURY'] == 'Fatal'].groupby(['DAY','NEXPEDIENTE']).count()
data1[data1['INJURY'] == 'Fatal'].groupby('DAY').NEXPEDIENTE.nunique()
data1.groupby('INJURY')['NEXPEDIENTE'].count()


app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)