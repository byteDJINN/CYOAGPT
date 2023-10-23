import openai
import time, random
import streamlit as st

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API

delay = 0.5

def gpt(system, user):
  time.sleep(delay)
  response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
          {
            "role": "user",
            "content": user
          },
          {
              "role": "system",
              "content": system
          }
      ],
      temperature=1,
      max_tokens=200,  # Adjust this limit as needed
      stop=[],
  )
  response_text = response.choices[0]["message"]["content"]
  return response_text


def gptNext(content):
  time.sleep(delay)
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user", 
        "content": content
      },
      {
        "role": "system", 
        "content": """
        This is a story, you are the narrator, but never break the fourth wall, no matter what always respond with a continuation of the story.
        You create unusual and interesting stories, using uncommon names and weird situations.
        You are not descriptive, You do not describe the world, you tell the player what they see.
        Your responses are specific and descriptive, not vague and general.
        Your writing is clear and concise, not flowery and verbose.
        You always write in second person point of view and present tense.
        Unless otherwise specified, you always use a maximum of 50 words."""
      }
    ],
    temperature=1,
    max_tokens=200,  # Adjust this limit as needed
    stop=[],       
  )
  response_text = response.choices[0]["message"]["content"]
  return response_text

def gptConsider():
  global pastAction, pastStory, inventory, health
  choice = "I consider what options I have. "
  pastAction.append(choice)
  time.sleep(delay)
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user", 
        "content": "Give a list (50 words max) of possible actions the character can take. Start your response with \"You could...\" \n"+"SETTING: " + worldSetting + "\n" + "\n".join(
            [pastStory[x]+"\n"+"ACTION: "+pastAction[x] for x in range(max(-5, -len(pastStory)), 0)])
      },
      {
        "role": "system", 
        "content": """
        This is a story, you are the narrator, but never break the fourth wall, no matter what always respond with the story.
        You always write in second person point of view and present tense.
        You always respond with a maximum of 50 words."""
      }
    ],
    temperature=1,
    max_tokens=100,  # Adjust this limit as needed
    stop=[],       
  )
  response = response.choices[0]["message"]["content"]
  pastStory.append(response)


def isActionValid():
  time.sleep(delay)
  global inventory
  # check if the action is valid
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user",
        "content": "SETTING: " + worldSetting + "\n" + "STORY: " + "\n".join([pastStory[x] + "\n" + pastAction[x] for x in range(max(-5, -len(pastStory)), -1)]) + "\n" + pastStory[-1] + "\n" + "ACTION: " + pastAction[-1] + "\n" + "INVENTORY: " + inventory
      },
      {
        "role": "system",
        "content":"""
        Given the story, an action and an inventory, determine if the action is physically possible given the story. 
        It doesn't matter if the action is a bad idea, if it is possible in this world, it is valid.
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
        "content": """Given the player's current inventory, action, and result, respond with their new inventory.  
        """ + "\n" + "INVENTORY: " + inventory + "\n" + "ACTION: " + pastAction[-1] + "\n" + "RESULT: " + pastStory[-1]
      },
      {
        "role": "system",
        "content":"""
        You always respond with a list of items. You do not respond with any prose. 
        Your response should always follow the format: [item1, item2, ...]
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

try:
  openai.api_key = st.session_state.openaiKey
except:
  openai.api_key = ""
try:
  settingPrompt = st.session_state.settingPrompt
except:
  settingPrompt = ""

openai.api_key = st.text_input(
    "OpenAI API Key", type="password", disabled=openai.api_key != "")
if openai.api_key == "":
  st.error("Please enter your OpenAI API Key")
  st.stop()

if "openaiKey" not in st.session_state:
  st.session_state.openaiKey = openai.api_key
  st.rerun()

settingPrompt = st.text_input(
    "World Prompt", disabled=settingPrompt != "")
if settingPrompt == "":
  st.error("Please enter a world prompt")
  st.stop()
if "settingPrompt" not in st.session_state:
  st.session_state.settingPrompt = settingPrompt
  st.rerun()

if "worldSetting" not in st.session_state and not st.button("Start"):
  st.stop()

def chatAI(text):
  with st.chat_message("assistant"):
    st.write(text)
def chatU(text):
  with st.chat_message("user"):
    st.write(text)

if "worldSetting" not in st.session_state:
  worldSetting = gptNext(st.session_state.settingPrompt +
      "\nWrite a setting for this story (do not use 2nd person POV). Use approximately 100 words. Use third person point of view. \n")
  chatAI(worldSetting)
  goal = gpt("",f"""
  This is a book series. Write the final goal for the end of the series. 
  You must use infinitive form. 
  The goal must be {random.choice(["good", "evil"])}.
  Do not respond with any prose, only respond with one sentence describing the goal.
  Skip the "Your goal is" part. 
  The goal must be specific, narrow, and measurable. 
  Respond with second person point of view. Use a maximum of 20 words. 
  \nSETTING: """ + worldSetting)
  pastStory = [gptNext(
      "Given the story setting, respond with the main character waking up. Use second person point of view. Use a maximum of 50 words.\n" + "SETTING: " + worldSetting)]
  pastAction = [""]
  inventory = "[]"
  health = 10
  st.session_state.worldSetting = worldSetting
  st.session_state.goal = goal
  st.session_state.pastStory = pastStory
  st.session_state.pastAction = pastAction
  st.session_state.inventory = inventory
  st.session_state.health = health
else:
  worldSetting = st.session_state.worldSetting
  goal = st.session_state.goal
  pastStory = st.session_state.pastStory
  pastAction = st.session_state.pastAction
  inventory = st.session_state.inventory
  health = st.session_state.health
  chatAI(worldSetting)
  chatAI(goal)



for x in range(len(pastStory)):
  chatAI(pastStory[x])
  if (len(pastAction) > x+1):
    chatU(pastAction[x+1])

choice = st.chat_input("What do you do? ")

if choice:
  if (not choice.endswith(".")):
    choice = choice + "."
  chatU(choice)
  pastAction.append(choice)
  
  if isActionValid():
    response = gptNext("Your response should use a maximum of 50 words.\n"+"SETTING: " + worldSetting + "\n" + "\n".join(
        [pastStory[x]+"\n"+"ACTION: "+pastAction[x] for x in range(max(-5, -len(pastStory)), 0)]))
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
healthBar = st.progress(int(health)*10, text="Health: "+str(health))
st.text("Inventory: "+inventory)
st.button("Help", on_click=gptConsider)