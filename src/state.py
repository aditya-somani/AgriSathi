# src/state.py
"""
Global Session State Management
-------------------------------
Centralizes all mutable session state variables to avoid circular imports.
"""
import logging

logger = logging.getLogger("agrisathi.state")

# Global variables
_current_phone: str = ""
_session_language: str = "english"  # Default to English as per new agnostic policy


def set_current_phone(phone: str):
    """Set current caller phone number."""
    global _current_phone
    _current_phone = phone
    logger.debug(f"State updated: Phone = {phone}")


def get_current_phone() -> str:
    """Get current caller phone number."""
    return _current_phone


def set_session_language(language: str):
    """Set current session language."""
    global _session_language
    _session_language = language.lower().strip()
    logger.debug(f"State updated: Language = {_session_language}")


def get_session_language() -> str:
    """Get current session language."""
    return _session_language
