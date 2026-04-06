---
name: load-user
description: Load user-specific workspace context for multi-user OpenClaw sessions. Detects Discord user from context, then loads the appropriate user workspace (AGENTS.md, USER.md, memory files) and sets up daily memory files. Includes Docker-based MCP server health check and auto-start.
---

# Load-User Skill

Dynamically load user workspace context based on Discord identity.

**Location:** `skills/load-user/` (shared root-level skill, accessible to all users)

## Quick Start

### Load Your User Context
```
/load-user
```

The skill automatically detects the Discord user and loads their workspace.

### Load Specific User Context
```
/load-user Set
/load-user Sigma
```

**Implementation:**
```bash
node skills/load-user/scripts/load-user.js Set
node skills/load-user/scripts/load-user.js Sigma
```

Or let the agent handle it:
```
@exec node skills/load-user/scripts/load-user.js Set
```

### Reset to Root Context
```
/new
```
or
```
/reset
```

> **Note:** Reference files cannot be unloaded mid-session. Use `/new` to start fresh with only root context.

## 🔧 Using Skills After Loading User

**Important:** After running `/load-user`, skills remain accessible but require **absolute paths** in Discord commands.

### The Problem

When you load a user workspace, the context shifts to `users/{name}/`. Relative paths like `skills/ngrok/...` may not resolve correctly from the user directory.

### The Solution

All skill scripts now use **absolute path resolution** via `__dirname`. They work from any context.

### Working Commands After /load-user

| Command | How to Run | Works? |
|---------|-----------|--------|
| `/tunnel` | `@exec node skills/ngrok/scripts/tunnel-start.js portfolio` | ✅ Yes (relative from root) |
| `/tunnel` (absolute) | `@exec node "C:/AI/_BOT/.openclaw/workspace/skills/ngrok/scripts/tunnel-start.js" portfolio` | ✅ Yes (always works) |
| `/onboard` | `@exec node skills/user-onboarding/scripts/onboard.js quick` | ✅ Yes |

### Verify Skills Are Accessible

Run this after `/load-user` to check all skills:
```bash
node skills/load-user/scripts/validate-skills.js Set
```

This outputs all available skills with their absolute paths.

### Skill Path Resolution

To get the absolute path to any skill script:
```bash
node skills/load-user/scripts/resolve-skill-path.js ngrok tunnel-start.js
# Output: C:\AI\_BOT\.openclaw\workspace\skills\ngrok\scripts\tunnel-start.js
```

## Output Format

When `/load-user` runs successfully, it confirms:

```
✅ Loaded user: {nickname} ({symbol})
📁 Workspace: users/{Name}/
📝 Context: AGENTS.md, USER.md, MEMORY.md, memory/{today}.md
🔌 MCP Server: ✅ Running
   ├─ Container: memory-{username}
   ├─ Port: {port}
   └─ Storage: {item_count} items
```

**Example for Set (∅):**
```
✅ Loaded user: Set (∅)
📁 Workspace: users/Set/
📝 Context: AGENTS.md, USER.md, MEMORY.md, memory/2026-02-13.md
🔌 MCP Server: ✅ Running
   ├─ Container: simple-graph-rawrity
   ├─ Port: 9301
   └─ Storage: 47 entities
```

**Example when MCP container is down (auto-started):**
```
✅ Loaded user: Set (∅)
📁 Workspace: users/Set/
📝 Context: AGENTS.md, USER.md, MEMORY.md, memory/2026-02-13.md
🔌 MCP Server: ⚠️ Auto-started
   ├─ Container: simple-graph-rawrity
   ├─ Port: 9301
   └─ 📝 Note: Container was stopped — started via docker-compose
      Run: docker-compose -f projects/simple-graph-mcp/docker-compose.yml ps
```

## MCP Server Health Check (Docker-Based)

On every `/load-user`, the skill checks your personal Simple Graph MCP Docker container status:

| Check | Method |
|-------|--------|
| Docker container | `docker-compose ps` checks for `simple-graph-{username}` |
| HTTP endpoint | `GET http://localhost:{port}/health` |
| Storage stats | Neo4j browser shows entity counts |

**Container Names & Ports:**
- **@rawrity_ (Set, ∅):** Container `simple-graph-rawrity`, Port 9301 (Neo4j: 7687)
- **@.ultra_mc (Sigma, Σ):** Container `simple-graph-sigma`, Port 9302 (Neo4j: 7787)
- **Ω (Ohm, default):** Container `simple-graph-agent`, Port 9300 (Neo4j: 7887)

**If MCP container is down:**
1. Auto-starts via `docker-compose up -d memory-{username}`
2. Waits for HTTP endpoint to respond
3. Shows a note to troubleshoot why it stopped
4. Suggests checking logs with `docker-compose logs`

## How It Works

1. **Detect Discord User ID** from runtime context (e.g., `85131474184986624`)
2. **Map ID to User Folder** via configured mapping
3. **Check MCP Container** — docker-compose ps + HTTP health check
4. **Auto-start if needed** — `docker-compose up -d memory-{username}`
5. **Load User Files** as Reference context:
   - `AGENTS.md` — user behavior rules
   - `USER.md` — who this user is
   - `memory/YYYY-MM-DD.md` — today's and yesterday's raw notes
   - `MEMORY.md` — curated long-term memory
6. **Create Daily File** — if `memory/{today}.md` doesn't exist, creates it
7. **Set User Context** — all subsequent operations use this user's workspace

## Session Lifecycle

```
/new                    → Fresh session (root AGENTS.md, SOUL.md only)
   ↓
/load-user              → Load user workspace + MCP container check
   ↓
[conversation]          → Operate in user context
   ↓
/new                    → Reset to root (unload user)
```

**Key points:**
- Start with `/new` to ensure clean root state
- Run `/load-user` to initialize user context
- MCP Docker container is checked and auto-started if needed
- User files stay loaded for the session
- Use `/new` to switch users or return to root

## User Mapping

| Discord User | User ID | Workspace Path | MCP Container | MCP Port | Neo4j Port |
|-------------|---------|----------------|---------------|----------|------------|
| @rawrity_ (Set, ∅) | 85131474184986624 | `users/Set/` | `simple-graph-rawrity` | 9301 | 7687 |
| @.ultra_mc (Sigma, Σ) | 296511082745298944 | `users/Sigma/` | `simple-graph-sigma` | 9302 | 7787 |

## File Loading Priority

When `/load-user` runs, these files are loaded as Reference:

1. **User AGENTS.md** — overrides root AGENTS.md behavior
2. **User USER.md** — tells me who you are
3. **Today's memory** — `memory/YYYY-MM-DD.md` (created if missing)
4. **Yesterday's memory** — for context continuity
5. **User MEMORY.md** — long-term curated memory

## Daily Memory Files

Each user has dated memory files in `users/{name}/memory/`:
- Format: `YYYY-MM-DD.md`
- Auto-created on first load of the day
- Populated with session summaries
- Loaded as Reference for context

## Docker MCP Server Management

For full control of MCP containers:

```bash
# Check status
cd projects/simple-graph-mcp
docker-compose ps
docker-compose logs simple-graph-rawrity
docker-compose logs simple-graph-sigma

# Start/Stop
docker-compose up -d              # Start all
docker-compose up -d simple-graph-rawrity   # Start just Rawrity
docker-compose stop               # Stop all
docker-compose down               # Remove containers

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d
```

**HTTP Endpoints:**
- Rawrity: `http://localhost:9301/health`
- Sigma: `http://localhost:9302/health`
- Ohm: `http://localhost:9300/health`

**Neo4j Browsers:**
- Rawrity: `http://localhost:7474`
- Sigma: `http://localhost:7574`
- Ohm: `http://localhost:7674`

## Multi-User Boundaries

- Each user's workspace is isolated by path
- Root files remain shared/common
- Memory files never leak between users
- Honor system enforced by skill logic
- Use `/new` between users to prevent context mixing

## Scripts

### `scripts/load-user.js`

Executable script that loads user workspace context with MCP Docker health check.

**Usage:**
```bash
node skills/load-user/scripts/load-user.js <Set|Sigma>
```

**What it does:**
1. Validates the user name against the user map
2. Checks if the user workspace exists
3. **Checks MCP Docker container** via `docker-compose ps`
4. **HTTP health check** on `localhost:{port}/health`
5. **Auto-starts container** if not running (with troubleshooting note)
6. Creates `memory/` directory if missing
7. Creates today's memory file (`YYYY-MM-DD.md`) if missing
8. Outputs confirmation with workspace path and MCP status
9. Signals files to load as references

**Output format:**
```
✅ Loaded user: {nickname} ({symbol})
📁 Workspace: users/{Name}/
📝 Context: AGENTS.md, USER.md, MEMORY.md, memory/YYYY-MM-DD.md
🔌 MCP Server: {status}
@reference users/{Name}/AGENTS.md
@reference users/{Name}/USER.md
...
```

## Testing

### Running the Command
```
/load-user Set
```
This executes:
```bash
@exec node skills/load-user/scripts/load-user.js Set
```

Then load the referenced files shown in output.

### Manual Verification
To verify user setup without the script:
```
@reference users/Set/AGENTS.md users/Set/USER.md
```

### MCP Status Check
To check MCP status manually:
```bash
cd projects/simple-graph-mcp
docker-compose ps
docker-compose logs --tail 20 simple-graph-rawrity
```

Or via bridge:
```bash
cd projects/simple-graph-mcp
python bridge.py
```

## Troubleshooting

**MCP container keeps stopping:**
```bash
cd projects/simple-graph-mcp
docker-compose logs simple-graph-rawrity   # Check for errors
docker-compose logs simple-graph-sigma
```

**Auto-start fails:**
- Verify Docker is running: `docker version`
- Check docker-compose.yml exists in `projects/simple-graph-mcp/`
- Ensure ports 9300-9302 are not blocked: `netstat -ano | findstr :9301`

**HTTP check fails but container is running:**
```bash
# Test manually
curl http://localhost:9301/health
python projects/simple-graph-mcp/bridge.py
```

**Adding a new user to Docker:**
1. Edit `projects/simple-graph-mcp/docker-compose.yml`
2. Copy an existing service block and modify:
   - Service name (e.g., `simple-graph-alice`)
   - Container name
   - Port (e.g., `9303:8000`)
   - Neo4j port (e.g., `7888:7687`)
3. Run `docker-compose up -d simple-graph-alice`

## Extending

To add a new user:
1. Create `users/{username}/` folder using `_TEMPLATE.md`
2. Add Discord ID → username mapping above with MCP container/port
3. Add service to `docker-compose.yml` in `projects/simple-graph-mcp/`
4. Update user detection logic in this skill
5. Populate USER.md with user info
6. Customize AGENTS.md for user preferences
7. Run `docker-compose up -d simple-graph-{username}`

## Related Skills

- `user-onboarding` — Conversational onboarding to populate Simple Graph MCP
- `profile-builder` — Gather and store professional user info

---

*Updated: 2026-02-18 — Migrated to Simple Graph MCP (Neo4j-based) with HTTP health checks.*
