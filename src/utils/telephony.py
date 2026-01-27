# src/utils/telephony.py
"""
Telephony Utilities
-------------------
Handles forceful hang-ups by deleting the LiveKit room.
"""
import logging
from livekit import api
from src.config import Config

logger = logging.getLogger("agrisathi.telephony")

async def hangup_call(room_name: str):
    """
    Deletes the LiveKit room effectively hanging up the phone call
    for all participants (telephony bridge).
    """
    try:
        logger.info(f"Forcefully hanging up call in room: {room_name}")
        
        # Initialize RoomServiceClient
        # We use the URL and API credentials from Config
        # LiveKit Server API Client
        # This class is the main entrypoint, which exposes all services.
        lkapi = api.LiveKitAPI(
            Config.LIVEKIT_URL,
            Config.LIVEKIT_API_KEY,
            Config.LIVEKIT_API_SECRET
        )
        
        # Delete room terminates all participants
        await lkapi.room.delete_room(api.DeleteRoomRequest(room=room_name))
        await lkapi.aclose()
        
        logger.info(f"Room {room_name} deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to hang up call for room {room_name}: {e}")
