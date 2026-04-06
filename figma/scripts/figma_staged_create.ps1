# Staged Figma Architecture Creation
# Stage 1: Start MCP and wait for connection
# Stage 2: Send commands once connected
# Usage: .\figma_staged_create.ps1 [1|2]

param(
    [Parameter()]
    [ValidateSet(1, 2)]
    [int]$Stage = 1
)

$ErrorActionPreference = "Stop"

# Config
$tokenPath = "$env:USERPROFILE\.openclaw\vault\figma-token"
$commandsPath = "$env:USERPROFILE\.openclaw\workspace\temp\figma_commands.json"

Write-Host ""
Write-Host "🎨 Figma Architecture Builder" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host ""

# Check token
if (-not (Test-Path $tokenPath)) {
    Write-Error "❌ Token not found at $tokenPath"
    exit 1
}

$token = Get-Content $tokenPath
Write-Host "✅ Token loaded" -ForegroundColor Green

# Check commands
if (-not (Test-Path $commandsPath)) {
    Write-Error "❌ Commands not found at $commandsPath"
    exit 1
}
Write-Host "✅ Commands loaded" -ForegroundColor Green

if ($Stage -eq 1) {
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  STAGE 1: START MCP SERVER AND WAIT FOR CONNECTION" -ForegroundColor Yellow
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  IMPORTANT:" -ForegroundColor Red
    Write-Host "   You MUST complete this step before Stage 2!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Instructions:" -ForegroundColor White
    Write-Host "   1. Run this script (MCP server will start)" -ForegroundColor Gray
    Write-Host "   2. Open Figma Desktop with 'Ohm Design Space'" -ForegroundColor Gray
    Write-Host "   3. In Figma: Plugins → Development → Figma Desktop Bridge" -ForegroundColor Gray
    Write-Host "   4. Wait for '🟢 CONNECTED' message below" -ForegroundColor Green
    Write-Host "   5. Keep this terminal OPEN" -ForegroundColor Red
    Write-Host "   6. Open NEW terminal and run:" -ForegroundColor Cyan
    Write-Host "      .\figma_staged_create.ps1 -Stage 2" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    
    $proceed = Read-Host "Press ENTER to start MCP server"
    Write-Host ""
    Write-Host "🚀 Launching MCP server..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    Waiting for Desktop Bridge connection..." -ForegroundColor Yellow
    Write-Host ""
    
    $env:FIGMA_API_KEY = $token
    npx figma-console-mcp
    
} elseif ($Stage -eq 2) {
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  STAGE 2: SEND ARCHITECTURE COMMANDS" -ForegroundColor Green
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    
    # Verify MCP is running
    $mcpRunning = Get-Process | Where-Object { $_.ProcessName -match "node" -or $_.CommandLine -match "figma-console-mcp" } | Select-Object -First 1
    
    if (-not $mcpRunning) {
        Write-Warning "⚠️  MCP server doesn't appear to be running"
        Write-Host "    Did you complete Stage 1?" -ForegroundColor Yellow
        Write-Host ""
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y") {
            exit 0
        }
    }
    
    Write-Host "📤 Sending architecture commands..." -ForegroundColor Cyan
    Write-Host ""
    
    $commands = Get-Content $commandsPath
    $total = $commands.Count
    $success = 0
    $failed = 0
    
    foreach ($i in 0..($total-1)) {
        $cmd = $commands[$i]
        $num = $i + 1
        Write-Host "   [$num/$total] Sending... " -ForegroundColor Gray -NoNewline
        
        try {
            $result = $cmd | npx figma-console-mcp 2>$null
            if ($result -match '"isError":true') {
                Write-Host "❌" -ForegroundColor Red
                $failed++
            } else {
                Write-Host "✅" -ForegroundColor Green
                $success++
            }
        } catch {
            Write-Host "❌" -ForegroundColor Red
            $failed++
        }
        
        Start-Sleep -Milliseconds 300
    }
    
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ COMPLETE!" -ForegroundColor Green
    Write-Host "   Success: $success | Failed: $failed" -ForegroundColor White
    Write-Host ""
    Write-Host "📁 Check your Figma file: Ohm Design Space" -ForegroundColor Cyan
    Write-Host ""
}
