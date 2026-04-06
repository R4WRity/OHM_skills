# Skill Propagation Solution

## Problem

When users run `/load-user` to switch to their workspace, skills like `/tunnel` and `/onboard` become inaccessible because:

1. Working directory changes to `users/{name}/`
2. Relative paths like `skills/ngrok/...` no longer resolve correctly
3. Commands fail with "file not found" or similar errors

## Solution

All skill scripts now use **`__dirname`** for path resolution, making them **working-directory independent**.

### Implementation

**Before (broken):**
```javascript
const STATE_FILE = './active-tunnels.json';  // Relative to cwd
```

**After (fixed):**
```javascript
const STATE_FILE = path.join(__dirname, '..', 'active-tunnels.json');  // Absolute
```

### Verified Skills

| Skill | Scripts | Status |
|-------|---------|--------|
| ngrok | tunnel-start.js, tunnel-stop.js, tunnel-status.js | ✅ Fixed |
| user-onboarding | onboard.js, onboard_bot.py, store_answer.py | ✅ Fixed |
| load-user | load-user.js, validate-skills.js | ✅ Fixed |

## Usage After /load-user

### Method 1: Relative from Workspace Root (Recommended)
```
@exec node skills/ngrok/scripts/tunnel-start.js portfolio
```

### Method 2: Absolute Path (Always Works)
```
@exec node "C:/Users/愛/.openclaw/workspace/skills/ngrok/scripts/tunnel-start.js" portfolio
```

### Method 3: Using Path Resolver
```
@exec node skills/load-user/scripts/resolve-skill-path.js ngrok tunnel-start.js
```

## New Helper Scripts

### validate-skills.js
Shows all available skills with their absolute paths:
```bash
node skills/load-user/scripts/validate-skills.js Set
```

### test-skill-propagation.js
Verifies skills work from user context:
```bash
node skills/load-user/scripts/test-skill-propagation.js Set
```

### resolve-skill-path.js
Returns absolute path to any skill script:
```bash
node skills/load-user/scripts/resolve-skill-path.js ngrok tunnel-start.js
# Output: C:\Users\愛\.openclaw\workspace\skills\ngrok\scripts\tunnel-start.js
```

## Updated Load-User Output

When you run `/load-user`, you'll now see:
```
✅ Loaded user: Set (∅)
📁 Workspace: users/Set/
📝 Context: AGENTS.md, USER.md, MEMORY.md, memory/2026-02-15.md
🔌 MCP Server: ✅ Running
...

🛠️ Available Skills (use from any context):
   ngrok: /tunnel, /tunnel_stop, /tunnel_status
   user-onboarding: /onboard, /onboard quick, /onboard full
   load-session: /load-session
   save-session: /save-session
   discord-user-bridge: /send-to

   All skills resolve paths via __dirname — they work regardless of user context.
   Run: node skills/load-user/scripts/validate-skills.js Set
```

## Testing the Fix

1. Run `/load-user Set` (or your username)
2. Try a skill command: `@exec node skills/ngrok/scripts/tunnel-status.js`
3. Should work regardless of working directory

## Notes

- Skills are discovered at startup by OpenClaw scanning `skills/*/SKILL.md`
- User context loading doesn't affect skill discovery
- Only script execution paths needed fixing
- All skills now use absolute path resolution
