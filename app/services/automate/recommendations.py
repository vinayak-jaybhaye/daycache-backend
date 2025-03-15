import google.generativeai as genai
from app.core.config import settings

# Configure Gemini API
GEMINI_API_KEY = settings.GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 1.5 Flash for faster responses
model = genai.GenerativeModel("gemini-1.5-flash")


def recommendations(prompt: str, num_recommendations=1):
    try:
        recommendation_prompt = f"""
        You are a helpful diary writing assistant. Based on the provided text, suggest {num_recommendations} possible continuations.
        response with only continuations each on a new line.
        Text: "{prompt}"
        """

        # Generate suggestions
        response = model.generate_content(
            recommendation_prompt,
            generation_config={
                "temperature": 0.8,  # Controls randomness (higher = more creative)
                "max_output_tokens": 100,  # Limit output length
            },
        )

        # Extract suggestions from the response
        if response.text:
            return response.text.strip().split("\n")[:num_recommendations]

    except Exception as e:
        print(f"Error generating suggestions: {e}")

    return []
