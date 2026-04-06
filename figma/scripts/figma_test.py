#!/usr/bin/env python3
"""
Test Figma MCP connection and verify setup.
Usage: python figma_test.py
"""

import json
import os
import subprocess
import sys

def get_token():
    """Get Figma token from vault."""
    token_paths = [
        os.path.expanduser("~/.openclaw/vault/figma-token"),
        os.path.expanduser("~/.openclaw/vault/figma_api_key"),
    ]
    
    for path in token_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read().strip()
    
    # Check environment
    token = os.environ.get('FIGMA_API_KEY') or os.environ.get('FIGMA_TOKEN')
    if token:
        return token
    
    return None

def check_npx():
    """Check if npx is available."""
    try:
        result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_figma_mcp():
    """Check if figma-console-mcp is installed."""
    try:
        result = subprocess.run(['npx', 'figma-console-mcp', '--version'], 
                                capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def main():
    print("🔍 Figma MCP Setup Verification\n")
    print("=" * 50)
    
    # Check token
    token = get_token()
    if token:
        print(f"✅ Figma token found: {token[:10]}...{token[-10:]}")
    else:
        print("❌ Figma token not found!")
        print("   Expected: ~/.openclaw/vault/figma-token")
        sys.exit(1)
    
    # Check npx
    if check_npx():
        print("✅ npx is available")
    else:
        print("❌ npx not found!")
        print("   Please install Node.js: https://nodejs.org")
        sys.exit(1)
    
    # Check figma-console-mcp
    print("\n📦 Checking figma-console-mcp...")
    if check_figma_mcp():
        print("✅ figma-console-mcp is available via npx")
    else:
        print("⚠️  figma-console-mcp will be installed on first run")
        print("   Command: npx figma-console-mcp")
    
    print("\n" + "=" * 50)
    print("\n✅ Setup verification complete!")
    print("\n📋 To use Figma MCP:")
    print("   1. Open Figma Desktop app")
    print("   2. Open any Figma file")
    print("   3. Go to Plugins → Development → Figma Desktop Bridge")
    print("   4. Run: npx figma-console-mcp")
    print("   5. The MCP server will auto-connect")
    
    print("\n🔑 Token location: ~/.openclaw/vault/figma-token")
    print("📖 Docs: https://docs.figma-console-mcp.southleft.com")

if __name__ == '__main__':
    main()
