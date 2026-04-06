#!/usr/bin/env python3
"""
System Health Diagnostics
Checks Docker, MCP servers, bridges, and updates Notion dashboard.
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# Notion API settings
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_PAGE_ID = "318efd3c-a094-8145-af0c-df3f7ec85c1f"

def run_cmd(cmd, cwd=None):
    """Run shell command, return (success, output)"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_docker():
    """Check Docker container status"""
    results = {}
    compose_dirs = [
        ("simple-graph", "projects/simple-graph-mcp"),
        ("tool-servers", "projects/mcp-tool-servers"),
    ]
    
    for name, path in compose_dirs:
        success, output = run_cmd("docker-compose ps --format json", cwd=path)
        if success:
            try:
                containers = json.loads(output) if output.strip() else []
                running = sum(1 for c in containers if c.get("State") == "running")
                total = len(containers)
                results[name] = {
                    "status": "healthy" if running == total and total > 0 else "degraded",
                    "running": running,
                    "total": total,
                    "containers": containers
                }
            except:
                results[name] = {"status": "error", "output": output[:200]}
        else:
            results[name] = {"status": "unavailable", "error": output[:200]}
    
    return results

def check_mcp_health():
    """Check MCP server HTTP health endpoints"""
    servers = {
        "simple-graph-agent": "http://localhost:9300/health",
        "simple-graph-rawrity": "http://localhost:9301/health",
        "simple-graph-sigma": "http://localhost:9302/health",
        "n8n-mcp": "http://localhost:9100/health",
        "comfyui-mcp": "http://localhost:9101/mcp",
    }
    
    results = {}
    for name, url in servers.items():
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                results[name] = {
                    "status": "healthy",
                    "response": data
                }
        except urllib.error.HTTPError as e:
            # comfyui-mcp returns different status but may still be up
            results[name] = {"status": "degraded", "error": f"HTTP {e.code}"}
        except Exception as e:
            results[name] = {"status": "down", "error": str(e)[:100]}
    
    return results

def check_bridges():
    """Check bridge scripts and services"""
    results = {}
    
    # Wallpaper bridge API (port 8080) - serves graph data to wallpaper
    try:
        req = urllib.request.Request("http://localhost:8080/api/graph/rawrity", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            node_count = len(data.get("nodes", []))
            results["wallpaper_bridge"] = {
                "status": "healthy",
                "http_status": resp.status,
                "graph_nodes": node_count,
                "using_mock": node_count < 10  # Mock data has < 10 nodes
            }
    except Exception as e:
        results["wallpaper_bridge"] = {"status": "down", "error": str(e)[:100]}
    
    # Browser MCP (if running)
    try:
        req = urllib.request.Request("http://localhost:9102/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            results["browser_mcp"] = {"status": "healthy"}
    except:
        results["browser_mcp"] = {"status": "not_running"}
    
    # Remote ComfyUI Backend (127.0.0.192:8188)
    try:
        req = urllib.request.Request("http://127.0.0.192:8188/system_stats", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            results["comfyui_backend"] = {
                "status": "healthy",
                "location": "127.0.0.192:8188"
            }
    except Exception as e:
        results["comfyui_backend"] = {
            "status": "unreachable",
            "error": str(e)[:100],
            "note": "Remote ComfyUI instance"
        }
    
    return results

def check_gpu():
    """Check GPU/VRAM if available"""
    success, output = run_cmd("nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits")
    if success:
        lines = output.strip().split('\n')
        if lines and lines[0]:
            parts = lines[0].split(', ')
            if len(parts) >= 3:
                used, total, util = int(parts[0]), int(parts[1]), int(parts[2])
                pct = (used / total) * 100 if total > 0 else 0
                return {
                    "status": "healthy" if pct < 80 else "warning",
                    "vram_used_mb": used,
                    "vram_total_mb": total,
                    "vram_pct": round(pct, 1),
                    "gpu_util_pct": util
                }
    return {"status": "unavailable", "note": "nvidia-smi not found or no GPU"}

def identify_issues(results):
    """Extract actionable issues from results"""
    issues = []
    
    # Docker issues
    for name, data in results.get("docker", {}).items():
        if data.get("status") != "healthy":
            issues.append({
                "component": f"docker:{name}",
                "severity": "high" if data.get("running", 0) == 0 else "medium",
                "message": f"{name}: {data.get('running', 0)}/{data.get('total', 0)} containers running"
            })
    
    # MCP issues
    for name, data in results.get("mcp", {}).items():
        if data.get("status") != "healthy":
            issues.append({
                "component": f"mcp:{name}",
                "severity": "high" if data.get("status") == "down" else "medium",
                "message": f"{name} is {data.get('status')}: {data.get('error', 'unknown')}"
            })
    
    # Bridge issues
    for name, data in results.get("bridges", {}).items():
        if data.get("status") not in ["healthy", "not_running"]:
            issues.append({
                "component": name,
                "severity": "medium",
                "message": f"{name} is {data.get('status')}"
            })
    
    # GPU issues
    gpu = results.get("gpu", {})
    if gpu.get("status") == "warning":
        issues.append({
            "component": "gpu",
            "severity": "low",
            "message": f"VRAM usage high: {gpu.get('vram_pct')}%"
        })
    
    return issues

def update_notion_system_status(results, issues):
    """Update the Notion System Status section"""
    if not NOTION_TOKEN:
        return False, "No NOTION_TOKEN available"
    
    # Build status blocks
    blocks = []
    
    # Status summary
    overall_status = "critical" if any(i["severity"] == "high" for i in issues) else \
                     "degraded" if issues else "healthy"
    
    status_emoji = "🟢" if overall_status == "healthy" else "🟡" if overall_status == "degraded" else "🔴"
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # System Status section update
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": f"Last Updated: {now}\n"}},
                {"type": "text", "text": {"content": f"Overall Status: {status_emoji} {overall_status.upper()}"}}
            ]
        }
    })
    
    # Docker status
    blocks.append({
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": "Docker Containers"}}]}
    })
    
    for name, data in results.get("docker", {}).items():
        emoji = "🟢" if data.get("status") == "healthy" else "🔴"
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": f"{emoji} {name}: {data.get('running', 0)}/{data.get('total', 0)} running"}}]
            }
        })
    
    # MCP status
    blocks.append({
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": "MCP Servers"}}]}
    })
    
    for name, data in results.get("mcp", {}).items():
        emoji = "🟢" if data.get("status") == "healthy" else "🟡" if data.get("status") == "degraded" else "🔴"
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": f"{emoji} {name}: {data.get('status')}"}}]
            }
        })
    
    # Issues section if any
    if issues:
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "⚠️ Active Issues"}}]}
        })
        
        for issue in issues:
            emoji = "🔴" if issue["severity"] == "high" else "🟡" if issue["severity"] == "medium" else "⚪"
            blocks.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": f"{emoji} [{issue['severity'].upper()}] {issue['component']}: {issue['message']}"}}],
                    "checked": False
                }
            })
    
    # Send to Notion - append to page
    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps({"children": blocks}).encode(),
            headers=headers,
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True, f"Updated Notion: HTTP {resp.status}"
    except Exception as e:
        return False, str(e)

def main():
    """Run full diagnostic and update Notion"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "docker": check_docker(),
        "mcp": check_mcp_health(),
        "bridges": check_bridges(),
        "gpu": check_gpu()
    }
    
    issues = identify_issues(results)
    results["issues"] = issues
    results["status"] = "healthy" if not issues else "degraded" if not any(i["severity"] == "high" for i in issues) else "critical"
    
    # Print JSON to stdout (for agent consumption)
    print(json.dumps(results, indent=2))
    
    # Run visual validation if wallpaper bridge was having issues
    if results.get("bridges", {}).get("wallpaper_bridge", {}).get("status") != "healthy":
        print("\nWallpaper bridge issue detected, attempting restart...", file=sys.stderr)
        restart_wallpaper_bridge()
        
        print("Running visual validation...", file=sys.stderr)
        visual_results = run_visual_validation()
        results["visual_validation"] = visual_results
        if visual_results.get("status") != "healthy":
            issues.append({
                "component": "wallpaper_visual",
                "severity": "medium",
                "message": f"Visual validation failed: {visual_results.get('issue', 'unknown')}"
            })
    
    # Update Notion if token available
    if NOTION_TOKEN:
        success, msg = update_notion_system_status(results, issues)
        print(f"\nNotion update: {'✅' if success else '❌'} {msg}", file=sys.stderr)
    else:
        print("\nNotion update: skipped (no token)", file=sys.stderr)
    
    return 0 if results["status"] == "healthy" else 1


def restart_wallpaper_bridge():
    """Restart the wallpaper bridge server"""
    import subprocess
    import time
    
    # Kill existing bridge processes
    subprocess.run("Get-Process python | Where-Object {$_.CommandLine -like '*bridge_server.py*'} | Stop-Process -Force",
                   shell=True, capture_output=True)
    time.sleep(2)
    
    # Start new bridge
    bridge_path = "projects/wallpapers/dataviz/retro-terminal"
    subprocess.Popen(
        ["python", "bridge_server.py"],
        cwd=bridge_path,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    time.sleep(3)
    print("Wallpaper bridge restarted", file=sys.stderr)


def run_visual_validation():
    """Run visual validation using Browser MCP"""
    try:
        import subprocess
        result = subprocess.run(
            ["python", "skills/diagnostics/scripts/visual_validate_wallpaper.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return {"status": "healthy"}
        else:
            return {"status": "degraded", "issue": result.stderr[:200]}
    except Exception as e:
        return {"status": "unknown", "issue": str(e)}


if __name__ == "__main__":
    sys.exit(main())
