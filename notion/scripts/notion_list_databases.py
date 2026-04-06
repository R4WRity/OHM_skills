#!/usr/bin/env python3
"""
List all databases accessible to the integration.
Usage: python notion_list_databases.py [--limit 100]
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
    token = os.environ.get('NOTION_TOKEN')
    if token:
        return token
    
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
    sys.exit(1)

def list_databases(limit=100):
    token = get_token()
    url = f"{NOTION_API_BASE}/search"
    
    data = json.dumps({
        "filter": {"value": "database", "property": "object"},
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
    parser = argparse.ArgumentParser(description='List Notion databases')
    parser.add_argument('--limit', type=int, default=100, help='Max results (default: 100)')
    args = parser.parse_args()
    
    print("Fetching databases...")
    result = list_databases(args.limit)
    
    databases = result.get('results', [])
    print(f"\nFound {len(databases)} accessible database(s):\n")
    
    for db in databases:
        title = ''.join([t.get('plain_text', '') for t in db.get('title', [])])
        print(f"• {title}")
        print(f"  ID: {db['id']}")
        print(f"  Properties: {', '.join(db.get('properties', {}).keys())}")
        print(f"  URL: {db.get('url', 'N/A')}")
        print()

if __name__ == '__main__':
    main()
