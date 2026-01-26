# AgriSathi - AI Context Memory

> Quick status for AI. Read `INSTRUCTIONS.md` for full rules.

## Status
| Field | Value |
|-------|-------|
| **Phase** | 1 - Minimal Agent BUILT (Learning Deep Concepts) |
| **Last Session** | 2026-01-25 |
| **Next Action** | Run agent in dev mode and test |
| **Blockers** | None |

## What Exists (Code)
- `src/config.py` - Configuration validation (MASTERED)
- `src/agent.py` - AgriSathiAgent class with Gemini Realtime
- `src/main.py` - Worker entrypoint (import fixed)
- `src/prompt.py` - Optimized system prompt for AgriSathi
- `src/tools/` - Integration tools (Registration, Web Search, Database)
- `.env.example` - All required env vars documented

## Concepts Covered
- [x] Call Flow (Twilio → SIP → LiveKit → Room → Agent) - MASTERED
- [x] **WebRTC Connection Flow (SDP → ICE → DTLS → SRTP)** - **MASTERED** ✅
- [x] **Async/Await & Event Loop** - **MASTERED** ✅
- [x] **LiveKit Agent Structure (Worker, Job, Room) - MASTER REFERENCE CREATED** ✅
- [x] Config Pattern (@classmethod) - MASTERED
- [x] **Complete AgriSathi Architecture (CODE_EXPLANATION_1.md)** - **MASTER REFERENCE CREATED** ✅

[x] **Session Resumption**:
    - Loaded context from `README.md`, `current_session.md`, and `INSTRUCTIONS.md`.
    - Synchronized memory with physical files (`prompt.py`, `src/tools/` detail added to README).
    - Synchronized environment context (using `uv` as package manager).
    - Created testing implementation plan.

## Available Workflows
| Workflow | Purpose |
|----------|---------|
| `/resume-session` | Load context at session start |
| `/save-session` | Save progress with dedup |
| `/end-session` | Archive and close the day |
| `/explain` | Deep explanation of any topic |

## Recent Decisions
1. ✅ Use MongoDB (free tier) for user memory
2. ✅ Use Gemini's built-in turn detection first
3. ✅ Approved project folder structure
4. ✅ User-triggered saves (`/save-session`) instead of relying on AI auto-save
5. ✅ Use `uv` as the primary package manager and `uv run` for execution
6. ✅ Technical explanations must include beginner-friendly analogies

## Read Next
1. `current_session.md` - Active work
2. `concepts/core/async_and_event_loop.md` - Currently reading
