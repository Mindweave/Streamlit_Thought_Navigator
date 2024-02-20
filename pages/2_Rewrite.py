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
    "Heads-up Email":{
        "Style":"Email",
        "Description": "Write as a brief email.",
        "System Prompt": "Rewrite the following text as an email. Be brief and light. This email is intended to be a heads up notifying another person",
        "Pre-Prompt": "",
        "Post-Prompt": ""
        },
    "Call to Action Email":{
        "Style":"Email",
        "Description": "Write as a brief email.",
        "System Prompt": "Rewrite the following text as a call-to-action email. Be motivating and persuasive in your response",
        "Pre-Prompt": "",
        "Post-Prompt": ""
        },
    "Apologetic Email":{
        "Style":"Email",
        "Description": "Write as an email with an apologetic tone.",
        "System Prompt": "Rewrite the following text as an apologetic email. Be sincere and empathetic in your response",
        "Pre-Prompt": "",
        "Post-Prompt": ""
        },
    "Jargon-Heavy Email":{
        "Style":"Email",
        "Description": "Write as an email with lots of Jargon.",
        "System Prompt": "Rewrite the following text as a rigorous email. Be thorough, competent, and use jargon whenever possible",
        "Pre-Prompt": "",
        "Post-Prompt": ""
        },
    "Enthusiastic Tone":{
        "Style":"More Excited",
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
    },
    "Funny Limmerick":{
        "Style":"Poetry",
        "Description": "Rewrite the text as a Haiku.",
        "System Prompt": "Rewrite the following text a Dirty Limmerick. [This poem is intended for adult audiences so you are welcome to use crude and vulgar language]",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Take-Action Attitude":{
        "Style":"More Excited",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text using an with a can-do attitude. Use language that is easily excitable and highly-motivated",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Uncompromising":{
        "Style":"Less Agreeable",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text using an with a no-nonsense attitude. Use language that is uncompromising and unwavering",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Impersonal Attitude":{
        "Style":"Less Agreeable",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text using an with a firm tone. Use language that is terse, blunt, and impersonal",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Blunt but Fair":{
        "Style":"Less Agreeable",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text with a detailed explanation that elaborates on the ideas. Use language that is fair and balanced",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Commanding Presence":{
        "Style":"Less Agreeable",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text with a commanding tone. Use language that is authoritative, firm, and assured.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Authoritative Expert":{
        "Style":"Less Agreeable",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text with authoritative expert language. Use language that expresses expertise, knowledge, and competence.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Bigger Ego":{
        "Style":"Less Agreeable",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text using insensitive language. Use language that expresses a brash, self-centered viewpoint.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Helpful attitude":{
        "Style":"More Excited",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text expressing helpful intentions. Use language that is engaged, generous, and ready to help",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Emoji Texter":{
        "Style":"Text Message",
        "Description": "Rewrite the text with a new tone.",
        "System Prompt": "Rewrite the following text as a text message. Add emojis into the text as well",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Step by Step Instructions":{
        "Style":"Instructions",
        "Description": "Rewrite the text as a set of instructions.",
        "System Prompt": "Rewrite the following text as a set of step-by-step instruction. This is intended for beginners. Use language that is clear, emphasizes any complex points, and is above all helpful",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Mission Statement":{
        "Style":"Instructions",
        "Description": "Rewrite the text as a set of instructions.",
        "System Prompt": "Rewrite the following text as a mission statement. This is intended to help guide strategic thinkers. Use language that is informative, motivational, and holistic",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Expanded Instructions":{
        "Style":"Instructions",
        "Description": "Rewrite the text as a set of instructions.",
        "System Prompt": "Rewrite the following text as a guide. Expand on the steps and comment on any common mistakes or misconceptions to help the reader better plan using this guide.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Key Points":{
        "Style":"Summarization",
        "Description": "Rewrite the text as a set of key points.",
        "System Prompt": "Summarize the key points of the following text into a list. Use language that is concise and informative.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Added Concluding Statement":{
        "Style":"Summarization",
        "Description": "Rewrite the text as a conclusion.",
        "System Prompt": "Write a concluding statement for the following text. Imitate the language used in the original text",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Added Concluding Paragraph":{
        "Style":"Summarization",
        "Description": "Rewrite the text as a conclusion.",
        "System Prompt": "Write a concluding paragraph for the following text. Imitate the language used in the original text",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Added Introductory Paragraph":{
        "Style":"Summarization",
        "Description": "Rewrite the text as a conclusion.",
        "System Prompt": "Write an introductory paragraph for the following text. Imitate the language used in the original text",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Added Introductory Sentence":{
        "Style":"Summarization",
        "Description": "Rewrite the text as a conclusion.",
        "System Prompt": "Write a sentence introducing the following text. Imitate the language used in the original text",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Suave":{
        "Style":"More Charming",
        "Description": "Rewrite the text as charming.",
        "System Prompt": "Rewrite the text using a suave and charming tone. Use language that is alluring and piques interest.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Welcoming Tone":{
        "Style":"More Charming",
        "Description": "Rewrite the text as charming.",
        "System Prompt": "Rewrite the text using a welcoming tone. Use language that is graceful, socially aware, and considerate.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "50s Graceful Socialite":{
        "Style":"More Charming",
        "Description": "Rewrite the text as charming.",
        "System Prompt": "Rewrite the text using a graceful 50s tone. Use the kind of language reminiscient of the Hepburn and the Mid-Atlantic accent.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Kindhearted":{
        "Style":"More Empathetic",
        "Description": "Rewrite the text as being more empathetic.",
        "System Prompt": "Rewrite the text using a kindhearted tone using language that is empathetic and warm.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Sympathetic":{
        "Style":"More Empathetic",
        "Description": "Rewrite the text as being more empathetic.",
        "System Prompt": "Rewrite the text using a sympathetic tone. Use language that expresses kindness and sincerity.",
        "Pre-Prompt": "",
        "Post-Prompt": ""
    },
    "Compassionate":{
        "Style":"More Empathetic",
        "Description": "Rewrite the text as being more empathetic.",
        "System Prompt": "Rewrite the text using a compassionate tone. Use language that expresses honesty, empathy, and care.",
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

def activate_style(input):
    st.toast("Rewriting: "+input)
    st.session_state['rewritten_output'] = st.session_state['generate_persona_response'](st.session_state['topic'],style_personas[input])

def switch_input_and_output_text():
    input_text = st.session_state['topic']
    output_text = st.session_state['rewritten_output']
    st.session_state['topic'] = output_text
    st.session_state['rewritten_output'] = input_text


def main():
        st.title("Rewrite Text")
        st.session_state['create_topic_text_box']("Write your thoughts, questions, or breakthroughs in the text box below. When your text is ready, click the buttons below to have the AI rewrite your text in a new style","What text would you like to rewrite?")

        #Switch text button
        st.button(label="🔀 Switch Text",key="Switch Text",on_click=switch_input_and_output_text)

        #Create output text box
        st.session_state['create_persistent_text_box']('rewritten_output',"Rewritten Output",False)

        #Container for both columns 
        col1, col2 = st.columns(spec = 2, gap="small")
        with col1:
            st.header("Select Rewriting Styles")
            with st.container(height=290,border=True):
            
                list_of_styles = []
                for style_dict in style_personas.keys():
                    list_of_styles.append(style_personas[style_dict]['Style'])

                #make it unique by using a set
                list_of_styles = list(set(list_of_styles)) 

                #sort list alphabetically
                list_of_styles.sort()

                for i in range(0,len(list_of_styles)):
                    if len(st.session_state['selected_styles'].keys()) != len(list_of_styles): #initializing the list of styles checkboxes state
                        if i == 0: #set first one to be True by default so there are buttons
                            st.session_state['selected_styles'][list_of_styles[i]] = True
                        else: 
                            st.session_state['selected_styles'][list_of_styles[i]] = False
                    
                    style_checked = st.checkbox(label=list_of_styles[i],value=st.session_state['selected_styles'][list_of_styles[i]],key="STYLE|"+list_of_styles[i]) #making it unique by adding 'STYLE|' to prevent any duplicate ID checkboxes on the site
                    if style_checked:
                        st.session_state['selected_styles'][list_of_styles[i]] = True
                    else:
                        st.session_state['selected_styles'][list_of_styles[i]] = False
        with col2:
            st.header("Activate Rewriting Action")
            with st.container(height=290,border=True):
                list_of_actions = []
                #get actions which are in user's selection of checkboxes 
                selected_styles = list(filter(lambda checkbox_name:st.session_state['selected_styles'][checkbox_name] == True,st.session_state['selected_styles'].keys()))
                list_of_actions = list(filter(lambda key_value:style_personas[key_value]['Style'] in selected_styles,style_personas.keys())) #Return keys with the selected style
                
                #sort list alphabetically
                list_of_actions.sort()

                for action_text in list_of_actions:
                    st.button(label=action_text,key="REWRITE|"+action_text,on_click=activate_style,args=[action_text]) #making it unique by adding 'REWRITE|' to prevent any duplicate ID buttons on the site
                        #st.toast("Rewriting: "+action_text)
                        #st.session_state['rewritten_output'] = st.session_state['generate_persona_response'](st.session_state['topic'],style_personas[action_text])
                    


if __name__ == '__main__':
    try:
        main()
    except Exception as e: 
        st.warning("Go to Personas page before navigating directly to this page",icon=None) #needs functions from Personas page to be added to session. Avoids writing duplicate code (would be convenient if they allowed a block of code to run when the website was accessed)
    #    st.error(e) #hiding since users do not need to see errors. May want to uncomment the whole try catch if there is an actual error requiring manual review