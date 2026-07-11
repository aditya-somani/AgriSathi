# src/tools/language_detection.py
"""
Language Detection Tool
-----------------------
Helper tool to explicitly set and track the session language.
"""

import logging
from livekit.agents import RunContext, function_tool
from src.database import db

logger = logging.getLogger("agrisathi.tools.language")


@function_tool()
async def detect_language(
    context: RunContext,
    detected_language: str,
) -> str:
    """
    Sets the conversation language for the current session.
    Call this tool IMMEDIATELY when you detect what language the user is speaking,
    especially at the start of the conversation or if they switch languages.
    
    Args:
        detected_language: The detected language (e.g., "hindi", "english", "bengali", "marathi").
    """
    # Normalize language string
    lang_lower = detected_language.lower().strip()

    current_phone = context.session.userdata["phone"]
    logger.info(f"Language detected/set to: {lang_lower} for phone {current_phone}")

    # Keep the session's language in sync for the rest of this call
    context.session.userdata["language"] = lang_lower

    # Also update the persistent database profile if we have a phone number
    if current_phone:
        try:
            db.update_language(current_phone, lang_lower)
            logger.debug(f"Updated persistent language preference for {current_phone}")
        except Exception as e:
            logger.error(f"Failed to update language in DB: {e}")

    return f"Language set to {lang_lower}. I will now respond in {lang_lower}."

