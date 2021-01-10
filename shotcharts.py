# Import packages
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import players
from nba_api.stats.static import teams

import json
import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

teamsUrlReq = requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json')
teams = json.loads(teamsUrlReq.text)

playersUrlReq = requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/players.json')
players = json.loads(playersUrlReq.text)


# Get team ID 
def get_team_id(team):
    team = team.lower()
    for t in teams:
        if t['teamName'].lower() == team:
            return t['teamId']
    return -1


# Get player ID 
def get_player_id(first, last):
    first = first.lower()
    last = last.lower()
    for p in players:
        if p['firstName'].lower() == first and p['lastName'].lower() == last:
            return p['playerId']
    return -1

# JSON request for 2020 Kuz
shot_json = shotchartdetail.ShotChartDetail(
    team_id = get_team_id('los angeles lakers'),
    player_id = get_player_id('kyle kuzma'),
    context_measure_simple = 'FGA', 
    season_nullable = '2019-20',
    season_type_all_star = 'Regular Season')

# Converting data into dictionary, getting relevant data
shot_data = json.loads(shot_json.get_json())
relevant_data = shot_data['resultSets'][0]
headers = relevant_data['headers']
rows = relevant_data['rowSet']

# Create pandas data frame
kuz_data = pd.DataFrame(rows)
kuz_data.columns = headers

