import os , sys
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import faiss
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader

from config.config import Config
from src.model import Model

if 'user_config' in st.session_state:
    st.session_state.user_config = {}

if 'model' in st.session_state:
    st.session_state.model = None

st.title(Config().get_title())

# Side Bar
with st.sidebar():

    model = st.selectbox(label= 'LLM Model', options= Config().get_model(), placeholder='Please Choose a LLM Model')
    if model == 'Groq':
        llm_model = st.selectbox(label= 'Model Type', options= Config().get_groq_model(), placeholder='Please Seletect Model Type')
        api = st.text_input(label= "Enter Groq API", type= 'password')
        if (llm_model and api):
            if st.button(label='Save Config', key='save groq config'):
                st.session_state.user_config.update({'llm_model':llm_model, 'api':api})
                st.session_state.model = Model().Groq_llm(st.session_state.user_config.get('llm_model'), st.session_state.user_config.get('api'))
                
            else:
                st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")
                st.stop()

    elif model == 'Ollama':
        llm_model = st.selectbox(label= 'Model Type', options= Config().get_ollama_model(), key= 'ollama',placeholder='Please Select Model Type')

        if llm_model and st.button(label='Save Config', key='save ollama config'):
            st.session_state.user_config.update({'llm_model':llm_model})
            st.session_state.model = Model().Ollama_llm(st.session_state.user_config.get('llm_model'))

