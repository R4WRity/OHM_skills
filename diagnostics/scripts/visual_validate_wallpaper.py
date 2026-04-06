#!/usr/bin/env python3
"""
Visual Validation for Wallpaper Dashboard
Uses Browser MCP HTTP API to capture screenshot and verify real data.
"""

import json
import urllib.request
import base64
import sys
import time
from datetime import datetime
from pathlib import Path

BROWSER_MCP_HEALTH_URL = "http://localhost:9102/health"
BROWSER_MCP_URL = "http://localhost:9102/mcp"
BROWSER_TOOLS_URL = "http://localhost:9102/tools"
WALLPAPER_URL = "http://localhost:8889/index.html"

def call_tool(tool_name, arguments=None):
    """Call Browser MCP tool via HTTP"""
    payload = {
        "name": tool_name,
        "arguments": arguments or {}
    }
    try:
        req = urllib.request.Request(
            BROWSER_MCP_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def validate_wallpaper():
    """Navigate to wallpaper and capture screenshot"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "status": "unknown"
    }
    
    # Test 1: Browser MCP availability
    print("[1/5] Checking Browser MCP...")
    try:
        req = urllib.request.Request(BROWSER_MCP_HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "healthy":
                results["tests"]["browser_mcp_health"] = {"status": "pass"}
            else:
                results["tests"]["browser_mcp_health"] = {"status": "fail"}
                results["status"] = "critical"
                return results
    except Exception as e:
        results["tests"]["browser_mcp_health"] = {"status": "fail", "error": str(e)}
        results["status"] = "critical"
        return results
    
    # Test 2: Navigate to wallpaper
    print("[2/5] Navigating to wallpaper...")
    nav_result = call_tool("navigate", {"url": WALLPAPER_URL})
    if nav_result.get("error") or nav_result.get("status") == "error":
        results["tests"]["navigation"] = {"status": "fail", "error": nav_result.get("error", "unknown")}
        results["status"] = "critical"
        return results
    results["tests"]["navigation"] = {"status": "pass", "result": nav_result.get("result")}
    
    # Wait for page to load
    time.sleep(3)
    
    # Test 3: Evaluate content
    print("[3/5] Analyzing page content...")
    eval_result = call_tool("evaluate", {
        "script": """
            const checks = {
                hasRawrity: document.body.innerText.toLowerCase().includes('rawrity'),
                hasSigma: document.body.innerText.toLowerCase().includes('sigma'),
                hasMock: document.body.innerText.includes('MOCK DATA'),
                connected: document.body.innerText.includes('CONNECTED'),
                title: document.title
            };
            JSON.stringify(checks);
        """
    })
    
    if eval_result.get("result"):
        try:
            page_data = json.loads(eval_result["result"]["result"])
            results["tests"]["content_analysis"] = {"status": "pass", "data": page_data}
            
            # Determine overall status
            if page_data.get("hasMock"):
                results["status"] = "degraded"
                results["issue"] = "Wallpaper showing MOCK DATA"
            elif page_data.get("hasRawrity") and page_data.get("connected"):
                results["status"] = "healthy"
            else:
                results["status"] = "unknown"
                results["issue"] = "Cannot verify real data connection"
        except Exception as e:
            results["tests"]["content_analysis"] = {"status": "fail", "error": str(e)}
            results["status"] = "degraded"
    else:
        results["tests"]["content_analysis"] = {"status": "fail", "error": eval_result.get("error")}
    
    # Test 4: Capture screenshot
    print("[4/5] Capturing screenshot...")
    screenshot_result = call_tool("screenshot", {"fullPage": False})
    
    screenshot_b64 = None
    if screenshot_result.get("result"):
        content = screenshot_result["result"]
        # Try to extract base64 image data
        if isinstance(content, dict) and "image" in content:
            screenshot_b64 = content["image"]
        elif isinstance(content, str) and content.startswith("data:image"):
            screenshot_b64 = content.split(",")[1] if "," in content else content
    
    if screenshot_b64:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        Path("memory").mkdir(exist_ok=True)
        screenshot_path = f"memory/wallpaper_screenshot_{timestamp}.png"
        try:
            with open(screenshot_path, "wb") as f:
                f.write(base64.b64decode(screenshot_b64))
            results["tests"]["screenshot"] = {"status": "pass", "path": screenshot_path}
            results["screenshot_path"] = screenshot_path
            print(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            results["tests"]["screenshot"] = {"status": "fail", "error": str(e)}
    else:
        results["tests"]["screenshot"] = {"status": "fail", "error": "No image data", "raw": str(screenshot_result)[:200]}
    
    return results

def main():
    print("=== Wallpaper Visual Validation ===\n")
    results = validate_wallpaper()
    
    print(f"\n=== Results ===")
    print(f"Overall Status: {results['status'].upper()}")
    
    for test_name, test_result in results['tests'].items():
        status = test_result.get('status', 'unknown')
        icon = "✅" if status == 'pass' else "❌" if status == 'fail' else "⚠️"
        print(f"{icon} {test_name}: {status}")
        if test_result.get('data'):
            print(f"   Data: {test_result['data']}")
    
    if results.get('issue'):
        print(f"\n⚠️ Issue: {results['issue']}")
    
    # Print results as JSON
    print("\n" + json.dumps(results, indent=2))
    
    return 0 if results['status'] == 'healthy' else 1

if __name__ == "__main__":
    sys.exit(main())
