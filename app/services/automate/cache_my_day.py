import google.generativeai as genai
from app.core.config import settings
from typing import Optional
import json
from typing import Dict
import re

# Initialize Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def cache_my_day(user: str, myday: str, dairy_assistant: str) -> dict:
    try:
        prompt = (
            f"You are my personal diary. Ask me about my day and extract key details for summarization.\n"
            f"Add what you have learned about my day in 'myday', put your follow-up question in 'DiaryAssistant', and you can find answers to your questions in 'User'.\n"
            f"Once you are done asking questions, put 'end' in 'DiaryAssistant'.\n"
            f"Return this information in JSON format.\n"
            f'{{\n'
            f'    "myday": "{myday}",\n'
            f'    "DiaryAssistant": "{dairy_assistant}",\n'
            f'    "User": "{user}"\n'
            f'}}'
        )

        # Call AI model
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        response = model.generate_content(prompt).text.strip()
        # print(response)

        # parse response
        parsed = extract_and_parse_json(response)

        return parsed
    except Exception as e:
        raise Exception(f"Gemini API failed: {e}")


def extract_and_parse_json(response_text: str) -> Dict[str, str]:
    try:
        # Use a regular expression to find the JSON object
        json_match = re.search(r'\{.*?\}', response_text, re.S)
        
        if not json_match:
            raise ValueError("No valid JSON found in the input.")

        # Extract JSON part from the string
        json_string = json_match.group(0)
        
        # Parse the JSON string
        response_data = json.loads(json_string)

        # Ensure all required fields are present
        return {
            "myday": response_data.get("myday", ""),
            "DiaryAssistant": response_data.get("DiaryAssistant", ""),
            "User": response_data.get("User", "")
        }

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error: {e}")
        return {"myday": "", "DiaryAssistant": "", "User": ""}