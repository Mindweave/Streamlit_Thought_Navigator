import streamlit as st
import requests
import json
import pandas as pd
import random


st.set_page_config(layout="wide") #sets the streamlit page to use the complete width of the screen

OPENAI_API_KEY = st.secrets["api_keys"]["OPEN_AI_KEY_TEXT"]
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state['messages'] = []

def main():
    #additional chat features: https://github.com/carolinedlu/llamaindex-chat-with-streamlit-docs/blob/main/streamlit_app.py

    st.title("Chat")
    if st.session_state['selected_persona_name'] != "" and st.session_state['selected_persona_details'] != "" and st.session_state['topic'] != "": #there is the needed data to chat
        st.markdown(f"Chatting with *{st.session_state['selected_persona_name']}*")

        #setting up chat history
        
        
        prompt = "" #setup full prompt for access later 
        
        if user_input := st.chat_input("Your question"): # Receive user input and save to chat history
            prompt = st.session_state['selected_persona_details']['Pre-Prompt']+user_input+st.session_state['selected_persona_details']['Post-Prompt'] #surrounding text in persona specific text
            st.session_state['messages'].append({"role": "user", "content": prompt})
        
        # Display the prior chat messages
        for message in st.session_state.messages: 
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # If last message is not from assistant, generate a new response
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state['generate_response_function'](prompt,st.session_state['selected_persona_details'])
                    st.write(response.response)
                    message = {"role": "assistant", "content": response.response}
                    st.session_state.messages.append(message) # Add response to message history

if __name__ == '__main__':
    main()