#!/usr/bin/env python3
"""
Test Figma API connection with a specific file.
Usage: python figma_test_file.py <file_key>
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

FIGMA_API_BASE = "https://api.figma.com/v1"

def get_token():
    """Get Figma token from vault."""
    path = os.path.expanduser("~/.openclaw/vault/figma-token")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return os.environ.get('FIGMA_API_KEY') or os.environ.get('FIGMA_TOKEN')

def api_request(endpoint, token):
    """Make a Figma API request."""
    url = f"{FIGMA_API_BASE}/{endpoint}"
    req = urllib.request.Request(
        url,
        headers={
            'X-Figma-Token': token,
            'Content-Type': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code}")
        print(e.read().decode('utf-8'))
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Test Figma file access')
    parser.add_argument('file_key', help='Figma file key (from URL)')
    args = parser.parse_args()
    
    token = get_token()
    if not token:
        print("❌ Figma token not found!")
        print("   Expected: ~/.openclaw/vault/figma-token")
        sys.exit(1)
    
    print("🎨 Testing Figma API Connection")
    print("=" * 60)
    print(f"File Key: {args.file_key}")
    print(f"Token: {token[:10]}...{token[-10:]}")
    print()
    
    # Test 1: Get file info
    print("📄 Test 1: Getting file info...")
    file_data = api_request(f"files/{args.file_key}", token)
    
    if file_data:
        print("✅ File access successful!")
        print(f"   Name: {file_data.get('name', 'Unknown')}")
        print(f"   Last Modified: {file_data.get('lastModified', 'Unknown')}")
        print(f"   Version: {file_data.get('version', 'Unknown')}")
        
        # Count pages
        document = file_data.get('document', {})
        children = document.get('children', [])
        print(f"   Pages: {len(children)}")
        for i, page in enumerate(children[:5]):
            print(f"      - Page {i+1}: {page.get('name', 'Unnamed')}")
    else:
        print("❌ Failed to get file info")
        return
    
    print()
    
    # Test 2: Get components
    print("🧩 Test 2: Getting components...")
    components_data = api_request(f"files/{args.file_key}/components", token)
    
    if components_data:
        components = components_data.get('meta', {}).get('components', [])
        print(f"✅ Found {len(components)} component(s)")
        for comp in components[:5]:
            print(f"   - {comp.get('name', 'Unnamed')}")
    else:
        print("ℹ️ No components found or API error")
    
    print()
    
    # Test 3: Get styles
    print("🎨 Test 3: Getting styles...")
    styles_data = api_request(f"files/{args.file_key}/styles", token)
    
    if styles_data:
        styles = styles_data.get('meta', {}).get('styles', [])
        print(f"✅ Found {len(styles)} style(s)")
        
        # Group by type
        style_types = {}
        for style in styles:
            stype = style.get('style_type', 'unknown')
            style_types[stype] = style_types.get(stype, 0) + 1
        
        for stype, count in style_types.items():
            print(f"   - {stype}: {count}")
    else:
        print("ℹ️ No styles found or API error")
    
    print()
    print("=" * 60)
    print("✅ All tests completed!")
    print()
    print("📋 The Figma REST API is working.")
    print("   To use the full MCP server with create/edit capabilities,")
    print("   ensure the Desktop Bridge plugin is running in Figma Desktop.")

if __name__ == '__main__':
    main()
