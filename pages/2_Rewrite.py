import streamlit as st
import requests
import json
import pandas as pd
import random
import time

st.set_page_config(layout="wide") #sets the streamlit page to use the complete width of the screen

OPENAI_API_KEY = st.secrets["api_keys"]["OPEN_AI_KEY_TEXT"]
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

style_personas = { #these personas are designed to have a single output of rewriting text in a new way. Not intended to reflect any person's perspective
    "Viral Tweet":{
        "Style":"Social Media",
        "Description": "Write as a viral tweet",
        "System Prompt": "Rewrite the user's text as a viral tweet. Use brief, evocative language, that would attract attention. Use relevant hashtags in the tweet",
        "Pre-Prompt": "",
        "Post-Prompt": "",
        },
    "Professional Email":{
        "Style":"Email",
        "Description": "Write as a professional email",
        "System Prompt": "Rewrite the following text as a strongly worded email. In the email be professional, courteous, and assertive",
        "Pre-Prompt": "",
        "Post-Prompt": "",
        },
    "Friendly Email":{
        "Style":"Email",
        "Description": "Write as a friendly email.",
        "System Prompt": "Rewrite the following text as an email. Avoiding using any common professional phrases",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Enthusiastic Tone":{
        "Style":"Tone",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text using an upbeat, positive, enthusiastic tone",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Haiku":{
        "Style":"Poetry",
        "Description": "Rewrite the text as a Haiku.",
        "System Prompt": "Rewrite the following text a Haiku",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    }
}

# user's rewritten output pulled into session state so it does not reset
if "rewritten_output" not in st.session_state.keys(): 
    st.session_state['rewritten_output'] = ""

#checkboxes and selection pulled into session state so they do not reset
if "selected_styles" not in st.session_state:
    st.session_state['selected_styles'] = {}

def checked_box(box_number):
    st.toast(f"Box Number: {box_number}")
    st.toast("Pre Styles")
    st.toast( st.session_state['style_checkboxes'] )
    st.session_state['style_checkboxes'][box_number] = not st.session_state['style_checkboxes'][box_number]
    st.toast("Post Styles")
    st.toast( st.session_state['style_checkboxes'] )

def test_input(input):
    st.toast(input)

def main():
        st.title("Rewrite Text")
        st.session_state['create_topic_text_box']("Write your thoughts, questions, or breakthroughs in the text box below. When your text is ready, click the buttons below to have the AI rewrite your text in a new style","What text would you like to rewrite?")

        #Create output text box
        st.session_state['create_persistent_text_box']('rewritten_output',"Rewritten Output",False)

        #Container for both columns 
        with st.container(height=300,border=True):
            col1, col2 = st.columns(spec = 2, gap="small")
            with col1:
                st.header("Select Rewriting Styles")
            
                list_of_styles = []
                for style_dict in style_personas.keys():
                    list_of_styles.append(style_personas[style_dict]['Style'])

                #make it unique by using a set
                list_of_styles = list(set(list_of_styles)) 

                #sort list alphabetically
                list_of_styles.sort()

                for i in range(0,len(list_of_styles)):
                    if len(st.session_state['selected_styles'].keys()) != len(list_of_styles): #initializing the list of styles to be false
                        st.session_state['selected_styles'][list_of_styles[i]] = False
                    
                    style_checked = st.checkbox(label=list_of_styles[i],value=st.session_state['selected_styles'][list_of_styles[i]],key="STYLE|"+list_of_styles[i],on_change= lambda:test_input(f"STYLE|{list_of_styles[i]}")) #making it unique by adding 'STYLE|' to prevent any duplicate ID checkboxes on the site
                    if style_checked:
                        st.session_state['selected_styles'][list_of_styles[i]] = True
                    else:
                        st.session_state['selected_styles'][list_of_styles[i]] = False
            with col2:
                st.header("Activate Rewriting Action")
                list_of_actions = []
                #get actions which are in user's selection of checkboxes 
                #selected_styles = list(filter(lambda checkbox:True == True,st.session_state['style_checkboxes']))
               # st.toast(selected_styles)
                #list_of_actions = list(filter(lambda key_value:style_personas[key_value]['Style'] in selected_styles,style_personas.keys())) #Return keys with the selected style
                
                #sort list alphabetically
                #list_of_actions.sort()

                #for action_text in list_of_actions:
                #    st.button(label=action_text,key="REWRITE|"+action_text,) #making it unique by adding 'REWRITE|' to prevent any duplicate ID buttons on the site



if __name__ == '__main__':
    #try:
    main()
    #except Exception as e: 
    #    st.warning("Go to Personas page before navigating directly to this page",icon=None) #needs functions from Personas page to be added to session. Avoids writing duplicate code (would be convenient if they allowed a block of code to run when the website was accessed)
    #    st.error(e)