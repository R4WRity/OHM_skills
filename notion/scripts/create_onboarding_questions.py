#!/usr/bin/env python3
"""Create Notion page with onboarding questions from file."""

import json
import os
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
    
    # Try vault
    vault_path = os.path.expanduser('~/.openclaw/vault/notion-token')
    if os.path.exists(vault_path):
        try:
            with open(vault_path, 'r') as f:
                return f.read().strip()
        except Exception:
            pass
    
    raise ValueError("Notion token not found")

def parse_markdown_to_blocks(content):
    """Convert markdown to Notion blocks."""
    blocks = []
    lines = content.split('\n')
    current_paragraph = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            if current_paragraph:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
                    }
                })
                current_paragraph = []
            continue
        
        # Headers
        if line.startswith('# '):
            if current_paragraph:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
                    }
                })
                current_paragraph = []
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                }
            })
        elif line.startswith('## '):
            if current_paragraph:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
                    }
                })
                current_paragraph = []
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                }
            })
        elif line.startswith('### '):
            if current_paragraph:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
                    }
                })
                current_paragraph = []
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                }
            })
        # Divider
        elif line.strip() == '---':
            if current_paragraph:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
                    }
                })
                current_paragraph = []
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        # Bold text (simplified)
        elif line.startswith('**') and line.endswith('**'):
            if current_paragraph:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
                    }
                })
                current_paragraph = []
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": line.replace('**', '')}, "annotations": {"bold": True}}
                    ]
                }
            })
        # Bullet points starting with -
        elif line.strip().startswith('- *') or line.strip().startswith('- "'):
            if current_paragraph:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
                    }
                })
                current_paragraph = []
            text = line.strip()[2:]  # Remove '- '
            # Remove italics markers for simplicity
            text = text.replace('*"', '"').replace('"*', '"').strip()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })
        # Italic quoted text
        elif line.strip().startswith('*"'):
            if current_paragraph:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
                    }
                })
                current_paragraph = []
            text = line.strip().strip('*')
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text}, "annotations": {"italic": True}}]
                }
            })
        else:
            # Regular paragraph
            current_paragraph.append(line)
    
    # Flush remaining paragraph
    if current_paragraph:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": ' '.join(current_paragraph)}}]
            }
        })
    
    return blocks

def create_page(parent_id, title, blocks):
    token = get_token()
    url = f"{NOTION_API_BASE}/pages"
    
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        "children": blocks
    }
    
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
        print(f"API Error: {e.code} - {error_body}")
        raise

def main():
    # Read the file
    file_path = r"C:\AI\_BOT\.openclaw\workspace\docs\onboarding-questions-reworked.md"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse to blocks
    blocks = parse_markdown_to_blocks(content)
    
    # Create page (as child of SOUL.md - OHM page)
    parent_id = "316efd3c-a094-81f5-b1c0-cdb3fb5be25d"
    title = "Reworked Onboarding Questions (Philosophy-Infused)"
    
    # Create in batches if too many blocks (Notion limit is 100 blocks)
    # For first request, we include children; subsequent requests append blocks
    result = create_page(parent_id, title, blocks[:100])
    
    # If more blocks, append them
    if len(blocks) > 100:
        page_id = result['id']
        for i in range(100, len(blocks), 100):
            batch = blocks[i:i+100]
            append_blocks(page_id, batch)
    
    print(f"[OK] Created page successfully!")
    print(f"  ID: {result['id']}")
    print(f"  URL: {result.get('url', 'N/A')}")

def append_blocks(page_id, blocks):
    """Append blocks to existing page."""
    token = get_token()
    url = f"{NOTION_API_BASE}/blocks/{page_id}/children"
    
    payload = {"children": blocks}
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        },
        method='PATCH'
    )
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

if __name__ == '__main__':
    main()
