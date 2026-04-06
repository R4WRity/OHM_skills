#!/usr/bin/env python3
"""
Wallpaper Bridge Manager
Check, validate, and restart wallpaper bridge when needed.
"""

import subprocess
import time
import json
import sys
from pathlib import Path

BRIDGE_URL = "http://localhost:8080"
BRIDGE_SCRIPT = Path("projects/wallpapers/dataviz/retro-terminal/bridge_server.py")

def check_bridge():
    """Check if bridge is healthy and serving real data"""
    try:
        import urllib.request
        req = urllib.request.Request(f"{BRIDGE_URL}/api/graph/rawrity")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            node_count = len(data.get("nodes", []))
            return {
                "status": "healthy" if node_count > 10 else "degraded",
                "node_count": node_count,
                "is_mock": node_count < 10,
                "http_status": resp.status
            }
    except Exception as e:
        return {
            "status": "down",
            "error": str(e)[:100],
            "node_count": 0,
            "is_mock": True
        }

def restart_bridge():
    """Kill and restart bridge server"""
    # Kill existing bridge processes
    try:
        # Find python processes running bridge_server
        result = subprocess.run(
            ["powershell", "-Command", 
             "Get-Process python | Where-Object {$_.CommandLine -like '*bridge_server*'} | Stop-Process -Force -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True
        )
    except:
        pass
    
    time.sleep(2)
    
    # Start new bridge
    if BRIDGE_SCRIPT.exists():
        subprocess.Popen(
            ["python", str(BRIDGE_SCRIPT)],
            cwd=str(BRIDGE_SCRIPT.parent),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        time.sleep(5)
        return True
    return False

def main(action="check"):
    if action == "check":
        result = check_bridge()
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "healthy" else 1
    
    elif action == "restart":
        print("Checking bridge before restart...")
        before = check_bridge()
        print(json.dumps(before, indent=2))
        
        if before["status"] != "healthy":
            print("\nRestarting bridge...")
            restart_bridge()
            
            print("\nVerifying restart...")
            after = check_bridge()
            print(json.dumps(after, indent=2))
            
            if after["status"] == "healthy":
                print("\n✅ Bridge successfully restarted and healthy")
                return 0
            else:
                print("\n❌ Bridge restart failed")
                return 1
        else:
            print("\n✅ Bridge already healthy, no restart needed")
            return 0
    
    else:
        print(f"Usage: {sys.argv[0]} [check|restart]")
        return 1

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "check"
    sys.exit(main(action))
