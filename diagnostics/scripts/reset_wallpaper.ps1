#!/usr/bin/env python3
"""
Quick Wallpaper Bridge Reset & Validation
To be run after bridge reset.
"""

import subprocess
import time
import json
import urllib.request
from datetime import datetime

def check_bridge():
    """Quick check if bridge is responding with real data"""
    try:
        req = urllib.request.Request("http://localhost:8080/api/graph/rawrity", timeout=5)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            node_count = len(data.get("nodes", []))
            return node_count > 10, node_count
    except Exception as e:
        return False, 0

def main():
    print("=== Wallpaper Bridge Reset ===")
    
    # Kill existing
    subprocess.run("taskkill /F /FI 'WINDOWTITLE eq *bridge_server*' 2>nul", shell=True, capture_output=True)
    subprocess.run("taskkill /F /im python.exe /FI 'COMMANDLINE eq *bridge_server*' 2>nul", shell=True, capture_output=True)
    time.sleep(2)
    
    # Start new bridge
    print("Starting bridge server...")
    subprocess.Popen(
        ["python", "bridge_server.py"],
        cwd="projects/wallpapers/dataviz/retro-terminal",
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    time.sleep(3)
    
    # Check
    healthy, count = check_bridge()
    print(f"\nBridge check: {'HEALTHY' if healthy else 'FAILED'}")
    print(f"Nodes returned: {count}")
    
    if healthy:
        print("\n✓ Wallpaper should now show real data")
        print("Current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print("\n✗ Bridge not responding with data")
    
    return 0 if healthy else 1

if __name__ == "__main__":
    exit(main())
