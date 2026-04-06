#!/usr/bin/env python3
"""
Fetch page content from Notion.
Usage: python notion_get_page.py <page_id>
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

def get_token():
    token = os.environ.get('NOTION_TOKEN')
    if not token:
        # Try reading from gateway config
        try:
            result = subprocess.run(
                ['openclaw', 'gateway', 'config.get'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                config = json.loads(result.stdout)
                token = config.get('parsed', {}).get('notion', {}).get('token')
        except Exception:
            pass
    
    if not token:
        print("Error: Notion token not configured.", file=sys.stderr)
        print("Run: openclaw config --section notion", file=sys.stderr)
        sys.exit(1)
    return token

def get_page(page_id):
    token = get_token()
    url = f"{NOTION_API_BASE}/pages/{page_id}"
    
    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {token}',
            'Notion-Version': NOTION_VERSION
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)

def get_page_blocks(page_id):
    token = get_token()
    url = f"{NOTION_API_BASE}/blocks/{page_id}/children"
    
    req = urllib.request.Request(
        url,
        headers={
            'Authorization': f'Bearer {token}',
            'Notion-Version': NOTION_VERSION
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)

def extract_text_from_block(block):
    block_type = block['type']
    if block_type in block and 'rich_text' in block[block_type]:
        return ''.join([t.get('plain_text', '') for t in block[block_type]['rich_text']])
    return f"[{block_type} block]"

def main():
    parser = argparse.ArgumentParser(description='Get Notion page content')
    parser.add_argument('page_id', help='Page ID (with or without dashes)')
    args = parser.parse_args()
    
    # Clean up page ID
    page_id = args.page_id.replace('-', '')
    
    print("Fetching page...")
    page = get_page(page_id)
    
    # Get title
    if 'Name' in page.get('properties', {}):
        title = ''.join([t.get('plain_text', '') for t in page['properties']['Name'].get('title', [])])
    elif 'title' in page.get('properties', {}):
        title = ''.join([t.get('plain_text', '') for t in page['properties']['title'].get('title', [])])
    else:
        title = "Untitled"
    
    print(f"\n# {title}")
    print(f"ID: {page['id']}")
    print(f"URL: {page.get('url', 'N/A')}")
    print(f"Created: {page.get('created_time', 'N/A')}")
    print(f"Last edited: {page.get('last_edited_time', 'N/A')}")
    print()
    
    print("Fetching content blocks...")
    blocks = get_page_blocks(page_id)
    
    print(f"\n--- Content ({blocks.get('results', []).__len__()} blocks) ---\n")
    
    for block in blocks.get('results', []):
        text = extract_text_from_block(block)
        if text.strip():
            print(text)

if __name__ == '__main__':
    main()
