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
    player_id = get_player_id('kyle', 'kuzma'),
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

# Drawing basketball court
def create_court(ax, color):
    # 3 point line
    ax.plot([-220, -220], [0, 140], linewidth = 2, color = color)
    ax.plot([220, 220], [0, 140], linewidth = 2, color = color)
    ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))

    # Key and lane
    ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
    ax.plot([80, 80], [0, 190], linewidth=2, color=color)
    ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
    ax.plot([60, 60], [0, 190], linewidth=2, color=color)
    ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
    ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))

    # Rim and backboard
    ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))
    ax.plot([-30, 30], [40, 40], linewidth=2, color=color)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 470)

    return ax

mpl.rcParams['font.family'] = 'Avenir'
mpl.rcParams['font.size'] = 18
mpl.rcParams['axes.linewidth'] = 2

# Draw court
fig = plt.figure(figsize=(4, 3.76))
ax = fig.add_axes([0, 0, 1, 1])
ax = create_court(ax, 'black')

ax.hexbin(kuz_data['LOC_X'], kuz_data['LOC_Y'] + 60, gridsize=(30, 30), extent=(-300, 300, 0, 940), bins='log', cmap='Purples')

plt.savefig('ShotChart1.png', dpi=300, bbox_inches='tight')
plt.show()

