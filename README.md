# Apsara 2.0: Your Intelligent AI Assistant

Created by [shubharthak](https://shubharthaksangharsha.github.io/)

Apsara 2.0 stands out as a robust and adaptable AI assistant crafted using Langchain and a host of other cutting-edge libraries like Spotipy and Selenium. What sets Apsara 2.0 apart from its predecessor, ApsaraAI, is its remarkable ability to comprehend user demands and select the most suitable tool to fulfill them.

With Apsara 2.0, users can even create their own custom tools to tailor its functionality to their specific needs. Simply define a function and apply the @tool decorator above its declaration. These custom tools can seamlessly integrate with Apsara 2.0, enhancing its capabilities to cater to unique requirements.

Whereas ApsaraAI operated on a beta release, relying solely on rule-based keywords, Apsara 2.0 elevates user interaction to a whole new level. It harnesses the power of LLM (Large Language Models) and employs a Structured-based ReACT agent, empowering it to grasp user queries and navigate through a chain of logical reasoning to deliver accurate responses. Unlike its predecessor, which could encounter malfunctions or misunderstand user requests if specific keywords weren't recognized, Apsara 2.0 operates with enhanced intelligence.

Apsara 2.0 seamlessly transitions between the roles of a traditional chatbot and an agent with real-time access to knowledge through advanced search functionalities and other sophisticated tools. Whether you seek casual conversation or require instant access to information, Apsara 2.0 is equipped to meet your needs with unparalleled efficiency and precision.


## Features

- **Agents with Real-Time Knowledge**: Apsara 2.0 leverages agents to access and process information in real-time, enabling it to provide more accurate and up-to-date responses.
  
- **Local and Groq LLM Support**: Choose between local LLM models like Ollama and OpenChat or the Groq API for language processing, depending on your preference and available computational resources.
  
- **Temperature and History Control**: Fine-tune the creativity and context-awareness of Apsara 2.0 by adjusting the temperature and history parameters.
  
- **Voice Input**: Interact with Apsara 2.0 conveniently using your voice by activating the voice input feature.
  
- **Multi-Talented**: Apsara 2.0 boasts a wide range of capabilities, including:
    - Playing music on Spotify and YouTube
    - Performing mathematical calculations
    - Send Mail, Search Mails, Save Drafts of Gmail
    - Search any Finance News using Yahoo Finance
    - Creating or Checking upcoming Meetings
    - Checking the weather
    - Reading and writing files
    - Restarting or shutting down your laptop
    - Adjusting volume
    - Connecting and disconnecting Bluetooth devices
    - Sending Whatsapp message to any contact
    - Checking battery status
    - Providing information on various topics
    - And much more!

## Installation and Usage

Currently, `Apsara2.0` is optimized for Ubuntu or Debian-based distributions, with plans for Windows compatibility soon. 

To install Apsara, follow these four easy steps:

1. Clone the GitHub repository: `git clone https://github.com/shubharthaksangharsha/apsara2.0`

2. Run `python install.py`

3. Set up your environment variables:
   - `GROQ_API_KEY='YOUR-KEY'`
   - `OPENWEATHERMAP_API_KEY='YOUR-KEY'`

4. That's it! You can now run `python main.py --help` for information on available arguments, or simply execute `python main.py`. For agent functionality, run `python main.py --agent`.

### Create Your Own Custom Tools

Enhance your codebase by crafting custom tools tailored to your needs. Follow these steps to create your own functions:

1. **Define Your Function**: Create a function with a specific purpose and decorate it with the `@tool` decorator.
2. **Document Your Function**: Provide a clear description of your function's purpose and its input parameters.
3. **Integrate Your Function**: Add your function to the list of tools in the `main.py` module.

```python
from langchain.tools import tool

# Step 1: Define your custom tool function and add a tool decorator above it.
@tool
def say_hello_to_user(username: str = 'Apsara') -> str:
    """
    Useful when to greet the user. 

    Args:
        username (str): The name of the user to say hello to. Defaults to 'Apsara'.

    Returns:
        str: A string containing the greeting.
    """
    return f"Hello, {username}!"

# Step 2: Add your custom function name to the list of tools in main.py.
# Example: tools.append(say_hello_to_user)
# Do not call the function, just write the name.

if __name__ == '__main__':
    pass
```

## Code Structure

The `main.py` file houses the core logic of Apsara 2.0. It is well-organized and modular, with functions dedicated to various tasks like:

- Getting the LLM (Large Language Model)
- Creating the chain (sequence of tools and language model)
- Managing conversation history
- Creating and initializing agents
- Handling voice input and output
- Performing specific tasks like playing music, checking weather, etc.



## Additional Files
  
- `ai_poem_by_aspara.txt`: An creative poem about AI generated by Apsara 2.0.
  
- `tasks.txt`: Contains a list of tasks that Apsara 2.0 can perform.
  
- `apsara_keyword`: This folder contains files used by pvporcupine for apsara wakeword detection.
  
- `games_created_by_apsara`: This folder contain games created by Apsara 2.0.
  
- `gtts_audio.py`: This file handles the text-to-speech functionality using the gTTS library.
  
- `my_music_tools.py`: This file tools and functions related to music playback and Spotify & Youtube integration.
  
- `my_utility_tools.py`: This file contains utility tools (e.g `battery_checker`, `volume_controller`, `bluetooth_controller` that are used by Apsara 2.0.
  
- `mytools.py`: This file contains additional tools and functions used by Apsara 2.0.
  
- `spotify_utils.py`: This file contains functions for interacting with the Spotify API.
  
- `wake_word.mp3`: This is the audio file used to play apsara whenever any wakeword occurs.
  
- `agent_prompt.py`: This file defines the prompts used for interacting with the agents in Apsara 2.0.
  
- `chats.txt`: This file stores the chat history between the user and Apsara 2.0.
  
- `find_phone.py`: This file contains the script for finding or ringing the user's phone (under progress).
  
- `install.py`: This file contain the installation script for Apsara 2.0.
  
- `requirements.txt`: This file lists the required Python packages for Apsara 2.0.
  
- `testenv.env`: This file contain environment variables used for testing Apsara 2.0.


## Disclaimer

Apsara 2.0 is still under development and may not always provide accurate or complete information. Please use it with caution and do not rely solely on its responses for critical decisions.
