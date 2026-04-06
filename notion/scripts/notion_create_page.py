#!/usr/bin/env python3
"""
Create a new page in Notion.
Usage: python notion_create_page.py --parent <parent_id> --title "Title" --content "Content text"
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

def create_page(parent_id, title, content=None):
    token = get_token()
    url = f"{NOTION_API_BASE}/pages"
    
    # Build children blocks if content provided
    children = []
    if content:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            }
        })
    
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        }
    }
    
    if children:
        payload["children"] = children
    
    data = json.dumps(payload).encode('utf-8')
    
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
        error_body = e.read().decode('utf-8')
        print(f"API Error: {e.code} - {error_body}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Create a Notion page')
    parser.add_argument('--parent', required=True, help='Parent page ID')
    parser.add_argument('--title', required=True, help='Page title')
    parser.add_argument('--content', help='Page content (optional)')
    args = parser.parse_args()
    
    parent_id = args.parent.replace('-', '')
    
    print(f"Creating page '{args.title}'...")
    result = create_page(parent_id, args.title, args.content)
    
    print(f"✓ Created page successfully!")
    print(f"  ID: {result['id']}")
    print(f"  URL: {result.get('url', 'N/A')}")
    print(f"  Created: {result.get('created_time', 'N/A')}")

if __name__ == '__main__':
    main()
