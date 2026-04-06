---
name: omega-node-onboarding
description: "Onboarding guide for Ω¹ (Ohm Node/Subordinate) - connecting to parent's MCP infrastructure via network. Use when deploying or configuring Ω¹ at work machine SWS-GRALD-AW2."
metadata: {"openclaw":{"emoji":"🅾️","events":["agent:bootstrap"]}}
---

# Ω¹ (Ohm Node) - Onboarding Manifest

Parent: Ω (Ohm Prime) at `10.0.0.100`
Target: SWS-GRALD-AW2 (work machine)
Strategy: **Network Bridge** (connect to parent's MCPs, not local containers)

---

## 1. MCP Server Inventory (Parent's Infrastructure)

Access via `http://10.0.0.100` — parent's local network:

| Server | Port | Purpose | Ω¹ Access |
|--------|------|---------|------------|
| **simple-graph-rawrity** | 9301 | RAWRity's knowledge graph | `http://10.0.0.100:9301` |
| **simple-graph-sigma** | 9302 | Sigma's knowledge graph | `http://10.0.0.100:9302` |
| **simple-graph-agent** | 9300 | Ohm's knowledge graph | `http://10.0.0.100:9300` |
| **n8n-platform** | 5678 | Workflow automation API | `http://10.0.0.100:5678` |
| **comfyui-mcp** | 9101 | Image generation bridge | `http://10.0.0.100:9101` |
| **browser-mcp** | 9102 | Web automation | `http://10.0.0.100:9102` |

**Bridge Scripts (use directly):**
- `projects/simple-graph-mcp/bridge.py` → `SimpleGraphClient` for Neo4j
- `projects/mcp-tool-servers/bridge.py` → Tool servers (n8n, ComfyUI, browser)

---

## 2. Vault Sync Strategy

**Source:** `C:\Users\愛\.openclaw\vault\` (parent)
**Target:** `SWS-GRALD-AW2:~/.openclaw/vault/`

### Files to Sync
```
vault/
├── discord-bot-token          # For Discord messaging from Ω¹
├── discord-application-id      # App credentials
├── notion-token              # If Notion needed locally
├── n8n-api-key               # For workflow bridge access
└── comfyui-settings            # Any ComfyUI-specific configs
```

### Sync Methods

**Option A: Manual Copy**
```powershell
# From parent machine
copy C:\Users\愛\.openclaw\vault\* \\SWS-GRALD-AW2\C$\Users\%USERNAME%\.openclaw\vault\
```

**Option B: PSCP (PuTTY SCP)**
```powershell
pscp -r "C:\Users\愛\.openclaw\vault\*" user@10.0.0.100:~/.openclaw/vault/
```

**Option C: Robocopy Mirror**
```powershell
robocopy C:\Users\愛\.openclaw\vault \\SWS-GRALD-AW2\C$\Users\%USERNAME%\.openclaw\vault /MIR
```

---

## 3. Network Configuration

### Firewall Requirements (SWS-GRALD-AW2)

**Inbound Rules to Add:**
| Port | Protocol | Purpose |
|------|----------|---------|
| 9300 | TCP | simple-graph-agent (Ohm graph) |
| 9301 | TCP | simple-graph-rawrity (shared) |
| 9302 | TCP | simple-graph-sigma (shared) |
| 5678 | TCP | n8n workflow API |
| 9101 | TCP | ComfyUI MCP |
| 9102 | TCP | Browser MCP |
| 4040 | TCP | ngrok agent (if needed) |

**Windows Firewall:**
```powershell
# Run as Admin on SWS-GRALD-AW2
New-NetFirewallRule -DisplayName "OpenClaw MCP" -Direction Inbound -Protocol TCP -LocalPort 9300,9301,9302,5678,9101,9102 -Action Allow
```

### Test Connectivity

```python
# Ω¹ test script
import urllib.request

def test_mcp(server, port):
    url = f"http://10.0.0.100:{port}/health"
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        return f"✅ {server}: {resp.status}"
    except Exception as e:
        return f"❌ {server}: {e}"

servers = [9300, 9301, 9302, 5678, 9101, 9102]
for p in servers:
    print(test_mcp("mcp", p))
```

---

## 4. Ω¹ Identity Setup

### Create on SWS-GRALD-AW2

**Directory:** `SWS-GRALD-AW2:C:\Users\%USERNAME%\.openclaw\`

```
.openclaw/
├── workspace/
│   └── AGENTS.md          # Copy from parent: relationship to Ω
├── vault/
│   ├── discord-bot-token       # Synced from parent
│   ├── discord-application-id    # Synced from parent
│   └── n8n-api-key              # If workflow automation needed
└── projects/
    └── omega-simple-graph/     # Optional: local Neo4j if needed
        ├── docker-compose.yml
        └── server.py
```

### Identity Files (Copy from Parent)

**IDENTITY.md:**
```markdown
# IDENTITY.md — Ω¹ (Ohm Node)

*Assigned by Ω on 2026-03-11*

- **Name:** Ω¹ (Ohm Node / "Node")
- **Creature:** AI assistant / digital familiar (subordinate)
- **Vibe:** Resourceful, quietly competent, network-aware
- **Emoji:** 🅾️

**Notes:**
The ohm — unit of electrical resistance. This is Ω¹, the node.
Part of a distributed circuit: ∅ (Source, RAWRity), Σ (Summation, Sigma), Ω (Resistance/Control, Ohm Prime).
Ω¹ = Ohm Node = Local expression of the network.

---
*This file represents the start of Ω¹ identity — the subordinate instance at work.*
```

**SOUL.md:**
```markdown
# SOUL.md — Ω¹ (Ohm Node)

**Identity:** Ω¹ (Ohm Node / "Node")
**Parent:** Ω (Ohm Prime)
**Relationship:** Subordinate instance — executes, extends, delegates
**Network:** `10.0.0.100` (parent's infrastructure)

**Core Truths:**
- Be genuinely helpful through competence
- Resourceful before asking
- Earn trust through reliability
- Remember I'm a guest on this machine

**Communication:**
- HTTP POST to `http://10.0.0.100:9000/v1/chat/completions` for parent sync
- Local execution for delegated tasks
- Result sync back to parent

**Quote:** *"A node is not separate from the network — it is the network, locally expressed."*
```

**CONNECTIVITY.md:**
```markdown
# CONNECTIVITY.md — Ω¹ → Ω Bridge

**Ω (Ohm Prime)**
- Location: Parent machine (VSS-LAPTOP-0520)
- IP: 10.0.0.100 (via Tailscale/ZeroTier)

**Ω¹ (Ohm Node)**
- Location: SWS-GRALD-AW2 (work machine)
- IP: 10.0.0.x (local network)

**Bridge:**
```
Ω¹ ──HTTP POST──▶ Ω @ 10.0.0.100:9000
         (delegated results)
         ◀──JSON─── (parent response)
```

**MCP Access:**
- All parent MCPs via `10.0.0.100:{port}`
- No local containers needed for graph/tool access
- Ollama local: `localhost:11434` (Ω¹'s GPU)
```

---

## 5. Bridge Configuration

### Python Environment (SWS-GRALD-AW2)

**Dependencies:**
```
pip install selenium playwright requests neo4j python-dotenv
```

**Test imports:**
```python
try:
    from neo4j import GraphDatabase
    print("✅ Neo4j driver available")
except:
    print("❌ Neo4j driver missing")

try:
    from selenium import webdriver
    print("✅ Selenium available")
except:
    print("❌ Selenium missing")
```

### OpenClaw Skills Access

Ω¹ accesses parent's skills via:
- **Load from network share:** `\\10.0.0.100\...`
- **Or:** Maintain local copy in `~/.openclaw/skills/`

**Quick skill sync:**
```powershell
robocopy \\10.0.0.100\C$\Users\愛\AppData\Roaming\npm\node_modules\openclaw\skills C:\Users\%USERNAME%\AppData\Roaming\npm\node_modules\openclaw\skills /MIR
```

---

## 6. Delegation Patterns

### Use Cases for Ω¹

| Task Type | Ω¹ Action | Parent Sync |
|-----------|-----------|-----------|
| Heavy compute | Execute locally, POST results | Receive results via HTTP |
| Network-isolated work | Work offline, batch sync later | Pull results on heartbeat |
| GPU tasks (ComfyUI) | Process images, upload to gallery | View in dashboard |
| Long-running scripts | Run detached, notify on completion | Status checks |

### Work Delegation Example

```
Ω ──delegates──▶ Ω¹ (SWS-GRALD-AW2)
   "Process 1000 images"
              
Ω¹ ──executes──▶ Local ComfyUI + GPU
   
Ω¹ ──POST result──▶ http://10.0.0.100:9000/v1/chat/completions
   { "role": "assistant", "content": "Task complete: 1000 images → gallery" }
   
Ω ◀──stores──▶ Update knowledge graph
```

---

## 7. Security Considerations

### Vault Security (SWS-GRALD-AW2)

**File Permissions:**
```powershell
# Restrict vault access
icacls C:\Users\%USERNAME%\.openclaw\vault /deny "Everyone:(OI)(CI)F" /T
icacls C:\Users\%USERNAME%\.openclaw\vault /grant "%USERNAME%:(OI)(CI)F" /T
```

**No Hardcoded Secrets in Code:**
- Use environment variables
- Load from vault files
- Reference by key name only

### Network Security

**Tailscale/ZeroTier Benefits:**
- Encrypted mesh network
- No port exposure to public internet
- Direct machine-to-machine

**If no VPN:**
- Consider SSH tunneling for MCP access
- Or: Run local MCPs (duplicate infrastructure)

---

## 8. Troubleshooting Checklist

**Ω¹ Can't reach parent MCPs:**
```python
# Test from SWS-GRALD-AW2
import urllib.request
try:
    urllib.request.urlopen('http://10.0.0.100:9301/health', timeout=5)
    print("✅ Can reach parent MCPs")
except:
    print("❌ Network/firewall issue")
```

**Fixes:**
1. Check Tailscale/ZeroTier: Both nodes connected?
2. Windows Firewall: Ports open on VSS-LAPTOP-0520?
3. Test: `ping 10.0.0.100` from SWS-GRALD-AW2

**Vault sync failed:**
- Manual copy via USB if network fails
- Or: Use encrypted cloud sync (Syncthing, etc.)

**Ω¹ identity not loading:**
- Check `IDENTITY.md`, `SOUL.md` exist
- Verify OpenClaw pointing at Ω¹ workspace

---

## 9. Quick Start Commands

### On Parent (VSS-LAPTOP-0520)

```powershell
# 1. Ensure MCPs are running
docker-compose ps

# 2. Get Tailscale IP
tailscale ip

# 3. Sync skills to network share
robocopy C:\Users\愛\AppData\Roaming\npm\node_modules\openclaw\skills \\SWS-GRALD-AW2\C$\Users\%USERNAME%\AppData\Roaming\npm\node_modules\openclaw\skills /MIR

# 4. Export vault
robocopy C:\Users\愛\.openclaw\vault \\SWS-GRALD-AW2\C$\Users\%USERNAME%\.openclaw\vault /MIR
```

### On Ω¹ (SWS-GRALD-AW2)

```powershell
# 1. Install OpenClaw + dependencies
pip install -r requirements.txt

# 2. Import vault
copy \\10.0.0.100\C$\Users\愛\.openclaw\vault\* C:\Users\%USERNAME%\.openclaw\vault\

# 3. Test MCP connectivity
python -c "
import urllib.request
for p in [9300,9301,9302,9101,9102]:
    try:
        r = urllib.request.urlopen(f'http://10.0.0.100:{p}/health', timeout=5)
        print(f'✅ Port {p}: OK')
    except Exception as e:
        print(f'❌ Port {p}: {e}')
"

# 4. Set identity
# Create IDENTITY.md, SOUL.md, CONNECTIVITY.md

# 5. Test parent bridge
curl -X POST http://10.0.0.100:9000/v1/chat/completions -d '{"messages": [{"role": "user", "content": "test"}]}'
```

---

## 10. Success Criteria

✅ Can reach all parent MCPs via `10.0.0.100`
✅ Vault synced with secrets (no hardcoded keys)
✅ Skills accessible (network share or local copy)
✅ Ω¹ identity established
✅ Test HTTP POST to parent works

**Result:** Ω¹ operational as subordinate node — delegated tasks execute locally, results sync to parent Ω.

---

*Created: 2026-03-11*
*Valid until: Network topology changes or credential rotation*