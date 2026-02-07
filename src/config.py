import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    """
    Single source of truth for all application configuration.
    Failed checks happen here at startup, not deep in the code.
    """
    LIVEKIT_URL = os.getenv("LIVEKIT_URL")
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_API_KEY_2 = os.getenv("GOOGLE_API_KEY_2")  # Second Gemini key for load balancing
    WEB_API_KEY = os.getenv("WEB_API_KEY")  # For Gemini with web search
    SUMMARY_API_KEY = os.getenv("SUMMARY_API_KEY")  # For session summarization
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # For Groq LLM (main agent)
    GROQ_API_KEY_2 = os.getenv("GROQ_API_KEY_2")  # For Groq summarization (lower-end model)
    CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")  # For Cartesia TTS (backup)
    # GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY")  # For Google STT/TTS
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")  # For Deepgram STT/TTS
    
    # Logic Configuration
    MAX_CALL_DURATION = 200  # 200 seconds 😮‍💨
    
    @classmethod
    def validate(cls):
        """Ensure critical variables are set.
        
        Note: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET are NOT validated here
        because LiveKit Cloud injects them automatically at runtime.
        """
        missing = []
        # if not cls.LIVEKIT_URL: missing.append("LIVEKIT_URL")
        # if not cls.LIVEKIT_API_KEY: missing.append("LIVEKIT_API_KEY")
        # if not cls.LIVEKIT_API_SECRET: missing.append("LIVEKIT_API_SECRET")
        # if not cls.GOOGLE_API_KEY: missing.append("GOOGLE_API_KEY")
        if not cls.WEB_API_KEY: missing.append("WEB_API_KEY")
        if not cls.CARTESIA_API_KEY: missing.append("CARTESIA_API_KEY")
        if not cls.DEEPGRAM_API_KEY: missing.append("DEEPGRAM_API_KEY")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Validate on import (fail fast)
# Config.validate()  # Commented out for now so you can run dry tests
