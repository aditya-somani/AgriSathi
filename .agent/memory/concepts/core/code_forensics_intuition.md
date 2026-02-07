# 🧠 Code Forensics: The Art of SDK Deduction

When working with cutting-edge or complex SDKs like **LiveKit Agents**, you will often find yourself in a situation where documentation is lagging behind features. This document outlines the **Code Forensics** methodology we used to master the internal workings of the library without a manual.

---

## 🏗️ Step 1: Inheritance Hunting (Finding the Ancestors)

In Python, classes often inherit massive amounts of functionality from their "parents." If a class like `AgentSession` seems small but does a lot (like firing events), it's probably inheriting that power.

### The Observation
We looked at the first line of `AgentSession` in the source code:
```python
class AgentSession(EventEmitter[EventTypes]):
```

### The Intuition
- **Identification**: `EventEmitter` is a universal software pattern (common in Node.js and Python).
- **The Deduction**: If it's an `EventEmitter`, it **MUST** have an `.on()` method, even if `AgentSession` doesn't define one itself.
- **The Action**: We searched for the parent class's `on` method to see its requirements.

---

## 📋 Step 2: Signature Forensics (Reading the Docstrings)

Once we found the `.on()` method, we looked at its "Signature" (the parameters it expects).

### The Observation
Inside the `EventEmitter` parent class (in the library files), we found:
```python
def on(self, event_type: str, callback: Callable):
    """Registers a listener for the specified event."""
```

### The Intuition
- **The Requirement**: We need a string (the event name) and a function (what to do when it happens).
- **The Logic**: To use this as a decorator, we use `@parent.on("event_name")`.

---

## 🚦 Step 3: Payload Triage (The "Source of Truth" Choice)

This is the most critical part of intuition. When presented with multiple strings (events) like `user_state_changed`, `user_input_transcribed`, and `conversation_item_added`, how do you choose the right one? 

We analyze the **Data Payload** (the variables inside the event) for its **Finality** and **Content**.

### 1. `user_state_changed` — The Acoustic Signal
- **Payload**: `old_state`, `new_state` (Literals like "speaking", "listening").
- **Deduction**: This is purely acoustic. It knows *noise* is happening, but it has no variable for *text*. 
- **Verdict**: Use for UI lights (Red/Green), not for logic.

### 2. `user_input_transcribed` — The Visual Stream
- **Payload**: `transcript` (string), `is_final` (boolean).
- **Deduction**: This is the "Ticker Tape." It fires 10 times a second. The `is_final` flag proves the system is still guessing. 
- **Verdict**: Use for real-time captions. Too unstable for business logic (like hanging up).

### 3. `conversation_item_added` — The Semantic Commit
- **Payload**: `item` (`ChatMessage` object).
- **Deduction**: In architecture terms, "Added" means "Stored in History." This event only fires when the system has reached a final, stable conclusion about what was said.
- **Verdict**: **The Source of Truth.** Use this for high-stakes decisions like hanging up, language detection, or sentiment analysis.

---

## 🧘 Mental Model Summary: The Courtroom Analogy

To understand these events, imagine a courtroom:
1.  **`user_state_changed`**: The witness opens their mouth to speak. (Signal)
2.  **`user_input_transcribed`**: The stenographer types what they *think* they hear in real-time. (Draft)
3.  **`conversation_item_added`**: The judge accepts the statement into the **Official Record**. (Commit)

**Always code against the Official Record.**
