---
name: figma

description: Connect to Figma for design extraction, creation, and debugging via the Figma Console MCP server. Supports reading files, extracting components/styles/variables, creating UI elements, and debugging Figma plugins.

metadata:
  {
    "openclaw":
      { "emoji": "🎨", "requires": { "env": ["FIGMA_API_KEY"], "tools": ["npx", "figma-desktop"], "note": "Requires Figma Desktop app with Desktop Bridge plugin" },
  }
---

# Figma Integration

This skill connects to Figma via the `figma-console-mcp` server, giving AI assistants complete access to Figma for extraction, creation, and debugging.

## Prerequisites

1. **Figma Desktop App** — Must have Figma installed locally
2. **Desktop Bridge Plugin** — Install from Figma: `Plugins → Development → Figma Desktop Bridge`
   - Manifest location: `C:\AI\_BOT\AppData\Roaming\npm\node_modules\figma-console-mcp\figma-desktop-bridge\manifest.json`
3. **API Token** — Personal access token configured in `~/.openclaw/vault/figma-token`

## Quick Start

### Step 1: Start MCP Server (in PowerShell)

```powershell
# Load token from vault
$env:FIGMA_API_KEY = Get-Content "$env:USERPROFILE\.openclaw\vault\figma-token"

# Start the MCP server
npx figma-console-mcp
```

Or run the helper script:
```powershell
. "$env:USERPROFILE\.openclaw\workspace\skills\figma\scripts\run_mcp.ps1"
```

### Step 2: Open Figma Desktop Bridge

1. Open any Figma file in **Figma Desktop** (not browser)
2. Go to: `Plugins → Development → Figma Desktop Bridge`
3. Wait for the MCP server console to show: `Connected successfully`

### Step 3: Test Connection

Once connected, the MCP server is ready. Available tools include:
- `figma_get_file` — Get file info and content
- `figma_get_components` — Extract component library
- `figma_get_styles` — Get color/text/effect styles
- `figma_get_variables` — Read design tokens
- `figma_create_rectangle` — Create UI elements
- `figma_take_screenshot` — Capture the canvas
- And 50+ more...

## Capabilities

### Read Operations (56+ tools)
- Get files, pages, and thumbnails
- Extract components and component sets
- Read styles (colors, text, effects, grids)
- Access variables/design tokens
- Get file statistics and analytics

### Write Operations (requires Desktop Bridge)
- Create frames, shapes, and UI elements
- Edit existing designs
- Manage variables (create/update/delete)
- Generate component documentation
- Take screenshots
- Debug plugin console logs

## Architecture

```
OpenClaw ←→ figma-console-mcp (stdio) ←→ WebSocket Bridge ←→ Figma Desktop ←→ Figma API
     ↑
   MCP Protocol (JSON-RPC)
```

## File Key Format

Figma file URLs look like:
```
https://www.figma.com/file/FILE_KEY/file-name
```

The `FILE_KEY` is the long alphanumeric string after `/file/`.

## Resources

- **Documentation:** https://docs.figma-console-mcp.southleft.com
- **NPM Package:** https://www.npmjs.com/package/figma-console-mcp
- **GitHub:** https://github.com/southleft/figma-console-mcp

## Troubleshooting

### "Failed to connect to Figma Desktop"
- Ensure Figma Desktop app is running (not browser)
- Check Desktop Bridge plugin is installed and open
- Verify token is valid at https://www.figma.com/developers/api#access-tokens
- Check firewall isn't blocking localhost:9222

### "WebSocket transport not available"
- First connection requires Desktop Bridge plugin to be active
- The MCP server will auto-connect once the plugin is open
- Try restarting the MCP server if connection fails
