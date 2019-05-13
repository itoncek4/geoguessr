"""
Created on Thu Mar 28 16:17:15 2019

@author: stefan
"""
# name the player for whom the plot should be made
player = 'player1'
# give path of folder in which your Country score file is
path = './'

# import libraries
import plotly as py
import plotly.graph_objs as go
import pandas as pd

#import data 
df = pd.read_csv(path + "Country_score.csv", index_col = 0)

# rename countries to fit
df.loc['South Africa'] = df.loc['RSA']
df = df.drop('RSA')
df.loc['China'] = df.loc['PRC']
df = df.drop('PRC')

# plot and save
data = dict (
    type = 'choropleth',
    locations = df.index,
    locationmode='country names',
    colorscale = [[0, '#FF3333'], [1, '#00FF00']],
    z=df[player])

map = go.Figure(data=[data])
py.offline.plot(map)

