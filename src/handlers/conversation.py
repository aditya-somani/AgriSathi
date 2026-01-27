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
            role = getattr(item, 'role', 'unknown')
            
            content = ""
            if hasattr(item, 'text_content') and item.text_content:
                content = item.text_content
            elif hasattr(item, 'content'):
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
                logger.debug(f"Logged [{role}]: {content[:50]}...")
        except Exception as e:
            logger.warning(f"Tracker error: {e}")
