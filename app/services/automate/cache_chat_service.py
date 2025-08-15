import logging
from typing import Optional

import google.generativeai as genai
from app.core.config import settings

# Configure Gemini API
GEMINI_API_KEY = settings.GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

logger = logging.getLogger(__name__)


def ask_cache_chat(
    content: str,
    max_tokens: int = 200,
    temperature: float = 0.6,
    stop_sequences: Optional[list[str]] = None,
) -> str:
    if stop_sequences is None:
        stop_sequences = ["\nUser:", "User:"]

    prompt = f"You are Cache ( your name = Cache), my diary. I am your friend who is sharing my thoughts with you.\nUser: {content}\nDiary:"

    logger.debug(f"Prompt sent to Gemini: {prompt}")

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
                "stop_sequences": stop_sequences,
            },
        )

        text = response.text.strip() if response.text else None
        if not text:
            logger.warning("Gemini returned empty text.")
            return "I'm having trouble responding. Try again later."

        return text

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        return "I'm having trouble responding. Try again later."


if __name__ == "__main__":
    test_entry = "Today I felt stressed after work. I need some ideas to relax and improve my mood."
    reply = ask_cache_chat(test_entry)
    print(f"Diary response: {reply}")
