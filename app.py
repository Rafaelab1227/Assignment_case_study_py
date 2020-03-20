# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

import pandas as pd
url="https://datos.madrid.es/egob/catalogo/300228-21-accidentes-trafico-detalle.csv"
data = pd.read_csv(url, sep=";", encoding="latin1")
data.head()

#import os
#c=pd.read_csv("2020_Accidentalidad.csv", sep=";", encoding="latin1" )
#c.head()
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Changes in dataset ------------------------------------------------------
# Changes in column names
data1 = data.rename(columns={"NÚMERO":"NUMERO","ESTADO METEREOLÓGICO":"ESTADO.METEREOLOGICO",\
    "TIPO VEHÍCULO":"TIPO.VEHICULO","LESIVIDAD*":"LESIVIDAD","Nº  EXPEDIENTE":"NEXPEDIENTE",\
        "TIPO ACCIDENTE":"TIPO.ACCIDENTE","TIPO PERSONA":"TIPO.PERSONA","RANGO DE EDAD":"RANGO.DE.EDAD"})
list(data1.columns)

#Create column of address
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
data1 = data1.fillna('Unknown')

#Eliminate all the names ("CALL.", "AV.", etc) that are not supported by geolocation & eliminate double direction.
data1['ADDRESS'] = data1['ADDRESS'].str.replace('.*\\/','')
data1['ADDRESS'] = data1['ADDRESS'].str.replace('.*\\. ','')
#data1.loc[105,]

#Change levels of injury based on dataset dictionary
data1['INJURY'] ="Mild"
data1.loc[2,]
#data1.loc[data1.LESIVIDAD==3,'INJURY']
data1.dtypes
data1.loc[data1.LESIVIDAD==3,'INJURY']= 'Fatal'
data1.loc[data1['LESIVIDAD']==14,'INJURY']= 'Without assistance'
data1.loc[data1.LESIVIDAD==70,'INJURY']= 'Unknown'

#Change type of variables
#data1 = data1.astype({'FECHA': 'float64', 'HORA': 'object'})
data1['FECHA'] = pd.to_datetime(data1['FECHA'])
data1['DAY'] = data1['FECHA'].dt.strftime('%A')
data1['FECHA'] = data1['FECHA'].dt.strftime('%d/%m/%Y')

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