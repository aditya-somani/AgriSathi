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
    current_phone = context.session.userdata["phone"]
    logger.info(f"Registering: {name}, {place}, {state}, {crops}, lang={language} for {current_phone}")
    db.register_farmer(current_phone, name, place, state, crops, language)

    # Keep the session's language in sync with what we just saved
    context.session.userdata["language"] = language

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
    current_phone = context.session.userdata["phone"]
    logger.info(f"Updating language to {language} for {current_phone}")
    db.update_language(current_phone, language)

    context.session.userdata["language"] = language

    return f"Understood. I will now communicate in {language}."

@function_tool()
async def update_farmer_profile(
    context: RunContext,
    name: str = None,
    place: str = None,
    state: str = None,
    crops: str = None,
):
    """
    Updates specific details in the farmer's profile (Name, Location, Crops).
    Call this when the user wants to correct or update their information.
    Do NOT call this for language changes (use update_language_preference instead).
    
    Args:
        name: New name (if changed).
        place: New village/city (if changed).
        state: New state (if changed).
        crops: New crops list (if changed).
    """
    current_phone = context.session.userdata["phone"]
    logger.info(f"Updating profile for {current_phone}: name={name}, place={place}, state={state}, crops={crops}")
    db.update_farmer_details(current_phone, name=name, place=place, state=state, crops=crops)
    
    return "Profile details updated successfully."
