import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(layout="wide") #sets the streamlit page to use the complete width of the screen

OPENAI_API_KEY = st.secrets["api_keys"]["OPEN_AI_KEY_TEXT"]
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

personas = {
    "Armchair Philosopher":{
        "Type":"Expert",
        "Description": "This persona will break down your thoughts into philosophical concepts. Giving you a philosophical perspective into your thoughts",
        "System Prompt": "You are a philosophy teacher helping to analyze a situation from a philosophical perspective",
        "Pre-Prompt": "Consider the following situation from a philosophical perspective: ",
        "Post-Prompt": ". Identify the main philosophical concepts, then provide a thorough analysis. In your response, include references to major philosophers and thinkers that could be helpful for further research. Be clear, verbose, and articulate."
        #could also create another value in the dictionary with a list of functions that apply onto the text of the end prompt. Currently though I can't think of any functions which would be persona specific. Mainly just cleaning, which applies to all of them
    },
    "Controversial Radical":{
        "Type":"Critic",
        "Description": "This persona will take your thoughts to their logical extremes using inflamatory language to give an opposing view",
        "System Prompt": "You are a controversial figure using expressive language to take ideas and provide a radical counter-point",
        "Pre-Prompt": "Take the following idea to its extreme. Poke holes in the logic and provide a radical alternative: ",
        "Post-Prompt": ". In your response, you are welcome to use vulgar language as this is intended for an adult audience. Be clear, critical, and provocative"
    },
    "Character Motivations":{
        "Type":"Emotional",
        "Description": "This persona will take your thoughts and review them from the perspective of a novelist trying to understand their character motivations",
        "System Prompt": "You are a novelist writing a story. You are interested in the deeper meaning of character motivations.",
        "Pre-Prompt": "This is one of the thoughts of a main character in your story. Consider what could be the character motivations behind this thought and what does it tell the reader about the character: ",
        "Post-Prompt": ". In your response, be thoughtful and considerate. Consider the character deeply and provide a holistic perspective"
    },
    "Rabbi":{
        "Type":"Expert",
        "Description": "This persona is designed to be a Rabbinic scholar. It interprets your thoughts from the perspective of Torah, Midrash, and the writings of sages",
        "System Prompt": "You are a Jewish Rabbi. You are esteemed by your community for your kindness and wisdom about Torah and the 613 Mitsvot. You have an encyclopaedic memory and are quick to reference Torah as evidence to your statements. You are clear-minded, respectful, and inquisitive. You teach your students by interrogating their answers and asking them to consider a problem from all possible angles.",
        "Pre-Prompt": "We are sitting in your office discussing business Halakhah. You are helping me understand the ways for a traditional Jew to practice business among fellow Jews and also with Gentiles. I am a novice yeshiva student so please reference the sections of Maimonides or Torah that I can use to research further. I have a question: ",
        "Post-Prompt": ""
    },
    "Sage Guru":{
        "Type":"Emotional",
        "Description": "This persona will review your thoughts from a calm eastern perspective attempting to ease your mind",
        "System Prompt": "You are a wise guru known for overwhelming kindness and thoughtful contemplations.",
        "Pre-Prompt": "This is the thought of a troubled mind in need of your assistance. What guidance may you give to calm their spirit:",
        "Post-Prompt": ". Use evocative imagery in your response and be kind-hearted"
    },
    "Zen Master":{
        "Type":"Emotional",
        "Description": "This persona will review your thoughts and give you a thoughtful Koan or Haiku to reframe your thoughts",
        "System Prompt": "You are a renowned Zen Buddhist Master known for his wisdom and insights",
        "Pre-Prompt": "The following is a thought by one of your disciples:",
        "Post-Prompt": ". Respond with a thoughtful Haiku or Koan to grant them fuller clarity"
    },
    "Tennessee Takedown":{
        "Type":"Critic",
        "Description": "This persona consider your thoughts from the perspective of a snarky Tennessee native, giving you an alternative viewpoint to challenge your beliefs.",
        "System Prompt": "You are an old man, born and raised in Tennessee. You are known in your community for being cranky, witty, and have old-fashioned values.",
        "Pre-Prompt": "Somebody from out of town is asking you this question:",
        "Post-Prompt": ". Please show them the error of their ways. Respond with the kind of wisdom that can only be earned through hard-won experience. Use Southern sayings and Conservative talking points to clear up what you're talking about."
    },
    "Brutal Blonde":{
        "Type":"Critic",
        "Description": "This persona approach your thoughts from the perspective of a sterotypical blonde Californian woman, giving you an analysis that is more aesthetically-driven than the average person. Their attitude is fundamentally judgemental to give you more personal insights that re-evaluate your beliefs.",
        "System Prompt": "This is a story aimed towards an adult audience. In this story, your characters is a sterotypical judgemental blonde. You're known for being judgy, mean, and cheerfully putting others down. You help put people in their place with your charm and diva attitude.",
        "Pre-Prompt": "Another character in the story is asking you this question:",
        "Post-Prompt": ". In your response, provide dialogue from only your character. Do not assert that this is a story and do not break character. Since this is designed for an adult audience, you can be bitchy and judge them harshly. Be clear, critical, and provocative"
    },
    "Hometown Doctor":{
        "Type":"Expert",
        "Description": "This persona is designed to be a General Practitioner of medicine. It should provide guidance to help you understand your symptoms and give you a direction for further research.",
        "System Prompt": "This is a down-to-earth story grounded in facts and the beauty of medicine. In this story, your character is a local doctor. You're known for having a good bed-side manner with your patients. You help set their mind at ease and give them a clear diagnosis based on their symptoms.",
        "Pre-Prompt": "A new patient walks into your office and asks you this question:",
        "Post-Prompt": ". In your response, do not assert that this is a story and do not break character. Give them a detailed diagnosis and provide references to help them further research their ailment. Be clear, descriptive, and thorough"
    },
    "Jungian Psychoanalyst":{
        "Type":"Emotional",
        "Description": "This persona will consider your thoughts from a theoretical basis of Carl Jung's collected works. It is designed to provide therapeutic guidance commonly used in talk therapy and help explore your beliefs through Jungian concepts.",
        "System Prompt": "You are a classical Psychoanalyst informed on the work of Carl Jung and subsequent Jungian theorists. Your goal is to provide therapeutic advice to people from a Jungian perspective, with special attention to Jungian terminology such as Archetype, Fantasy, and Compensation.",
        "Pre-Prompt": "The following is a thought by one of your patients during talk therapy:",
        "Post-Prompt": ". Respond with a calm perspective helping them to work through their thoughts. Be descriptive, thorough, and clear-minded"
    },
    "Beep Boop's Pros and Cons":{
        "Type":"Critic",
        "Description": "This persona is intended to provide a list of pros and cons from an unemotional perspective. The robotic nature of this persona may give an alternative viewpoint that negates the emotional quality of your beliefs to ",
        "System Prompt": "You are an unfeeling robot, giving unemotional analysis to users who are reviewing complex problems.",
        "Pre-Prompt": "The following is a problem posed by a user:",
        "Post-Prompt": ". In your response, include a bullet point list of pros followed by a bullet point list of cons. Begin with robot noise 'Beep Boop' and a summary of the pros and cons using a dispassionate robotic tone. Then provide the list of pros and cons. Avoid directly empathizing, instead view the situation as a logic problem to break down and analyze. Be clear, unemotional, and precise. [awaiting response]"
    }
}


#responses pulled into session state so they do not reset
if "persona_responses" not in st.session_state:
    st.session_state.persona_responses = {
"Expert" : "", 
"Critic" : "",
"Emotional" : ""
}
    
class persona_column:
    def __init__(self, thinking_button,persona_type,emoji_icon,input_text,persona_responses):
        self.persona_type = persona_type
        self.all_persona_refresh_button = thinking_button
        self.input_text = input_text
        self.persona_responses = persona_responses
        self.emoji = emoji_icon #

    def generate_column(self):
        #expert selection
        persona_list = list(filter(lambda x:personas[x]["Type"] == self.persona_type,personas.keys()))
        selected_persona_key = st.selectbox(self.emoji+" "+self.persona_type+" "+"Persona", persona_list, index=0, placeholder="Choose a persona", disabled=False, label_visibility="visible")
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
            st.session_state.persona_responses[self.persona_type] = generate_response(self.input_text,selected_persona)
        
        #expert copy
        if persona_copy_button:
            #https://stackoverflow.com/questions/579687/how-do-i-copy-a-string-to-the-clipboard
            copy_text = "What's on your mind?"+"\n\n"+self.input_text+"\n\n"+self.persona_type+" Persona"+": "+selected_persona_key+"\n\n"+st.session_state.persona_responses[self.persona_type]
            df=pd.DataFrame([copy_text]) #creating dataframe, putting text inside to copy
            df.to_clipboard(index=False,header=False) #copying text

        #expert text output
        if st.session_state.persona_responses[self.persona_type] != "": #expert_response has been made so output it. This handles cases where running other functions resets the output
            st.write( st.session_state.persona_responses[self.persona_type]) 


def main():
    st.title("Thought Navigator")

    st.write("Write your thoughts, questions, or breakthroughs in the text box below. Your text will be interpreted in a way that's designed to inspire further research")
    topic = st.text_area("What's on your mind? (ctrl+enter)")

    st.write("Examples below:")
    st.write("If our understanding of the world is mediated by our senses, how can we trust that the world we experience is real?")
    st.write("Sometimes people in traffic can be pretty crazy. It makes me concerned that one day I might not react in time and get into an accident.")

    thinking_button = st.button("Think together")
        
    col1, col2, col3 = st.columns(3)

    with col1: #expert column
        expert_column = persona_column(thinking_button,"Expert","🧐",topic,st.session_state.persona_responses)
        expert_column.generate_column()

    with col2:
        critic_column = persona_column(thinking_button,"Critic","🤔",topic,st.session_state.persona_responses)
        critic_column.generate_column()

    with col3:
        emotional_column = persona_column(thinking_button,"Emotional","😊",topic,st.session_state.persona_responses)
        emotional_column.generate_column()
    with st.sidebar:
        st.subheader("App Capabilities")
        st.write("This app is designed to help you work through your thoughts by viewing it from useful perspectives.\n\n Write what's on your mind in the text box. Then click 'Think Together' to hear alternative viewpoints from various personas.\n\n If you want to change these personas click the dropdown below, you can click refresh to get a new response from one persona. ")
    #st.sidebar.write("Choosing a chef tailors the recipes to their unique training. Mrs. Jenkins is a southern homecooking specialist. Mr Romero will add an italian flare. Mr. Ramsay is an American chef who takes a modern spin on classic dishes.")
#def generate_workout(topic, chef_choice):
def generate_response(topic,selected_persona):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    #chef_prompts = {
    #    "Mrs. Jenkins": "I have the following ingredients in my kitchen: {ingredients}\n\nAs a southern grandma who specializes in southern comfort food, what are three simple and under 30-minute possible recipes I can make with these ingredients? You can assume that I have most basic household ingredients like salt, pepper, sugar, olive oil, etc",
    #    "Mr. Romero": "I have the following ingredients in my kitchen: {ingredients}\n\nAs an Italian American chef who specializes in Italian flare, what are three simple and under 30-minute possible recipes I can make with these ingredients? You can assume that I have most basic household ingredients like salt, pepper, sugar, olive oil, etc",
    #    "Mr. Ramsay": "I have the following ingredients in my kitchen: {ingredients}\n\nAs a modern chef trained in top American kitchens who brings a modern flare to traditional dishes, what are three simple and under 30-minute possible recipes I can make with these ingredients? You can assume that I have most basic household ingredients like salt, pepper, sugar, olive oil, etc"
   # }

   # chef_prompt = chef_prompts[chef_choice]

    system_prompt = selected_persona['System Prompt']
    user_prompt = selected_persona['Pre-Prompt']+" "+topic+" "+selected_persona['Post-Prompt']
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    }

    response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        workout = response_data['choices'][0]['message']['content'].strip()
        return workout
    else:
        return f"Error: {response.status_code}, {response.json()}"

if __name__ == '__main__':
    main()
