import httpx
from app.core.config import settings

HUGGINGFACE_API_KEY = settings.HUGGINGFACE_API_KEY

def generate_suggestions(prompt: str, num_suggestions=3):
    url = "https://api-inference.huggingface.co/models/google/flan-t5-small"

    if not HUGGINGFACE_API_KEY:
        raise ValueError("Missing Hugging Face API key. Set it in your environment variables.")

    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 50,
            "num_return_sequences": num_suggestions,
            "temperature": 0.8,
            "do_sample": True
        }
    }

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        suggested = [item['generated_text'].strip() for item in data]
        return suggested

    except httpx.HTTPStatusError as http_err:
        print(f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
    except Exception as err:
        print(f"Unexpected error: {err}")
    
    return []

# if __name__ == "__main__":
#     prompt = "My name is David. I am a software engineer. Guess my favourite programming language."
#     suggestions = generate_suggestions(prompt)
#     for idx, suggestion in enumerate(suggestions, 1):
#         print(f"Suggestion {idx}: {suggestion}")
