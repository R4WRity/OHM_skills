# Launch MCP and create architecture diagram
# This script starts the MCP server and pipes the commands

$env:FIGMA_API_KEY = Get-Content "$env:USERPROFILE\.openclaw\vault\figma-token"
$commandsFile = "$env:USERPROFILE\.openclaw\workspace\temp\figma_commands.json"

Write-Host "🎨 Starting Figma MCP Server + Creating Architecture..." -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Make sure:" -ForegroundColor Yellow
Write-Host "   • Figma Desktop is OPEN" -ForegroundColor Gray
Write-Host "   • Desktop Bridge plugin is RUNNING" -ForegroundColor Gray
Write-Host "   • 'Ohm Design Space' file is active" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop after completion" -ForegroundColor Gray
Write-Host ""
Start-Sleep -Seconds 2

Get-Content $commandsFile | npx figma-console-mcp
