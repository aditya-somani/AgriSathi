---
description: How to resume work on AgriSathi after a break or new session
---

# Resuming AgriSathi Development

// turbo-all

## When Starting a New Session

1. Read the AI operating instructions
```bash
cat .agent/memory/INSTRUCTIONS.md
```

2. Read quick status
```bash
cat .agent/memory/README.md
```

3. Read current session context
```bash
cat .agent/memory/current_session.md
```

4. Check for pending questions
```bash
cat .agent/memory/questions/pending.md
```

5. Continue from "Next Up" in current_session.md

## During Session (Autonomous)

AI will automatically:
- Update current_session.md as work progresses
- Create concept files when explaining new topics
- Track questions in questions/pending.md
- Log decisions in decisions.md

## Before Ending a Session

1. Update README.md status
2. Summarize current_session.md
3. Move resolved questions to resolved.md
4. Archive session if complete
