import os
import logging
import random
from datetime import datetime
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from livekit.agents import RunContext, function_tool
from src.config import Config
from src.state import get_session_language

logger = logging.getLogger("agrisathi.tools.search")


def get_random_api_key() -> str:
    """Randomly select between available API keys for load balancing."""
    keys = [k for k in [Config.WEB_API_KEY, Config.GOOGLE_API_KEY_2] if k]
    if not keys:
        raise ValueError("No API keys available for web search")
    selected = random.choice(keys)
    logger.debug(f"Using API key: ...{selected[-8:]}")  # Log last 8 chars for debugging
    return selected


@function_tool()
async def web_search(
    ctx: RunContext,
    query: str,
) -> str:
    """
    Web search for current/latest agricultural information related to schemes, 
    farming, or any other agricultural OR non-agricultural related information.

    Args:
        query: The query to search for - be specific and relevant.

    Returns:
        str: The search results
    """
    logger.info(f"Web search: {query}")
    
    try:
        # Setting up client with random key selection for load balancing
        api_key = get_random_api_key()
        client = genai.Client(api_key=api_key)
        model_id = "gemini-2.5-flash"  # model name

        # Setting up google search tool
        google_search_tool = Tool(
            google_search=GoogleSearch()
        )

        # Setting up config
        config = GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
            temperature=0.2,  # Lower temperature for faster, more focused responses
        )
        
        # Enhanced query for agricultural context
        today = datetime.now().strftime("%d %B %Y")
        user_lang = get_session_language()
        
        system_instruction = f"""
You are an expert agricultural interpreter for Indian farmers. 
Your goal is to use the Google Search tool to find information and then convert that raw data into a simple, actionable answer.

**Rules:**
1. No jargon.
2. Focus on **ACTION**: What should the farmer DO?
3. **CRITICAL**: Respond in the user's language: {user_lang}.
4. Today's date is {today}.

**Examples:**
- **User Query**: "Delhi weather"
  - **Your Answer**: (If user lang is Hindi) "Mausam saaf hai. Fasal katne ke liye aaj ka din badhiya hai."
  - **Your Answer**: (If user lang is English) "Weather is clear. It is a good day for harvesting."

- **User Query**: "PM Kisan Yojana detail"
  - **Your Answer**: (If user lang is Hindi) "Agar aapke paas 2 hectare se kam zameen hai, toh sarkar 6000 rupaye degi."
  - **Your Answer**: (If user lang is English) "If you have less than 2 hectares of land, government will give 6000 rupees."
"""
        
        focused_query = f"{system_instruction}\n\nUser Query: {query}"
        
        response = client.models.generate_content(
            model=model_id,
            contents=focused_query,
            config=config,
        )
        
        result = response.text
        logger.info(f"Search result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in web_search: {e}")
        return "Maaf kijiye, search mein problem aa gayi. Thodi der baad try karein."
