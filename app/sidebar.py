import os , sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from config.config import Config
from src.model import Model
import streamlit as st

# ----- Config ----- #
class sidebar_config:
    def __init__(self):
        if 'user_config' not in st.session_state:
            st.session_state.user_config = {}

        if 'model' not in st.session_state:
            st.session_state.model = None

        if 'data' not in st.session_state:
            st.session_state.data = []
        
        if 'config_saved' not in st.session_state:
            st.session_state.config_saved = False
        
        with st.sidebar:
            if st.session_state.config_saved == False:
            
                model = st.selectbox(label= 'LLM Model', options= Config().get_model())
                if model == 'Groq':
                    llm_model = st.selectbox(label= 'Model Type', 
                                             options= Config().get_groq_model())
                    api = st.text_input(label= "Enter Groq API", 
                                        type= 'password')
                    if llm_model and api:
                        if st.button(label='Save Config', key='save groq config'):
                            st.session_state.user_config.update({
                                'llm_model':llm_model, 
                                'api':api, 
                                'model':'Groq'
                                })
                            st.session_state.model = Model(st.session_state.user_config.get('llm_model')).Groq_llm(st.session_state.user_config.get('api'))
                            st.session_state.config_saved = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")
                        st.stop()

                elif model == 'Ollama':
                    llm_model = st.selectbox(label= 'Model Type', options= Config().get_ollama_model(), key= 'ollama')
                    if llm_model:
                        if st.button(label='Save Config', key='save ollama config'):
                            st.session_state.user_config.update({'llm_model':llm_model, 
                                                                 'model':'Ollama'})
                            st.session_state.model = Model(st.session_state.user_config.get('llm_model')).Ollama_llm()
                            st.session_state.config_saved = True
                            st.rerun()

            # --- Show selected config
            elif st.session_state.config_saved:
                st.markdown("### Selected Configuration")
                st.write(f"**Model**: {st.session_state.user_config['model']}")
                st.write(f"**Model Type**: {st.session_state.user_config['llm_model']}")

                if st.button('Reset Config'):
                    st.session_state.config_saved = False
                    st.session_state.user_config = {}
                    st.session_state.model = None
                    st.session_state.data = []
                    st.rerun()

