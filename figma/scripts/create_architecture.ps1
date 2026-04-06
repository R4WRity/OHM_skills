# Create OpenClaw Architecture in Figma
# Run this WHILE npx figma-console-mcp is running in another terminal

$token = Get-Content "$env:USERPROFILE\.openclaw\vault\figma-token"
$fileKey = "hK9QLlgqO45nJ1xuCAQLXp"

Write-Host "🎨 Creating OpenClaw Architecture..." -ForegroundColor Cyan

# Note: This requires the MCP server to be running
# and accepting JSON-RPC commands via stdin

$commands = @'
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"figma_create_frame","arguments":{"name":"OpenClaw Gateway","x":50,"y":100,"width":1100,"height":250,"fills":[{"type":"SOLID","color":{"r":0.39,"g":0.4,"b":0.94}}]}}}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"Router → Sessions","fontSize":14,"x":70,"y":140}}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"Message Handler","fontSize":14,"x":70,"y":170}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"Agent Dispatcher","fontSize":14,"x":70,"y":200}}}
{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"MCP Client","fontSize":14,"x":70,"y":230}}}
{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"figma_create_frame","arguments":{"name":"User Workspaces","x":50,"y":400,"width":1100,"height":280,"fills":[{"type":"SOLID","color":{"r":0.06,"g":0.73,"b":0.51}}]}}}
{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"∅ RAWRity (Omega) → Port 9301","fontSize":14,"x":70,"y":440}}}
{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"Σ Sigma (UltraMC) → Port 9302","fontSize":14,"x":450,"y":440}}}
{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"Ω Ohm (Agent) → Port 9300","fontSize":14,"x":750,"y":440}}}
{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"figma_create_frame","arguments":{"name":"MCP Servers","x":50,"y":720,"width":1100,"height":250,"fills":[{"type":"SOLID","color":{"r":0.96,"g":0.62,"b":0.04}}]}}}
{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"Simple Graph (9300-9302) - Neo4j Knowledge Graphs","fontSize":14,"x":70,"y":760}}}
{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"n8n-mcp (9100) - Workflow Automation","fontSize":14,"x":70,"y":800}}}
{"jsonrpc":"2.0","id":13,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"ComfyUI-mcp (9101) - Image Generation","fontSize":14,"x":70,"y":840}}}
{"jsonrpc":"2.0","id":14,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"Figma-mcp (9223) - Design Bridge","fontSize":14,"x":70,"y":880}}}
{"jsonrpc":"2.0","id":15,"method":"tools/call","params":{"name":"figma_create_frame","arguments":{"name":"External Services","x":50,"y":1020,"width":1100,"height":220,"fills":[{"type":"SOLID","color":{"r":0.93,"g":0.28,"b":0.6}}]}}}
{"jsonrpc":"2.0","id":16,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"Discord | Notion | ComfyUI Local (8188) | Neo4j Browsers | Brave Search","fontSize":14,"x":70,"y":1060}}}
{"jsonrpc":"2.0","id":17,"method":"tools/call","params":{"name":"figma_create_text","arguments":{"characters":"OpenClaw Framework Architecture v2026.2","fontSize":24,"x":50,"y":50}}}
'@

# Save commands to file
$commands | Out-File -FilePath "$env:TEMP\figma_commands.jsonl" -Encoding UTF8

Write-Host "✅ Commands prepared!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Make sure npx figma-console-mcp is running" -ForegroundColor Gray
Write-Host "   2. Copy and paste the commands from:" -ForegroundColor Gray
Write-Host "      $env:TEMP\figma_commands.jsonl" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Or run directly with:" -ForegroundColor Yellow
Write-Host "      Get-Content '$env:TEMP\figma_commands.jsonl' | npx figma-console-mcp" -ForegroundColor Cyan
