import os
import google.generativeai as genai
import requests
import streamlit as st

#Variables and stuff
fd_base = "https://api.football-data.org/v4"
headers = {"X-Auth-Token": "3200441e79214695acea9bfb1e3e310b"}
GEMINI_KEY = st.secrets["key"]
genai.configure(api_key=GEMINI_KEY)


st.title("Premier League Matchup Analyzer")

#Find Standings
def get_standings():
    url = f"{fd_base}/competitions/PL/standings"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error("Error fetching standings data.")
        return None

    data = response.json()
    if "standings" not in data:
        return None

    return data

standings_json = get_standings()
if not standings_json:
    st.stop()

#Team from Standings
def extract_teams(standings_json):
    table = standings_json["standings"][0]["table"]

    teams = []
    for row in table:
        teams.append({
            "id": row["team"]["id"],
            "name": row["team"]["name"]
        })

    return teams

teams = extract_teams(standings_json)

team_names = []
for team in teams:
    team_names.append(team["name"])

#Team Selection
st.subheader("Select Two Teams for a Match Preview")

team1_name = st.selectbox("Team 1", team_names)
team2_name = st.selectbox("Team 2", team_names, index=1)

for team in teams:
    if team["name"] == team1_name:
        team1_id = team["id"]
    if team["name"] == team2_name:
        team2_id = team["id"]

#Team Stats
def get_team_stats(team_id, standings_json):
    table = standings_json["standings"][0]["table"]

    for row in table:
        if row["team"]["id"] == team_id:
            return row

    return None

team1_stats = get_team_stats(team1_id, standings_json)
team2_stats = get_team_stats(team2_id, standings_json)

#Tone Select
tone_options = ["Professional", "Casual", "Analytical", "Humorous"]
tone = st.selectbox("Select the tone for the analysis", tone_options)

#Gemini Call
prompt = f"""
Compare these two Premier League teams using official standings data.

Team 1: {team1_name}
Stats (raw data): {team1_stats}

Team 2: {team2_name}
Stats (raw data): {team2_stats}

Write a {tone.lower()} analysis comparing strengths, weaknesses,
style of play, form indicators, and who might have the advantage.
Use the data directly to justify the analysis.
"""

if st.button("Generate Match Analysis"):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    st.write(response.text)
