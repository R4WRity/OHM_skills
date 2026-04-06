#!/usr/bin/env python3
"""
Run Figma MCP server and test connection.
Usage: python figma_run_mcp.py
"""

import json
import os
import subprocess
import sys

def get_token():
    """Get Figma token from vault."""
    path = os.path.expanduser("~/.openclaw/vault/figma-token")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return os.environ.get('FIGMA_API_KEY')

def send_request(proc, request):
    """Send JSON-RPC request to MCP server."""
    request["jsonrpc"] = "2.0"
    line = json.dumps(request) + "\n"
    proc.stdin.write(line.encode())
    proc.stdin.flush()
    
    # Read response
    response_line = proc.stdout.readline()
    return json.loads(response_line)

def main():
    token = get_token()
    if not token:
        print("❌ Figma token not found!")
        sys.exit(1)
    
    print("🎨 Starting Figma MCP Server...")
    print(f"Token: {token[:10]}...{token[-10:]}")
    print("=" * 60)
    print()
    print("📋 Instructions:")
    print("   1. Open Figma Desktop with any file")
    print("   2. Run Plugins → Development → Figma Desktop Bridge")
    print("   3. Wait for 'Connected successfully' message below")
    print("   4. Press Ctrl+C to stop when done testing")
    print()
    print("=" * 60)
    print()
    
    # Start MCP server
    env = os.environ.copy()
    env["FIGMA_API_KEY"] = token
    
    proc = subprocess.Popen(
        ["npx", "figma-console-mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        cwd="C:\\AI\\_BOT"
    )
    
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            text = line.decode('utf-8', errors='replace').rstrip()
            if text:
                print(text)
                sys.stdout.flush()
                
                # Check for successful connection
                if "Connected successfully" in text or "auto-connect" in text.lower():
                    print("\n✅ Figma MCP is connected!")
                    print("   You can now use tools to read/create designs.")
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping MCP server...")
        proc.terminate()
        proc.wait()
        print("✅ Server stopped.")

if __name__ == '__main__':
    main()
