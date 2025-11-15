import requests
import json
import pandas as pd
import streamlit as st
from pprint import pprint

st.title("Premier League Top Scorers")

uri = 'https://api.football-data.org/v4/competitions/PL/scorers'
headers = { 'X-Auth-Token': '3200441e79214695acea9bfb1e3e310b' }

def get_flag(nationality):
    if nationality in ["England","Scotland","Wales", "Northern Ireland"]:
        nationality = "United Kingdom"
    flagsURL = f'https://restcountries.com/v3.1/name/{nationality}'
    response = requests.get(flagsURL)
    dataFLAGS = response.json()[0]
    return dataFLAGS['flags']['png']


#Top Scorer Graph

minimumPlayers = st.slider(
"Choose the number of top scorers to display.",
    min_value = 1,
    max_value = 25
)

response = requests.get(uri+f"?limit={minimumPlayers}", headers=headers)
goalScorers = []
for scorer in response.json()['scorers']:
    goalScorers.append({
        "name": scorer['player']['name'],
        "goals": scorer['goals']
    })
topScorerDF = pd.DataFrame(goalScorers)


detailedPlayers = []
for scorer in response.json()['scorers']:
    nationality = scorer['player']['nationality']
    flag = get_flag(nationality)
    detailedPlayers.append({
        "name": scorer['player']['name'],
        "team": scorer['team']['name'],
        "nationality": scorer['player']['nationality'],
        "flag": flag,
        "goals": scorer['goals'],
        "position": scorer['player']['section'],
        "assists": scorer['assists'] if scorer['assists'] is not None else 0,
        "crest": scorer['team']['crest']    
    })
detailedDF = pd.DataFrame(detailedPlayers)

chart = st.scatter_chart(
    topScorerDF,
    x = "name",
    y = "goals",
    x_label = "Players",
    y_label = "Goals Scored"
)

st.header("Detailed Player Statistics")
# Player Info

playerNames = list(topScorerDF["name"])

selectedPlayer = st.selectbox(
    "Select a player to view stats",
    playerNames,
    placeholder = None
)

if selectedPlayer:
    playerData = detailedDF[detailedDF["name"] == selectedPlayer].iloc[0]
    st.write(f"**Player:** {playerData['name']}")
    st.write(f"**Team:** {playerData['team']}")
    st.image(playerData["crest"], width=200)
    st.write(f"**Nationality:** {playerData['nationality']}")
    st.image(playerData["flag"], width=200)
    st.write(f"**Position:** {playerData['position']}")  
    st.write(f"**Goals:** {playerData['goals']}")  
    st.write(f"**Assists:** {playerData['assists']}") 




