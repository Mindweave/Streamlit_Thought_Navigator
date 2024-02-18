import streamlit as st
import requests
import json
import pandas as pd
import random
import time

st.set_page_config(layout="wide") #sets the streamlit page to use the complete width of the screen

OPENAI_API_KEY = st.secrets["api_keys"]["OPEN_AI_KEY_TEXT"]
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

def chat_requirements_notification():
     st.warning("You need to get a response from a persona and click the 'Chat' button. Then you can chat with a persona",icon=None)

def full_user_prompt(user_input,selected_persona_details):
    return selected_persona_details['Pre-Prompt']+user_input+selected_persona_details['Post-Prompt']

def remove_prompt_extra_text(user_prompt,selected_persona_details):
    return user_prompt[len(selected_persona_details['Pre-Prompt']):len(user_prompt)-len(selected_persona_details['Post-Prompt'])] #start from end of pre prompt. go to end of post prompt

list_of_session_variables_needed = ['selected_persona_name','selected_persona_details','topic','persona_responses']

def has_chat_variables(list_of_session_variables_needed):
    for i in list_of_session_variables_needed:
        if hasattr(st.session_state, i):
            continue
        else:
            return False
    return True

def chat_variables_found(list_of_session_variables_needed):
    for i in list_of_session_variables_needed:
        if hasattr(st.session_state, i):
            st.info("loaded "+i+": "+str(st.session_state[i]),icon="✅")
        else:
            st.error("missing "+i+": "+str(st.session_state[i]),icon="⚠️")

def typewriter_output(text_to_output):
    split_text = text_to_output.split(" ")

    grouped_split_text = [split_text[0]] #start with first word

    for word in split_text:
        if random.choice([True,False]):
            #if true, group it with previous
            grouped_split_text[len(grouped_split_text)-1] += " "+word
        else:
            #if false, create a new group
            grouped_split_text.append(" "+word)

    for words in grouped_split_text:
        yield words
        time.sleep(0.02)

def main():
    #additional chat features: https://github.com/carolinedlu/llamaindex-chat-with-streamlit-docs/blob/main/streamlit_app.py

    st.title("Chat")
    if has_chat_variables(list_of_session_variables_needed): #the variables in the session state may not be defined yet
        if st.session_state['selected_persona_name'] != "" and st.session_state['selected_persona_details'] != "" and st.session_state['topic'] != "": #there is the needed data to chat
            st.markdown(f"Chatting with *{st.session_state['selected_persona_name']}*")

            #setting up chat history
            if st.session_state['messages'] == []: #only add history if it is empty
                st.session_state['messages'].append({'role': 'system', 'content': st.session_state['selected_persona_details']['System Prompt']}) #persona system
                st.session_state['messages'].append({'role': 'user', 'content': full_user_prompt(st.session_state['topic'],st.session_state['selected_persona_details'])}) #users initial message
                st.session_state['messages'].append({'role': 'assistant', 'content': st.session_state['persona_responses'][st.session_state['selected_persona_details']['Type']]}) #get last message from selected type of persona

            
            
            current_prompt = "" #setup full prompt for access later 
            
            if user_input := st.chat_input("Your question"): # Receive user input and save to chat history
                current_prompt = full_user_prompt(user_input,st.session_state['selected_persona_details']) #surrounding text in persona specific text
                st.session_state['messages'].append({"role": "user", "content": current_prompt})
                st.session_state['use_chat_typewriter_effect'] = True
            
            # If last message is not from assistant, generate a new response
            if st.session_state.messages[-1]["role"] != "assistant":
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state['generate_openai_response'](st.session_state['messages'])
                        message = {"role": "assistant", "content": response}
                        st.session_state.messages.append(message) # Add response to message history

            # Display the prior chat messages with cleanup
            for i in range(0,len(st.session_state['messages'])):
                message = st.session_state['messages'][i]

                with st.chat_message(message["role"]):
                    if(len(message['content'])>0): #has content to output
                        if message["role"] == "assistant":
                            if i == len(st.session_state['messages'])-1 and st.session_state['use_chat_typewriter_effect']: #output last persona message as typewriter
                                st.write_stream(typewriter_output(message["content"])) #returns a stream with delays. Then writes the stream with the typewriter delays
                                st.session_state['use_chat_typewriter_effect'] = False
                            else:
                                st.write(message["content"]) #return full output of assistant
                        elif message["role"] == "system":
                            continue #ignore any system information
                        elif message["role"] == "user":
                            st.write(remove_prompt_extra_text(message["content"],st.session_state['selected_persona_details'])) #cleanup user input

        else:
            chat_requirements_notification() #data in variables did not meet all criteria
            #print out each variable
            #chat_variables_found(list_of_session_variables_needed)
    else:
        #did not have session variables ready   
        chat_requirements_notification()
        #print out each variable
        #chat_variables_found(list_of_session_variables_needed)

if __name__ == '__main__':
    main()