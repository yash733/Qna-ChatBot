import os , sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from config.config import Config
from src.model import Model
from src.main import model_utility

if 'user_config' not in st.session_state:
    st.session_state.user_config = {}

if 'model' not in st.session_state:
    st.session_state.model = None

if 'data' not in st.session_state:
    st.session_state.data = []

# ----- Title -----
st.title(Config().get_title())

# Side Bar
with st.sidebar:
    st.session_state.user_config.update({'llm_data_collected' : True})
    model = st.selectbox(label= 'LLM Model', options= Config().get_model(), placeholder='Please Choose a LLM Model')
    if model == 'Groq':
        llm_model = st.selectbox(label= 'Model Type', options= Config().get_groq_model(), placeholder='Please Seletect Model Type')
        api = st.text_input(label= "Enter Groq API", type= 'password')
        if (llm_model and api):
            if st.button(label='Save Config', key='save groq config') and st.session_state.user_config.get('llm_data_collected') == True:
                st.session_state.user_config.update({'llm_model':llm_model, 'api':api, 'llm_data_collected':False})
                st.session_state.model = Model(st.session_state.user_config.get('llm_model')).Groq_llm(st.session_state.user_config.get('api'))
                
            else:
                st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")
                st.stop()

    elif model == 'Ollama':
        llm_model = st.selectbox(label= 'Model Type', options= Config().get_ollama_model(), key= 'ollama',placeholder='Please Select Model Type')

        if llm_model and st.button(label='Save Config', key='save ollama config') and st.session_state.user_config.get('llm_data_collected') == True:
            st.session_state.user_config.update({'llm_model':llm_model, 'llm_data_collected':False})
            st.session_state.model = Model(st.session_state.user_config.get('llm_model')).Ollama_llm()

if st.session_state.user_config.get('llm_data_collected') == False:
    data = st.text_area(label='Enter link, if multiple seperate with ", "')
    st.write(data)
    if data != None:
        st.session_state.data = data.split(', ')
        user_query = st.chat_input("Enter your query - ")
        if user_query and st.session_state.data :
            runnable = model_utility().chat_history()
            st.chat_message(runnable.invoke({'user_query':user_query},
                            config={'configurable':{'session_id':'1235'}})['answer'])