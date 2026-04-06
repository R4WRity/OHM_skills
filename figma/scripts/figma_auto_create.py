#!/usr/bin/env python3
"""
Automated Figma MCP setup with connection waiting.
This runs MCP server, waits for Desktop Bridge, then creates the architecture.
"""

import json
import os
import subprocess
import sys
import time
import threading
import select

TOKEN_PATH = os.path.expanduser("~/.openclaw/vault/figma-token")
COMMANDS_PATH = os.path.expanduser("~/.openclaw/workspace/temp/figma_commands.json")
MAX_WAIT_SECONDS = 60

def get_token():
    """Get Figma token."""
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as f:
            return f.read().strip()
    return os.environ.get('FIGMA_API_KEY')

def check_commands_file():
    """Check if commands file exists."""
    if not os.path.exists(COMMANDS_PATH):
        print(f"❌ Commands file not found: {COMMANDS_PATH}")
        return []
    try:
        with open(COMMANDS_PATH, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Error reading commands: {e}")
        return []

def print_header():
    """Print formatted header."""
    print("=" * 60)
    print("🎨 Figma Automated Architecture Builder")
    print("=" * 60)
    print()

def print_status(msg, level="info"):
    """Print status message."""
    colors = {
        "info": "",
        "success": "✅ ",
        "warning": "⚠️  ",
        "error": "❌ ",
        "cyan": ""
    }
    print(f"{colors.get(level, '')}{msg}")

def main():
    print_header()
    
    # Check prerequisites
    token = get_token()
    if not token:
        print_status("Figma token not found", "error")
        sys.exit(1)
    print_status(f"Token loaded: {token[:10]}...{token[-10:]}", "success")
    
    commands = check_commands_file()
    if not commands:
        print_status("No commands to send", "error")
        sys.exit(1)
    print_status(f"Loaded {len(commands)} commands", "success")
    print()
    
    # Instructions
    print("📋 Instructions:")
    print("   1. This script will start the MCP server")
    print("   2. You MUST open Desktop Bridge plugin in Figma")
    print("   3. The script will wait for connection")
    print("   4. Once connected, commands will be sent automatically")
    print()
    
    input("Press ENTER to start (Ctrl+C to cancel)...")
    print()
    
    # Start MCP server
    print_status("Starting MCP server...", "cyan")
    print()
    
    env = os.environ.copy()
    env["FIGMA_API_KEY"] = token
    
    # Start MCP process
    proc = subprocess.Popen(
        ["npx", "figma-console-mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        cwd="C:\\AI\\_BOT",
        text=True,
        bufsize=1
    )
    
    # Wait for connection
    print_status("Waiting for Desktop Bridge connection...", "warning")
    print("   (Open Plugins → Development → Figma Desktop Bridge now)")
    print()
    
    connected = False
    start_time = time.time()
    
    while time.time() - start_time < MAX_WAIT_SECONDS and not connected:
        # Check for output
        if proc.poll() is not None:
            print_status("MCP server exited unexpectedly", "error")
            sys.exit(1)
        
        # Try to read line
        try:
            import select
            ready, _, _ = select.select([proc.stdout], [], [], 1.0)
            if ready:
                line = proc.stdout.readline()
                if line:
                    print(f"   {line.strip()}")
                    if "connected" in line.lower() or "success" in line.lower():
                        connected = True
                        print_status("Desktop Bridge connected!", "success")
        except:
            time.sleep(1)
        
        elapsed = int(time.time() - start_time)
        if not connected and elapsed % 2 == 0:
            sys.stdout.write(f"\r   Waiting... ({elapsed}s / {MAX_WAIT_SECONDS}s)")
            sys.stdout.flush()
    
    if not connected:
        print()
        print_status(f"Timeout: No connection within {MAX_WAIT_SECONDS}s", "error")
        proc.terminate()
        proc.wait()
        sys.exit(1)
    
    # Small delay to stabilize
    time.sleep(2)
    
    # Send commands
    print()
    print_status("Sending architecture commands...", "cyan")
    print()
    
    success = 0
    failed = 0
    
    for i, cmd in enumerate(commands, 1):
        sys.stdout.write(f"   [{i}/{len(commands)}] Sending... ")
        sys.stdout.flush()
        
        try:
            # Send command
            proc.stdin.write(cmd + "\n")
            proc.stdin.flush()
            
            # Wait for response
            time.sleep(0.5)
            
            # Read response
            responses = []
            while True:
                import select
                ready, _, _ = select.select([proc.stdout], [], [], 0.5)
                if not ready:
                    break
                line = proc.stdout.readline()
                if line:
                    responses.append(line.strip())
            
            # Check for error
            error_found = False
            for resp in responses:
                if '"isError":true' in resp or 'error' in resp.lower():
                    error_found = True
            
            if error_found:
                print("❌")
                failed += 1
            else:
                print("✅")
                success += 1
                
        except Exception as e:
            print(f"❌ ({e})")
            failed += 1
        
        time.sleep(0.2)
    
    # Summary
    print()
    print("=" * 60)
    print()
    print_status("Complete!", "success")
    print(f"   Success: {success} | Failed: {failed}")
    print()
    print("📁 Check your Figma file: Ohm Design Space")
    
    # Cleanup
    proc.terminate()
    proc.wait()
    
    input("\nPress ENTER to exit...")

if __name__ == '__main__':
    main()
