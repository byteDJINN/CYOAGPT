from anthropic import Anthropic
import time, random
import streamlit as st

delay = 0.5
model = "claude-3-sonnet-20240229"

def gpt(system, user):
  time.sleep(delay)
  response = client.messages.create(
      model=model,
      messages=[
          {
            "role": "user",
            "content": system + "\n" + user
          }
      ],
      temperature=1,
      max_tokens=200,  # Adjust this limit as needed
  )
  response_text = response.content[0].text
  return response_text


def gptNext(content):
  time.sleep(delay)
  response = client.messages.create(
    model=model,
    messages=[
      {
        "role": "user", 
        "content": """
        This is a story, you are the narrator, but never break the fourth wall, no matter what always respond with a continuation of the story.
        You are not descriptive, You do not describe the world, you tell the player what they see.
        Your responses are specific and descriptive, not vague and general.
        Your writing is clear and concise, not flowery and verbose.
        You always write in second person point of view and present tense.
        Unless otherwise specified, you always use a maximum of 50 words. """ + "\n" + 
        content
      },
    ],
    temperature=1,
    max_tokens=200,  # Adjust this limit as needed   
  )
  response_text = response.content[0].text
  return response_text

def gptConsider():
  global pastAction, pastStory, inventory, health
  choice = "I consider what options I have. "
  pastAction.append(choice)
  time.sleep(delay)
  response = client.messages.create(
    model=model,
    messages=[
      {
        "role": "user", 
        "content": """
        This is a story, you are the narrator, but never break the fourth wall, no matter what always respond with the story.
        You always write in second person point of view and present tense.
        You always respond with a maximum of 50 words. """ + "\n" + 
        "Give a list (50 words max) of possible actions the character can take. Start your response with \"You could...\" \n"+"SETTING: " + worldSetting + "\n" + "\n".join(
            [pastStory[x]+"\n"+"ACTION: "+pastAction[x] for x in range(max(-5, -len(pastStory)), 0)])
      },
    ],
    temperature=1,
    max_tokens=100,  # Adjust this limit as needed    
  )
  response = response.content[0].text
  pastStory.append(response)


def isActionValid():
  time.sleep(delay)
  global inventory
  # check if the action is valid
  response = client.messages.create(
    model=model,
    messages=[
      {
        "role": "user",
        "content": """
        Given the story, an action and an inventory, determine if the action is physically possible given the story. 
        It doesn't matter if the action is a bad idea, if it is possible in this world, it is valid.
        You always respond with either 1 or 0. """ + "\n" + 
        "SETTING: " + worldSetting + "\n" + "STORY: " + "\n".join([pastStory[x] + "\n" + pastAction[x] for x in range(max(-5, -len(pastStory)), -1)]) + "\n" + pastStory[-1] + "\n" + "ACTION: " + pastAction[-1] + "\n" + "INVENTORY: " + inventory
      },
    ],
    temperature=1,
    max_tokens=2,  # Adjust this limit as needed
  )
  response_text = response.content[0].text
  if response_text == "1":
    return True
  return False

def getInventory():
  time.sleep(delay)
  global inventory
  # check if the last item affects the inventory
  response = client.messages.create(
    model=model,
    messages=[
      {
        "role": "user",
        "content": """
        Given the story, and the player's old inventory, check if anything should be changed and respond with their new inventory. This should be like a video game inventory. 
        You always respond with a list of items. In the format [item1, item2, item3].
        Do not respond with the word "INVENTORY".
        Each item in the list should be a single word. 
        """ + "\n" + "STORY: " + "\n".join(
            ["ACTION: "+pastAction[x] + "\n"+ pastStory[x] for x in range(max(-5, -len(pastStory)), 0)]) + "\n" + "INVENTORY: " + inventory
      },
    ],
    temperature=1,
    max_tokens=50, 
  )
  response_text = response.content[0].text
  return response_text

def getHealth():
  time.sleep(delay)
  global health
  # check if health is changed
  response = client.messages.create(
    model=model,
    messages=[
      {
        "role": "user",
        "content": """
        Given the player's current health, their action and the result, you should respond with their new health.
        The maximum health is 10. 
        You always respond with a single number indicating their health. Yo do not respond with any prose. 
        You do not respond with the word 'HEALTH'. You only respond with a single number.""" + "\n" + 
        "HEALTH: " + str(health) + " \n" + "ACTION: " + pastAction[-1] + "\n" + "RESULT: " + pastStory[-1]
      }
    ],
    temperature=1,
    max_tokens=2, 
  )
  response_text = response.content[0].text
  if response_text.isdigit():
    return response_text
  print("fail: "+response_text)
  return health 
APIKey = ""
try:
  APIKey = st.session_state.APIKey
except:
  APIKey = ""
try:
  settingPrompt = st.session_state.settingPrompt
except:
  settingPrompt = ""

APIKey = st.text_input(
    "Anthropic API Key", type="password", disabled=APIKey != "")
if APIKey == "":
  st.error("Please enter your Anthropic API Key")
  st.stop()

if "APIKey" not in st.session_state:
  st.session_state.APIKey = APIKey
  st.rerun()

client = Anthropic(
    api_key=APIKey,
)

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
  Your response should start with a verb.
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
st.text("Inventory: " + inventory)
st.button("Help", on_click=gptConsider)