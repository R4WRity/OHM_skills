#!/usr/bin/env python3
"""
Create OpenClaw Architecture diagram in Figma via MCP.
This script launches the MCP server and sends all commands.
Usage: python figma_build_architecture.py
"""

import json
import os
import subprocess
import sys
import time

def get_token():
    path = os.path.expanduser("~/.openclaw/vault/figma-token")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return os.environ.get('FIGMA_API_KEY')

def main():
    token = get_token()
    if not token:
        print("❌ Figma token not found!")
        sys.exit(1)
    
    print("🎨 OpenClaw Architecture Builder")
    print("=" * 60)
    print()
    print("⚠️  REQUIRED: Before running:")
    print("   1. Figma Desktop is OPEN")
    print("   2. Desktop Bridge plugin is RUNNING")
    print("   3. File 'Ohm Design Space' is active")
    print()
    print("This script will:")
    print("   - Start MCP server")
    print("   - Wait for connection")
    print("   - Create architecture diagram")
    print()
    input("Press ENTER when ready...")
    print()
    
    # Architecture definition
    architecture = [
        # Title
        {
            "name": "figma_create_text",
            "args": {
                "characters": "⚡ OpenClaw Framework Architecture",
                "fontSize": 32,
                "x": 50, "y": 30,
                "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}]
            }
        },
        # Layer 1: Gateway
        {
            "name": "figma_create_frame",
            "args": {
                "name": "🤖 OpenClaw Gateway",
                "x": 50, "y": 100,
                "width": 1100, "height": 200,
                "background": {"r": 0.39, "g": 0.4, "b": 0.94}  # Indigo
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "• Router → Sessions → Agent Dispatcher → MCP Client",
                "fontSize": 16, "x": 70, "y": 140
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "• Message Handler | Heartbeat Manager | Cron Scheduler",
                "fontSize": 16, "x": 70, "y": 170
            }
        },
        
        # Connection arrow
        {
            "name": "figma_create_line",
            "args": {
                "x": 600, "y": 300,
                "width": 0, "height": 60,
                "strokes": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}]
            }
        },
        
        # Layer 2: User Workspaces
        {
            "name": "figma_create_frame",
            "args": {
                "name": "👤 User Workspaces",
                "x": 50, "y": 380,
                "width": 1100, "height": 280,
                "background": {"r": 0.06, "g": 0.73, "b": 0.51}  # Emerald
            }
        },
        {
            "name": "figma_create_frame",
            "args": {
                "name": "∅ RAWRity",
                "x": 80, "y": 420,
                "width": 320, "height": 200,
                "background": {"r": 0.1, "g": 0.5, "b": 0.4}
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "Port 9301\nNeo4j 7474/7687\nWorkspace: .",
                "fontSize": 14, "x": 100, "y": 450
            }
        },
        {
            "name": "figma_create_frame",
            "args": {
                "name": "Σ Sigma",
                "x": 440, "y": 420,
                "width": 320, "height": 200,
                "background": {"r": 0.1, "g": 0.5, "b": 0.4}
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "Port 9302\nNeo4j 7574/7787\nWorkspace: users/Sigma",
                "fontSize": 14, "x": 460, "y": 450
            }
        },
        {
            "name": "figma_create_frame",
            "args": {
                "name": "Ω Ohm (Agent)",
                "x": 800, "y": 420,
                "width": 320, "height": 200,
                "background": {"r": 0.1, "g": 0.5, "b": 0.4}
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "Port 9300\nNeo4j 7674/7887\nGraph: Agent Memory",
                "fontSize": 14, "x": 820, "y": 450
            }
        },
        
        # Connection arrow
        {
            "name": "figma_create_line",
            "args": {
                "x": 600, "y": 660,
                "width": 0, "height": 60,
                "strokes": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}]
            }
        },
        
        # Layer 3: MCP Servers
        {
            "name": "figma_create_frame",
            "args": {
                "name": "🔧 MCP Servers",
                "x": 50, "y": 740,
                "width": 1100, "height": 300,
                "background": {"r": 0.96, "g": 0.62, "b": 0.04}  # Amber
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "Simple Graph (9300-9302) — Knowledge Graphs with Neo4j",
                "fontSize": 14, "x": 70, "y": 780
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "n8n-mcp (9100) — Workflow Automation + ComfyUI (9101)",
                "fontSize": 14, "x": 70, "y": 820
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "Figma-mcp (9223) ← YOU ARE HERE — Design Bridge",
                "fontSize": 14, "x": 70, "y": 860,
                "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 0}}]  # Yellow highlight
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "Notion (REST API) — Notes, databases, documentation",
                "fontSize": 14, "x": 70, "y": 900
            }
        },
        
        # Connection arrow
        {
            "name": "figma_create_line",
            "args": {
                "x": 600, "y": 1040,
                "width": 0, "height": 60,
                "strokes": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}]
            }
        },
        
        # Layer 4: External Services
        {
            "name": "figma_create_frame",
            "args": {
                "name": "🌐 External Services",
                "x": 50, "y": 1120,
                "width": 1100, "height": 180,
                "background": {"r": 0.93, "g": 0.28, "b": 0.6}  # Pink
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "Discord (Chat) • Notion (Docs) • ComfyUI Local (8188) • Neo4j Browsers • Web Search (Brave)",
                "fontSize": 14, "x": 70, "y": 1160
            }
        },
        {
            "name": "figma_create_text",
            "args": {
                "characters": "Network Imports: \\Vss-laptop-0520\_net  •  Vault: Secrets Storage",
                "fontSize": 12, "x": 70, "y": 1200
            }
        },
        
        # Footer
        {
            "name": "figma_create_text",
            "args": {
                "characters": "OpenClaw v2026.2.3 | Ohm Ω | Last Updated: Feb 26, 2026",
                "fontSize": 12, "x": 50, "y": 1320,
                "fills": [{"type": "SOLID", "color": {"r": 0.6, "g": 0.6, "b": 0.6}}]
            }
        },
    ]
    
    print(f"📦 Prepared {len(architecture)} elements to create")
    print()
    print("📝 JSON-RPC Commands:")
    print("-" * 60)
    
    for i, cmd in enumerate(architecture, 1):
        request = {
            "jsonrpc": "2.0",
            "id": i,
            "method": "tools/call",
            "params": {
                "name": cmd["name"],
                "arguments": cmd["args"]
            }
        }
        print(json.dumps(request))
    
    print("-" * 60)
    print()
    print("📋 To execute:")
    print("   Save these commands to a file, then pipe to the MCP server:")
    print()
    print("   # In PowerShell:")
    print("   Get-Content commands.json | npx figma-console-mcp")
    print()
    print("   # Or manually paste each line into the running MCP server")

if __name__ == '__main__':
    main()
