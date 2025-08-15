import httpx
from app.core.config import settings

HUGGINGFACE_API_KEY = settings.HUGGINGFACE_API_KEY

def generate_suggestions(prompt: str, num_suggestions=3):
    url = "https://api-inference.huggingface.co/models/google/flan-t5-small"

    if not HUGGINGFACE_API_KEY:
        raise ValueError(
            "Missing Hugging Face API key. Set it in your environment variables."
        )

    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

    # Instruction for FLAN-T5
    system_instruction = (
        "You are a helpful assistant that provides exactly 3 short suggestions for a journal entry. "
        "Each suggestion should be a single sentence and directly relevant to the provided entry content. "
        "Respond only with the suggestions, nothing else."
    )

    full_prompt = f"{system_instruction}\nEntry: {prompt}\nSuggestions:"

    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.9,
            "num_return_sequences": 1,
        },
    }

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        raw_text = data[0]["generated_text"]

        # Split and clean suggestions
        suggestions = []
        for line in raw_text.split("\n"):
            line = line.strip("-*1234567890. ").strip()
            if line:
                suggestions.append(line)

        return suggestions[:num_suggestions]

    except httpx.HTTPStatusError as http_err:
        print(f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
    except Exception as err:
        print(f"Unexpected error: {err}")

    return []


if __name__ == "__main__":
    prompt = "Today I felt stressed after work. I need some ideas to relax and improve my mood."
    suggestions = generate_suggestions(prompt)
    for idx, suggestion in enumerate(suggestions, 1):
        print(f"Suggestion {idx}: {suggestion}")
