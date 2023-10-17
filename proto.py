import openai
import json

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API

openai.api_key_path = "openai_api_key.txt"


def run_conversation(question):
    # Step 1: send the user's question to GPT-3 with the requirement for a terminal command
    prompt = f"Generate a terminal command to: {question}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=30,  # Adjust this limit as needed
        stop=None,       # Do not set a stopping condition
    )
    response_text = response.choices[0].text.strip()

    return response_text


# Example usage
user_question = "Give me the HTML for somewebsite.com"
response = run_conversation(user_question)
print(response)
