# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

import pandas as pd
url="https://datos.madrid.es/egob/catalogo/300228-21-accidentes-trafico-detalle.csv"
data = pd.read_csv(url, sep=";", encoding="latin1")
data.head()

import os
c=pd.read_csv("2020_Accidentalidad.csv", sep=";", encoding="latin1" )
c.head()
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Changes in dataset ------------------------------------------------------
# Changes in column names
data1 = data.rename(columns={"NÚMERO":"NUMERO","ESTADO METEREOLÓGICO":"ESTADO.METEREOLOGICO",\
    "TIPO VEHÍCULO":"TIPO.VEHICULO","LESIVIDAD*":"LESIVIDAD","Nº  EXPEDIENTE":"NEXPEDIENTE",\
        "TIPO ACCIDENTE":"TIPO.ACCIDENTE","TIPO PERSONA":"TIPO.PERSONA","RANGO DE EDAD":"RANGO.DE.EDAD"})
list(data1.columns)

data1['ADDRESS'] =data1.apply(lambda x: '.'.join([x['CALLE'],', ',x['NUMERO'],', ','MADRID, SPAIN']),axis=1)
list(data1.columns)
data1.head()
data1.describe()
print(data1)

#data1 =data1.assign(is_senior = lambda dataframe: dataframe['CALLE','NUMERO'].map(lambda name: CALLE+", "+NUMERO))
data1['ADDRESS'] = data1['ADDRESS'].str.replace('\.','')
data1.loc[1,'ADDRESS']
data1['ADDRESS'] = data1['ADDRESS'].str.replace(', -, ',', 0,')
data1['ADDRESS'] = data1['ADDRESS'].str.replace(' NA, ','')
data1 = data1.fillna('Unknown')



#Change levels of injury based on dataset dictionary
data$INJURY <- "Mild"
data[is.na(data$LESIVIDAD),match("LESIVIDAD",names(data))]<- "Unknown"
data[is.na(data$LESIVIDAD), match("INJURY",names(data))] <- "Unknown"
data[data$LESIVIDAD=="3", match("INJURY",names(data))] <- "Fatal"
data[data$LESIVIDAD=="14"|data$LESIVIDAD=="", match("INJURY",names(data))] <- "Without assistance"
data[data$LESIVIDAD=="77", match("INJURY",names(data))] <- "Unknown"





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