# LiveKit Connection Architecture: WebSocket Signaling + WebRTC Media

**Category**: core
**Difficulty**: 5 (Network Architecture + Protocol Details)
**Status**: mastered
**Related**: [async_and_event_loop, livekit_agent_structure]

## One-Liner
LiveKit uses a **persistent WebSocket** for signaling (room state, participant events) and **WebRTC peer connections** for low-latency media transport (audio/video over UDP).

## The Technical Reality

### What `await ctx.connect()` Actually Does

When you call `await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)` in your agent, here's the exact sequence:

1. **WebSocket Connection Establishment**
   - Opens a persistent WebSocket connection to `LIVEKIT_URL` (e.g., `wss://your-project.livekit.cloud`)
   - This is a **TCP-based** connection for reliability
   - Uses the `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` for authentication

2. **Signaling Exchange (SDP Negotiation)**
   
   **Simple explanation**: Like two people agreeing on what language to speak.
   
   - Agent sends an **SDP Offer** (Session Description Protocol) - a text file listing capabilities
   - SDP describes: "I can handle Opus audio at 48kHz, I support encryption"
   - LiveKit server responds with an **SDP Answer**: "I also support Opus at 48kHz, let's use that"
   - This negotiation happens **over the WebSocket**, not WebRTC yet
   
   **What's in an SDP?**
   ```
   Audio: Opus codec, 48000 Hz, stereo
   Video: None (we're audio-only)
   Encryption: Yes, using DTLS
   ```

3. **ICE Candidate Exchange**
   
   **Simple explanation**: Like exchanging addresses so you can reach each other.
   
   - **ICE (Interactive Connectivity Establishment)** finds the best network path
   - Both sides exchange **ICE candidates** (potential IP:port combinations where they can be reached)
   - Your computer might have multiple addresses:
     - Private IP: `192.168.1.5:12345` (only works inside your home network)
     - Public IP: `203.0.113.42:54321` (your router's address on the internet)
     - Relay address: `relay.livekit.io:3478` (a middleman if direct connection fails)
   - Uses **STUN servers** to discover your public IP address (you can't know this from inside your network)
   - If direct connection fails, falls back to **TURN relay servers** (a middleman that forwards packets)
   
   **The process**: Both sides try each address until they find one that works.

4. **WebRTC Peer Connection Established**
   
   **Simple explanation**: Like setting up a secret code so only you two can understand each other.
   
   - Once ICE succeeds (you found each other's address), you need to secure the connection
   - **DTLS handshake**: Both sides exchange encryption keys securely
   - **SRTP (Secure Real-time Transport Protocol)**: All audio packets are now encrypted before being sent over **UDP**
   - This is a **separate connection** from the WebSocket

### Summary: The 4-Step Connection Flow

```
Step 1: WebSocket Opens (TCP)
Agent ←→ LiveKit: "Hello, I'm authenticated"

Step 2: SDP Negotiation (over WebSocket)
Agent → LiveKit: "I can do Opus audio"
LiveKit → Agent: "Me too! Let's use Opus"

Step 3: ICE Exchange (over WebSocket)
Agent → LiveKit: "Try reaching me at 203.0.113.42:54321"
LiveKit → Agent: "Got it! Try me at 198.51.100.10:9000"
[Both try connecting... Success!]

Step 4: WebRTC Connection (UDP - separate from WebSocket)
Agent ↔ LiveKit: [Exchange encryption keys via DTLS]
Agent ↔ LiveKit: [Audio packets now flow, encrypted with SRTP]

WebSocket stays open for room events, WebRTC carries the audio!
```

### Why Two Separate Connections?

| Aspect | WebSocket (Signaling) | WebRTC (Media) |
|--------|----------------------|----------------|
| **Protocol** | TCP (reliable, ordered) | UDP (unreliable, fast) |
| **Purpose** | Room state, participant join/leave, chat messages | Audio/video packets |
| **Latency** | ~50-200ms acceptable | Must be <100ms for natural conversation |
| **Packet Loss** | Retransmit until received | Drop and continue (better to skip a frame than freeze) |
| **Encryption** | TLS (WebSocket Secure) | DTLS + SRTP |

**Critical Insight**: If you tried to send audio over WebSocket (TCP), a single lost packet would **block the entire stream** while TCP retransmits it. This is called **Head-of-Line Blocking**. WebRTC's UDP approach says "if packet 47 is lost, just play packet 48—the user won't notice 20ms of missing audio."

### The `AutoSubscribe.AUDIO_ONLY` Parameter

```python
await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
```

This tells LiveKit: "When participants publish tracks, automatically subscribe to **audio tracks only**, ignore video."

**Why this matters**:
- Each subscribed track consumes bandwidth and CPU
- An AI voice agent doesn't need video—subscribing to it wastes resources
- In a room with 10 participants each publishing video, you'd be decoding 10 video streams for no reason

**Under the hood**: LiveKit sends a `subscribe` message over the WebSocket for each audio track, but **never** sends one for video tracks.

## In AgriSathi's Code

```python
# src/agent.py
await self.ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
```

**What happens**:
1. WebSocket opens to LiveKit Cloud
2. SDP negotiation: "I support Opus audio codec at 48kHz"
3. ICE finds best path (probably direct UDP if both are on good networks)
4. WebRTC connection established
5. When farmer starts speaking, their audio arrives as **RTP packets** over the WebRTC connection
6. When Gemini responds, agent sends audio back the same way

**The WebSocket stays open** the entire call to handle:
- New participants joining
- Participant disconnections
- Data messages (if you send text chat)
- Room closure events

## Common Debugging Scenarios

| Symptom | Likely Cause | Where to Look |
|---------|--------------|---------------|
| "Connected" but no audio | WebSocket OK, WebRTC failed | ICE candidates, firewall blocking UDP |
| Connection drops after 30s | WebSocket timeout | Check `LIVEKIT_URL` is correct, network stable |
| Audio choppy/robotic | Packet loss on WebRTC | Network quality, bandwidth constraints |

## User Notes
- Initial confusion: "Don't we use WebRTC for audio?" → **Correct**. WebSocket is just the control plane.
- Text messages *can* go over WebRTC DataChannels, but LiveKit typically uses the WebSocket for guaranteed delivery.
- The farmer's phone → Twilio → LiveKit uses **SIP over UDP**, which LiveKit then bridges to WebRTC for your agent.
