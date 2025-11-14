import requests
import json
import pandas as pd
import streamlit as st
from pprint import pprint

#/v4/competitions/{id}/scorers
	
uri = 'https://api.football-data.org/v4/competitions/PL/scorers'
headers = { 'X-Auth-Token': '3200441e79214695acea9bfb1e3e310b' }

minimumPlayers = st.slider(
"Choose the number of top scorers to display.",
    min_value = 1,
    max_value = 25
)

response = requests.get(uri+f"?limit=25", headers=headers)
goalScorers = []
for index in response.json()['scorers']:
    if len(goalScorers) == minimumPlayers:
        break
    else:
        goalScorers.append(
            {'name': index['player']['name'],
             'goals': index['goals']}
            )
    
print (goalScorers)

topScorerDF = pd.DataFrame(goalScorers)

st.scatter_chart(
    topScorerDF,
    x = "name",
    y = "goals",
    x_label = "Players",
    y_label = "Goals Scored"
)

sblist = []
for player in goalScorers:
    sblist.append(player['name'])
    

selection = st.selectbox(
    "Select a player:",
    sblist)



