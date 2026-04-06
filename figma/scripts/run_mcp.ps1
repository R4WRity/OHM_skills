# Run Figma MCP Server with Figma Desktop Bridge
# Usage: Run this in PowerShell

$env:FIGMA_API_KEY = Get-Content "$env:USERPROFILE\.openclaw\vault\figma-token"

Write-Host "🎨 Starting Figma MCP Server..." -ForegroundColor Cyan
Write-Host "Token: $($env:FIGMA_API_KEY.Substring(0,10))...$($env:FIGMA_API_KEY.Substring($env:FIGMA_API_KEY.Length-10))" -ForegroundColor Gray
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Instructions:" -ForegroundColor White
Write-Host "   1. Open Figma Desktop with any file" -ForegroundColor Gray
Write-Host "   2. Run Plugins → Development → Figma Desktop Bridge" -ForegroundColor Gray
Write-Host "   3. Wait for 'Connected successfully' message below" -ForegroundColor Gray
Write-Host "   4. Press Ctrl+C to stop when done testing" -ForegroundColor Gray
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host ""

npx figma-console-mcp
