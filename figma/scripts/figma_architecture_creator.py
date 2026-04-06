#!/usr/bin/env python3
"""
Automated Figma architecture diagram creator.
Starts MCP server, waits for Desktop Bridge, sends commands.
"""

import json
import os
import subprocess
import sys
import threading
import time
import queue

TOKEN_PATH = os.path.expanduser("~/.openclaw/vault/figma-token")
COMMANDS_PATH = os.path.expanduser("~/.openclaw/workspace/temp/figma_commands.json")
MAX_WAIT = 60

def get_token():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH) as f:
            return f.read().strip()
    return os.environ.get('FIGMA_API_KEY')

def load_commands():
    if not os.path.exists(COMMANDS_PATH):
        return None
    with open(COMMANDS_PATH) as f:
        return [line.strip() for line in f if line.strip()]

def read_output(process, output_queue):
    """Read output from process and add to queue."""
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            output_queue.put(('stdout', line.strip()))
    except:
        pass

def main():
    print("=" * 60)
    print("🎨 Figma Architecture Creator")
    print("=" * 60)
    print()

    # Check prerequisites
    token = get_token()
    if not token:
        print("❌ Figma token not found")
        sys.exit(1)
    print(f"✅ Token: {token[:10]}...{token[-10:]}")

    commands = load_commands()
    if not commands:
        print("❌ Commands file not found")
        sys.exit(1)
    print(f"✅ Commands: {len(commands)}")
    print()

    print("📋 Instructions:")
    print("   1. This will start MCP server and wait")
    print("   2. Open: Plugins → Development → Figma Desktop Bridge")
    print("   3. Watch for '🟢 Connected' message")
    print("   4. Commands will auto-send after connection")
    print()
    input("Press ENTER to start...")
    print()

    # Start MCP server
    print("🚀 Starting MCP server...")
    print()

    env = os.environ.copy()
    env['FIGMA_API_KEY'] = token

    try:
        process = subprocess.Popen(
            ['npx', 'figma-console-mcp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd='C:\\AI\\_BOT',
            env=env
        )
    except Exception as e:
        print(f"❌ Failed to start MCP: {e}")
        sys.exit(1)

    # Start output reader thread
    output_queue = queue.Queue()
    reader_thread = threading.Thread(target=read_output, args=(process, output_queue))
    reader_thread.daemon = True
    reader_thread.start()

    # Wait for connection
    print("⏳ Waiting for Desktop Bridge...")
    print("   (Open Bridge plugin in Figma now)")
    print()

    connected = False
    start_time = time.time()
    last_status = time.time()

    while time.time() - start_time < MAX_WAIT and not connected:
        # Check queue for output
        try:
            while True:
                source, line = output_queue.get(timeout=0.1)
                print(f"   {line[:100]}")
                
                # Check for connection
                if any(x in line.lower() for x in ['connected', 'success', 'figma']):
                    if 'connected' in line.lower() and 'figma' in line.lower():
                        connected = True
                        print()
                        print("✅ Desktop Bridge connected!")
                        break
        except queue.Empty:
            pass

        # Show waiting status
        if time.time() - last_status > 2:
            elapsed = int(time.time() - start_time)
            print(f"\r   Waiting... ({elapsed}s / {MAX_WAIT}s)    ", end='', flush=True)
            last_status = time.time()

        if process.poll() is not None:
            print()
            print("❌ MCP server exited")
            sys.exit(1)

    if not connected:
        print()
        print(f"\n❌ Timeout after {MAX_WAIT}s")
        process.terminate()
        return

    # Give connection time to stabilize
    print()
    print("⏱️  Stabilizing connection (3s)...")
    time.sleep(3)

    # Send commands
    print()
    print("📤 Sending commands...")
    print()

    success = 0
    failed = 0

    for i, cmd in enumerate(commands, 1):
        print(f"[{i}/{len(commands)}] ", end='', flush=True)
        
        try:
            # Send command
            process.stdin.write(cmd + '\n')
            process.stdin.flush()
            
            # Wait for response
            time.sleep(0.5)
            
            # Check responses
            error = False
            try:
                while True:
                    source, line = output_queue.get(timeout=0.5)
                    if '"isError":true' in line or 'not found' in line.lower():
                        error = True
                    if line:
                        pass  # Consume output
            except queue.Empty:
                pass
            
            if error:
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
    print(f"✅ Complete! Success: {success}, Failed: {failed}")
    print()
    print("📁 Check Figma: Ohm Design Space")
    
    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=5)
    except:
        process.kill()

if __name__ == '__main__':
    main()
