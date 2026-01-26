# AgriSathi Code Explanation: Master Reference

This file contains the verbatim deep-dive explanations for the AgriSathi project, focusing on reasoning, intuition, and line-by-line logic.

---

## 📋 Main Topics Covered
1. The Entrypoint: `main.py` & The Worker
2. The Agent "Wake Up": Imports & Structure
3. Execution Logic (`entrypoint`) - Part A: Connection & Identity
4. Execution Logic (`entrypoint`) - Part B: Database Deep Dive
5. Execution Logic (`entrypoint`) - Part C: Prompt Engineering
6. Execution Logic (`entrypoint`) - Part D: The Session Engine & Tools
7. The Session Engine: `AgentSession` & Interruption Architecture
8. The Registration Tool (`src/tools/registration.py`)
9. The Web Search Tool (`src/tools/web_search.py`)
10. Architecture Philosophy: Decoupling vs. Monolith

---

## 1. The Entrypoint: `main.py` & The Worker

### The 10,000 Ft View
Before we talk about AI or audio, we need an **Entrypoint**. This is the front door of your application. In LiveKit, your agent doesn't just "run" like a normal script; it waits for a signal. The `main.py` starts a **Worker**, and that worker's only job is to watch for incoming calls and hand them over to your "Entrypoint" function in `agent.py`.

### Deep Dive (Under the Hood)
When a call arrives, LiveKit creates a specialized object called **`JobContext`** (often shortened to `ctx`). This is the most important variable in the entire first phase of the call.
- **Why it exists**: The `JobContext` carries the **Token**, the **Room Name**, and the **Participant Info**.
- **The Logic**: Without `ctx`, your code wouldn't know which room to join. It's the umbilical cord between your Python code and the LiveKit Server. When you call `await ctx.connect()`, you are telling the worker: *"Okay, I've seen the job, now actually plug me into the audio stream so I can start listening."*

### Real-World Analogy: The Dispatch Operator
Imagine a large taxi company. 
- **`main.py`** is the **Dispatch Office** that stays open 24/7.
- **A "Job"** is when a customer calls for a ride.
- **`JobContext` (ctx)** is the **Manifest** the operator hands to the driver. It contains the pick-up address (Room Name) and the customer's name (Participant Identity). 
- The driver (your `entrypoint` function) reads the manifest and says, *"Got it, I'm heading to that address now"* (`ctx.connect()`).

### Direct Code Mapping
- **`src/main.py: L21-25`**: Here, `cli.run_app` tells the worker: *"Start the office and use `entrypoint` as the driver's instructions."*
- **`src/agent.py: L31`**: `async def entrypoint(ctx: JobContext):` — This is where the driver receives the manifest.
- **`src/agent.py: L37`**: `await ctx.connect(...)` — This is where the driver actually arrives at the customer's house and starts the session.

---

## 2. The Agent "Wake Up": Imports & Structure

### The Bridge: From Worker to Agent
We just saw how `main.py` acts as the **Dispatcher**. It tells the worker: *"When a call comes in, run the `entrypoint` function in `agent.py`."*
But before `entrypoint` can run, Python reads the file from top to bottom. It needs to load the **Tools** (Skills) and define the **Personality** (Class) of the agent. This is the "Wake Up" phase.

### Deep Dive: The Imports (The "Tool Shelf")
At the top of `src/agent.py`, we import specific **Plugins** for things like LLM (Google Gemini), TTS (Cartesia), and VAD (Silero).
- **The Reasoning**: This stays modular. Think of this as stocking the shelves before opening a shop. If we want to change a tool later, we just swap the "brand" on the shelf (the import) without rewriting our entire store logic.
- **`ALL_TOOLS`**: We import this list from our `src/tools` folder. We keep tool code separate so `agent.py` doesn't get cluttered. 

### Deep Dive: The `AgriSathiAssistant` Class & `super().__init__`
```python
class AgriSathiAssistant(Agent):
    def __init__(self, instructions: str) -> None:
        super().__init__(
            instructions=instructions,
            tools=ALL_TOOLS,
        )
```
- **Inheritance (`class ...(Agent)`)**: Our assistant **inherits** from LiveKit's base `Agent`. This is the "Skeleton" that already knows how to listen and speak; we just add the "Brain."
- **The "Backpack" (`super().__init__`)**: This is the most critical setup line. 
    - **Analogy**: Imagine you buy a car chassis (the base `Agent`). You want to add your special paint (`instructions`) and a GPS (`tools`). 
    - **The Logic**: The `super().__init__` call hands these items to the "Factory" (the Parent Class) so it can wire them deep into the car's internal system. 
    - **The Result**: Without this line, the "engine" (audio buffers, LLM connections) would never start. By calling `super()`, we ensure the complex LiveKit background code runs for our specific agent.
- **The Magic of `tools=ALL_TOOLS`**: This registers our functions with the LLM. It's the moment the AI discovers it has the power to Google Search or Register a Farmer.

### Doubts and Revision Notes
- **Doubt**: *"Can I just write `self.tools = tools` instead?"*
    - **Answer**: No. Because the base `Agent` class needs to do professional "wiring" (JSON schema generation) behind the scenes to make those tools visible to the AI. Always use `super()`.
- **Doubt**: *"What if I forget to inherit from `Agent`?"*
    - **Answer**: The LiveKit worker will error out because it only knows how to handle objects that follow the `Agent` blueprint.

---

## 3.A Execution Logic (`entrypoint`) - Part A: Connection & Identity

Once the Worker assigns a job to our "Driver" (`entrypoint`), the very first few lines are about **opening the door** and **checking the ID**.

### 1. The Room Connection (`ctx.connect`)
```python
await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
```
- **The Logic**: The JobContext (`ctx`) has a "Room" variable. Calling `connect` is the final step where the agent actually "walks into" that room.
- **`auto_subscribe=AutoSubscribe.AUDIO_ONLY`**: Since AgriSathi is a voice assistant, we don't want to receive video data (it would waste bandwidth and CPU). We tell the server: *"Only send me the sound."*

### 2. Identity Extraction (`wait_for_participant`)
```python
participant = await ctx.wait_for_participant()
phone = participant.identity
```
- **The Reasoning**: The room is "dark" for a split second until it detects a participant. We use `await` to pause until the bridge is stable.
- **The Identity**: In a phone call (SIP), the participant's "Identity" is their phone number. This is our "Single Source of Truth."
- **Why this is better than asking?**: As verified in our discussion, asking for a phone number via voice leads to STT errors ("7 thousand" vs "7000"). Extracting it from the system metadata is 100% accurate and faster for the user.
- **The Global Storage**: We call `set_current_phone(phone)` to store this number in a shared location in `src/tools/registration.py`.
    - **Doubt**: *"Why a global variable?"*
    - **Answer**: Because variables in Python are local to their file. The registration tool in another file needs to know this phone number without the AI having to "tell" it. The global variable acts as a bridge between the **Call Session** and the **Tool Actions**.

---

## 3.B Execution Logic (`entrypoint`) - Part B: Database Deep Dive

### The 10,000 Ft View
AgriSathi uses **SQLite** as its internal memory. Unlike big databases that live on separate servers, SQLite is **file-based**. It lives in `data/agrisathi.db`. It's lightweight, requires zero setup, and is perfect for a local assistant.

### Deep Dive: The Schema & Setup
The "Schema" is the structure of the filing cabinet. We defined a table called `farmers` with the following rules:
- **Phone as Primary Key**: We use the phone number as the unique ID. This is our "Single Source of Truth." Two farmers might share a name, but never a phone number.
- **Location Refactor**: We store `place` (village/city) and `state` separately for better accuracy.
- **Automatic Setup**: We use `CREATE TABLE IF NOT EXISTS`. 
    - **Logic**: This is an optimized check. It doesn't rebuild the table every time; it simply checks if the "drawer" exists and moves on. If it's missing, it creates it.

### Deep Dive: Connection vs. Cursor
- **Connection (`conn`)**: This is the **Pipe**. It maintains the physical link to the file on your hard drive. 
- **Cursor (`cursor`)**: This is the **Worker/Assistant**. You give commands to the cursor (like `execute`), and it goes into the file to fetch or write the data.

### Deep Dive: SQL Execution & Parameter Binding
```python
cursor.execute("SELECT * FROM farmers WHERE phone = ?", (phone,))
```
- **The `?` Placeholder (Parameter Binding)**: This is a critical security feature. 
    - **Why not f-strings?** If we wrote `f"SELECT... WHERE phone = {phone}"`, a hacker could inject malicious SQL commands (SQL Injection). 
    - **How it works**: By using `?` (the tuple), we tell SQLite: *"Here is the template. Please verify and sanitize this variable `phone` before putting it into the query."* It treats the input strictly as data, never as executable code.
- **Cursor Memory**: The `cursor` is stateful. When you run `execute`, it finds the results but doesn't hand them all to you immediately (to save RAM). You have to ask for them using `fetchone()` (get one result) or `fetchall()` (get all results).

### Advanced Concept: Indexing
- **What is it?**: An Index is like the "Table of Contents" at the back of a book. Without an index, if you search for "Ramesh," the database has to scan every single row (Full Table Scan). With an index, it jumps straight to "R".
- **Primary Key Magic**: In SQLite, when we define `PRIMARY KEY (phone)`, it **automatically** creates an index on the `phone` column. 
    - **Result**: Our lookups happen in `O(log n)` time (instant) instead of `O(n)` time (slow). We don't need to add manual indexing because `PRIMARY KEY` does it for us!

### Direct Code Mapping
- **`src/tools/database.py: L30-40`**: The `CREATE TABLE` command defining our data structure.
- **`src/tools/database.py: L62`**: The parameterized query `WHERE phone = ?` for secure lookup.

---

## 3.C Execution Logic (`entrypoint`) - Part C: Prompt Engineering

### The 10,000 Ft View
The **System Prompt** is the "Personality" of the agent. But a truly smart agent doesn't have a static personality. It changes based on who is calling. We take the "Static Prompt" (base rules) and merge it with "Dynamic Data" (the farmer's history).

### Deep Dive: The Base Prompt (`src/prompt.py`)
This file contains the **SYSTEM_PROMPT**. It’s the "Law of the Land."
- **The Critical Rule**: Language Mirroring. *"ALWAYS reply in the SAME language the user speaks."*
- **The Reasoning**: Direct translation often sounds robotic. By telling the AI to "Mirror," we allow it to use the natural rhythm of Hinglish if the farmer does.

### Deep Dive: Dynamic Construction (The "Briefing")
Back in `agent.py`, we construct `custom_instructions`. 

**The Branching Logic**:
- **Case A: Existing User**
    - **The Logic**: We take the `SYSTEM_PROMPT` and append: *"You are talking to Ramesh from Lucknow. He grows Rice. His last conversation was about pests."*
    - **The Why**: This is how we achieve **Instant Personalization**. The LLM reads this and immediately knows how to greet the user without asking redundant questions.
- **Case B: New User**
    - **The Logic**: We append instructions like: *"This is a new user. Be extra warm. Introduce yourself. Gently ask for their name, place, and state."*

### Real-World Analogy: The Briefing Folder
Imagine a diplomat going into a meeting.
- **`SYSTEM_PROMPT`**: This is the **Diplomatic Code of Conduct** (Be polite, speak their language, don't share secrets). It never changes.
- **`custom_instructions`**: This is the **Briefing Folder** she receives 5 minutes before the meeting. It says, *"The person you are meeting is Mr. Sharma. He likes tea and is interested in irrigation."* 
- **The Result**: She combines her Conduct with the Briefing to have a perfect meeting.

---

## 3.D Execution Logic (`entrypoint`) - Part D: The Session Engine & Tools

### The 10,000 Ft View
Now that the agent knows *who* is calling (Identity/DB) and *how* to behave (Prompt), it's time to **Start the Engine**. This is where we assemble the critical components: the Ears (STT), the Brain (LLM), the Mouth (TTS), and the Reflexes (VAD).

### Deep Dive: The `AgentSession` Configuration
```python
session = AgentSession(
    stt=DeepgramSTT(model="nova-3", language="hi"),
    llm=google.LLM(model="gemini-2.5-flash"),
    tts=CartesiaTTS(model="sonic-3", ...),
    vad=silero.VAD.load(),
    turn_detection=MultilingualModel(),
)
```
1.  **STT (Deepgram Nova-3)**: "The Ears." We explicitly choose `nova-3` because it has superior Hindi/Hinglish transcription capabilities compared to standard models.
2.  **LLM (Gemini 2.5 Flash)**: "The Brain." Fast, efficient, and handles the `SYSTEM_PROMPT` instructions.
3.  **TTS (Cartesia Sonic-3)**: "The Mouth." This is an ultra-low latency model. Standard TTS can take 2-3 seconds; Cartesia takes <300ms, making the conversation feel real.
4.  **VAD (Silero)**: "The Reflexes." VAD stands for **Voice Activity Detection**. It's a small, fast AI that runs *locally* (on the server, not the cloud) to check "Is someone speaking?".
    -   **Why crucial?**: Without VAD, the agent would keep talking over you. With VAD, it knows to stop listening when you pause and stop talking when you interrupt.
5.  **Turn Detection**: This decides "Did the user finish their sentence, or just take a breath?".

### Deep Dive: Starting the Drive (`session.start`)
```python
await session.start(
    room=ctx.room,
    agent=AgriSathiAssistant(instructions=custom_instructions),
)
```
-   **The Fusion**: This is the line where everything clicks together.
-   We take the **Engine** (`session` with all its tools).
-   We connect it to the **Road** (`ctx.room`).
-   We put our **Driver** (`AgriSathiAssistant`) in the seat, armed with their **Briefing** (`custom_instructions`).

### The Result
Once this line runs, the agent is "Alive." It is listening to the room, processing audio through Deepgram, thinking with Gemini, and ready to speak with Cartesia.

---

## 4. The Session Engine: `AgentSession` & Interruption Architecture

### The 10,000 Ft View
`AgentSession` is the **Operating System** of your agent. It wires the Ears (STT), Brain (LLM), and Mouth (TTS) into a single, automated loop. 

### Deep Dive: VAD vs. Turn Detection (The "Silence" Paradox)
Silence is ambiguous. Does it mean "I'm done" or "I'm thinking"? 
-   **VAD (The Reflex)**: **L108** in `agent.py`. It only detects "Noise vs. Silence." It is ultra-fast. Its only job is **Barge-in**: cut the AI's audio the moment the human starts making noise.
-   **Turn Detection (The Judge)**: **L110** in `agent.py`. It waits for a VAD silence, then analyzes the grammar/context. If a sentence is incomplete, it tells the agent to wait; if complete, it signals the "Reply" sequence.

---

## 5. The Registration Tool (`src/tools/registration.py`)

### Line-by-Line Breakdown:
- **`_current_phone` (L15)**: A global "baton." Since the LLM doesn't speak the phone number, we save it here during the `entrypoint` call so the tool can find it later.
- **`@function_tool()` (L24)**: A decorator that performs **Introspection**. It scans the function arguments and docstrings to generate a JSON Schema that Gemini understands.
- **The DB Call (L46)**: Uses a **Parameterized Query** (`INSERT OR REPLACE`) to ensure security and uniqueness.

---

## 6. The Web Search Tool (`src/tools/web_search.py`)

### The "Nesting" Strategy (AI inside a Tool)
To avoid reading dry technical data to farmers, we use a **secondary Gemini call** inside the tool.
-   **Step 1 (Grounding)**: Gemini Search Tool finds raw data.
-   **Step 2 (Interpretation)**: A specific "Inner Prompt" (**L59**) instructs a second Gemini instance to translate that raw data into actionable, jargon-free advice (e.g., converting "0mm precip" into "Barish nahi hai").

---

## 7. Architecture Philosophy: Decoupling vs. Monolith

### Why `AgentSession` and `AgriSathiAssistant` are separate:
-   **`AgentSession` (Hardware)**: Manages WebSocket connections and audio buffers. It is stateless.
-   **`AgriSathiAssistant` (Software)**: Manages personality, chat history, and tools.
-   **The Benefit**: This allows us to **Mid-Call Evolve**. You can keep the phone call connected (One Session) but switch the "Agent" from a *Farming Expert* to a *Vendor Expert* by simply swapping the class instance, without reconnecting the hardware.

---

## 8. In-Depth Tool Walkthrough: Registration (`src/tools/registration.py`)

### A. The Global State Pattern (The "Baton")
```python
# L15: Module-level storage
_current_phone: str = ""

# L18-21: The setter called by entrypoint
def set_current_phone(phone: str):
    global _current_phone
    _current_phone = phone
```

**Line-by-Line Logic**:
- **L15**: `_current_phone` is a module-level variable. In a LiveKit worker handling one session at a time, this acts as "session memory."
- **L20**: `global _current_phone` is mandatory. Without this keyword, Python would create a *new local variable* instead of updating the one at the top of the file.
- **The Why**: Gemini doesn't know the phone number. We extract it from `participant.identity` in the entrypoint and store it here so tools can access it later without the AI having to speak it.

### B. The Function Tool Decorator
```python
# L24: Introspection magic
@function_tool()
async def register_farmer(
    context: RunContext,
    name: str,
    place: str,
    state: str,
    crops: str,
    language: str = "hindi",
):
    """
    Registers a new farmer into the database for personalized service.
    Call this tool when the user wants to sign up or register.
    
    Args:
        name: The full name of the farmer (e.g., Ramesh Kumar).
        place: The village or city where the farmer lives (e.g., Lucknow).
        state: The state where the farmer lives (e.g., Uttar Pradesh).
        crops: The main crops the farmer grows, comma-separated (e.g., wheat, rice).
        language: Preferred language - "hindi", "english", or "hinglish". Default is "hindi".
    """
```

**Line-by-Line Logic**:
- **L24**: `@function_tool()` performs **Python Introspection**. It reads the function signature and docstring to generate a JSON Schema that Gemini understands.
- **L25**: `async def` makes this non-blocking. The agent can still listen while waiting for database I/O.
- **L26**: `context: RunContext` is injected by LiveKit. It contains session metadata and chat history.
- **L33-43**: The **docstring** is critical. This is the "instruction manual" Gemini reads to know *when* to call this tool and *what parameters* to extract from the user's voice.

### C. The Database Call
```python
# L44-46: Accessing the global and persisting to DB
global _current_phone
logger.info(f"Registering: {name}, {place}, {state}, {crops}, lang={language} for {_current_phone}")
db.register_farmer(_current_phone, name, place, state, crops, language)
return f"Registration complete for {name} ji from {place}, {state}. I will remember your preference for {language}."
```

**Line-by-Line Logic**:
- **L44**: `global _current_phone` tells Python to read from the module-level variable.
- **L46**: `db.register_farmer(...)` calls the database singleton. It uses a parameterized query (`INSERT OR REPLACE`) for security.
- **L47**: The return string goes to Gemini's "brain" as a `tool_response`. Gemini then decides how to verbally confirm this to the user.

---

## 9. In-Depth Tool Walkthrough: Web Search (`src/tools/web_search.py`)

### A. Setting Up the Search Client
```python
# L41: Local client instantiation
client = genai.Client(api_key=Config.WEB_API_KEY)
model_id = "gemini-2.5-flash"

# L45-47: Enabling Google Search
google_search_tool = Tool(
    google_search=GoogleSearch()
)
```

**Line-by-Line Logic**:
- **L41**: We create a *dedicated* Gemini client for search. This isolates it from the main agent's LLM connection.
- **L45-47**: `GoogleSearch()` is the **Grounding Tool**. It allows Gemini to query the live web instead of relying on training data.

### B. Configuration for Determinism
```python
# L50-54: The AI's "rules of engagement"
config = GenerateContentConfig(
    tools=[google_search_tool],
    response_modalities=["TEXT"],
    temperature=0.2,
)
```

**Line-by-Line Logic**:
- **L51**: `tools=[google_search_tool]` plugs the search capability into this specific Gemini instance.
- **L52**: `response_modalities=["TEXT"]` forces text-only output (no images/audio).
- **L53**: `temperature=0.2` is the **critical setting**. Scale: 0.0 (pure logic) to 1.0 (creative). We keep it low for factual accuracy.

### C. The "Inner Interpreter" Pattern
```python
# L59-74: The nested AI prompt
system_instruction = f"""
You are an expert agricultural interpreter for Indian farmers. 
Your goal is to use the Google Search tool to find information and then convert that raw data into a simple, actionable answer.

**Rules:**
1. No jargon (e.g., instead of 'precipitation 0%', say 'barish nahi hogi').
2. Focus on **ACTION**: What should the farmer DO?
4. Today's date is {today}.

**Examples:**
- **User Query**: "Delhi weather"
  - **Your Answer**: "Mausam saaf hai. Fasal katne ke liye aaj ka din badhiya hai. Barish ki koi sambhavna nahi hai." (Clear weather. Good day for harvesting.)
"""

# L76: Wrapping the user's query
focused_query = f"{system_instruction}\n\nUser Query: {query}"

# L78-82: The recursive AI call
response = client.models.generate_content(
    model=model_id,
    contents=focused_query,
    config=config,
)
```

**Line-by-Line Logic**:
- **L59-74**: This is **Edge Intelligence**. We instruct a secondary Gemini pass to act as a "translator" between raw search data and farmer-friendly advice.
- **L76**: We combine the system instruction with the user's specific query.
- **L78**: `generate_content` executes the search + interpretation in one call. This is "AI within a Tool."
- **The Result**: Instead of returning "Precipitation: 0mm", the tool returns "Barish nahi hogi" (No rain).

### D. Error Handling
```python
# L88-90: Graceful degradation
except Exception as e:
    logger.error(f"Error in web_search: {e}")
    return "Maaf kijiye, search mein problem aa gayi. Thodi der baad try karein."
```

**Line-by-Line Logic**:
- We wrap everything in `try/except` to prevent crashes.
- If the API fails, we return a polite error message in Hindi that the main agent can speak to the user.

---
