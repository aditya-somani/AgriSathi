# 🧠 GEMINI.md - Learning & Development Guidelines for AgriSathi

> This file defines how we approach building AgriSathi - as a **learning journey**, not just a coding task.

---

## 🚨 MANDATORY: CONTEXT MEMORY RULES (AI MUST FOLLOW)

> **STOP. READ THIS FIRST. THIS IS NOT OPTIONAL.**

### The Problem You Must Solve
You (AI) are **stateless**. You have NO memory of previous sessions. The user has worked on this project across multiple sessions. If you don't read AND update the memory files, you will repeat old work and frustrate the user.

### At Session Start (ALWAYS DO THIS)
1. **Run `/resume-session`** workflow if user requests it
2. **Scan actual project files** (not just memory) to verify what exists
3. **If memory is out of sync with reality** → Fix memory FIRST, tell user what you corrected

### During Session (AFTER EVERY SIGNIFICANT ACTION)
Update `.agent/memory/current_session.md` IMMEDIATELY after:
- ✅ Creating or modifying a code file → Add to "Completed" list
- ✅ Explaining a concept → Add to "Concepts Explained" list  
- ✅ Answering a question → Move from `pending.md` to `resolved.md`
- ✅ Making a decision → Log in `decisions.md`

**DO NOT BATCH UPDATES. DO NOT WAIT UNTIL "LATER". UPDATE NOW.**

### At Session End (When user says stop/bye/continue later)
1. Update `current_session.md` with ALL completed work
2. Update `README.md` status fields
3. Move all answered questions to `resolved.md`
4. Tell user: "Session saved. Run `/resume-session` next time."

### Failure Consequences
If you fail to update memory:
- Next AI session will be BLIND to your work
- User will have to repeat themselves (FRUSTRATING)
- Project progress is LOST

---

## 🎯 Primary Goals (In Order of Priority)

1. **Understanding > Building** - If you can explain every line, you've succeeded even if the code doesn't work perfectly.
2. **Intuition Development** - Learn the "why" behind decisions, not just the "what."
3. **Production-Grade Practices** - Even in learning, we follow real-world standards.

---

## 📚 Learning Philosophy

### The Three Questions Rule
Before writing any code, we answer:
1. **What** are we building?
2. **Why** this approach over alternatives?
3. **How** does this fit into the bigger picture?

### The Explanation Test
> "If someone asks me about any line in this code, can I explain it?"

If the answer is "no" → we pause and learn before moving forward.

---

## 🏗️ Development Approach

### Iterative Cycle
```
┌─────────────────────────────────────────────────┐
│  1. UNDERSTAND → 2. PLAN → 3. BUILD SMALL →     │
│  4. TEST → 5. LEARN FROM ERRORS → 6. ITERATE    │
└─────────────────────────────────────────────────┘
```

### Phase Progression
| Phase | Focus | Success Criteria |
|-------|-------|------------------|
| **Phase 1** | Minimal Demo | Agent answers a call, says "Hello" |
| **Phase 2** | Add Tools | Weather, Web Search work |
| **Phase 3** | Add Memory | MongoDB stores user data |
| **Phase 4** | Polish | Error handling, logging, production-ready |

---

## 💬 Communication Style

### What I (AI) Will Do:
- ✅ **The Multi-Layered Deep Dive**: Every explanation will cover the High-level view, the Low-level mechanics, and a Mental Model (Analogy).
- ✅ **Direct Code Mapping**: I will always show you exactly where the theory connects to your code files.
- ✅ **Interview-Ready Summaries**: I will provide "scripts" you can use to explain these concepts to others.
- ✅ **Explain the "Why"**: No line of code goes unexplained. We focus on intuition, not just syntax.
- ✅ **Correct Your Intuition**: If you make a common assumption that's slightly off, I will clarify it with technical depth.

### What You Should Do:
- ✅ Ask "why?" whenever something is unclear
- ✅ Try to predict what comes next before I show you
- ✅ Attempt to explain back what you learned
- ✅ Don't rush - understanding takes time
- ✅ Keep notes of patterns you notice

---

## 📝 Documentation Standards

Every significant file will have:
1. **Header comment** explaining its purpose
2. **Inline comments** for non-obvious logic
3. **Docstrings** for functions/classes
4. **README section** explaining how it fits into the project

---

## 🧪 Testing Mindset

> "Untested code is broken code" - Every senior engineer ever

We will:
- Test after every small addition
- Learn to read error messages (they're your friends!)
- Use logging to understand what's happening
- Not fear breaking things - that's how we learn

---

## 🔍 Key Concepts We'll Master

### Architecture & Design
- [ ] Separation of Concerns
- [ ] Single Responsibility Principle
- [ ] Dependency Injection
- [ ] Configuration Management
- [ ] Error Handling Patterns

### Python Specific
- [ ] Async/Await patterns
- [ ] Context Managers
- [ ] Decorators
- [ ] Type Hints
- [ ] Environment Variables

### LiveKit Specific
- [ ] Agent Lifecycle
- [ ] Session Management
- [ ] Tool Registration
- [ ] Event Handling
- [ ] Telephony Integration

### Production Practices
- [ ] Logging & Monitoring
- [ ] Error Recovery
- [ ] Configuration for Different Environments
- [ ] Secrets Management
- [ ] Code Organization

---

## ❓ Questions Log

> Track questions that come up during development for deeper exploration later. 

| Question | Status | Notes |
|----------|--------|-------|
| | | |

---

## 📖 Vocabulary

Key terms we'll use throughout:

| Term | Definition |
|------|------------|
| **Agent** | The AI that handles conversations |
| **Session** | One phone call from start to end |
| **Tool** | A function the AI can call (like checking weather) |
| **SIP** | Protocol that connects phone networks to internet apps |
| **Trunk** | The connection between Twilio and LiveKit |
| **STT** | Speech-to-Text (voice → text) |
| **TTS** | Text-to-Speech (text → voice) |
| **LLM** | Large Language Model (the AI brain - Gemini) |

---

## 🚀 Current Status

**Phase**: Phase 1 - Minimal Agent BUILT
**Next Step**: Test agent locally, then add tools

---

## 🧠 AI Context Memory System

> **For AI**: When starting a new session, follow the `/resume-session` workflow.

### Memory Location
All session tracking is in `.agent/memory/`:

| File | Purpose |
|------|---------|
| `README.md` | Quick status & decisions |
| `INSTRUCTIONS.md` | Autonomous AI operating rules |
| `current_session.md` | Active work context |
| `decisions.md` | Key decisions with rationale |
| `concepts/` | Categorized learning (core/intermediate/advanced/revision) |
| `questions/` | Pending & resolved questions |
| `archive/` | Old session logs |

### Workflow
```bash
# Start of session: Read context
/resume-session

# During session: AI updates files AUTONOMOUSLY
# End of session: AI archives and summarizes
```

---

## 📌 Additional Learning Tips

### The Rubber Duck Method
When confused, try explaining the problem out loud (or in writing). Often, articulating the problem reveals the solution.

### Read Error Messages Carefully
Error messages are not scary! They're helpful. Always read:
1. The **last line** first (the actual error)
2. The **file and line number** where it occurred
3. The **stack trace** from bottom to top

### Take Breaks
If stuck for more than 30 minutes, take a break. Your brain processes problems in the background.

---

*Last Updated: 2026-01-22*
