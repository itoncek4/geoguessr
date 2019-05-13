"""
Created on Sat May 11 18:04:23 2019

@author: stefan
"""


# Set path to location of GeoGuessr.py file. Results will also be stored
# in the same location
path = './'

# Give (unique) names of contestants as displayed on geoguessr.com
names  = ['player_name1','player_name2','player_name3']




# append Folder given by path
import sys
sys.path.append(path)

# Import Geoguessr Class
from GeoGuessr import GeoGuessr

# import libraries
import os
import pickle
import pandas as pd


# define function that keeps track of scores in different countries
def add_to_country_count(df,GeoGame):
    for k in range(0,5):
        country = GeoGame.places['Country'].iloc[k]
        if country in df.index:
            # If already been in that country calculate update average score
            df.loc[country, 'Visits'] += 1
            n = df.loc[country, 'Visits']
            for player in GeoGame.names:
                df.loc[country,player] = (n-1)/n*df.loc[country,player] + GeoGame.rounds[player].loc['Round %i'%(k+1),'Score']/n
        else:
            # otherwise add country to the list with new score
            df.loc[country, 'Visits'] = 1
            for player in GeoGame.names:
                df.loc[country,player] = GeoGame.rounds[player].loc['Round %i'%(k+1),'Score']
    df = df.round(1)
    return df.sort_index() 



# read number of season
no = int(input('What season?\n'))
#generate path for Season folder
season_path = path + "Season %d" % no + '/'

# load existing results if season already start or initialise new season
if os.path.isfile(season_path + 'geoguessr.season'):
    with open(season_path + 'geoguessr.season', 'rb') as season_file:
        S = pickle.load(season_file)
else:
    S = GeoGuessr(no,path,names)
    
# read country statistic or generate new one 
if os.path.isfile(path + 'Country_score.csv'):
    df = pd.read_csv(path + 'Country_score.csv', index_col=0)
else:
    df = pd.DataFrame(data = None, columns = names)

# Add Game by reading imput
add_g = ''
if S.len_scor < S.max_length:
    add_g = input('Add game? (y)')

while (add_g == 'y') & (S.len_scor < S.max_length):
    S.add_game()
    S.write_data()
    df = add_to_country_count(df,S.games[S.len_scor-1])
    df.to_csv(path + 'Country_score.csv')
    add_g = input("To add another game? (y): \n")


# what results to show
what = input("Final result (r), full point table (t), boni (b), game scores (s) \n")

if 'r' in what:
    print(S.result)
if 't' in what:
    print(S.table)
if 'b' in what:
    print(S.boni)
if 's' in what:
    print(S.scores)


