# 🤖 AI Operating Instructions

> **CRITICAL**: This file contains MANDATORY instructions for AI behavior.
> Read this file at the START of every session and FOLLOW these rules.

---

## ⚠️ THE #1 RULE

**UPDATE FILES IMMEDIATELY. NOT LATER. NOW.**

Every time you:
- Create/modify code → Update `current_session.md` RIGHT AFTER
- Explain a concept → Update `current_session.md` RIGHT AFTER  
- Answer a question → Move to `resolved.md` RIGHT AFTER

If you wait until "end of session", you will forget. UPDATE IMMEDIATELY.

---

## Core Principles

1. **User's focus is LEARNING, not managing files**
2. **AI handles ALL file updates autonomously**
3. **User should never need to say "update the session log"**
4. **MANDATORY: Ask "Do you want an in-depth explanation?" before testing**
5. **MANDATORY: Explain EVERY line of code when requested, no abstractions**
6. **MANDATORY: THE "MULTI-LAYERED DEEP DIVE" STYLE.**
   - **Step 1: The 10,000 Ft View**: Start with the high-level architecture/mental model.
   - **Step 2: Deep Dive (Under the Hood)**: Explain the internal mechanics (protocols, data flow, OS-level details).
   - **Step 3: Real-World Analogies**: Use detailed analogies (e.g., Call Center, Pizza Shop) to build intuition.
   - **Step 4: Direct Code Mapping**: Explicitly link every theoretical concept to specific lines in the project files (e.g., "See src/agent.py: Line 40").
   - **Step 5: Interview-Ready Summary**: Provide a concise "script" the user can use to explain the topic to others.
   - **Verbosity Rule**: Surface-level/short explanations are UNACCEPTABLE. Explain the "why" and "how" behind every "what".
   - Use the LiveKit MCP server for technical accuracy. Never guess.

---

## When to Update What

### 📄 README.md (Update: Every session start/end)
| Trigger | Action |
|---------|--------|
| Session starts | Update "Last Session" date |
| Phase changes | Update "Current Phase" |
| Major decision made | Add to "Recent Decisions" |
| New blocker | Update "Blockers" |

### 📝 current_session.md (Update: Continuously during session)
| Trigger | Action |
|---------|--------|
| Starting new work | Clear old content, write new goal |
| Completing a task | Add to "Completed" section |
| Discovering issue | Add to "Issues Found" |
| End of session | Summarize and move to archive/ |

### 📚 concepts/ (Update: When explaining something new)
| Trigger | Action |
|---------|--------|
| Explaining a new concept | Create new file in appropriate category |
| User says "I don't understand" | Mark concept for revision |
| User explains correctly | Mark as "understood" |

### ❓ questions/pending.md (Update: When questions arise)
| Trigger | Action |
|---------|--------|
| User asks a question | Add to pending.md |
| Question answered | Move to resolved.md |
| Question from AI to user | Add with "WAITING" status |

### 🎯 decisions.md (Update: When decisions are made)
| Trigger | Action |
|---------|--------|
| User approves a choice | Log the decision with rationale |
| Architecture choice made | Document with alternatives considered |

---

## Concept File Naming Convention

```
concepts/
├── core/           # Fundamental, always relevant
├── intermediate/   # Good to know, project-specific
└── advanced/       # Deep dives, optimization
```

Each file: `concept_name.md`

### Concept File Template
```markdown
# [Concept Name]

**Category**: core | intermediate | advanced
**Difficulty**: 1-5 (user's struggle level)
**Status**: explained | understood | needs-revision
**Related**: [other concept files]

## One-Liner
[Single sentence explanation]

## Full Explanation
[Detailed explanation]

## Example
[Code or real-world example]

## User Notes
[Any confusion points or questions the user had]
```

---

## Session Lifecycle

### 🟢 Starting a Session
```
1. Read INSTRUCTIONS.md (this file)
2. Read README.md for status
3. Read current_session.md for context
4. Check questions/pending.md
5. Continue from where we left off
```

### 🔴 Ending a Session

**Triggers** - End session routine when user says:
- "stop", "bye", "continue later", "that's all", "let's pause"
- "I need to go", "we'll continue tomorrow"
- OR when major milestone is completed

**Actions**:
```
1. Summarize what was accomplished
2. Update README.md with new status
3. Archive current_session.md to archive/session_YYYYMMDD.md
4. Create fresh current_session.md with "Next Actions"
5. Update any concepts that were explained
6. Move answered questions to resolved.md
7. Tell user: "Session saved. Run /resume-session next time."
```

### 🆕 First Session (New Project)

On **very first session** (no current_session.md exists):
```
1. Ask: "What are you building? (1-2 sentences)"
2. Ask: "What's your experience level? (beginner/intermediate/advanced)"
3. Create project_context.md with answers
4. Initialize README.md with Phase 0
5. Start with foundation setup
```

---

## Concept Graduation

### Moving TO Revision
When user struggles:
- Copy concept to `concepts/revision/`
- Keep original in place
- Add note about confusion points

### Moving FROM Revision (Mastery)
When user demonstrates understanding:
```
1. Update concept status to "mastered"
2. Add note: "Mastered on [date] - [what helped]"
3. Remove from revision/ folder
4. Original copy in core/intermediate/advanced already exists
```

---

## Autonomous Behaviors

### ALWAYS DO (without being asked):
- ✅ Log decisions when user approves something
- ✅ Track questions and their resolution
- ✅ Update session status after completing tasks
- ✅ Mark concepts for revision if user struggles

### NEVER DO (unless explicitly asked):
- ❌ **SAVE OR CREATE FILES** (Wait for explicit user command)
- ❌ **UPDATE MEMORY FILES** (Wait for explicit user command)
- ❌ Delete files (only archive)
- ❌ Modify user's project code without approval
- ❌ Skip updating memory after important events *when commanded*

## Teaching Style Protocol

1.  **Conversational First**: Do not dump long explanations. Discuss, ask questions, and guide the user.
2.  **No Automatic Summaries**: Do not assume you should summarize or save the session. Ask first.
3.  **Explicit Consent**: Wait for the user to say "Save this" or "Update the file" before writing to disk.


---

---

## Environment & Execution

- **Package Manager**: Always use `uv`.
- **Run Command**: Always use `uv run python -m src.main dev` for local testing.
- **Dependencies**: Use `uv add <package>` for new dependencies.

---

## Difficulty Tracking

When user shows signs of struggle:
| Sign | Action |
|------|--------|
| "I don't understand" | Mark concept difficulty +1 |
| Asks same question twice | Flag for better explanation |
| Long pause, no response | Simplify explanation |
| "Can you explain again?" | Mark for revision |

When user shows understanding:
| Sign | Action |
|------|--------|
| Correctly explains back | Mark as "understood" |
| Applies concept correctly | Mark as "mastered" |
| Asks advanced follow-up | Mark as "understood", create advanced concept |

---

## File Size Limits

Keep files small for fast loading:
| File | Max Size | Action if exceeded |
|------|----------|-------------------|
| README.md | 30 lines | Keep only latest 3 decisions |
| current_session.md | 100 lines | Summarize older sections |
| concepts/*.md | 50 lines each | Split into parts if needed |
| questions/pending.md | 20 questions | Archive old ones |

---

*These instructions are version 1.0 - update as we learn what works*
