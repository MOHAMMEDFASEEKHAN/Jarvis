import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key found:", bool(api_key))

client = genai.Client(
    api_key=api_key
)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="What is coding? Explain in simple words."
)

print(response.text)