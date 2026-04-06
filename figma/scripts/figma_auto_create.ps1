# Automated Figma Architecture Creation
# This script launches MCP, waits for connection, then sends commands
# Usage: .\figma_auto_create.ps1

$ErrorActionPreference = "Stop"

# Config
$tokenPath = "$env:USERPROFILE\.openclaw\vault\figma-token"
$commandsPath = "$env:USERPROFILE\.openclaw\workspace\temp\figma_commands.json"
$maxWaitSeconds = 60

Write-Host "🎨 Figma Automated Architecture Builder" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host ""

# Check prerequisites
if (-not (Test-Path $tokenPath)) {
    Write-Error "❌ Figma token not found at $tokenPath"
    exit 1
}

if (-not (Test-Path $commandsPath)) {
    Write-Error "❌ Commands file not found at $commandsPath"
    exit 1
}

$token = Get-Content $tokenPath
Write-Host "✅ Token loaded: $($token.Substring(0,10))...$($token.Substring($token.Length-10))" -ForegroundColor Green
Write-Host ""

# Check Figma is running
try {
    $figmaProcess = Get-Process "Figma" -ErrorAction SilentlyContinue
    if (-not $figmaProcess) {
        Write-Warning "⚠️ Figma Desktop doesn't appear to be running"
        Write-Host "Please open Figma Desktop and the 'Ohm Design Space' file first" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Figma Desktop is running" -ForegroundColor Green
    }
} catch {}

Write-Host ""
Write-Host "📋 Instructions:" -ForegroundColor White
Write-Host "   1. This script will start the MCP server" -ForegroundColor Gray
Write-Host "   2. You MUST open Desktop Bridge plugin in Figma" -ForegroundColor Yellow
Write-Host "   3. The script will wait for connection (up to $maxWaitSeconds sec)" -ForegroundColor Gray
Write-Host "   4. Once connected, commands will be sent automatically" -ForegroundColor Gray
Write-Host ""

$proceed = Read-Host "Press ENTER to start (or Ctrl+C to cancel)"

# Start MCP server in background
Write-Host ""
Write-Host "🚀 Starting MCP server..." -ForegroundColor Cyan
Write-Host ""

$env:FIGMA_API_KEY = $token

# Create a job to run MCP and capture output
$mcpJob = Start-Job {
    param($cmdPath)
    $env:FIGMA_API_KEY = Get-Content "$env:USERPROFILE\.openclaw\vault\figma-token"
    npx figma-console-mcp 2>&1
}

# Wait for connection
Write-Host "⏳ Waiting for Desktop Bridge connection..." -ForegroundColor Yellow
Write-Host "   (Open Plugins → Development → Figma Desktop Bridge now)" -ForegroundColor Gray
Write-Host ""

$connected = $false
$elapsed = 0
$checkInterval = 2

while ($elapsed -lt $maxWaitSeconds -and -not $connected) {
    Start-Sleep -Seconds $checkInterval
    $elapsed += $checkInterval
    
    # Check job output for connection message
    $output = Receive-Job -Job $mcpJob -Keep
    if ($output -match "Connected successfully" -or $output -match "auto-connect.*success") {
        $connected = $true
        Write-Host ""
        Write-Host "✅ Desktop Bridge connected!" -ForegroundColor Green
    } else {
        Write-Host "   Waiting... ($elapsed sec / $maxWaitSeconds sec)" -ForegroundColor Gray
    }
}

if (-not $connected) {
    Write-Host ""
    Write-Error "❌ Timeout: Desktop Bridge didn't connect within $maxWaitSeconds seconds"
    Stop-Job -Job $mcpJob
    Remove-Job -Job $mcpJob -Force
    exit 1
}

# Small delay to ensure connection is stable
Start-Sleep -Seconds 2

# Send commands
Write-Host ""
Write-Host "📤 Sending architecture commands..." -ForegroundColor Cyan
Write-Host ""

$commands = Get-Content $commandsPath
$totalCommands = $commands.Count
$successCount = 0
$failCount = 0

foreach ($i in 0..($totalCommands-1)) {
    $cmd = $commands[$i]
    $cmdNum = $i + 1
    
    Write-Host "   [$cmdNum/$totalCommands] Sending command..." -ForegroundColor Gray -NoNewline
    
    try {
        # Send command to MCP stdin (via job)
        $tempCmd = $cmd | ConvertFrom-Json
        $result = Invoke-Command -Job $mcpJob -ScriptBlock {
            param($inputCmd)
            $inputCmd | npx figma-console-mcp
        } -ArgumentList $cmd
        
        Write-Host " ✅" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host " ❌" -ForegroundColor Red
        $failCount++
    }
    
    # Small delay between commands
    Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Complete!" -ForegroundColor Green
Write-Host "   Success: $successCount | Failed: $failCount" -ForegroundColor White
Write-Host ""
Write-Host "📁 Check your Figma file: Ohm Design Space" -ForegroundColor Cyan

# Cleanup
Stop-Job -Job $mcpJob
Remove-Job -Job $mcpJob -Force

Read-Host "Press ENTER to exit"
