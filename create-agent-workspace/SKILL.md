# Skill: Create Agent Workspace

**Purpose:** Create a new isolated agent workspace with proper KG integration and workspace location.

**Trigger Phrases:**
- "Create a new agent for [name]"
- "Set up [name]'s workspace"
- "Create agent workspace for [name]"
- "I need a new agent for [user]"

---

## What This Does

Creates a new OpenClaw agent workspace with:
1. **Isolated directory** under `C:\AI\_BOT\.openclaw\workspace-{name}\`
2. **Dedicated KG port** (9303+, incrementing from user KGs)
3. **Proper openclaw.json** with KG URL and workspace path
4. **Core framework files** (SOUL.md, USER.md, IDENTITY.md, etc.)
5. **Memory directory** for daily logs

---

## Workspace Architecture

```
C:\AI\_BOT\.openclaw\
├── workspace/           (Ohm's main workspace)
├── workspace-rawrity/   (RAWRity's KG: 9301)
├── workspace-sigma/     (Sigma's KG: 9302)
└── workspace-{name}/    (New agent's KG: 9303+)
```

**KG Port Assignment:**
- Ohm (main): 9300
- RAWRity: 9301
- Sigma: 9302
- New agents: 9303, 9304, 9305... (increment)

---

## Configuration Steps

### 1. Create Workspace Directory

```bash
New-Item -ItemType Directory -Force -Path "C:\AI\_BOT\.openclaw\workspace-{name}"
```

### 2. Create openclaw.json

```json
{
  "meta": {
    "agentType": "user",
    "userName": "{Name}",
    "kgPort": 9303,
    "workspaceLocation": "C:\\AI\\_BOT\\.openclaw\\workspace-{name}"
  },
  "agents": {
    "defaults": {
      "workspace": "C:\\AI\\_BOT\\.openclaw\\workspace-{name}",
      "kgUrl": "http://localhost:9303",
      "model": {
        "primary": "ollama/qwen3.5:cloud"
      }
    }
  },
  "gateway": {
    "port": 18789,
    "bind": "loopback",
    "tools": {
      "allow": ["cron", "gateway", "sessions_spawn"]
    }
  },
  "skills": {
    "entries": {
      "sag": {
        "apiKey": "e41f9681fea166e92475b5c12cbf8231570419c491b6c3a883696e81f688b32b"
      }
    }
  }
}
```

### 3. Copy Framework Files

From `C:\AI\_BOT\.openclaw\workspace\`:
- `SOUL.md` → Edit for user identity
- `USER.md` → Create with user info
- `IDENTITY.md` → Edit for user agent name
- `HEARTBEAT.md` → Copy as-is
- `AGENTS.md` → Copy as-is
- `TOOLS.md` → Copy as-is
- `MEMORY.md` → Create empty or with initial memories

### 4. Create Memory Directory

```bash
New-Item -ItemType Directory -Force -Path "C:\AI\_BOT\.openclaw\workspace-{name}\memory"
```

Create `memory/YYYY-MM-DD.md` with today's date.

### 5. Set Up Knowledge Graph (Optional)

If user needs a dedicated KG:

```bash
# Start new Simple Graph MCP instance on port 9303
docker run -d ^
  -p 9303:8000 ^
  -p 7675:7674 ^
  -p 7888:7887 ^
  -e NEO4J_AUTH=neo4j/demodemo ^
  -e GROUP_ID={name} ^
  --name simple-graph-{name} ^
  ghcr.io/openclaw/simple-graph-mcp:latest
```

**Note:** User must set model via Nerve UI after spawning agent (I cannot change model selection).

---

## Example: Create Ω¹ (Omega-1) Workspace

**Context:** Subordinate Ohm instance at work machine

```bash
# Create directory
New-Item -ItemType Directory -Force -Path "C:\AI\_BOT\.openclaw\workspace-omega1"

# Create openclaw.json with kgPort: 9303
# Copy framework files
# Edit IDENTITY.md: "You are Ω¹ (Omega-1), subordinate to Ohm Prime"
# Edit USER.md: "This workspace serves Ohm Prime infrastructure"
```

---

## Post-Creation Checklist

After creating workspace:

- [ ] User spawns agent in Nerve UI
- [ ] User selects model (qwen3.5:cloud or kimi-k2.5:cloud)
- [ ] Agent reads SOUL.md, USER.md, MEMORY.md on startup
- [ ] Agent queries KG at http://localhost:9303 (if KG exists)
- [ ] Test with simple query: "What's in my workspace?"

---

## Migration Notes

**Old Path (Deprecated):** `C:\Users\OHM\.openclaw\workspace-{name}\`  
**New Path (Current):** `C:\AI\_BOT\.openclaw\workspace-{name}\`

All new agent workspaces should use `C:\AI\_BOT\.openclaw\` prefix to keep everything together.

**Existing workspaces to migrate:**
- `workspace-rawrity` → ✅ Migrated 2026-04-05
- `workspace-sigma` → ✅ Migrated 2026-04-05

---

## Troubleshooting

**Agent can't find KG:**
- Check KG container is running: `docker ps | findstr simple-graph`
- Verify port: http://localhost:930X/health
- Check openclaw.json has correct `kgUrl`

**Agent uses wrong workspace:**
- Verify `agents.defaults.workspace` in openclaw.json
- Check workspace directory exists
- Restart agent session

**Model not loading:**
- User must set model in Nerve UI (I cannot change this)
- Verify model is available: `ollama list`
- Check model config in openclaw.json

---

**Last Updated:** 2026-04-05 (Workspace Consolidation)  
**Location:** `C:\AI\_BOT\.openclaw\workspace\skills\create-agent-workspace\SKILL.md`
