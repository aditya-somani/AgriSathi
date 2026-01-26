# src/tools/language_detection.py
"""
Language Detection Tool
-----------------------
Helper tool to explicitly set and track the session language.
"""

import logging
from livekit.agents import RunContext, function_tool
from src.database import db
import src.tools.registration as registration

logger = logging.getLogger("agrisathi.tools.language")

# Global variable to track current session language
_session_language: str = "hindi"  # Default fallback


def get_session_language() -> str:
    """
    Returns the current session language.
    Used by other tools (like web_search) to format their responses.
    """
    return _session_language


def set_session_language(language: str):
    """
    Manually set the session language (e.g., from profile loading).
    """
    global _session_language
    _session_language = language


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
    global _session_language
    
    # Normalize language string
    lang_lower = detected_language.lower().strip()
    
    # Update global state
    _session_language = lang_lower
    
    logger.info(f"Language detected/set to: {lang_lower} for phone {registration._current_phone}")
    
    # Also update the persistent database profile if we have a phone number
    if registration._current_phone:
        try:
            db.update_language(registration._current_phone, lang_lower)
            logger.debug(f"Updated persistent language preference for {registration._current_phone}")
        except Exception as e:
            logger.error(f"Failed to update language in DB: {e}")
            
    return f"Language set to {lang_lower}. I will now respond in {lang_lower}."
