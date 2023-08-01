import openai
import os
from dotenv import load_dotenv

# load openai api key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# export
openai_client = openai

