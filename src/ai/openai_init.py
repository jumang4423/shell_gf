import openai
import os
from dotenv import load_dotenv

# load openai api key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# export constants
openai_client = openai
GPT_3 = "gpt-3.5-turbo-16k"
GPT_4 = "gpt-4-0613"
JUMANGO = "ft:gpt-3.5-turbo-0613:saasis::7qknygYx"


# export fn
def summarize_arr(conv_arr: list, gpt_model: str) -> str:
    """
    summarize conversation array
    """
    THIS_SYSTEM_PROMPT = f"""
    based on given conversation of user and ai, summarize the conversation.
    but list up THREE important points, very short and clear.
    <<example>>
    <history>
    user: why does dog bark?
    ai: well, dog barks because it is a dog.
    user: wtf
    ai: what is wrong with you?
    <ai summary>
    - user asked why dog barks.
    - ai said said nonsense.
    - both user and ai got angry.
    """
    messages = [
        {"role": "system", "content": THIS_SYSTEM_PROMPT},
    ]
    messages.extend(conv_arr)
    response = openai_client.ChatCompletion.create(
        model=gpt_model,
        messages=messages,
    )
    response_str = response.choices[0].message.content

    return response_str
