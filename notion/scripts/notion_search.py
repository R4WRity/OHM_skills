#!/usr/bin/env python3
"""
Search Notion content using the API.
Usage: python notion_search.py "query" [--limit 10]
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

def get_token():
    # Check environment variable first
    token = os.environ.get('NOTION_TOKEN')
    if token:
        return token
    
    # Try reading from config file
    config_path = os.path.expanduser('~/.openclaw/openclaw.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                token = config.get('notion', {}).get('token')
                if token:
                    return token
        except Exception:
            pass
    
    print("Error: Notion token not configured.", file=sys.stderr)
    print("Add 'notion.token' to your ~/.openclaw/openclaw.json", file=sys.stderr)
    sys.exit(1)

def search_notion(query, limit=10):
    token = get_token()
    url = f"{NOTION_API_BASE}/search"
    
    data = json.dumps({
        "query": query,
        "page_size": limit
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Search Notion content')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--limit', type=int, default=10, help='Max results (default: 10)')
    args = parser.parse_args()
    
    results = search_notion(args.query, args.limit)
    
    print(f"Found {results['results'].__len__()} results:")
    print()
    
    for item in results['results']:
        item_type = item['object']
        if item_type == 'page':
            title = item.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled')
        else:
            title = item.get('title', [{}])[0].get('plain_text', 'Untitled')
        
        url = item.get('url', 'N/A')
        print(f"• {title}")
        print(f"  Type: {item_type} | ID: {item['id']}")
        print(f"  URL: {url}")
        print()

if __name__ == '__main__':
    main()
