# Call Flow: Phone to Agent

**Category**: core
**Difficulty**: 2 (Conceptually simple, technically complex)
**Status**: understood
**Related**: [livekit_architecture.md]

## One-Liner
A phone call travels via SIP to LiveKit Cloud, which creates a Room where your Agent (Python Worker) joins as a participant.

## Full Explanation

You (the user) nailed the core journey: **Twilio -> SIP -> LiveKit -> Room**.

Here is the technical breakdown of what happens under the hood:

1.  **THE CALL**: Farmer dials number.
2.  **THE CARRIER**: Twilio receives the call.
3.  **THE HANDOFF**: Twilio looks at your "SIP Trunk" config and forwards the audio stream to LiveKit Cloud via SIP protocol.
4.  **THE ROOM**: LiveKit Cloud receives the SIP stream. It creates a **Room** (just like a Zoom meeting room).
5.  **THE DISPATCH**: It creates a "SIP Participant" in that room representing the farmer.
6.  **THE WORKER**: Your Python code (`agent.py`) is running a "Worker". It listens for new rooms.
7.  **THE JOIN**: The Worker sees the new room and connects only *your* Agent to it.
8.  **THE CONVERSATION**:
    *   Farmer logs -> Twilio -> LiveKit -> **Agent**
    *   Agent (Gemini) -> LiveKit -> Twilio -> **Farmer**

## User Notes
*   "Agent sitting in cloud" is closer to: "Agent *Worker* connects to Cloud".
*   The latency is low because WebRTC (LiveKit) and SIP are both real-time protocols.
