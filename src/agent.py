# src/agent.py
"""
AgriSathi AI - Main Agent Orchestrator
--------------------------------------
Handles LiveKit lifecycle, STT/TTS pipeline, and session coordination.
"""
import logging
import asyncio
from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext
from livekit.plugins import google
from livekit.plugins import silero
from livekit.plugins import openai as lk_openai
from livekit.plugins.deepgram import STT as DeepgramSTT
from livekit.plugins.cartesia import TTS as CartesiaTTS
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from src.config import Config
from src.database import db
from src.tools import ALL_TOOLS
from src.prompt import SYSTEM_PROMPT

# Modular Handlers
from src.handlers.summary import save_session_summary
from src.handlers.conversation import attach_conversation_tracker
from src.utils.telephony import hangup_call

logger = logging.getLogger("agrisathi.agent")
logger.setLevel(logging.INFO)

class AgriSathiAssistant(Agent):
    """AgriSathi Identity and Tool definitions."""
    def __init__(self, instructions: str) -> None:
        super().__init__(
            instructions=instructions,
            tools=ALL_TOOLS,
        )

async def entrypoint(ctx: JobContext):
    """Main call handler."""
    logger.info(f"Incoming call in room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # 1. Identity & Profile
    participant = await ctx.wait_for_participant()
    phone = participant.identity

    farmer_profile = db.get_farmer(phone)

    # 2. Instruction Building
    custom_instructions = SYSTEM_PROMPT
    session_language = "english"
    if farmer_profile:
        history = "\n- ".join(farmer_profile['history'][-5:]) if farmer_profile['history'] else "No history."
        lang = farmer_profile.get('preferred_language', 'English')
        session_language = lang.lower() if lang else "english"
        custom_instructions += f"\n\n## User: {farmer_profile['name']}\n- Location: {farmer_profile['place']}\n- Past: {history}\n- Language: {lang}"
    else:
        custom_instructions += "\n\n## Status: New User. Greet in English/Neutral and detect language."

    # 3. Session Setup
    session = AgentSession(
        stt=DeepgramSTT(model="nova-3", language='multi'),
        # llm=lk_openai.LLM(
        #     model="openai/gpt-oss-20b",
        #     api_key=Config.GROQ_API_KEY,
        #     base_url="https://api.groq.com/openai/v1",
        # ),
        llm=google.LLM(model="gemini-3"),
        tts=CartesiaTTS(model="sonic-3", voice="faf0731e-dfb9-4cfc-8119-259a79b27e12"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        preemptive_generation=True,
    )

    # Per-call state lives on the session object, NOT in a shared global.
    # A single worker serves many calls, so a module-level variable would be
    # overwritten by the next caller. userdata is isolated per session.
    session.userdata = {"phone": phone, "language": session_language}

    # 4. Attach Modular Handlers
    conversation_log = []
    attach_conversation_tracker(session, conversation_log)
    
    # 5. Start Agent
    await session.start(
        room=ctx.room,
        agent=AgriSathiAssistant(instructions=custom_instructions),
    )
    logger.info(f"Agent started for {phone}")

    # 6. Call Duration Watchdog (Hangs up entire telephony call)
    async def _enforce_time_limit():
        try:
            await asyncio.sleep(Config.MAX_CALL_DURATION)
            logger.warning(f"Timeout ({Config.MAX_CALL_DURATION}s) reached. Hanging up.")
            await hangup_call(ctx.room.name) # Full room deletion (strict hangup)
        except asyncio.CancelledError:
            pass

    timer_task = asyncio.create_task(_enforce_time_limit())

    # 7. Cleanup & Summarization
    async def cleanup():
        timer_task.cancel()
        await save_session_summary(phone, conversation_log)
        logger.info(f"Session cleaned up for {phone}")

    ctx.add_shutdown_callback(cleanup)
