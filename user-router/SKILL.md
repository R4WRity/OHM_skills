# User Router Skill

Route Discord messages to user-specific agent sessions based on Discord user ID.

## Problem

OpenClaw's `bindings.match` doesn't support `userId` for Discord — only `guildId`. This means all messages from a Discord server go to the same agent, even if you want separate workspaces for different users.

## Solution

This skill intercepts messages and spawns/routes to user-specific sub-agents:

- **RAWRity** (user ID: `85131474184986624`) → rawrity agent session
- **Sigma** (user ID: `296511082745298944`) → sigma agent session

## Usage

From the main agent (rawrity), when you receive a Discord message:

```python
from skills.user_router.scripts.router import route_message

# Route current message to appropriate user agent
result = route_message(
    user_id="85131474184986624",  # from Discord metadata
    message="User's message here",
    channel="discord"
)
```

Or use the command wrapper:

```bash
# In OpenClaw chat
/route-to-user sigma
```

## User Mapping

| Discord User | User ID | Agent | Workspace |
|--------------|---------|-------|-----------|
| RAWRity_ | 85131474184986624 | rawrity | root workspace |
| UltraMC (Sigma) | 296511082745298944 | sigma | users/sigma/ |

## Architecture

```
Discord Message
    ↓
Main Agent (rawrity) receives via binding
    ↓
User Router skill checks author ID
    ↓
Spawns/routes to user-specific sub-agent
    ↓
Sub-agent processes with their own MCP/memory
```

## Files

- `SKILL.md` - This documentation
- `scripts/router.py` - Routing logic
- `scripts/bridge.py` - OpenClaw integration wrapper

## Configuration

Add to your OpenClaw channel config if needed:

```json
"discord": {
  "users": {
    "85131474184986624": "rawrity",
    "296511082745298944": "sigma"
  }
}
```

Note: This is read by the skill, not by OpenClaw's native bindings.
