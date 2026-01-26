# src/tools/registration.py
"""
Farmer Registration Tool
------------------------
Handles saving farmer profile data to the SQLite database.
"""

import logging
from livekit.agents import RunContext, function_tool
from src.database import db

logger = logging.getLogger("agrisathi.tools.registration")

# Global variable to track current caller's phone
_current_phone: str = ""


def set_current_phone(phone: str):
    """Called by the entrypoint to set the current caller's phone number."""
    global _current_phone
    _current_phone = phone


@function_tool()
async def register_farmer(
    context: RunContext,
    name: str,
    place: str,
    state: str,
    crops: str,
    language: str = "hindi",
):
    """
    Registers a new farmer into the database for personalized service.
    Call this tool when the user wants to sign up or register.
    
    Args:
        name: The full name of the farmer (e.g., Ramesh Kumar).
        place: The village or city where the farmer lives (e.g., Lucknow).
        state: The state where the farmer lives (e.g., Uttar Pradesh).
        crops: The main crops the farmer grows, comma-separated (e.g., wheat, rice).
        language: Preferred language - "hindi", "english", or "hinglish". Default is "hindi".
    """
    global _current_phone
    logger.info(f"Registering: {name}, {place}, {state}, {crops}, lang={language} for {_current_phone}")
    db.register_farmer(_current_phone, name, place, state, crops, language)
    return f"Registration complete for {name} ji from {place}, {state}. I will remember your preference for {language}."


@function_tool()
async def update_language_preference(
    context: RunContext,
    language: str,
):
    """
    Updates the user's preferred language. Call this when the user explicitly
    asks to change the conversation language or says something like 
    "English mein baat karo" or "Hindi mein bolo".
    
    Args:
        language: The new preferred language - "hindi", "english", or "hinglish" etc.
    """
    global _current_phone
    logger.info(f"Updating language to {language} for {_current_phone}")
    db.update_language(_current_phone, language)
    return f"Understood. I will now communicate in {language}."
