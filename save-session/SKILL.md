---
name: save-session
description: Save current conversation session to persistent storage. Use before switching Discord users or when you want to pause and resume a conversation later. Creates/updates docs/saved-session.md with conversation summary.
---

# Save-Session Skill

Capture the current conversation state for later retrieval.

## Quick Start

### Save Current Session
```
/save-session
```

Saves conversation summary to `docs/saved-session.md`.

## What Gets Saved

1. **Session summary** — key topics discussed, decisions made
2. **Active projects** — what you're currently working on
3. **Memory references** — files modified, searches run
4. **Next steps** — pending actions or follow-ups
5. **Timestamp** — when session was saved
6. **User context** — which user workspace is active

## Output Format

```
✅ Session saved
📁 Location: docs/saved-session.md
⏰ Time: 2026-02-13 14:35 PST
📝 Content: Summary | Decisions | Next Steps
```

## Session Lifecycle

```
[conversation]          → Work with user
   ↓
/save-session          → Save state before switch
   ↓
/new                   → Switch Discord users
   ↓
/load-user {other}     → Load other user context
   ↓
[other conversation]   → Work with other user
   ↓
/new                   → Switch back
   ↓
/load-session          → Restore previous session
   ↓
[conversation]         → Continue where you left off
```

## Implementation

### Script Usage
```bash
node skills/save-session/scripts/save-session.js "{optional note}"
```

Or let the agent handle it:
```
@exec node skills/save-session/scripts/save-session.js
```

### Without Script
Manually save by:
```
@reference docs/saved-session.md
```
Then say "Update this file with our current conversation state."

## Related

- `load-session` — Restore saved session
- `load-user` — Switch user context

---
*Updated: 2026-02-13 — Created for multi-user Discord session switching.*
