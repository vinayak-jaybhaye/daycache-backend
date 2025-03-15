import google.generativeai as genai
import requests
import json
import re
from datetime import date, datetime
from typing import List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.schemas.cache_chat_context import ContextQuery
from app.models.entry import Entry
from app.models.day import Day
from app.core.config import settings

HF_API_TOKEN = settings.HUGGINGFACE_API_KEY
HF_CHAT_API_URL = (
    "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
)
REQUEST_TIMEOUT = 15  # seconds

GEMINI_API_KEY = settings.GEMINI_API_KEY


def extract_json_from_llm_response(response_data: str) -> Tuple[Set[str], Set[date]]:
    locations = set()
    dates = set()

    json_match = re.search(r'\{.*\}', response_data, re.DOTALL)
    if not json_match:
        print("No JSON found in response")
        return set(), set()
    json_str = json_match.group(0)
    

    try:
        response_json = json.loads(json_str)
        locations = set(response_json.get("locations", []))
        dates = set(response_json.get("dates", []))
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return set(), set()
    return locations, dates


def extract_locations_and_dates_from_llm(text: str) -> Tuple[Set[str], Set[date]]:
    genai.configure(api_key=GEMINI_API_KEY)

    prompt = f"""
            Your only task is to extract city names and dates (interpret relative dates eg. yeseterday, today based on today's date ({datetime.today().date()})) from the provided text. 
            return the json object in the following format:
            {{
              "locations": ["city_1", "city_2"],
              "dates": ["YYYY-MM-DD", "YYYY-MM-DD"]
            }}

            ### Input Text:
            {text}
        """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        if not response or not response.text:
            print("Empty response from Gemini API")
            return set(), set()

        print(response.text)

        [locations, dates] = extract_json_from_llm_response(response.text)
        # print(f"Extracted locations: {locations}, dates: {dates}")

    except (json.JSONDecodeError, KeyError, Exception) as e:
        print(f"Error during model call or parsing: {e}")
        return set(), set()

    return locations, dates


def fetch_context(user_id: int, locations: List[str], dates: List[date], db: Session) -> List[str]:
    if not dates:
        dates = [datetime.today().date()]  # Default to today

    # Join Day and Entry tables and filter by user_id and date
    query = db.query(Entry.content).join(Day).filter(
        Day.user_id == user_id,
        Day.date.in_(dates)
    )

    # Perform substring search on location
    if locations:
        location_query = or_(*[Entry.location.ilike(f"%{loc}%") for loc in locations])
        query = query.filter(location_query)

    # Fetch all potential results (limit to 100 for efficiency)
    results = [entry.content for entry in query.distinct().limit(100).all()]

    return results


def add_context(user_id: int, question: str, db: Session) -> str:
    [locations, dates] = extract_locations_and_dates_from_llm(question)

    entries = fetch_context(user_id, locations=locations, dates=dates, db=db)
    
    if not entries:
        return f"No relevant entries found for: {question}"

    context = "\n".join(entries[:5])  # Show top 5 entries
    return f"Question: {question}\n\nRelevant Entries:\n{context}"