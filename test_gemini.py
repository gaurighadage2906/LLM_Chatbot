import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY was not found.")
    exit()

print("Gemini API key found.")

client = genai.Client(api_key=api_key)

try:

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Say hello in one short sentence."
    )

    print("\nSUCCESS!")
    print(response.text)

except Exception as e:

    print("\nAPI FAILED")
    print(type(e).__name__)
    print(str(e))