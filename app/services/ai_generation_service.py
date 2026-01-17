import json
from google import genai
from app.core.config import settings

# Initialize client once
client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"


def ai_generate_summary_and_tags(text: str) -> tuple[str, list[str]]:
    """
    Generate a diary summary and tags using Gemini.

    Returns:
        (summary: str, tags: list[str])
    """
    if not text.strip():
        return "", []

    prompt = f"""
You are analyzing a personal diary.

TASK:
1. Write a concise 1–3 sentence summary of the day.
2. Extract 3–7 short lowercase tags describing themes or activities.

RULES:
- Respond ONLY in valid JSON
- No markdown
- No explanations
- Tags must be lowercase, single words if possible

FORMAT:
{{
  "summary": "string",
  "tags": ["tag1", "tag2"]
}}

DIARY:
{text}
""".strip()
    return text, ["untagged"]

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        raw_text = response.text.strip()

        # ---- Parse JSON ----
        data = json.loads(raw_text)

        summary = data.get("summary", "").strip()
        tags = data.get("tags", [])

        # ---- Defensive validation ----
        if not isinstance(summary, str):
            summary = ""

        if not isinstance(tags, list):
            tags = []

        tags = [
            str(tag).strip().lower()
            for tag in tags
            if isinstance(tag, (str, int)) and str(tag).strip()
        ]

        return summary, tags

    except json.JSONDecodeError:
        raise RuntimeError(
            f"Gemini returned invalid JSON:\n{raw_text}"
        )

    except Exception as e:
        raise RuntimeError(f"Gemini API failed: {e}")
