import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Get all models and filter for chat/text models
all_models = [m.id for m in client.models.list().data]

# Exclude audio and guard models
chat_models = [
    m for m in all_models 
    if not m.startswith("whisper") and "prompt-guard" not in m and "orpheus" not in m
]

print("Available text/chat models:")
for model_id in sorted(chat_models):
  print(f"  - {model_id}")