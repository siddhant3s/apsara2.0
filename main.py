#Langchain
from langchain.chains import ConversationChain, LLMChain
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import StreamingStdOutCallbackHandler, StdOutCallbackHandler
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from mytools import *
from my_music_tools import * 
from my_utility_tools import * 
from whatsapp_tool import * 

#agents modules
from langchain import hub 
from langchain.agents import AgentType, initialize_agent, load_tools,AgentExecutor,  create_structured_chat_agent
from agent_prompt import get_agent_prompt

#extra lib 
import sys 
import os
from time import sleep 
import warnings
import argparse

#voice 
from gtts_audio import speak
import speech_recognition as sr
import pvporcupine
import pyaudio
import struct 

#Load environment variables 
load_dotenv()

parser = argparse.ArgumentParser(description='A chatbot that can use either the Groq API or a local LLM model using Ollama and openchat to generate responses. The chatbot has two main functionalities: it can use agents that have real-time knowledge using search and other advanced tools, or it can use a normal chatbot.')
# Add the arguments
parser.add_argument('--agent', action='store_true', help='Use the agent functionality for real-time knowledge. Default is False', default=False)
parser.add_argument('--local', action='store_true', help='Use local LLM - Ollama(openchat) or Groq. True for local and False for Groq. Default is False', default=False)
parser.add_argument('--gemini', action='store_true', help='Use gemini pro LLM. It does not work with the agent functionality for now as Gemini does not support System Messages. Default is False', default=False)
parser.add_argument('--temp', action='store', help='Set the temperature for the LLM. Default is 0.0', default=0.0, type=float)
parser.add_argument('--hist', action='store_true', help='Set the history for the LLM. Default is 2 messages', default=False)
parser.add_argument('--voice', action='store', help='Activate voice input by saying Apsara by passing on. Default is off', default='off', type=str)
parser.add_argument('--gmail', action='store', help='Use Gmail tools for the LLM. Make sure you have credentials.json file. Default is on', default='on', type=str)


# Parse the arguments
args = parser.parse_args()


# Now you can use them
print('Temperature: ', args.temp)
print('Using Gmail: ', args.gmail)
if args.agent:
    print("Using agent")
else: 
    print("Using chain")

if args.local:
    print("Using local")
else:
     print("Using Groq")

print('Starting...')

if args.gmail == 'on':
    from gmail_tools import * 



# Suppress specific warnings
warnings.filterwarnings("ignore")

#Set Langsmith functionality on 
#os.environ["LANGCHAIN_TRACING_V2"] = "true"
#os.environ["LANGCHAIN_PROJECT"] = "Apsara 2.0"


#Create LLM
def get_llm(temperature=0.5, local=True, groq_api_key: str = None):
    if local:
        llm = ChatOllama(model='openchat', temperature=args.temp, streaming=True, callbacks=[StreamingStdOutCallbackHandler()])
        return llm
    # if args.hugging:
        # llm = HuggingFaceEndpoint(repo_id='mistralai/Mixtral-8x7B-Instruct-v0.1',  max_new_tokens=2048)
        # return llm                     
    if args.gemini:
        llm = ChatGoogleGenerativeAI(model='gemini-pro', api_key=os.environ.get('geminiv2'), temperature=temperature, callbacks=[StdOutCallbackHandler()])
        return llm 
    
    llm = ChatGroq(api_key=groq_api_key,  streaming=True, temperature=args.temp, 
                       callbacks=[StreamingStdOutCallbackHandler()])
    return llm 

#Create Chain 
def get_chain(llm=None, memory=None):
    prompt = PromptTemplate(input_variables=["question"], template="""
        The following is a friendly conversation between a human and an AI. 
        The AI is talkative and provides lots of specific details from its context. 
        If the AI does not know the answer to a question, it truthfully says it does not know.
        
        {chat_history}
                                                 
        Human:{question}
        AI:""")
    chain = ConversationChain(llm=llm, memory=memory, prompt=prompt, input_key='question'
                              , verbose=False)
    return chain 

def clear_history():
    history = []

def create_agent():
    tools = load_tools(["llm-math", 'serpapi', 'wikipedia', 'human'], llm=llm)
    #Search tools 
    #tools.append(search_tool), 
    if args.gmail == 'on':
      #Gmail tools
      tools.append(send_mail), tools.append(search_google), tools.append(get_thread), tools.append(create_draft), 
      tools.append(get_message)
      #Calendar tools 
      tools.append(get_date), tools.append(create_event), tools.append(get_events)
    #Yahoo Finance Tool
    tools.append(yfinance_tool)
    #Weather tools
    tools.append(mylocation), tools.append(weather_tool)
    #Read and write tools
    tools.append(read_tool), tools.append(write_save_tool), 
    #Get today date tool
    tools.append(get_today_date)
    #Play on youtube tool
    tools.append(play_youtube)
    #Utility tools 
    #TODO -> tools.append(find_or_ring_phone)
    tools.append(restart_laptop), tools.append(shutdown_laptop), tools.append(check_battery)
    tools.append(increase_volume), tools.append(decrease_volume), tools.append(mute_volume), tools.append(umute_volume)
    #Spotify tools 
    tools.append(open_spotify), tools.append(play_spotify), tools.append(detect_spotify_device), 
    tools.append(print_current_song_details), tools.append(pause_or_resume_spotify)
    tools.append(play_album_on_spotify), tools.append(play_artist_on_spotify)
    #Python tool
    # tools.append(python_tool)
    #Internal Knowledge tool 
    # tools.append(internal_knowledge_tool) #TODO
    
    #Bluetooth tools 
    tools.append(connect_bluetooth_device), tools.append(disconnect_bluetooth_device)
    tools.append(bluetooth_available_devices)
    tools.append(turn_on_bluetooth), tools.append(turn_off_bluetooth)

    #Whatsapp tool 
    tools.append(send_whatsapp_message)
    
    if args.hist:    
        prompt = get_agent_prompt()
        agent =  create_structured_chat_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                                       max_iterations=10, handle_parsing_errors=True, memory=memory)
        return agent_executor
    else:
        agents = ["zero-shot-react-description", "conversational-react-description",
           "chat-zero-shot-react-description", "chat-conversational-react-description", 
           "structured-chat-zero-shot-react-description"]
        agent = initialize_agent(tools=tools, llm=llm, agent=AgentType(agents[-1]),
        max_iterations=10,
        verbose=True, 
        handle_parsing_errors=True)
        return agent  

#greeting function
def wishMe():
    '''
    This function greets the user based on the current time by playing an audio file using the os.system() method.

    Returns:
        None
    '''
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        os.system('mpg123 wish_me/good_morning.mp3')
    elif hour >= 12 and hour < 18:
        os.system('mpg123 wish_me/good_afternoon.mp3')
    else:
        os.system('mpg123 wish_me/good_evening.mp3')


#take voice command from the user microphone and convert it into text 
def takeCommand(pause_threshold = 0.6, timeout=5, phrase_time_limit=8):
    """
    This function listens to the user's voice input through the microphone and returns a string output.

    Args:
    pause_threshold (float): The minimum length of silence (in seconds) that is considered the end of a phrase.
    timeout (int): The maximum number of seconds that the function will wait for speech before timing out and returning.
    phrase_time_limit (int): The maximum number of seconds that this function will allow a phrase to continue before stopping and returning the first part of the speech recognized.

    Returns:
    str: The text of the speech recognized from the user's input.

    Raises:
    None
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = pause_threshold
        try:
            audio = r.listen(source,timeout=timeout,phrase_time_limit=phrase_time_limit)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
        except Exception as e:
            print("Say that again please...")
            return "None"
    return query

def voice(agent_complete_toggle=True):
    '''
    This function is used to start the voice assistant.
    agent_complete_toggle: whether to use agent or not.
    '''
    if agent_complete_toggle:
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)
            if keyword_index >= 0:
                os.system('mpg123 wake_word.mp3')
                query = takeCommand()
                if 'None' in query:
                    continue
                if 'exit' in query or 'bye' in query:
                        print('Okay bye...')
                        break
                try:
                    response = agent.invoke({'input': query})
                    answer = response['output'] 
                    speak(answer)
                except Exception as e:
                    print(e)
                    print('Please try again')
                    pass
                with open('chats.txt', 'a') as f: 
                        f.writelines(f'\nHuman: {query}\n')
                        f.writelines(f'Agent: {answer}\n')
                print()  

    else: 
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)
            if keyword_index >= 0:
                os.system('mpg123 wake_word.mp3')
                query = takeCommand()
                if 'None' in query:
                    continue
                if 'show_history' in query:
                    print(memory.buffer_as_str)
                    continue
                if 'exit' in query:
                    sys.exit()
                if 'clear_history' in query:
                    memory.clear()
                    print('Cleared history')
                    continue
                response = chain.invoke(query)    
                with open('chats.txt', 'a') as f: 
                        f.writelines(memory.buffer_as_str)
                print()           
    
def chat(agent_complete_toggle=True):
    if agent_complete_toggle:
        while True:
            query = input ('> ')
            if 'show_history' in query:
                print(memory.buffer_as_str)
                continue
            if 'exit' in query:
                    sys.exit()
            if 'clear_history' in query:
                memory.clear()
                print('Cleared history')
                continue
            print('Human: ', query)
            answer = None 
            try:
                response = agent.invoke({'input': query})
                answer = response['output']
            except Exception as e:
                print(e)
                print('Please try again')
                pass
            with open('chats.txt', 'a') as f: 
                    f.writelines(f'\nHuman: {query}\n')
                    f.writelines(f'Agent: {answer}\n')
            if args.hist:
                print('Printing History')
                print(memory.buffer_as_str)
            print()  

    else: 
        while True:
            query = input ('> ')
            if 'show_history' in query:
                print(memory.buffer_as_str)
                continue
            if 'exit' in query:
                sys.exit()
            if 'clear_history' in query:
                memory.clear()
                print('Cleared history')
                continue
            response = chain.invoke(query)    
            with open('chats.txt', 'a') as f: 
                    f.writelines(memory.buffer_as_str)
            print(response['response'])
            print()        

if __name__ == '__main__':
    local = args.local
    api_key = os.environ.get('groq')
    memory = ConversationBufferWindowMemory(k=2, return_messages=True, memory_key='chat_history')
    llm = get_llm(temperature=args.temp, local=local, groq_api_key=api_key)
    chain = get_chain(llm=llm, memory=memory)
    agent = create_agent()
    
    if args.voice == 'on':
        porcupine = None
        audio_stream = None
        paudio = None
        pico_key = os.environ.get('pico_key')
        porcupine = pvporcupine.create(access_key = pico_key, keyword_paths=['./apsara_keyword/ap-sara_en_linux_v2_2_0.ppn','./apsara_keyword/app-sara_en_linux_v2_2_0.ppn'])
        paudio = pyaudio.PyAudio()
        audio_stream = paudio.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
        voice(agent_complete_toggle=args.agent)
    else:
        chat(agent_complete_toggle=args.agent)
    
    
