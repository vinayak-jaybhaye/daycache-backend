import google.generativeai as genai
from app.core.config import settings

# Initialize Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_summary(text: str) -> str:
    try:
        # Create a prompt for summarization
        prompt = f"This is my personal diary, summarize today for me and respond with only summary nothing else: {text}"

        # Use the 'gemini-pro' model for text generation
        model = genai.GenerativeModel("models/gemini-2.0-flash")

        # Generate a summary
        response = model.generate_content(prompt)
       
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini API failed: {e}")

    