# src/handlers/summary.py
"""
Session Summary Handler
-----------------------
Asynchronously generates and saves conversation summaries.
"""
import logging
from datetime import datetime
from livekit.agents import llm
from livekit.plugins import openai as lk_openai
from src.config import Config
from src.database import db

logger = logging.getLogger("agrisathi.handlers.summary")

async def save_session_summary(phone: str, conversation_log: list[str]):
    """
    Generates an intelligent summary using Groq and saves to database.
    """
    if not conversation_log or len(conversation_log) < 2:
        summary = "Brief call, no significant interaction"
        db.add_summary(phone, summary)
        return

    try:
        # Format the conversation for summarization
        conversation_text = "\n".join(conversation_log[-20:])
        
        summary_prompt = f"""You are a strictly factual conversation summarizer. 
CRITICAL: Do NOT invent information. If the user only said "Hi" or "Hello" and hung up, your summary MUST reflect ONLY that. Do NOT assume they want assistant help if they didn't ask for it.

Rules:
1. Summarize in EXACTLY 10 words or less.
2. If the call was just a greeting: "User greeted and disconnected" or "Brief greeting only".
3. Provide ONLY the summary, no other text.

Conversation:
{conversation_text}

Summary:"""
        
        summary_ctx = llm.ChatContext()
        summary_ctx.add_message(role="user", content=summary_prompt)
        
        llm_client = lk_openai.LLM(
            model="llama-3.1-8b-instant",
            api_key=Config.GROQ_API_KEY_2,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.3,
        )
        
        # chat() is sync but returns an async iterable stream
        response = llm_client.chat(chat_ctx=summary_ctx)
        
        summary = ""
        async for chunk in response:
            if chunk.delta and chunk.delta.content:
                summary += chunk.delta.content
        
        summary = summary.strip().strip('"').strip("'").rstrip('.')
        
        if not summary:
            summary = f"Call on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
        db.add_summary(phone, summary)
        logger.info(f"Summary saved for {phone}: {summary}")
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        fallback = f"Call on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        db.add_summary(phone, fallback)
