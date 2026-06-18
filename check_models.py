from google import genai
import os
from dotenv import load_dotenv # <--- To jest kluczowe!

load_dotenv() # <--- To wczytuje plik .env do pamięci

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("BŁĄD: Zmienna GOOGLE_API_KEY jest pusta!")
else:
    client = genai.Client(api_key=api_key)
    for m in client.models.list():
        print(f"Model: {m.name}")