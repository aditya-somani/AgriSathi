# src/handlers/conversation.py
"""
Conversation Tracker
--------------------
Captures and formats conversation items for logging and processing.
"""
import logging

logger = logging.getLogger("agrisathi.handlers.conversation")

def attach_conversation_tracker(session, conversation_log: list[str]):
    """
    Attaches an event listener to the session to track messages.
    """
    @session.on("conversation_item_added")
    def on_item_added(event):
        try:
            item = event.item
            # Only log actual messages (filter out tool calls/outputs for the transcript)
            if item.type != "message":
                return

            role = item.role
            content = item.text_content or ""
            
            if content.strip():
                conversation_log.append(f"{role}: {content.strip()}")
                logger.debug(f"Logged [{role}]: {content[:50]}...")
        except Exception as e:
            logger.warning(f"Tracker error: {e}")
