# Memory System Review - Before Finalizing

## Potential Gaps Identified

### 1. Session End Detection
**Gap**: How does AI know when a session "ends"?
**Solution**: Add explicit triggers:
- User says "let's stop here" / "continue tomorrow" / "bye"
- Context window warning
- User explicitly closes conversation

### 2. Concept Graduation Path
**Gap**: How do concepts move FROM revision BACK to mastered?
**Solution**: When user successfully explains a concept, move FROM revision TO original category with "mastered" status.

### 3. Project-Agnostic vs Project-Specific
**Gap**: GEMINI.md has project-specific content (phases for AgriSathi)
**Solution**: Split into:
- `GEMINI.md` - Project-agnostic learning philosophy
- `.agent/memory/project_context.md` - Project-specific goals/phases

### 4. First Session Initialization
**Gap**: What happens on very first session of a new project?
**Solution**: Add "onboarding" flow in INSTRUCTIONS.md:
- AI asks for project description
- AI asks for user's experience level
- AI creates initial structure based on answers

### 5. Multiple AI Providers
**Gap**: Instructions reference "AI" but what if different AI tools are used?
**Solution**: Keep instructions generic, they apply to any AI assistant.

## Proposed Additions to INSTRUCTIONS.md

```markdown
## Session End Triggers

AI should initiate end-of-session routine when:
- User says: "stop", "bye", "continue later", "that's all", "let's pause"
- User hasn't responded in a while (context may be lost)
- Major milestone completed

## Concept Graduation

When user demonstrates mastery:
1. Move concept from `revision/` back to original category
2. Update status to "mastered"
3. Add note: "Mastered on [date] after [what helped]"

## First Session Onboarding

On very first session of new project:
1. Ask: "What are you building? (1-2 sentences)"
2. Ask: "What's your experience level? (beginner/intermediate/advanced)"
3. Create project_context.md with answers
4. Start Phase 0: Foundation
```

## Decision

These additions are improvements, not critical fixes.
The current system WILL WORK without them.

Recommendation: Add these refinements, then create workflow.
