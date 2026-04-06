---
name: load-session
description: Restore previously saved conversation session from docs/saved-session.md. Use after switching Discord users or returning to a conversation. Loads session context including projects, decisions, and next steps.
---

# Load-Session Skill

Restore a previously saved conversation state.

## Quick Start

### Load Saved Session
```
/load-session
```

Loads session from `docs/saved-session.md`.

## What Gets Loaded

1. **Conversation summary** — what you were discussing
2. **Active projects** — work in progress
3. **Decisions made** — important choices documented
4. **Next steps** — pending actions to continue
5. **File references** — relevant files from that session

## Output Format

```
✅ Session loaded
📁 Source: docs/saved-session.md
⏰ Saved: 2026-02-13 14:35 PST
📝 Restored: Summary | Projects | Next Steps

---
[Session content follows...]
```

## Session Lifecycle

```
[conversation]          → Work with user
   ↓
/save-session          → Save state before break/switch
   ↓
/new                   → Switch/clear session
   ↓
/load-session          → Restore previous session
   ↓
[conversation]         → Continue where you left off
```

## Implementation

### Script Usage
```bash
node skills/load-session/scripts/load-session.js
```

Or let the agent handle it:
```
@exec node skills/load-session/scripts/load-session.js
```

### Without Script
Manually load by:
```
@reference docs/saved-session.md
```
Then say "Load this session and summarize what we were working on."

## File Format

Sessions are stored in `docs/saved-session.md` with:
- Timestamp of save
- Active user workspace
- Conversation summary
- Project list
- Decisions made
- Next steps (checkbox format)
- File references

## Related

- `save-session` — Save current conversation
- `load-user` — Switch to different user workspace

---
*Updated: 2026-02-13 — Created for multi-user Discord session switching.*
