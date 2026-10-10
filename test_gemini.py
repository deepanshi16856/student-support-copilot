
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Check your .env file.")

client = genai.Client(api_key=api_key)

for attempt in range(3):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Reply with exactly: Gemini API connection successful"
        )
        print(response.text)
        break
    except Exception as error:
        print(f"Attempt {attempt + 1} failed: {error}")
        if attempt < 2:
            time.sleep(5)
        else:
            print("Please try again later if the model remains unavailable.")