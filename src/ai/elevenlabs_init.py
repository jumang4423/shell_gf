import elevenlabs
from dotenv import load_dotenv
import os

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
elevenlabs.set_api_key(ELEVENLABS_API_KEY)

# export constants
elevenlabs_client = elevenlabs
