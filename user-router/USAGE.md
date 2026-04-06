# User Router - Usage Guide

## The Problem

When using OpenClaw with Discord:
- `bindings.match` only supports `guildId`, not `userId`
- All messages from a server go to the same agent (e.g., `rawrity`)
- You want RAWRity and Sigma to have separate workspaces/contexts

## The Solution

This skill provides user detection and routing advice. When the main agent receives a message, it checks who sent it and advises on proper handling.

## How It Works

### Current State (Guild-Based Routing)

All messages from Discord server `1423444489237958890` → `rawrity` agent

```json
// openclaw.json
"bindings": [
  {
    "agentId": "rawrity",
    "match": {
      "channel": "discord",
      "guildId": "1423444489237958890"
    }
  }
]
```

### User Detection

When a message arrives, OpenClaw provides metadata:

```
[Discord rawrity_ user id:85131474184986624 ...]
[Discord ultra_mc user id:296511082745298944 ...]
```

The user ID is visible in the message context.

## Usage

### From OpenClaw Agent (Python)

When you receive a Discord message, check the user:

```python
from skills.user_router.scripts.bridge import check_user_and_advise, get_user_info

# The user ID is in the runtime context
# Check if message is from Sigma
if "296511082745298944" in str(message_context):
    # Option 1: Spawn isolated sub-agent
    sessions_spawn(
        task="Create cover letters for job applications",
        label="sigma-session",
        agent_id="sigma"
    )
    
    # Option 2: Route to Sigma's context
    /load-user sigma
```

### Manual Routing

When Sigma messages and you're in the rawrity session:

1. **Acknowledge you're in rawrity's context**
2. **Switch to Sigma context:**
   ```
   /load-user sigma
   ```
3. **Or spawn sub-agent:**
   ```
   sessions_spawn(task="user's request here", label="sigma")
   ```

### Automatic Detection (Future Enhancement)

We could add this to `HEARTBEAT.md` or a custom hook:

```python
# On each Discord message
from skills.user_router.scripts.bridge import check_user_and_advise

user_id = extract_from_metadata()  # "296511082745298944"
advice = check_user_and_advise(user_id, message_content)
# Use advice to route appropriately
```

## User Mapping

| Discord User | ID | Agent | Graph Port | Workspace |
|--------------|-------|-------|------------|-----------|
| RAWRity_ | 85131474184986624 | rawrity | 9301 | `.` |
| UltraMC (Sigma) | 296511082745298944 | sigma | 9302 | `users/sigma` |

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/load-user rawrity` | Switch to RAWRity's workspace |
| `/load-user sigma` | Switch to Sigma's workspace |
| `/new` | Reset to root (no user context) |
| `sessions_spawn(task, label, agent_id)` | Create isolated sub-agent |

## Testing

Run the router test:

```bash
cd skills/user-router/scripts
python router.py
```

Check the bridge:

```bash
python bridge.py
```

## Limitations

- OpenClaw doesn't auto-route by user ID at the gateway level
- The routing happens at the application level (in your responses)
- Requires manual `/load-user` or `sessions_spawn` to switch contexts

## Future Options

1. **Channel-based routing:** Create separate Discord channels per user
2. **Multiple bot instances:** Run separate OpenClaw instances per user
3. **Custom gateway middleware:** Modify OpenClaw's Discord provider (requires code changes)

## Summary

This skill gives you the **information** to route correctly, but OpenClaw's current architecture requires manual or semi-manual routing via `/load-user` or `sessions_spawn`.

The guild-based binding ensures all messages arrive in one place; this skill helps you sort them out from there.
