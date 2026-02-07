# Key Decisions Log

> Permanent record of important decisions with rationale.

---

## Decision 1: Memory Storage
**Date**: 2026-01-22 | **Status**: ✅ Approved

**Choice**: MongoDB (free tier) over Vector Database

**Alternatives Considered**:
- Pinecone (vector DB) - overkill for 5-10 fields per user
- PostgreSQL - harder schema migrations for MVP

**Rationale**: Simple key-value lookup, free tier sufficient, can add vector search later if needed.

---

## Decision 2: Turn Detection
**Date**: 2026-01-22 | **Status**: ✅ Approved

**Choice**: Gemini's built-in VAD first, switch to LiveKit's if issues

**Alternatives Considered**:
- LiveKit multilingual turn detector - requires separate STT model

**Rationale**: Start simple, add complexity only if problems arise.

---

## Decision 3: Project Structure
**Date**: 2026-01-22 | **Status**: ✅ Approved

**Choice**: Modular structure with src/, tools/, database/, utils/

**Rationale**: Separation of concerns, each folder has one job.

---

## Decision 4: Memory System Design
**Date**: 2026-01-22 | **Status**: ✅ Approved

**Choice**: v2 design with autonomous AI updates, category-based concepts

**Rationale**:
1. User should focus on learning, AI handles file management.
2. ✅ User-triggered saves (`/save-session`) instead of relying on AI auto-save

---

## Decision 5: Package Manager
**Date**: 2026-01-22 | **Status**: ✅ Approved

**Choice**: Use `uv` as the primary package manager and `uv run` for execution

**Rationale**: Faster dependency resolution, matching user environment, and consistent execution via `uv run python -m src.main dev`.

---

*Add new decisions as they are made*

---

## Decision 6: Profile Update Logic
**Date**: 2026-01-28 | **Status**: ✅ Implemented

**Choice**: Partial update query in SQLite (dynamic query building)

**Alternatives Considered**:
- `INSERT OR REPLACE` - required fetching all data first or asking user for everything again.

**Rationale**: Allows users to update just one field (e.g., "Change my crop to Wheat") seamlessly without re-confirming name/location.
