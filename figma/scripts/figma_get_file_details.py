#!/usr/bin/env python3
"""
Get detailed Figma file structure.
Usage: python figma_get_file_details.py <file_key>
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

FIGMA_API_BASE = "https://api.figma.com/v1"

def get_token():
    path = os.path.expanduser("~/.openclaw/vault/figma-token")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return os.environ.get('FIGMA_API_KEY')

def api_request(endpoint, token):
    url = f"{FIGMA_API_BASE}/{endpoint}"
    req = urllib.request.Request(
        url,
        headers={'X-Figma-Token': token}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.read().decode('utf-8')}")
        return None

def count_nodes_by_type(node, counts=None):
    """Recursively count node types."""
    if counts is None:
        counts = {}
    
    node_type = node.get('type', 'UNKNOWN')
    counts[node_type] = counts.get(node_type, 0) + 1
    
    for child in node.get('children', []):
        count_nodes_by_type(child, counts)
    
    return counts

def list_all_nodes(node, depth=0, max_depth=3):
    """List nodes with indentation."""
    if depth > max_depth:
        return []
    
    results = []
    name = node.get('name', 'Unnamed')
    node_type = node.get('type', 'UNKNOWN')
    results.append((depth, name, node_type))
    
    for child in node.get('children', []):
        results.extend(list_all_nodes(child, depth + 1, max_depth))
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Get Figma file details')
    parser.add_argument('file_key', help='Figma file key')
    parser.add_argument('--depth', type=int, default=3, help='Max depth to traverse')
    args = parser.parse_args()
    
    token = get_token()
    if not token:
        print("❌ Token not found")
        sys.exit(1)
    
    print(f"🔍 Getting file details for: {args.file_key}")
    print("=" * 60)
    
    # Get file with geometry
    print("\n📄 Fetching file structure...")
    file_data = api_request(f"files/{args.file_key}?geometry=paths", token)
    
    if not file_data:
        print("❌ Failed to fetch file")
        sys.exit(1)
    
    print(f"✅ File: {file_data.get('name')}")
    print(f"   Last Modified: {file_data.get('lastModified')}")
    print(f"   Thumbnail: {file_data.get('thumbnailUrl', 'N/A')[:60]}...")
    
    # Traverse document
    document = file_data.get('document', {})
    
    # Count all node types
    print("\n📊 Node Type Summary:")
    counts = count_nodes_by_type(document)
    for node_type, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"   {node_type}: {count}")
    
    # List structure
    print(f"\n🗂️  File Structure (depth {args.depth}):")
    nodes = list_all_nodes(document, max_depth=args.depth)
    
    for depth, name, node_type in nodes:
        indent = "  " * depth
        print(f"{indent}• {name} ({node_type})")

if __name__ == '__main__':
    main()
