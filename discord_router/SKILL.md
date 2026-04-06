# Discord Channel Router

Route **all** Discord messages to per-user agents based on channel (auto-routing mode).

## Overview

When Message Content Intent is enabled, OpenClaw receives **every** message in subscribed channels. This skill routes those messages to the appropriate user's agent.

**Flow:**
```
Discord Message Received
  ↓
Message has content?
  ↓
Check channel_routing.json
  ↓
Match? → Forward to sub-agent via sessions_send()
No match? → Handle in main OpenClaw session
```

## Configuration

### 1. Routing Config

Edit `config/channel-routing.json`:

```json
{
  "routing": [
    {
      "channel_id": "1468088770065862822",
      "channel_name": "empty-set-chat",
      "agent_label": "RAWRity",
      "agent_session": "agent:main:subagent:9a13a3da-c78b-4ead-be6c-d7db0449fc48",
      "user_id": "85131474184986624"
    },
    {
      "channel_id": "1468088770996867228",
      "channel_name": "sigma-chat",
      "agent_label": "Sigma",
      "agent_session": "agent:main:subagent:5480d04d-64bd-43df-94b9-49c915254909",
      "user_id": "296511082745298944"
    }
  ]
}
```

### 2. OpenClaw Integration

In main session, when ANY Discord message arrives:

```python
from skills.discord_router.router import route_message
from sessions_send import sessions_send

# Called on every Discord message (with Message Content Intent)
def on_discord_message(channel_id: str, message: str, author: dict):
    result = route_message(channel_id, message, author.get('id'))
    
    if result["routed"]:
        # Forward to user's agent
        sessions_send(
            result["agent_session"],
            f"[{result['channel_name']}] {author.get('name', 'User')}: {message}"
        )
        # Main OpenClaw stays silent (NO_REPLY)
        return "NO_REPLY"
    else:
        # Handle in main session
        return message
```

### 3. Required Discord Gateway Settings

Ensure OpenClaw Gateway has:
- `MESSAGE_CONTENT` intent enabled
- Bot present in both channels
- Channels subscribed in config

## Current Routing

| Channel | User | Agent | Session |
|---------|------|-------|---------|
| **#empty-set-chat** | RAWRity (∅) | RAWRity Agent | `9a13a3da-...` |
| **#sigma-chat** | Sigma (Σ) | Sigma Agent | `5480d04d-...` |
| Other channels | — | Main OpenClaw | (current) |

## Agent Behavior

**What agents see:**
```
[empty-set-chat] RAWRity_: What's in my Notion?
```

**Agent responds** → Result announced back to channel via main session.

## Testing

```bash
# Test routing logic
python skills/discord_router/test_routing.py
```

## Architecture

```
┌─────────────────────────────────────────┐
│     Discord Gateway (Message Intent)    │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │  Channel Router      │
        │  (this skill)        │
        └────┬──────────┬─────┘
             │          │
    ┌────────┴──┐   ┌───┴────────┐
    │ RAWRity   │   │ Sigma    │   ┌────────────┐
    │ Agent     │   │ Agent    │   │ Main       │
    │ (9301)    │   │ (9302)   │   │ OpenClaw   │
    └────┬──────┘   └─────┬────┘   └────────────┘
         │                │
         └──────┬─────────┘
                │
        ┌───────┴───────┐
        │  Announce Results│
        └───────────────┘
```
