import requests

def generate_summary(text: str) -> str:
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer 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"}

    payload = {
        "inputs": text,
        "parameters": {
            "max_length": 200,
            # "min_length": 50,
            "do_sample": False
        }
    }

    print("text", text)
    text = "This is my personal diary please summarize today for me" + text

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"HF API failed: {response.text}")

    summary = response.json()[0]['summary_text']
    return summary


# string = "Are you struggling with losing the numbering, bulleted, or tabbed formatting when"
# summary = generate_summary("")
# print(summary)