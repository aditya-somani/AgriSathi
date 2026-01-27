# src/tools/__init__.py
"""
AgriSathi Tools Package
-----------------------
This package contains all the tools (functions) that the AI agent can call.
Each tool is defined in its own file for modularity.
"""

from src.tools.registration import register_farmer, update_language_preference
from src.tools.web_search import web_search
from src.tools.language_detection import detect_language

# Export all tools as a list for easy import into the Agent
ALL_TOOLS = [register_farmer, update_language_preference, web_search, detect_language]
