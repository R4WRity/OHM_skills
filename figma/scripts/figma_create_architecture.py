#!/usr/bin/env python3
"""
Create OpenClaw Framework Architecture diagram in Figma.
Usage: python figma_create_architecture.py <file_key>
"""

import argparse
import json
import os
import subprocess
import sys

FIGMA_FILE_KEY = "hK9QLlgqO45nJ1xuCAQLXp"

def get_token():
    path = os.path.expanduser("~/.openclaw/vault/figma-token")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return os.environ.get('FIGMA_API_KEY')

def create_mcp_request(tool_name, args_dict):
    """Create JSON-RPC request for MCP."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": args_dict
        }
    }

def send_to_mcp(proc, request):
    """Send request to MCP server."""
    line = json.dumps(request) + "\n"
    proc.stdin.write(line.encode())
    proc.stdin.flush()
    
    # Read response
    response_line = proc.stdout.readline()
    return json.loads(response_line.decode())

def create_architecture_diagram():
    """Create the full architecture diagram via MCP."""
    token = get_token()
    if not token:
        print("❌ Figma token not found!")
        sys.exit(1)
    
    print("🎨 Creating OpenClaw Framework Architecture...")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: Before running:")
    print("   1. Make sure Figma Desktop is open")
    print("   2. Desktop Bridge plugin is active")
    print("   3. npx figma-console-mcp is running in another terminal")
    print()
    print("Architecture includes:")
    print("   • OpenClaw Gateway (central hub)")
    print("   • User Workspaces (∅ RAWRity, Σ Sigma)")
    print("   • MCP Servers (Simple Graph, n8n, ComfyUI, Figma)")
    print("   • Neo4j Databases (7474, 7574, 7674)")
    print("   • External Services (Discord, Notion, ComfyUI)")
    print()
    print("=" * 60)
    
    # Instructions for manual creation
    print("\n📋 Manual MCP Commands:")
    print()
    print("1. Start MCP server:")
    print(f"   $env:FIGMA_API_KEY = Get-Content '$env:USERPROFILE\\.openclaw\\vault\\figma-token'")
    print("   npx figma-console-mcp")
    print()
    print("2. Once connected, use these tool calls:")
    print()
    
    # Define the architecture
    architecture = {
        "title": "OpenClaw Framework Architecture",
        "layers": [
            {
                "name": "🤖 OpenClaw Gateway",
                "y": 100,
                "color": "#6366F1",  # Indigo
                "components": [
                    "Router → Sessions",
                    "Message Handler",
                    "Agent Dispatcher",
                    "MCP Client"
                ]
            },
            {
                "name": "👤 User Workspaces",
                "y": 400,
                "color": "#10B981",  # Emerald
                "components": [
                    "∅ RAWRity (Omega)",
                    "  └─ Port 9301 / Neo4j 7474",
                    "Σ Sigma (UltraMC)",
                    "  └─ Port 9302 / Neo4j 7574",
                    "Ω Ohm (Agent)",
                    "  └─ Port 9300 / Neo4j 7674"
                ]
            },
            {
                "name": "🔧 MCP Servers",
                "y": 700,
                "color": "#F59E0B",  # Amber
                "components": [
                    "Simple Graph (9300-9302)",
                    "  └─ HTTP + Neo4j Bridge",
                    "n8n-mcp (9100)",
                    "  └─ Workflow Docs + Execution",
                    "ComfyUI-mcp (9101)",
                    "  └─ Image Generation",
                    "Figma-mcp (9223)",
                    "  └─ Design Bridge"
                ]
            },
            {
                "name": "🌐 External Services",
                "y": 1000,
                "color": "#EC4899",  # Pink
                "components": [
                    "Discord (Bot)",
                    "Notion (API)",
                    "ComfyUI Local (8188)",
                    "Neo4j Browsers (7474/7574/7674)",
                    "Web Search (Brave)"
                ]
            }
        ]
    }
    
    print(json.dumps({
        "tool": "figma_create_frame",
        "args": {
            "name": "OpenClaw Architecture",
            "x": 0,
            "y": 0,
            "width": 1200,
            "height": 1400,
            "fill_color": "#1E1E1E"
        }
    }, indent=2))
    print()
    
    for i, layer in enumerate(architecture["layers"]):
        print(f"# Layer {i+1}: {layer['name']}")
        print(json.dumps({
            "tool": "figma_create_frame",
            "args": {
                "name": layer["name"],
                "x": 50,
                "y": layer["y"],
                "width": 1100,
                "height": 250,
                "fill_color": layer["color"],
                "layoutMode": "VERTICAL",
                "itemSpacing": 10
            }
        }, indent=2))
        print()
        
        for j, component in enumerate(layer["components"]):
            print(json.dumps({
                "tool": "figma_create_text",
                "args": {
                    "text": component,
                    "fontSize": 14,
                    "color": "#FFFFFF",
                    "x": 70,
                    "y": layer["y"] + 40 + (j * 30)
                }
            }, indent=2))
            print()
    
    # Connection arrows
    print("# Connections (using lines between layers)")
    connections = [
        ("Gateway", "Workspaces", "Routes messages"),
        ("Workspaces", "MCP Servers", "Tool calls"),
        ("MCP Servers", "External", "API requests")
    ]
    
    for conn in connections:
        print(f"# {conn[0]} → {conn[1]}: {conn[2]}")
    
    print()
    print("=" * 60)
    print("⚠️  Run the MCP server first, then copy/paste these JSON-RPC calls!")

def main():
    # Just output instructions since MCP requires running server
    create_architecture_diagram()

if __name__ == '__main__':
    main()
