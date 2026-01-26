# 📞 Telephony & SIP (Session Initiation Protocol)

> How we bridge the "Old World" (Phone Lines) to the "New World" (Real-time AI).

---

## 🏛️ The Architecture

When you call a phone number, the signal travels over the **PSTN** (Public Switched Telephone Network). Our AI lives in a **WebRTC** room. SIP is the bridge.

### The Flow
```mermaid
graph LR
    User["📱 User Mobile"] -- "PSTN" --> Twilio["📞 Twilio (Gateway)"]
    Twilio -- "SIP (VoIP)" --> LiveKit_SIP["🌉 LiveKit SIP Service"]
    LiveKit_SIP -- "WebRTC" --> Room["🏠 LiveKit Room"]
    Room -- "Media" --> Agent["🤖 AgriSathi Agent"]
```

---

## 🗝️ Key Terms

### 1. SIP (Session Initiation Protocol)
The industry standard protocol for starting, managing, and ending voice/video calls over IP. Think of it as the "Handshake" for phone calls.

### 2. SIP Trunk
A "virtual phone line" that connects your PBX (or in our case, LiveKit) to the traditional phone network (PSTN) via a provider like Twilio.

### 3. Inbound Trunk
A configuration in LiveKit that defines how to handle incoming calls. It includes credentials and security settings to ensure only authorized providers (like Twilio) can send calls.

### 4. SIP Dispatch Rule
A set of logic in LiveKit that decides: *"When a call comes from Number X for Trunk Y, which room should it go to?"*
- **Example**: Match prefix `+1` -> Send to room `agrisathi_test`.

### 5. SIP Participant
Once a call is connected, the person on the phone appears in the LiveKit room as a normal "Participant," but with no data/video—only an audio track.

---

## 🔬 Why Twilio?
Twilio acts as our gateway. They handle the messy regulatory parts of owning a phone number and provide a clean API/SIP interface to forward that audio to our LiveKit server.

### The "Indian Number" Problem
- **Regulation**: India has strict TRAI regulations. To own a +91 number for VOIP, you often need a physical office in India or a GCL (Global Carrier License).
- **Alternative**: Use a US number. Most modern users have WhatsApp/VoIP, but for a "Real Call," a US Toll-Free or Local number is the fastest way to prototype.

---

## 🛠️ The Connection (The "Glue")
To connect them, we tell Twilio:
> "Whenever someone calls this number, send a SIP INVITE to `myserver.livekit.cloud`."

And we tell LiveKit:
> "Whenever you see a SIP INVITE from Twilio, accept it and put it in the room where AgriSathi is waiting."
