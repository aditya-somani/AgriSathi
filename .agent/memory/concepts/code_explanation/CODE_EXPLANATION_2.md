# 🧠 Deep Dive: Multi-Language Architecture & Tool Fixes

> **Goal**: Make AgriSathi truly multilingual (Hindi/English/etc.) and ensure it always speaks tool outputs.

---

## 1. The Architecture of Language Support

We moved from a **Static (Hardcoded)** model to a **Dynamic (State-Aware)** model.

### ❌ Old Way (Static)
1.  **Input**: Deepgram hardcoded to `'hi'` (Hindi).
2.  **Logic**: Prompt hardcoded with Hindi examples.
3.  **Output**: `web_search` output hardcoded to return Hinglish.

### ✅ New Way (Dynamic 3-Layer)

| Layer | Component | Function |
|-------|-----------|----------|
| **1. Acoustic** | **Deepgram STT** | Auto-detects *what* language is spoken (`language="multi"`). |
| **2. Logical** | **`detect_language` Tool** | Formalizes the decision ("User is definitely speaking English") and stores it in session state. |
| **3. Generation** | **Adaptive Prompting** | Tools and LLM read the session state to generate the correct output language. |

---

## 2. Code Walkthrough

### A. The "Ears": Deepgram Auto-Connect (`agent.py`)

We changed how the session starts. Instead of assuming Hindi, we let Deepgram decide.

```python
# src/agent.py

if stored_lang:
    # If we KNOW the user (database), use their preference
    stt_lang = LANGUAGE_CODE_MAP.get(stored_lang.lower(), 'hi')
    set_session_language(stored_lang.lower())
else:
    # If NEW user, turn on "Universal Mode"
    stt_lang = 'multi'  # <--- MAGIC HAPPENS HERE
    set_session_language("hindi") # Default fallback until detected
```

**Why**: `language='multi'` tells Deepgram to listen for *any* supported language and switch its transcription model on the fly.

### B. The "Brain": Explicit State Tracking (`tools/language_detection.py`)

The LLM needs to "know" that the language changed. We created a tool for this.

```python
# src/tools/language_detection.py

@function_tool()
async def detect_language(context: RunContext, detected_language: str):
    global _session_language
    _session_language = detected_language  # <--- Updates global state
    
    # Also save to DB for next time!
    db.update_language(registration._current_phone, detected_language)
    
    return f"Language set to {detected_language}."
```

**Why**: We need a single source of truth (`_session_language`) that *other* tools can read.

### C. The "Voice": Context-Aware Search (`tools/web_search.py`)

This is where the magic happens for the *user*. The search tool now checks the state before answering.

```python
# src/tools/web_search.py

# 1. READ the state
user_lang = get_session_language()

# 2. INJECT into prompt
system_instruction = f"""
...
**CRITICAL**: Respond in the user's language: {user_lang}.
...
**Examples**:
- If user lang is English: "Weather is clear..."
- If user lang is Hindi: "Mausam saaf hai..."
"""
```

**Why**: Previously, even if you spoke English, the tool returned Hindi text. Now, the prompt dynamically rewrites itself based on the session variable.

---

## 3. Fixing the "Silent Tool" Issue

**The Problem**: Llama-3.3 (via Groq) is powerful but gets confused by complex system prompts. When it got confused, it would call a tool but fail to generate the *follow-up speech*.

**The Fix (`prompt.py`)**: We simplified the instructions to be "Command Style" rather than "Narrative Style".

```python
## CRITICAL INSTRUCTIONS
1. **Detect Language**: ...
2. **Speak Tool Results**: 
   - After running `web_search`, you **MUST** verbally tell the user.
   - **NEVER** run a tool and stay silent.
```

**Concept**: **Chain-of-Command Prompting**. Instead of giving vague advice ("be helpful"), we give strict operational constraints ("Call tool X, then Speak Y").

---

## 4. Summary for Your Mental Model

Think of the new system like a **Translator with a Notepad**:
1.  **Deepgram** hears the sound and writes down the text (in whatever language).
2.  **LLM** reads the text. If it sees a new language, it writes "ENGLISH" on the Notepad (`detect_language`).
3.  **Web Search Tool** looks at the Notepad before answering. If it says "ENGLISH", it translates the weather report to English.
4.  **TTS** speaks whatever text comes out.

This ensures the entire pipeline—from ear to brain to mouth—is synchronized to the user's language.
