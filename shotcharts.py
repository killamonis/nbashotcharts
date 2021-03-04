# Import packages
import NBAapi as nba
import json
import requests
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib.patches import Circle, Polygon, Rectangle, Arc
import matplotlib.pyplot as plt

teams_url = requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/teams.json')
teams = json.loads(teams_url.text)

players_url = requests.get('https://raw.githubusercontent.com/bttmly/nba/master/data/players.json')
players = json.loads(players_url.text)


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

#Gets the specific shot zone of an individual field goal attempt
def get_shot_zone(x, y):
    d = np.sqrt(x**2 + y**2)
    z = np.arctan2(y,x) * 180/np.pi
    loc = None
    if (y < 0) and (x > 0):
        z = 0
    elif (y < 0) and (x < 0):
        z = 180
    if d <= 8:
        loc = ('Less Than 8 ft.', 'Center(C)')
    elif (d > 8) and (d <= 16):
        if z < 60:
            loc = ('8-16 ft.','Right Side(R)')
        elif (z >= 60) and (z <= 60):
            loc = ('8-16 ft.','Center(C)')
        else:
            loc = ('8-16 ft.','Left Side(L)')
    elif (d > 16) & (d <= 23.75):
        if z < 36:
            loc = ('16-24 ft.','Right Side(R)')
        elif (z >= 36) & (z < 72):
            loc = ('16-24 ft.','Right Side Center(RC)')
        elif (z >= 72) & (z <= 108):
            loc = ('16-24 ft.','Center(C)')
        elif (z > 108) & (z < 144):
            loc = ('16-24 ft.','Left Side Center(LC)')
        else:
            loc = ('16-24 ft.','Left Side(L)')
    elif (d > 23.75):
        if z < 72:
            loc = ('24+ ft.','Right Side Center(RC)')
        elif (z >= 72) & (z <= 108):
            loc = ('24+ ft.','Center(C)')
        else:
            loc = ('24+ ft.','Left Side Center(LC)')
    if (np.abs(x) >= 22):
        if (x > 0) & (np.abs(y)<8.75):
            loc = ('24+ ft.','Right Side(R)')
        elif (x < 0) & (np.abs(y)<8.75):
            loc = ('24+ ft.','Left Side(L)')
        elif (x > 0) & (np.abs(y)>=8.75):
            loc = ('24+ ft.','Right Side Center(RC)')
        elif (x < 0) & (np.abs(y)>=8.75):
            loc = ('24+ ft.','Left Side Center(LC)')
    if (y >= 40):
        loc = ('Back Court Shot', 'Back Court(BC)')
    return loc

#Plots an NBA-size court
#Adjusted from danielwelch's implementation
def create_court(ax=None, color='black', lw=4):
    ax = plt.gca(xlim = [30,-30],ylim = [-7,43],xticks=[],yticks=[],aspect=1.0)
    hoop = Circle((0, 0), radius=0.75, linewidth=lw, color=color)
    backboard = Rectangle((-3, -0.75), 6, -0.1, linewidth=lw, color=color)
    outer_box = Rectangle((-8, -5.25), 16, 19, linewidth=lw, color=color, fill=False)
    inner_box = Rectangle((-6, -5.25), 12, 19, linewidth=lw, color=color, fill=False)
    top_free_throw = Arc((0, 13.75), 12, 12, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
    bottom_free_throw = Arc((0, 13.75), 12, 12, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed')
    restricted = Arc((0, 0), 8, 8, theta1=0, theta2=180, linewidth=lw, color=color)
    corner_three_a = Rectangle((-22, -5.25), 0, np.sqrt(23.75**2-22.0**2)+5.25, linewidth=lw, color=color)
    corner_three_b = Rectangle((22, -5.25), 0, np.sqrt(23.75**2-22.0**2)+5.25, linewidth=lw, color=color)
    three_arc = Arc((0, 0), 47.5, 47.5, theta1=np.arccos(22/23.75)*180/np.pi, 
                    theta2=180.0-np.arccos(22/23.75)*180/np.pi, linewidth=lw,color=color)
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, bottom_free_throw, 
                    restricted, corner_three_a, corner_three_b, three_arc]
    ax.plot([-25,25],[-5.25,-5.25],linewidth=lw,color=color)
    for element in court_elements:
        ax.add_patch(element)
    return ax

shotchart,league_average = nba.shotchart.shotchartdetail(playerid = get_player_id('Kyle', 'Kuzma'), season = '2019-20')
league = league_average.loc[:,'SHOT_ZONE_AREA':'FGM'].groupby(['SHOT_ZONE_RANGE','SHOT_ZONE_AREA']).sum()
league['FGP'] = 1.0 * league['FGM']/league['FGA']
player_zones = shotchart.groupby(['SHOT_ZONE_RANGE', 'SHOT_ZONE_AREA', 'SHOT_MADE_FLAG']).size().unstack(fill_value=0)
player_zones['FGP'] = 1.0 * player_zones.loc[:,1]/player_zones.sum(axis=1)

player_vs_league = (player_zones.loc[:,'FGP'] - league.loc[:,'FGP']) * 100
x = 0.1 * shotchart.LOC_X.values
y = 0.1 * shotchart.LOC_Y.values
hexbins = plt.hexbin(x, y, gridsize=35, extent=[-25,25,-6.25,50-6.25])
counts = hexbins.get_array()
verts = hexbins.get_offsets()

ax = create_court()
s = 0.85
bins = np.concatenate([[-np.inf], np.linspace(-9, 9, 200), [np.inf]])
colors = [(0.0, 0.20, 0.80), (0.9,1.0,0.6), (0.70, 0, 0)]
color_map = mpl.LinearSegmentedColormap.from_list('my_list', colors, N=len(bins)-1)

xy = s*np.array([np.cos(np.linspace(np.pi/6,np.pi*330/180,6)),np.sin(np.linspace(np.pi/6,np.pi*330/180,6))]).T
b = np.zeros((6,2))

counts_norm = np.zeros_like(counts)
counts_norm[counts >= 4] = 1
counts_norm[(counts>=2) & (counts<4)] = 0.5
counts_norm[(counts>=1) & (counts<2)] = 0.3

patches = []
colors = []

for offc in range(verts.shape[0]):
    if counts_norm[offc] != 0:
        xc, yc = verts[offc][0], verts[offc][1]
        b[:,0] = xy[:,0]*counts_norm[offc] + xc
        b[:,1] = xy[:,1]*counts_norm[offc] + yc
        p_diff = player_vs_league.loc[get_shot_zone(xc, yc)]
        inds = np.digitize(p_diff, bins, right=True) - 1
        patches.append(Polygon(b))
        colors.append(inds)

p = mpl.PatchCollection(patches,cmap=color_map,alpha=1)
p.set_array(np.array(colors))
ax.add_collection(p)
p.set_clim([0, len(bins)-1])

