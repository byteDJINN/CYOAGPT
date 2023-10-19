import openai
import time
import streamlit as st

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API

delay = 0.5


def gptNext(content):
  time.sleep(delay)
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user", 
        "content": "Respond with a maximum of 50 words\n"+content
      },
      {
        "role": "system", 
        "content": """
        This is a story, you are a professional writer, but never break the fourth wall, no matter what always respond with the story.
        You always write in second person point of view.
        You always respond with a maximum of 50 words.
        You always write in full sentences using 2nd person point of view."""
      }
    ],
    temperature=1,
    max_tokens=100,  # Adjust this limit as needed
    stop=['\n'],       
  )
  response_text = response.choices[0]["message"]["content"]
  return response_text

def isActionValid():
  time.sleep(delay)
  global inventory
  # check if the action is valid
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user",
        "content": "SETTING: " + setting + "\n" + "STORY: " + "\n".join([pastStory[x] + "\n" + pastAction[x] for x in range(max(-5,-len(pastStory)),-1)]) + "\n" + pastStory[-1] + "\n" + "ACTION: " + pastAction[-1] + "\n" + "INVENTORY: " + inventory
      },
      {
        "role": "system",
        "content":"""
        Given the story, an action and an inventory, determine if the action is physically possible given the story. 
        It doesn't matter if the action is not a good idea, if it is possible in this world, it is valid.
        You always respond with either 1 or 0. """
      }
    ],
    temperature=1,
    max_tokens=1,  # Adjust this limit as needed
    stop=['\n'],
  )
  response_text = response.choices[0]["message"]["content"]
  if response_text == "1":
    return True
  return False

def getInventory():
  time.sleep(delay)
  global inventory
  # check if the last item affects the inventory
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user",
        "content": "Below is the current inventory and action taken. Your response should always follow the format: [item1, item2, ...]" + "\n" + "INVENTORY: " + inventory + "\n" + "ACTION: " + pastAction[-1] + "\n" + "RESULT: " + pastStory[-1]
      },
      {
        "role": "system",
        "content":"""
        Given the player's inventory, action, and result, you always respond with their new inventory.
        You always respond with a list of items. You do not respond with any prose. 
        You do not respond with the word 'INVENTORY'. You only respond with a single list of items."""
      }
    ],
    temperature=1,
    max_tokens=50, 
    stop=['\n'],
  )
  response_text = response.choices[0]["message"]["content"]
  return response_text

def getHealth():
  time.sleep(delay)
  global health
  # check if health is changed
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user",
        "content": "HEALTH: " + str(health) + " \n" + "ACTION: " + pastAction[-1] + "\n" + "RESULT: " + pastStory[-1]
      },
      {
        "role": "system",
        "content":"""
        Given the player's current health, their action and the result, you should respond with their new health.
        The maximum health is 10. 
        You always respond with a single number indicating their health. Yo do not respond with any prose. 
        You do not respond with the word 'HEALTH'. You only respond with a single number."""
      }
    ],
    temperature=1,
    max_tokens=1, 
    stop=[],
  )
  response_text = response.choices[0]["message"]["content"]
  if response_text.isdigit():
    return response_text
  print("fail: "+response_text)
  return health 

# text input
openai.api_key = st.text_input("OpenAI API Key", type="password")

def chatAI(text):
  with st.chat_message("assistant"):
    st.write(text)
def chatU(text):
  with st.chat_message("user"):
    st.write(text)

if "setting" not in st.session_state:
  setting = gptNext(
      "Write a description (maximum of 50 words) for the setting of a story world as if it were the beginning of a novel (do not use second person).")
  pastStory = [gptNext("Given the story setting, respond with the beginning of the story, it should be a scenario with conflict or a hook, it should use second person point of view.\n" + "SETTING: " + setting) ]
  pastAction = [""]
  inventory = "[]"
  health = 10
  st.session_state.setting = setting
  st.session_state.pastStory = pastStory
  st.session_state.pastAction = pastAction
  st.session_state.inventory = inventory
  st.session_state.health = health
setting = st.session_state.setting
pastStory = st.session_state.pastStory
pastAction = st.session_state.pastAction
inventory = st.session_state.inventory
health = st.session_state.health

chatAI(setting)
for x in range(len(pastStory)):
  chatAI(pastStory[x])
  if (len(pastAction) > x+1):
    chatU(pastAction[x+1])


choice = st.chat_input("What do you do? ")
if choice:
  chatU(choice)
  pastAction.append(choice)
  
  if isActionValid():
    response = gptNext("SETTING: " + setting + "\n" + "\n".join(
        [pastStory[x]+"\n"+pastAction[x] for x in range(max(-5, -len(pastStory)), 0)]))
    chatAI(response)
    pastStory.append(response)
    inventory = getInventory()
    #chatAI("IV: "+inventory)
    health = getHealth()
    #chatAI("HP: "+str(health))
  else:
    pastAction = pastAction[:-1]
    st.session_state.pastAction = pastAction
    chatAI("Nuh uh")
