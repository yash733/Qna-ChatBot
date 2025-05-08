import os , sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from config.config import Config
from src.main import model_utility
from sidebar import sidebar_config


# ----- Title -----
st.title(Config().get_title())

# Side Bar
sidebar_config()


if st.session_state.config_saved == True:
    with st.container():
        st.markdown("### 📚 Data Sources")
        data = st.text_area(
            label='Enter URLs (separate multiple links with commas)',
            placeholder="https://example1.com, https://example2.com",
            help="Enter one or more URLs to analyze"
        )
        
    #st.write(data)
    if data != None:
        st.session_state.data = [url.strip() for url in data.split(',')]

        cols = st.columns(len(st.session_state.data))
        for idx, url in enumerate(st.session_state.data):
            with cols[idx]:
                st.markdown(f"🔗 `{url[:30]}...`")

        user_query = st.chat_input("Enter your query - ")
        if user_query and st.session_state.data :
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    runnable = model_utility().chat_history()
                    response = runnable.invoke({'input': user_query},
                                                config={'configurable': {'session_id': '1235'}})['answer']
                    st.markdown(response)