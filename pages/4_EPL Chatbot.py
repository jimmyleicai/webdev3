import streamlit as st
import requests
import google.generativeai as genai
import time

def url_info(): 
    url = "https://api.football-data.org/v4/competitions/PL/scorers"
    headers = { 'X-Auth-Token': '3200441e79214695acea9bfb1e3e310b' }
    response = requests.get(url+"?limit=50", headers=headers)
    goalScorers = []
    for scorer in response.json()['scorers']:
        goalScorers.append({
            "name": scorer['player']['name'],
            "team": scorer['team']['name'],
            "nationality": scorer['player']['nationality'],
            "goals": scorer['goals'],
            "position": scorer['player']['section'],
            "assists": scorer['assists'] if scorer['assists'] is not None else 0,
            "crest": scorer['team']['crest']    
        })
    context_str = "Premier League Top 50 goalscorers data: "
    for player in goalScorers:
        context_str += f"Player: {player['name']}, Club: {player['team']}, Nationality: {player['nationality']}, Goals: {player['goals']}, Position: {player['position']}, Assists: {player['assists']}. "
    return context_str

gemini_context = url_info()


key = st.secrets["key"]

genai.configure(api_key=key)

st.title("Chat with Gemini about Premier League's Hottest Talents")

if 'model' not in st.session_state:
    st.session_state.model = genai.GenerativeModel("gemini-2.5-flash")

if "messages" not in st.session_state:
    st.session_state.messages = []

instruction = ("You are an AI chatbot specialized in the Premier League's hottest young talents. "
                "You must use the following data to answer user questions: "
                f"{gemini_context}")


if not st.session_state.messages:
    greetings_prompt =  instruction + '''\n\Write a short statement introducing yourself as an 
                        AI chatbot designed to help the user with whatever questions 
                        they have about the Premier League's hottest talents.'''
    try: 
        greeting_response = st.session_state.model.generate_content(greetings_prompt, stream=True)
        greeting = ""
        
        greeting_container = st.empty()
        for chunk in greeting_response:
            if hasattr(chunk, 'text') and chunk.text:
                greeting += chunk.text
                greeting_container.markdown(greeting)
                time.sleep(0.25)
        st.session_state.messages.append({"role": "assistant", "content": greeting})
        st.rerun()
    except Exception as e:
        error_message = f"The following error ocurred: {e}. We apologise for the inconvenience :("
        st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


chatPrompt = st.chat_input("Ask Gemini something about the top 50 goalscorers of the Premier League")
if chatPrompt:
    st.session_state.messages.append({"role": "user", "content": chatPrompt})
    with st.chat_message("user"):
        st.markdown(chatPrompt)
    
    full_convo = [{"role": "user", "parts": [instruction]}]

    for message in st.session_state.messages:
        role = 'user' if message['role'] == 'user' else 'model'
        full_convo.append({
            'role': role,
            'parts': [message['content']]  
            })

    try:
        response_stream = st.session_state.model.generate_content(full_convo, stream=True)
        response = "" 
        with st.chat_message("assistant"):
            response_container = st.empty()
            for chunk in response_stream:
                if hasattr(chunk, "text") and chunk.text:
                    response += chunk.text
                    response_container.markdown(response)
                    time.sleep(0.5)
        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        error_message = f"The following error ocurred: {e}. We apologise for the inconvenience :("
        st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})


    st.rerun()
