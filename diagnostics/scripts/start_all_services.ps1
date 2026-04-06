# Start All OpenClaw Services
# Powershell script to launch all required services

Write-Host "=== Starting OpenClaw Services ===" -ForegroundColor Cyan

# 1. Simple Graph MCP Servers
cd projects/simple-graph-mcp
Write-Host "Starting Simple Graph MCP servers..." -ForegroundColor Green
docker-compose -f docker-compose.multiuser.yml up -d
cd ../..

# Wait for Neo4j to be healthy
Write-Host "Waiting for Neo4j instances to be healthy..." -ForegroundColor Yellow
Start-Sleep 10

# 2. Tool Servers (n8n-mcp, comfyui-mcp, etc.)
cd projects/mcp-tool-servers
Write-Host "Starting Tool MCP servers..." -ForegroundColor Green
docker-compose up -d
cd ../..

# 3. Wallpaper Bridge
Write-Host "Starting Wallpaper Bridge..." -ForegroundColor Green
Start-Process python -ArgumentList "bridge_server.py" -WorkingDirectory "projects/wallpapers/dataviz/retro-terminal" -WindowStyle Hidden
Start-Sleep 2

# 4. Static Wallpaper Server (port 8889)
Write-Host "Starting Wallpaper static server..." -ForegroundColor Green
Start-Process python -ArgumentList "-m","http.server","8889","--bind","0.0.0.0" -WorkingDirectory "projects/wallpapers/dataviz/control-terminal-v1.1" -WindowStyle Hidden

Write-Host ""
Write-Host "=== Services Started ===" -ForegroundColor Cyan

# Check status
Write-Host ""
Write-Host "Checking service health..." -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test wallpaper bridge
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/api/graph/rawrity" -Method GET -TimeoutSec 5
    Write-Host "✅ Wallpaper Bridge: OK (200)" -ForegroundColor Green
} catch {
    Write-Host "❌ Wallpaper Bridge: Failed" -ForegroundColor Red
}

# Test static server
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8889/index.html" -Method HEAD -TimeoutSec 5
    Write-Host "✅ Static Server: OK (200)" -ForegroundColor Green
} catch {
    Write-Host "❌ Static Server: Failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Quick Links ===" -ForegroundColor Cyan
Write-Host "Neo4j Browsers:"
Write-Host "  - RAWRity: http://localhost:7474"
Write-Host "  - Sigma:   http://localhost:7574"
Write-Host "  - Agent:   http://localhost:7674"
Write-Host ""
Write-Host "Wallpaper: http://localhost:8889/index.html"
Write-Host "API Bridge: http://localhost:8080/api/graph/rawrity"
Write-Host ""
