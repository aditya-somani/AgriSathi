import logging
import random
from datetime import datetime
from livekit.agents import Agent, AgentSession, AutoSubscribe, JobContext, llm
from livekit.plugins import google, silero
from livekit.plugins import openai as lk_openai
from livekit.plugins.deepgram import STT as DeepgramSTT
from livekit.plugins.cartesia import TTS as CartesiaTTS
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from src.config import Config
from src.database import db
from src.tools import ALL_TOOLS
from src.tools.registration import set_current_phone
from src.tools.language_detection import set_session_language
from src.prompt import SYSTEM_PROMPT

# Configure logging
logger = logging.getLogger("agrisathi")
logger.setLevel(logging.INFO)

# The base Agent class has complex code inside its __init__ function that you can't see here. It sets up:
# 1. The audio buffer listener.
# 2. The connection to the LLM.
# 3. The event loop handler etc...
# This Agent class has all the necessary code and functionality in its constructor which are necessary for an agent to be created. 
# So instead of writing all the custom code by ourselves, we just inherit from it. And if we just wrote self.tools=tools and skipped super().__init__ it would never work. 
class AgriSathiAssistant(Agent):
    """
    The Agent class defines WHO the assistant is.
    LLM is defined in AgentSession with STT-TTS pipeline.
    """
    def __init__(self, instructions: str) -> None:
        super().__init__(
            instructions=instructions,
            tools=ALL_TOOLS,
        )

# This is the front door of your application. In LiveKit, your agent doesn't just "run" like a normal script; 
# it waits for a signal. The main.py starts a Worker, and that worker's only job is to watch for incoming calls and hand them over to your "Entrypoint" function in agent.py.
# When a call arrives, LiveKit creates a specialized object called JobContext (often shortened to ctx).
# The JobContext carries the Token, the Room Name, and the Participant Info.
async def entrypoint(ctx: JobContext):
    """
    Called for every new call. Using Deepgram STT + Gemini LLM + Cartesia TTS.
    """
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # 1. Identity Extraction
    participant = await ctx.wait_for_participant()
    phone = participant.identity
    set_current_phone(phone)
    logger.info(f"Incoming call from: {phone}")

    # 2. Database Lookup
    farmer_profile = db.get_farmer(phone)
    
    # 3. Dynamic Prompt Construction
    custom_instructions = SYSTEM_PROMPT
    if farmer_profile:
        history_str = "\n- ".join(farmer_profile['history']) if farmer_profile['history'] else "No previous history."
        lang = farmer_profile.get('preferred_language', 'hindi')
        custom_instructions += f"""
        
## Current User Info
- Name: {farmer_profile['name']}
- Location: {farmer_profile['place']}, {farmer_profile['state']}
- Crops: {farmer_profile['crops']}
- Preferred Language: {lang}
- Past Conversations:
  - {history_str}

**CRITICAL**: 
1. Greet this user by name in their language ({lang}).
2. Continue speaking in {lang} unless they specifically ask to switch.
3. Reference their location ({farmer_profile['place']}, {farmer_profile['state']}) or crops naturally.
"""
    else:
        custom_instructions += """

## Current User Info
- Status: New User (not registered)
- Preferred Language: Unknown (detect from speech)

**CRITICAL**: 
1. New caller. Warmly introduce yourself.
2. Detect their language and respond accordingly.
3. Ask for name, place, and state to help better.
4. Use register_farmer once you have details, including their language preference.
"""

    # 4. Create Session 
    # STT: Deepgram Nova-3 (best Hindi support)
    # LLM: Gemini 2.5 Flash
    # TTS: Cartesia Sonic-3
    # VAD: Silero (for voice activity detection)
    # Turn Detection: Multilingual model
    # Determine primary STT language
    # Map stored language names to Deepgram language codes
    # Map stored language names to Deepgram language codes
    LANGUAGE_CODE_MAP = {
        "hindi": "hi",
        "english": "en",
        "hinglish": "hi",  # Hinglish is best handled by Hindi model
        "bengali": "bn",
        "marathi": "mr",
        "tamil": "ta",
        "telugu": "te",
    }
    stored_lang = farmer_profile.get('preferred_language', 'hindi') if farmer_profile else None
    
    if stored_lang:
        stt_lang = LANGUAGE_CODE_MAP.get(stored_lang.lower(), 'hi')
        # Also set the session state immediately since we know the user
        set_session_language(stored_lang.lower())
    else:
        stt_lang = 'multi'  # Auto-detect for new users
        set_session_language("multi/hindi") # Default fallback until detected


    session = AgentSession(
        stt=DeepgramSTT(
            model="nova-3",
            language=stt_lang,
        ),
        # LLM: Groq (llama-3.3-70b-versatile) via OpenAI-compatible API
        # Note: 8b-instant struggled with function calling, Llama-3-Groq-70B-Tool-Use is better
        llm=lk_openai.LLM(
            model="Llama-3-Groq-70B-Tool-Use",
            api_key=Config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        ),
        # Commented out Gemini LLM (hitting rate limits)
        # llm=google.LLM(
        #     model="gemini-2.5-flash",
        # ),
        tts=CartesiaTTS(
            model="sonic-3",
            voice="faf0731e-dfb9-4cfc-8119-259a79b27e12",  # Good quality voice
        ),
        # VAD for voice activity detection
        vad=silero.VAD.load(),
        # Turn detection for knowing when user finished speaking
        turn_detection=MultilingualModel(),
    )
    
    # 5. Track conversation in real-time (MUST be registered BEFORE session.start())
    conversation_log: list[str] = []
    
    @session.on("conversation_item_added")
    def track_conversation(event):
        """Capture each conversation item as it happens."""
        try:
            item = event.item
            role = getattr(item, 'role', 'unknown')
            
            # Extract text content from ChatMessage
            content = ""
            if hasattr(item, 'text_content'):
                # Preferred: use text_content property if available
                content = item.text_content or ""
            elif hasattr(item, 'content'):
                # Fallback: manually extract from content
                item_content = item.content
                if isinstance(item_content, str):
                    content = item_content
                elif isinstance(item_content, list):
                    for part in item_content:
                        if hasattr(part, 'text'):
                            content += part.text or ""
                        elif isinstance(part, str):
                            content += part
                elif hasattr(item_content, 'text'):
                    content = item_content.text or ""
            
            if content.strip():
                conversation_log.append(f"{role}: {content.strip()}")
                logger.info(f"Tracked message [{len(conversation_log)}]: {role}: {content[:80]}...")
            else:
                logger.debug(f"Skipped empty message from {role}")
                
        except Exception as e:
            logger.warning(f"Error tracking conversation item: {e}")
    
    # 6. Start Session (after event listener is registered)
    await session.start(
        room=ctx.room,
        agent=AgriSathiAssistant(instructions=custom_instructions),
    )

    # 7. Session Cleanup with LLM-based Summarization
    summary_saved = False  # Prevent duplicate saves
    
    async def save_session_context():
        """
        Generates an intelligent summary of the conversation using Gemini.
        Uses the tracked conversation_log instead of session.history.
        """
        nonlocal summary_saved
        if summary_saved:
            logger.debug("Summary already saved, skipping duplicate")
            return
        summary_saved = True
        
        try:
            # Check if there's any meaningful conversation
            if len(conversation_log) < 2:
                # No real conversation happened (just greeting or immediate disconnect)
                summary = "Brief call, no significant interaction"
            else:
                # Format the conversation for summarization
                conversation_text = "\n".join(conversation_log[-20:])  # Last 20 messages max
                
                # Create a summarization prompt
                summary_prompt = f"""You are a conversation summarizer. Summarize the following conversation in EXACTLY 10 words or less (only extend if absolutely necessary).

Focus on: What the user asked about or accomplished.
Language: English only (even if conversation was in Hindi/Hinglish).
Format: Simple sentence, no quotes, no punctuation at the end.

Examples:
- "Asked about wheat prices and weather forecast"
- "Registered as new farmer from Lucknow"
- "Inquired about PM Kisan scheme eligibility criteria"
- "Discussed pest control methods for rice crops"

Conversation:
{conversation_text}

Summary (10 words max):"""
                
                # Use Groq (llama-3.1-8b-instant) for fast, cheap summarization
                summary_ctx = llm.ChatContext()
                summary_ctx.add_message(role="user", content=summary_prompt)
                
                llm_client = lk_openai.LLM(
                    model="llama-3.1-8b-instant",
                    api_key=Config.GROQ_API_KEY_2,
                    base_url="https://api.groq.com/openai/v1",
                    temperature=0.3,  # Low temperature for consistent, factual summaries
                )
                response = await llm_client.chat(
                    chat_ctx=summary_ctx,
                )
                
                # Extract the summary from the response
                summary = ""
                async for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        summary += chunk.choices[0].delta.content
                
                # Clean up the summary (remove extra whitespace, quotes, trailing punctuation)
                summary = summary.strip().strip('"').strip("'").rstrip('.')
                
                # Fallback if LLM returns empty
                if not summary:
                    summary = f"Call on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Save to database
            db.add_summary(phone, summary)
            logger.info(f"Session summary saved for {phone}: {summary}")
            
        except Exception as e:
            # Fallback to timestamp if summarization fails
            logger.error(f"Error generating summary: {e}")
            if not summary_saved:
                fallback_summary = f"Call on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                db.add_summary(phone, fallback_summary)
                logger.info(f"Fallback summary saved for {phone}")

    ctx.add_shutdown_callback(save_session_context)

    logger.info("Agent session started with Deepgram STT + TTS + Silero VAD")
