"""
@author: stefan
"""
# import libraries
from lxml import html
import requests
import pandas as pd
import numpy as np
import os
from geopy.geocoders import Nominatim
import pickle
import json



def find_lat_long_country(rounds):
    # function to read latitude, longitude and Country into dataframe
    
    game = pd.DataFrame(data = None, columns = ['Lat','Long','Country'], index = ['Round %d'%i for i in range(1,6) ])
    # initalise Geolocator
    geolocator = Nominatim(user_agent="me")
    # for each round in game, read data out of input
    for k in range(0,5):
        game['Lat'].iloc[k] = rounds[k]['lat']
        game['Long'].iloc[k] = rounds[k]['lng']
        # determine address of location from coordinates and read country if it is part of the address.
        location = geolocator.reverse([game['Lat'].iloc[k], game['Long'].iloc[k]],language = 'en')
        if not 'error' in location.raw:
            if 'country' in location.raw['address']:
                game['Country'].iloc[k] = location.raw['address']['country']

    return game


def find_distance_score(rounds):
    # function to read distance and Score into dataframe
            
    game = pd.DataFrame(data = None, columns = ['Distance', 'Score'], index = ['Round %d'%i for i in range(1,6) ])
    # for each round in game, read data out of input
    for k in range(0,5):
        game['Distance'].iloc[k] = rounds[k]['distance']
        game['Score'].iloc[k] = rounds[k]['score'][0]['amount']
    
    return game





# Define Class GeoGame which reads and stores one GeoGuessr game
class GeoGame:
    
    def __init__(self,link,names):
        # input: link of the game and names of the players (as on geoguessr webpage)
        # each player should have a unique name!!
        self.link = link
        self.names = names
        self.places = []
        self.rounds = {}
        self.results = pd.DataFrame(data = None, columns = self.names, index = ['Scores', 'Countries'])
        self.read_game()
        
        
    def read_game(self):
        # read website data
        page = requests.get(self.link)
        tree = html.fromstring(page.content)
        # get interesting information
        z = tree.xpath('//script[@type="text/javascript"]/text()')
        a = str(z[2])
        i1 = a.find('{')
        i2 = a.rfind(';')
        # transform data into readable format
        result_json = json.loads(a[i1:i2])
        # find game locations
        self.places = find_lat_long_country(result_json['rounds'])
        # define help variable
        hv = result_json['hiScores']

        # for each player that played read their result
        for k in range(0,len(hv)):
            gameToken = hv[k]['gameToken']
            player = hv[k]['playerName']
            # only consider players with prespecified names
            if player in self.names:
                page = requests.get('https://www.geoguessr.com/results/' + gameToken)
                tree = html.fromstring(page.content)
                z = tree.xpath('//script[@type="text/javascript"]/text()')
                a = str(z[2])
                i1 = a.find('{')
                i2 = a.rfind(';')
                result_json = json.loads(a[i1:i2])
                guesses = result_json['players'][0]['guesses']
                self.rounds[player] = find_lat_long_country(guesses).join(find_distance_score(guesses))
        self.calc_res()
                
    def calc_res(self):
        # write results in a dataframe. Set results to zero if player did not play
        for player in self.names:
            if player in self.rounds.keys():
                self.results.loc['Scores', player] = self.rounds[player]['Score'].sum()
                self.results.loc['Countries',player] = sum(self.places['Country'] == self.rounds[player]['Country'])
            else:
                self.results.loc['Scores', player] = 0
                self.results.loc['Countries',player] = 0
            

    
    
        
        
        
# Class Geoguessr combines several Geoguessr games into a season
class GeoGuessr:
    
    max_length = 12 # specifies the games per season
    
    def __init__(self, SeasonNo, path, names):
        # path gives the place for all things to be stored
        # names are the unique player names of the contestants (as on geoguessr webpage)
        self.season = SeasonNo
        self.path = path + "Season %d" % self.season + '/'
        self.names = names
        self.links = pd.Series([])
        self.scores = pd.DataFrame([], columns = self.names)
        self.table = pd.DataFrame([], columns = self.names)
        self.len_scor = 0
        self.boni = pd.Series(data = None, index = ['Win highest scoring game',
                                                      'Win lowest scoring game',
                                                      'Win closest game',
                                                      'Highest single score',
                                                      'Largest win margin',
                                                      'Largest 2nd place margin',
                                                      'Always second',
                                                      'Best last place',
                                                      'Most exciting',
                                                      'Most consistent',
                                                      'Strongest finish'])
        self.run = pd.Series(data = np.array([0,0,0]), index = self.names)
        self.result = pd.Series(data = None, index = self.names)
        self.games = []
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
                
        
    def write_data(self):
        # Save (intermediate) results to csv files
        self.scores.to_csv(self.path + 'Scores.csv', sep = ";",index = False)
        self.links.to_csv(self.path + 'Links.csv', sep = ";",index = False)
        self.table.to_csv(self.path + 'Points.csv', sep = ";")
        self.boni.to_csv(self.path + 'Boni.csv', sep = ";")
        with open(self.path +'geoguessr.season', 'wb') as season_file:
            pickle.dump(self, season_file)
        
    def add_game(self):
        # Add a GeoGuessr Game to the Season if Season is not finished
        if self.len_scor >= self.max_length:
            return
        self.links.loc[self.len_scor] = input("Game Link: ")
        self.games.append(GeoGame(self.links.loc[self.len_scor],self.names))
        self.scores.loc[self.len_scor] = self.games[self.len_scor].results.loc['Scores']
        self.len_scor +=1
        # calculate current standings
        self.calc_points()
        
    def calc_points(self):
        #Calulating the points of all participants
        scores = self.scores
        len_scor = self.len_scor
        len_name = len(self.names)
        
        ###### Calculate Points #######

        points = pd.DataFrame(np.zeros([len_scor,len_name]), columns = self.names)
        place = pd.DataFrame(data = None, columns = self.names)
        
        ###### Points for order of results ######       
        for j in range(0,len_scor):
            #only consider players who player/scored more than 0
            non_zero = scores.iloc[j][scores.iloc[j]>0]
            order = non_zero.sort_values(ascending = True).keys()
            # Tag Winner, Loser and 2nd place
            place.loc[j,order[-1]] = 'Winner'
            place.loc[j,order[-2]] = '2nd'
            place.loc[j,order[0]] = 'Loser'
            points.loc[j,order[-1:]] += 1
            for k in range(1,len(order)):
                points.loc[j,order[k:]] += 1 
        
        ###### In-Game Bonus Points #########

        # Bonus point for scoring above 20000
        above20 = (scores >= 20000)
        points[above20] += 1

        # If all non-zero reults are within 10% of the winner
        # everyone expect winner gets one point
        highest = list(scores.max(axis = 1))
        winner = (place == 'Winner')
        lowest = list(scores[scores>0].min(axis = 1))
        hv = np.array(lowest)>=0.9*np.array(highest)
        closeG = np.array([hv,hv,hv]).transpose()
        points[closeG & ~winner & (scores>0)] += 1
        
        # 0.2 points for right Country
        for k in range(0,len_scor):
            points.iloc[k] += self.games[k].results.loc['Countries']*0.2
            
        # Sum of all points
        sum_points = points.sum()
        
        # functions I need
        def find_max(vec):
            m_vec = vec.max()
            z = list(vec[vec == m_vec].keys())
            return(z)
    
        def find_min(vec):
            m_vec = vec.min()
            z = list(vec[vec == m_vec].keys())
            return(z)
    
        ######### Seasonal Bonus Points #############

        # always second (Bonus point for player with most second places)
        help_v = find_max(scores[place=='2nd'].count())
        sum_points[help_v] += 1
        self.boni['Always second'] = help_v

        # most exciting and most consisent player get a bonus point
        help_v = find_max(scores.std())
        sum_points[help_v] += 1
        self.boni['Most exciting'] = help_v
        help_v = find_min(scores.std())
        sum_points[help_v] += 1
        self.boni['Most consistent'] = help_v

        # highest single score
        # player with n highest single scores gets n points
        help_v = find_max(scores.max())
        z = 1
        if len(help_v) == 1:
            not_hss = list(scores.columns[scores.columns != help_v[0]])
            mx_not_hss = scores[not_hss].max().max()
            z = int((scores[help_v] > mx_not_hss).sum())
        sum_points[help_v] += z
        self.boni['Highest single score'] = help_v

        # best last place
        help_v = find_max(scores[place=='Loser'].max())
        sum_points[help_v] += 1
        self.boni['Best last place'] = help_v

        # strongest finish for best result in last 3 games
        if len_scor >= self.max_length-2:
            help_v = find_max(points[(self.max_length-3):len_scor].sum())
            sum_points[help_v] += 3
            self.boni['Strongest finish'] = help_v

        # largest win margin
        win_margins = list(scores[winner].max(axis =1) - scores[~winner].max(axis =1))
        ind = win_margins.index(max(win_margins))
        help_v = find_max(scores.iloc[ind])
        sum_points[help_v] += 1
        self.boni['Largest win margin'] = help_v

        # largest second place margin
        sec_margins = list(scores[~winner].max(axis =1) - scores[~(place=='2nd') & ~winner].max(axis =1))
        ind = sec_margins.index(max(sec_margins))
        help_v = find_max(scores[~winner].iloc[ind])
        sum_points[help_v] += 1
        self.boni['Largest 2nd place margin'] = help_v

        # Win highest scoring game
        sum_sco = list(scores.sum(axis = 1))
        ind = sum_sco.index(max(sum_sco))
        help_v = find_max(scores.iloc[ind])
        sum_points[help_v] += 1
        self.boni['Win highest scoring game'] = help_v

        # Win lowest scoring game
        sum_sco = list(scores.sum(axis = 1))
        ind = sum_sco.index(min(sum_sco))
        help_v = find_max(scores.iloc[ind])
        sum_points[help_v] += 1
        self.boni['Win lowest scoring game'] = help_v

        # Win closest Game
        win_margins2last = list(scores[winner].max(axis =1) - scores[place=='Loser'].min(axis =1))
        ind = win_margins2last.index(min(win_margins2last))
        help_v = find_max(scores.iloc[ind])
        sum_points[help_v] += 1
        self.boni['Win closest game'] = help_v


        bonus_points = sum_points - points.sum()
        bonus_points.name = 'Bonus points'

        ######### Run points ##########

        # runpoints function
        def add_run_points(threshold,streak):
            for name in scores.columns:
                under = [-1]
                under.extend( scores[name].index[scores[name]<threshold].tolist() )
                under.append(len_scor)
                under = np.array(under)
                rp = sum( np.maximum( under[1:]-under[:-1] - streak ,0) )
                sum_points[name] += rp
                self.run[name] += rp

        # run points starting at 10 games over 12000 points in a row
        # and 5 games over 95% of the Average
        add_run_points(12000,10)   
        add_run_points(0.95*self.scores.mean().mean(),5) 


        ##### Put results together ######
        run_points = sum_points - points.sum() - bonus_points
        run_points.name = 'Run points'

        without_bp = points.sum()
        without_bp.name ='Sum'

        sum_points.name = 'Total'

        ave = scores.mean()
        ave.name = 'Average'

        points.index = ['Game %d' % (i+1) for i in range(0,len_scor)]

        points = points.append(without_bp)
        points = points.append(bonus_points)
        points = points.append(run_points)
        points = points.append(sum_points)
        points = points.append(ave)
        self.table = points.round(1)
        self.result = sum_points

        
