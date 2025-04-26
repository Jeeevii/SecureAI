import requests
import os
from dotenv import load_dotenv

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = "gemini-2.0-flash"  # or "gemini-2.0-pro", depending on what you wanna test
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_KEY}"

def generate_content(prompt):
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        output = response.json()
        try:
            text = output['candidates'][0]['content']['parts'][0]['text']
            return text
        except (KeyError, IndexError):
            return "Response format unexpected. Check the API output!"
    else:
        return f"Error {response.status_code}: {response.text}"

if __name__ == "__main__":
    prompt = input("Enter your prompt for Gemini: ")
    response = generate_content(prompt)
    print("\nGemini says:\n")
    print(response)
