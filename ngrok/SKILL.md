---
name: ngrok
description: Dockerized ngrok agent for exposing local folders and ports as public URLs. Use when the user wants to share local projects via public tunnel, create temporary public URLs for websites, or expose development servers. Supports Discord commands like /tunnel <folder>, /tunnel_stop, and /tunnel_status.
---

# Ngrok Tunnel Manager Skill

Dockerized ngrok agent with CLI management for exposing local endpoints via your paid account.

## Quick Start

### Discord Commands (Recommended)

Expose a local folder as a public website in one command:

**In Discord, use:**
```
@exec node skills/ngrok/scripts/tunnel-start.js portfolio
```

**Output:**
```
🚀 Tunnel ready!
📁 Serving: portfolio/index.html
🌐 Local: http://localhost:8000
🔗 Public: https://look-ma-im-creative.ngrok.io
```

| Discord Command | Script | Description |
|-----------------|--------|-------------|
| `/tunnel <folder>` | `tunnel-start.js` | Start server + tunnel for folder (auto-generates witty subdomain) |
| `/tunnel_stop` | `tunnel-stop.js` | Stop active tunnel and kill HTTP server |
| `/tunnel_status` | `tunnel-status.js` | Show URL, uptime, requests, and recent traffic |

**Note:** Discord commands use `@exec node skills/ngrok/scripts/<script>.js [args]` format.

### Discord Setup

Add to your Discord agent's configuration to enable these shortcuts:

```yaml
# In your agent config (e.g., discord.yaml)
commands:
  tunnel:
    pattern: "^/tunnel (.+)$"
    action: "exec"
    command: "node skills/ngrok/scripts/tunnel-start.js {1}"
  
  tunnel_stop:
    pattern: "^/tunnel_stop$"
    action: "exec"
    command: "node skills/ngrok/scripts/tunnel-stop.js"
  
  tunnel_status:
    pattern: "^/tunnel_status$"
    action: "exec"
    command: "node skills/ngrok/scripts/tunnel-status.js"
```

Or manually in Discord:
- Type: `@exec node skills/ngrok/scripts/tunnel-start.js portfolio`
- Type: `@exec node skills/ngrok/scripts/tunnel-status.js`
- Type: `@exec node skills/ngrok/scripts/tunnel-stop.js`

### Manual CLI Commands

```bash
# 1. Start the ngrok agent (Dockerized)
python bridge.py docker up

# 2. Create a tunnel
python bridge.py start --name myapp --port 3000 --subdomain mycoolapp

# 3. Access your site
# https://mycoolapp.ngrok.io → localhost:3000

# 4. List active tunnels
python bridge.py list

# 5. Stop a tunnel
python bridge.py stop myapp
```

## Prerequisites

- **ngrok authtoken** stored in `~/.openclaw/vault/ngrok-auth-token`
- **Paid ngrok account** (for custom subdomains)
- Docker Desktop running

## Commands

| Command | Description |
|---------|-------------|
| `python bridge.py docker up` | Start the ngrok agent container |
| `python bridge.py docker down` | Stop the agent container |
| `python bridge.py docker logs` | View agent logs |
| `python bridge.py start --name X --port Y` | Create a new tunnel |
| `python bridge.py list` | Show active tunnels |
| `python bridge.py stop <name>` | Stop a tunnel |
| `python bridge.py status` | Check agent health |
| `python bridge.py web` | Open web interface (localhost:4040) |

## Start Tunnel Options

```bash
python bridge.py start \
  --name api-server \        # Tunnel identifier
  --port 8080 \              # Local port to expose
  --subdomain myapi \        # Custom subdomain (paid)
  --domain api.example.com   # Custom domain (paid + dashboard setup)
```

## Architecture

```
skills/ngrok/
├── docker-compose.yml      # Ngrok agent container
├── ngrok.yml              # Agent configuration
├── bridge.py              # CLI/API interface
├── SKILL.md               # This file
├── scripts/               # Discord command implementations
│   ├── tunnel-start.js    # /tunnel command
│   ├── tunnel-stop.js     # /tunnel_stop command
│   └── tunnel-status.js   # /tunnel_status command
├── active-tunnels.json    # Runtime state (gitignored)
└── endpoints/             # Saved tunnel configs (gitignored)
```

**Container:** `ngrok/ngrok:latest`  
**Port:** `4040` - Web inspection interface  
**API:** Local agent API (not ngrok cloud API)

### ⚠️ Critical: Docker Networking

**The ngrok agent runs in a Docker container**, which means:

```
┌─────────────────────────────────────────────────────────┐
│ Host Machine                                            │
│  └─ Your Service: 0.0.0.0:8000                          │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Docker Container (ngrok-agent)                      │ │
│ │  └─ ngrok tunnel → MUST use host.docker.internal    │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Tunnel Configuration:**
```json
// ❌ WRONG - refers to container's localhost (nothing running there)
{ "addr": "http://localhost:8000" }

// ✅ CORRECT - routes to host machine
{ "addr": "http://host.docker.internal:8000" }
```

**Server Binding:**
```powershell
# Server must bind to ALL interfaces
python -m http.server 8000 --bind 0.0.0.0

# ❌ This will fail (ngrok cannot reach 127.0.0.1 from container)
python -m http.server 8000 --bind 127.0.0.1
```

**Every tunnel created via this skill must use `host.docker.internal`** — this is a Docker networking requirement, not optional.

## How It Works

1. **Docker container** runs ngrok agent in `--none` mode (no default tunnels)
2. **bridge.py** talks to agent's local API on `localhost:4040`
3. **Dynamic tunnels** created via POST `/api/tunnels`
4. **Configs saved** to `endpoints/{name}.json` for reference

## Discord Command Details

### `/tunnel <folder_path>`

Starts a complete tunnel workflow:

1. **Finds available port** (starting at 8000)
2. **Generates witty subdomain** based on folder content type
3. **Starts Python HTTP server** for the folder
4. **Creates ngrok tunnel** with custom subdomain
5. **Saves state** for `/tunnel_status` and `/tunnel_stop`

**Example outputs:**
```
/tunnel portfolio
🚀 Tunnel ready!
📁 Serving: portfolio/index.html
🌐 Local: http://localhost:8000
🔗 Public: https://hired-please.ngrok.io
📊 Check status: /tunnel_status
🛑 Stop tunnel: /tunnel_stop
```

**Witty subdomain generators:**
| Folder Type | Example Subdomains |
|-------------|-------------------|
| portfolio | `hired-please`, `pixels-and-paychecks`, `look-ma-im-creative` |
| docs | `the-paper-trail`, `boring-but-important`, `read-me-or-else` |
| project | `work-in-prog`, `it-compiles-ship-it`, `certified-fresh-code` |
| data | `numbers-and-stuff`, `trust-me-im-data`, `excel-but-cooler` |
| personal | `organized-chaos`, `digital-hoard`, `my-stuff-dont-touch` |
| (other) | `{foldername}-rawrity-special` |

### `/tunnel_stop`

Stops the active tunnel and HTTP server:
```
🛑 Stopping tunnel: tunnel-1234567890
   🔗 https://hired-please.ngrok.io (offline)
   📁 Server on port 8000 killed

📊 Served: portfolio
⏱️ Duration: 45m 12s
```

### `/tunnel_status`

Shows real-time tunnel information:
```
📡 Active Tunnel
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Folder: portfolio
🔗 Public URL: https://hired-please.ngrok.io
🌐 Local: http://localhost:8000
🎭 Subdomain: hired-please
⏱️ Uptime: 12m 34s
📈 Requests: 47

🔧 Configuration:
   Protocol: http
   Forwarding to: host.docker.internal:8000
   Region: us

📋 Recent Requests (last 3):
   1. GET / → 200 (5:42:01 PM)
   2. GET /style.css → 200 (5:42:02 PM)
   3. GET /script.js → 200 (5:42:03 PM)
```

## Paid Account Features

- ✅ Custom subdomains (`mycoolapp.ngrok.io`)
- ✅ Reserved domains (`api.yourdomain.com`)
- ✅ Multiple concurrent tunnels (Hobbyist: 1 agent, multiple tunnels through it)
- ✅ Web inspection interface

### ngrok Hobbyist Plan (Your Account)

| Feature | Hobbyist ($5/mo) |
|---------|-----------------|
| Online ngrok processes | 1 agent |
| Concurrent tunnels | Unlimited via agent |
| Custom subdomains | ✅ Yes |
| Custom domains | ✅ Yes |
| Rate limit | 40 connections/minute |
| Basic auth | ✅ Yes |
| TCP endpoints | ✅ Yes |

**Current usage:** Single tunnel at a time (simplest for your workflow)

## Integration Examples

**Expose MCP servers:**
```bash
python bridge.py start --name simple-graph-rawrity --port 9301 --subdomain mem-rawrity
python bridge.py start --name simple-graph-sigma --port 9302 --subdomain mem-sigma
python bridge.py start --name comfyui --port 9101 --subdomain comfy
```

**Expose development servers:**
```bash
python bridge.py start --name nextjs-dev --port 3000 --subdomain myproject-dev
python bridge.py start --name api-local --port 8080 --subdomain myapi-dev
```

## Web Interface

Open http://localhost:4040 to:
- View request logs
- Inspect traffic
- Replay requests
- See tunnel status

Or run: `python bridge.py web`

## Security

- Authtoken in vault (never committed)
- Web interface bound to localhost only
- Configs in `endpoints/` are gitignored

## Troubleshooting

**"Agent not running" error:**
```bash
python bridge.py docker up
```

**Port 4040 already in use:**
```bash
# Find and stop the process
docker ps  # check for existing ngrok containers
docker stop ngrok-agent
```

**Custom subdomain not working:**
- Verify paid account is active
- Check subdomain isn't reserved by someone else
- Try a different subdomain

## Differences from Cloud API Approach

| | Local Agent API (this skill) | ngrok Cloud API |
|---|---|---|
| **Auth** | Authtoken only | Requires separate API key |
| **Use case** | Dynamic tunnel management | Cloud endpoint CRUD |
| **Scope** | Local agent only | Account-wide endpoints |
| **Complexity** | Simpler | More features, more setup |

For most use cases, the local agent API is sufficient and simpler.

---

*Created: 2026-02-14*  
*Paid ngrok features enabled*
