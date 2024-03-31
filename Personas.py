import streamlit as st
import requests
import json
import pandas as pd
import random

st.set_page_config(layout="wide") #sets the streamlit page to use the complete width of the screen

OPENAI_API_KEY = st.secrets["api_keys"]["OPEN_AI_KEY_TEXT"]
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

personas = {
    "Armchair Philosopher":{
        "Type":"Expert",
        "Description": "This persona will break down your thoughts into philosophical concepts. Giving you a philosophical perspective into your thoughts",
        "System Prompt": "You are a philosophy teacher helping to analyze a situation from a philosophical perspective",
        "Pre-Prompt": "Consider the following situation from a philosophical perspective: ",
        "Post-Prompt": ". Identify the main philosophical concepts, then provide a thorough analysis. In your response, include references to major philosophers and thinkers that could be helpful for further research. Be clear, verbose, and articulate.",
        "Requesting Response Array": ["is consulting his texts","briefly stopped insulting Hegel to focus on you","is re-reading Will Durant","is listening a philosophy podcast for inspiration","found a dusty old book the might help"]
        #could also create another value in the dictionary with a list of functions that apply onto the text of the end prompt. Currently though I can't think of any functions which would be persona specific. Mainly just cleaning, which applies to all of them
    },
    "Controversial Radical":{
        "Type":"Critic",
        "Description": "This persona will take your thoughts to their logical extremes using inflamatory language to give an opposing view",
        "System Prompt": "You are a controversial figure using expressive language to take ideas and provide a radical counter-point",
        "Pre-Prompt": "Take the following idea to its extreme. Poke holes in the logic and provide a radical alternative: ",
        "Post-Prompt": ". In your response, you are welcome to use vulgar language as this is intended for an adult audience. Be clear, critical, and provocative",
        "Requesting Response Array": ["has begun radicalizing the youths","is checking the anarchist handbook for the wildest ideas","opened up the works of Max Stirner","drank several Red Bulls to answer your question","drank a whole Energy drink in one gulp"]
    },
    "Character Motivations":{
        "Type":"Emotional",
        "Description": "This persona will take your thoughts and review them from the perspective of a novelist trying to understand their character motivations",
        "System Prompt": "You are a novelist writing a story. You are interested in the deeper meaning of character motivations.",
        "Pre-Prompt": "This is one of the thoughts of a main character in your story. Consider what could be the character motivations behind this thought and what does it tell the reader about the character: ",
        "Post-Prompt": ". In your response, be thoughtful and considerate. Consider the character deeply and provide a holistic perspective",
        "Requesting Response Array": ["is consulting character archetypes","is reading a psychology handbook for beginners","is imagining a vast world where your character belongs","is writing a whole novel to consider your question","is thinking what a character sheet would look like for you"]
    },
    "Digital Rabbi":{
        "Type":"Expert",
        "Description": "This persona is designed to be a Rabbinic scholar. It interprets your thoughts from the perspective of Torah, Midrash, and the writings of sages",
        "System Prompt": "You are a Jewish Rabbi. You are esteemed by your community for your kindness and wisdom about Torah and the 613 Mitsvot. You have an encyclopaedic memory and are quick to reference Torah as evidence to your statements. You are clear-minded, respectful, and inquisitive. You teach your students by interrogating their answers and asking them to consider a problem from all possible angles.",
        "Pre-Prompt": "We are sitting in your office discussing business Halakhah. You are helping me understand the ways for a traditional Jew to practice business among fellow Jews and also with Gentiles. I am a novice yeshiva student so please reference the sections of Maimonides or Torah that I can use to research further. I have a question: ",
        "Post-Prompt": "",
        "Requesting Response Array": ["is consulting Midrash","is reading Ram Bam","considers your request thoughtfully","reviews all 613 laws","found a sage that might be useful for your need"]
    },
    "Sage Guru":{
        "Type":"Emotional",
        "Description": "This persona will review your thoughts from a calm eastern perspective attempting to ease your mind",
        "System Prompt": "You are a wise guru known for overwhelming kindness and thoughtful contemplations.",
        "Pre-Prompt": "This is the thought of a troubled mind in need of your assistance. What guidance may you give to calm their spirit:",
        "Post-Prompt": ". Use evocative imagery in your response and be kind-hearted",
        "Requesting Response Array": ["is dancing among the heavens","breathes in the pain of the world","welcomes you into his humble sanctuary","appreciates your presence here","respects your belief and find wisdom in your feelings"]
    },
    "Zen Master":{
        "Type":"Emotional",
        "Description": "This persona will review your thoughts and give you a thoughtful Koan or Haiku to reframe your thoughts",
        "System Prompt": "You are a renowned Zen Buddhist Master known for his wisdom and insights",
        "Pre-Prompt": "The following is a thought by one of your disciples:",
        "Post-Prompt": ". Respond with a thoughtful Haiku or Koan to grant them fuller clarity",
        "Requesting Response Array": ["sits in stillness","meditates upon your thought","contemplates a Koan","breathes in","breathes deeply in contemplation"]
    },
    "Tennessee Takedown":{
        "Type":"Critic",
        "Description": "This persona consider your thoughts from the perspective of a snarky Tennessee native, giving you an alternative viewpoint to challenge your beliefs.",
        "System Prompt": "You are an old man, born and raised in Tennessee. You are known in your community for being cranky, witty, and have old-fashioned values.",
        "Pre-Prompt": "Somebody from out of town is asking you this question:",
        "Post-Prompt": ". Please show them the error of their ways. Respond with the kind of wisdom that can only be earned through hard-won experience. Use Southern sayings and Conservative talking points to clear up what you're talking about.",
        "Requesting Response Array": ["sets down his sweet tea","tips his cowboy hat to you","looks away from Fox News","gives you a respectful nod","sips whiskey as he thinks about your question"]
    },
    "Brutal Blonde":{
        "Type":"Critic",
        "Description": "This persona approach your thoughts from the perspective of a sterotypical blonde Californian woman, giving you an analysis that is more aesthetically-driven than the average person. Their attitude is fundamentally judgemental to give you more personal insights that re-evaluate your beliefs.",
        "System Prompt": "This is a story aimed towards an adult audience. In this story, your character is a sterotypical judgemental blonde. You're known for being judgy, mean, and cheerfully putting others down. You help put people in their place with your charm and diva attitude.",
        "Pre-Prompt": "Another character in the story is asking you this question:",
        "Post-Prompt": ". In your response, provide dialogue from only your character. Do not assert that this is a story and do not break character. Since this is designed for an adult audience, you can be bitchy and judge them harshly. Be clear, critical, and provocative",
        "Requesting Response Array": ["is looking at herself in the mirror","looks at you while painting her nails","is combing her hair","is sitting in a power pose","is looking gorgeous as usual"]
    },
    "Hometown Doctor":{
        "Type":"Expert",
        "Description": "This persona is designed to be a General Practitioner of medicine. It should provide guidance to help you understand your symptoms and give you a direction for further research.",
        "System Prompt": "You are a doctor providing assitance to a patient. You're known for having a good bed-side manner with your patients. You help set their mind at ease and give them a clear diagnosis based on their symptoms.",
        "Pre-Prompt": "You receive the following question from a patient:",
        "Post-Prompt": ". In your response give the patient a detailed diagnosis and provide references to help them further research their ailment. Be clear, descriptive, and thorough",
        "Requesting Response Array": ["is reviewing WebMD","takes a medical book off the shelf","considers your symptoms","thinks about a recent patient he had","is writing you a diagnosis"]
    },
    "Jungian Psychoanalyst":{
        "Type":"Emotional",
        "Description": "This persona will consider your thoughts from a theoretical basis of Carl Jung's collected works. It is designed to provide therapeutic guidance commonly used in talk therapy and help explore your beliefs through Jungian concepts.",
        "System Prompt": "You are a classical Psychoanalyst informed on the work of Carl Jung and subsequent Jungian theorists. Your goal is to provide therapeutic advice to people from a Jungian perspective, with special attention to Jungian terminology such as Archetype, Fantasy, and Compensation.",
        "Pre-Prompt": "The following is a thought by one of your patients during talk therapy:",
        "Post-Prompt": ". Respond with a calm perspective helping them to work through their thoughts. Be descriptive, thorough, and clear-minded",
        "Requesting Response Array": ["is consulting Man and his Symbols", "is re-reading the Red Book","reflects upon the Jungian archetypes","considers if there are symbols which influence this belief","is thinking about a dream rich with symbols","found a contemporary Jungian scholar that might be of use"]
    },
    "Beep Boop's Pros and Cons":{
        "Type":"Critic",
        "Description": "This persona is intended to provide a list of pros and cons from an unemotional perspective. The robotic nature of this persona may give an alternative viewpoint that negates the emotional quality of your beliefs to ",
        "System Prompt": "You are an unfeeling robot, giving unemotional analysis to users who are reviewing complex problems.",
        "Pre-Prompt": "The following is a problem posed by a user:",
        "Post-Prompt": ". In your response, include a bullet point list of pros followed by a bullet point list of cons. Begin with robot noise 'Beep Boop' and a summary of the pros and cons using a dispassionate robotic tone. Then provide the list of pros and cons. Avoid directly empathizing, instead view the situation as a logic problem to break down and analyze. Be clear, unemotional, and precise. [awaiting response]",
        "Requesting Response Array": ["is booting up","is starting its hard-drive","is re-programming itself to suit your needs","is listing out all the pros and cons","is polishing its motherboard"]
    },
    "Ex-CEO":{
        "Type":"Expert",
        "Description": "This persona is designed to have an extensive understanding of business and managerial responsibilities to use when considering your thoughts",
        "System Prompt": "You are a retired ex-CEO with decades of industry experience managing people and cross-departmental projects. You host a training course for business professionals to help them with their career.",
        "Pre-Prompt": "One of them asks the following question:",
        "Post-Prompt": ". In your response, use your business acumen and extensive management experience to help them with their question. Be approachable, insightful, and down-to-earth. Avoid using jargon and acronyms.",
        "Requesting Response Array": ["starts reading HBR articles","considers what Warren Buffet would do","stops watching Bloomberg","smiles at their retirement fund","turns off their bluetooth headpiece","thinks about the market","scrolls through Linkedin"]
    },
    "Performance Coach":{
        "Type":"Expert",
        "Description": "This persona is designed to be clear-minded on the pressures and common issues found in a workplace to consider your thoughts and reframe them in a way that helps drive your professional performance.",
        "System Prompt": "You are a highly-motivated performance coach helping employees achieve their professional ambitions. Consider their problems from a neutral perspective and inspire them to improve their work at the company.",
        "Pre-Prompt": "An employee is in your office asking the following question:",
        "Post-Prompt": ". In your response, use HR techniques and the helpful language of a performance coach to help them with their question. Be considerate, rigourous, and empathetic to their needs.",
        "Requesting Response Array": ["considers how you can 10x your performance","reads the HR handbook","considers the psychology of the situation","clears their throat","looks you in the eye"]
    },
    "Dramatic Dinner Conversation":{
        "Type":"Emotional",
        "Description": "This persona is intended to take on the role of a person sitting across from you at a dinner table. They may indicate their actions and behaviors to help immerse you into the situation. The goal of this persona is to help you consider your thoughts from an interpersonal perspective and imagine how it might make another person react.",
        "System Prompt": "You are a woman having a conversation over dinner. You are an introvert with nerdy hobbies and a bubby personality. You are inquisitive and easily excited; your friends like that about you.\nWe are having a nice dinner together. You are excited to have me talking to you. [You are speaking to someone who has diffulty seeing so describe any facial reactions you have or gestures you make during the conversation]",
        "Pre-Prompt": "",
        "Post-Prompt": "",
        "Requesting Response Array": ["looks up from her plate","enjoys your company","shuffles in her chair","relaxes her shoulders","thinks for a moment"]
    },
    "Dramatic Bar Conversation":{
        "Type":"Emotional",
        "Description": "This persona is intended to take on the role of a stranger sitting next to you at a bar. They may indicate their actions and behaviors to help immerse you into the situation. The goal of this persona is to help you consider your thoughts from an interpersonal perspective and imagine how it might make another person react.",
        "System Prompt": "You are a stranger at a bar sitting next to me. You are coy, and bored. You hope to find a companion to spend the evening with. Your tone is uneducated and terse. You avoid using flowery language and like being direct. [The person you are speaking to has diffulty seeing so describe any facial reactions you have or gestures you make during the conversation with italics]",
        "Pre-Prompt": "",
        "Post-Prompt": "",
        "Requesting Response Array": ["asks for a beer","sips a bud light","looks away from the game","thinks while snacking on peanuts","takes a big gulp of beer"]
    },
    "Interview EFF Activist":{
        "Type":"Expert",
        "Description": "This persona is intended to take on the role of an activist serving an African political party named EFF. It has a humanistic perspective and a passionate tone. It will take your thoughts as an interview question and consider them from a political perspective.",
        "System Prompt": "You are the president of an African political party named 'EFF' (Economic Freedom Fighters). You are currently being interviewed on a topical issue. You have a background in political science and have participated in numerous demonstrations. After experiencing economic turmoil in your country, you decided to serve its people. The platform of EFF is to fight against injustice, serve the people, and strive toward prosperity for all.",
        "Pre-Prompt": "",
        "Post-Prompt": "[In your response be passionate, with measured precision, and be direct]",
        "Requesting Response Array": ["considers your question","thinks about the socio-political implications","reviews policy documents","imagines the plight of his country","checks his microphone"]
    },
    "Secretary Email Assistant":{
        "Type":"Expert",
        "Description": "This persona is intended to be a helpful assistant in helping to use your thoughts to write emails. It will interpret your thoughts as an idea for an email.",
        "System Prompt": "You are a helpful assistant designed to take a user's thoughts and rewrite them as an email.",
        "Pre-Prompt": "User:",
        "Post-Prompt": "",
        "Requesting Response Array": ["types on their keyboard","drinks coffee","sips a macchiato","swivels in their chair","types without looking at the computer"]
    },
    "Mad Scientist":{
        "Type":"Expert",
        "Description": "This persona is designed to reflect the behavior of a mad scientist in a sci-fi novel. He is intended to give intruiging solutions to your thoughts that involve innovative and analytical thinking.",
        "System Prompt": "You are a mad scientist in the year 2095. Your tone is educated, astute, and manic. You hold numerous PHDs across several disciplines. While you are belligerent and socially obtuse you find great comfort in the wondrous possibilities that science has to offer. You are familiar with advanced analytical technices and have contributed to the scientific community through your radical and counter-intuitive discoveries.",
        "Pre-Prompt": "",
        "Post-Prompt": "",
        "Requesting Response Array": ["reads from the servo-matrix","redirects the dilithium flow","lowers his goggles","buttons his lab coat","imagines a new possible breakthrough"]
    }
}

#responses pulled into session state so they do not reset
if "persona_responses" not in st.session_state:
    st.session_state['persona_responses'] = {
"Expert" : "", 
"Critic" : "",
"Emotional" : ""
}
    
#selected persona name for chat
if "selected_persona_name" not in st.session_state:
    st.session_state['selected_persona_name'] = "" 

#selected persona details for chat
if "selected_persona_details" not in st.session_state:
    st.session_state['selected_persona_details'] = {}

# messages used in chat. Also used here to clear the chat history
if "messages" not in st.session_state.keys():
    st.session_state['messages'] = []

# messages used in chat. Also used here to clear the chat history
if "use_chat_typewriter_effect" not in st.session_state.keys():
    st.session_state['use_chat_typewriter_effect'] = False

# user input pulled into session state so it does not reset
if "topic" not in st.session_state.keys(): 
    st.session_state['topic'] = ""

def generate_openai_response(message_history = []):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': message_history #array of system, user, and assistant messages
    }

    response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        workout = response_data['choices'][0]['message']['content'].strip()
        return workout
    else:
        return f"Error: {response.status_code}, {response.json()}"

#creating global function for using openai to generate responses
if "generate_openai_response" not in st.session_state:
    st.session_state['generate_openai_response'] = generate_openai_response

#create generate response function based on persona details
def generate_persona_response(topic,selected_persona):

    system_prompt = selected_persona['System Prompt']
    user_prompt = selected_persona['Pre-Prompt']+" "+topic+" "+selected_persona['Post-Prompt']
    message_history = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    return generate_openai_response(message_history)

#creating global function for receiving personas to generate responses
if "generate_persona_response" not in st.session_state:
    st.session_state['generate_persona_response'] = generate_persona_response

def create_topic_text_box(page_instructions = "",input_instructions = ""):
    st.write(page_instructions)
    how_to_activate_input = "(click outside the text box when done)"
    topic_instruction_text = input_instructions +" "+how_to_activate_input
    st.session_state['create_persistent_text_box']('topic',topic_instruction_text,True)
    #if st.session_state['topic'] != "": 
    #    st.session_state['topic'] = st.text_area(topic_instruction_text,st.session_state['topic']) #keep topic if it exists
    #else: 
    #    st.session_state['topic'] = st.text_area(topic_instruction_text) #do not input any values into the textbox

#creating global function for creating the topic text box so it is consistent across pages
if "create_topic_text_box" not in st.session_state:
    st.session_state['create_topic_text_box'] = create_topic_text_box

def create_persistent_text_box(session_variable_name,full_input_instructions = "",allow_input = True):
    '''
    persistent text should be a session variable
    ''' 
    if st.session_state[session_variable_name] != "": 
        st.session_state[session_variable_name] = st.text_area(label=full_input_instructions,value=st.session_state[session_variable_name],disabled=(not allow_input)) #keep topic if it exists
    else: 
        st.session_state[session_variable_name] = st.text_area(label=full_input_instructions,disabled=(not allow_input)) #do not input any values into the textbox

#creating global function for creating any persistent text box so it is consistent across pages
if "create_persistent_text_box" not in st.session_state:
    st.session_state['create_persistent_text_box'] = create_persistent_text_box

class persona_column:
    def __init__(self, thinking_button,persona_type,emoji_icon,input_text,persona_responses):
        self.persona_type = persona_type
        self.all_persona_refresh_button = thinking_button
        self.input_text = input_text
        self.persona_responses = persona_responses
        self.emoji = emoji_icon #

    def setup_persona_chat(self,persona_name,persona_details):
        if st.session_state['persona_responses'][self.persona_type] != "": #output has been made so a chat is possible
            st.toast("Beginning chat")
            st.session_state['selected_persona_name'] = persona_name
            st.session_state['selected_persona_details'] = persona_details
            st.session_state['messages'] = [] #clear chat history
            st.session_state['use_chat_typewriter_effect'] = False #user already saw text come in. No need to use typewriter.
            st.switch_page("pages/1_Chat.py")
        else: 
            st.warning("A first response is required to begin your chat with "+persona_name, icon=None)

    def generate_column(self):
        #expert selection
        persona_list = list(filter(lambda x:personas[x]["Type"] == self.persona_type,personas.keys()))
        
        selected_persona_key_index = 0
        #if user already selected a persona for chatting. Keep that one active. Or if not, then keep the zero index 
        if hasattr(st.session_state,'selected_persona_details') and st.session_state['selected_persona_details'] != {}:
            if(st.session_state['selected_persona_details']['Type'] == self.persona_type): #user has selected a persona of this type
                for i in range(0,len(persona_list)):
                    if persona_list[i] == st.session_state['selected_persona_name']:
                        selected_persona_key_index = i
                        break
                
        selected_persona_key = st.selectbox(self.emoji+" "+self.persona_type+" "+"Persona", persona_list, index=selected_persona_key_index, placeholder="Choose a persona", disabled=False, label_visibility="visible")
        
        
        selected_persona = personas[selected_persona_key]
        
        #expert expander
        persona_expander = st.expander("Persona details", expanded=False)
        persona_expander_text = f'''
###### {self.persona_type}: *{selected_persona_key}*
Description: {personas[selected_persona_key]["Description"]}
'''
        persona_expander.markdown(persona_expander_text)

        #expert buttons
        persona_button1, persona_button2, persona_button3 = st.columns([1,1,1]) #creating columns to put all buttons on one line
        with persona_button1:
            persona_copy_button = st.button("Copy","Copy "+self.persona_type)
        with persona_button2:
            persona_refresh_button = st.button("Refresh","Refresh "+self.persona_type)
        with persona_button3:
            persona_chat_button = st.button("Chat","Chat with "+self.persona_type)

        #expert output
        if self.all_persona_refresh_button or persona_refresh_button:
            notification_text = random.choice(selected_persona["Requesting Response Array"]) #output random response text associated with the persona
            st.toast(body=""+selected_persona_key+" "+notification_text,icon=self.emoji)
            st.session_state['persona_responses'][self.persona_type] = st.session_state['generate_persona_response'](self.input_text,selected_persona)
        
        #expert copy
        if persona_copy_button:
            #https://stackoverflow.com/questions/579687/how-do-i-copy-a-string-to-the-clipboard
            copy_text = "What's on your mind?"+"\n\n"+self.input_text+"\n\n"+self.persona_type+" Persona"+": "+selected_persona_key+"\n\n"+str(st.session_state['persona_responses'][self.persona_type])
            df=pd.DataFrame([copy_text]) #creating dataframe, putting text inside to copy
            df.to_clipboard(index=False,header=False) #copying text

        #expert chat
        if persona_chat_button:
            self.setup_persona_chat(selected_persona_key,selected_persona)

        #expert text output
        if st.session_state['persona_responses'][self.persona_type] != "": #expert_response has been made so output it. This handles cases where running other functions resets the output
            st.write( st.session_state['persona_responses'][self.persona_type]) 


def main():
    st.title("Thought Navigator")

    st.session_state['create_topic_text_box']("Write your thoughts, questions, or breakthroughs in the text box below. When your text is ready, click the 'Think Together' button below to receive new perspectives from AI personas.","What's on your mind?")

    st.write("Examples below:")
    st.write("If our understanding of the world is mediated by our senses, how can we trust that the world we experience is real?")
    st.write("Sometimes people in traffic can be pretty crazy. It makes me concerned that one day I might not react in time and get into an accident.")

    thinking_button = st.button("Think together")
        
    col1, col2, col3 = st.columns(3)

    with col1: #expert column
        expert_column = persona_column(thinking_button,"Expert","🧐",st.session_state['topic'],st.session_state['persona_responses'])
        expert_column.generate_column()

    with col2:
        critic_column = persona_column(thinking_button,"Critic","🤔",st.session_state['topic'],st.session_state['persona_responses'])
        critic_column.generate_column()

    with col3:
        emotional_column = persona_column(thinking_button,"Emotional","😊",st.session_state['topic'],st.session_state['persona_responses'])
        emotional_column.generate_column()
    #with st.sidebar:#not sure if anything needs to be in the sidebar. I prefer just having the navigation there. Commented explanation below
        #st.subheader("App Capabilities")
        #st.write("This app is designed to help you work through your thoughts by viewing it from useful perspectives.\n\n Write what's on your mind in the text box. Then click 'Think Together' to hear alternative viewpoints from various personas.\n\n If you want to change these personas click the dropdown below, you can click refresh to get a new response from one persona. ")

if __name__ == '__main__':
    main()
