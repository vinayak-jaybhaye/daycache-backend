import google.generativeai as genai
import os

from app.core.config import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_cache_chat(content: str, max_tokens: int = 200) -> str:
    prompt = f"""
    You are Cache, my diary. I am your friend who is sharing my thoughts with you.
    User: {content}
    Diary:
    """

    print(f"Prompt: {prompt}")
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,  # Strict output limit
                "temperature": 0.6,  # Lower randomness for predictable replies
                "stop_sequences": ["\nUser:", "User:"],  # Stop after the diary's response
            },
        )

        return response.text.strip() if response.text else "I'm having trouble responding. Try again later."

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm having trouble responding. Try again later."
