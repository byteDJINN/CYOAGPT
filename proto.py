import openai
import time

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API

openai.api_key_path = "openai_api_key.txt"


def gptNext(content):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user", 
        "content": content
      },
      {
        "role": "system", 
        "content": "You are the narrator of this CYOA story. You only respond with one sentence answers."
      }
    ],
    temperature=1.2,
    max_tokens=100,  # Adjust this limit as needed
    stop=['\n'],       
  )
  response_text = response.choices[0]["message"]["content"]
  return response_text

def gptConfirm(past):
  def isActionValid():
    # check if the action is valid
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {
          "role": "user",
          "content": "PAST: " + past[-2] + "\n" + "ACTION: " + past[-1] + "\n" + "INVENTORY: []"
        },
        {
          "role": "system",
          "content":"Given the past, an action, and an inventory, determine if the action is valid. Respond with either 1 or 0. "
        }
      ],
      temperature=0,
      max_tokens=1,  # Adjust this limit as needed
      stop=['\n'],
    )
    response_text = response.choices[0]["message"]["content"]
    if response_text == "1":
      return True
    return False
  def isInventory():
    # check if the last item affects the inventory
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {
          "role": "user",
          "content": "ACTION: " + past[-1]
        },
        {
          "role": "system",
          "content":"Given an action, if the subject received/bought/found... an item respond with 1, if the subject lost/consumed/dropped... an item respond with -1, otherwise respond with 0. "
        }
      ],
      temperature=0,
      max_tokens=1,  # Adjust this limit as needed
      stop=['\n'],
    )
    response_text = response.choices[0]["message"]["content"]
    if response_text in ["1", "0", "-1"]:
      return response_text
    return None

  return isActionValid()



scenario = gptNext("Create an initial scenario for a CYOA story")
print(scenario)
past = [scenario]
for i in range(10):
  choice = input("> ")
  past.append(choice)
  if gptConfirm(past):
    response = gptNext("\n".join(past[-10:]))
    print(response)
    past.append(response)
  else:
    past = past[:-1]
    print("Nuh uh")
