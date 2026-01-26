# Resolved Questions

> Archive of answered questions for reference.

---

## Session 1 (2026-01-22)

### Q: Vector DB vs MongoDB for user memory?
**Answer**: Use MongoDB because:
- Only storing 5-10 fields per user
- No semantic search needed
- Free tier is plenty

**Key Learning**: Vector DBs are for semantic similarity search, not simple key-value.

---

### Q: LiveKit turn detector vs Gemini built-in?
**Answer**: Start with Gemini's VAD because:
- Simpler setup
- LiveKit's requires separate STT

**Key Learning**: Start simple, add complexity only when needed.

### Q: Call Flow Understanding
**Asked**: 2026-01-22
**Answer**: User correctly identified: Twilio -> SIP -> LiveKit Room -> Agent.
**Refinement**: Clarified that Agent is a "Worker" process that connects to the room, not just "sitting" in the cloud.
**Status**: MASTERED

---

### Q: What is `logging.basicConfig(level=logging.INFO)`?
**Asked**: 2026-01-25
**Answer**: It's a "quick-start" setup for the Python logging system. It configures the **Root Logger** (the master logger) to show messages of importance `INFO` and higher. Without it, your application might stay silent when things happen because it won't know where to print the messages.
**Key Learning**: `basicConfig` is for global setup; `getLogger` is for modular logging.

### Q: In production, do we use a logger or basicConfig only?
**Asked**: 2026-01-25
**Answer**: In production, we use **both**. `basicConfig` is used once (in `main.py`) to set global rules, and `logging.getLogger(__name__)` is used in every other module to ensure we can trace logs back to exact files and potentially change log levels for specific components.
**Status**: MASTERED

---

*Answered questions are moved here automatically*
