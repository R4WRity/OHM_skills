#!/usr/bin/env python3
"""Add structured blocks to the System Health Dashboard page."""
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

def add_blocks(page_id, blocks):
    token = get_token()
    url = f"{NOTION_API_BASE}/blocks/{page_id}/children"
    data = json.dumps({"children": blocks}).encode('utf-8')
    req = urllib.request.Request(
        url, data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        },
        method='PATCH'
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)

def heading1(text):
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def heading2(text):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def paragraph(text, bold=False):
    rt = {"type": "text", "text": {"content": text}}
    if bold:
        rt["annotations"] = {"bold": True}
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [rt]}}

def bullet(text):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def callout(text, emoji="ℹ"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": text}}], "icon": {"type": "emoji", "emoji": emoji}}}

def main():
    page_id = sys.argv[1] if len(sys.argv) > 1 else "318efd3c-a094-8145-af0c-df3f7ec85c1f"
    page_id = page_id.replace('-', '')

    blocks = [
        paragraph("This is a living document maintained by the Notion Diagnostics Agent. It tracks system health, MCP server status, and tool improvement ideas."),
        paragraph("Last Updated: 2026-03-03 12:00 PM PST"),
        divider(),
        
        heading1("System Status"),
        heading2("GPU / VRAM"),
        bullet("Total VRAM: 8 GB"),
        bullet("Free VRAM: [TBD - update via diagnostics]"),
        bullet("Active Models: [TBD]"),
        
        heading2("Docker Containers"),
        bullet("simple-graph-rawrity: [TBD]"),
        bullet("simple-graph-sigma: [TBD]"),
        bullet("simple-graph-agent (Ohm): [TBD]"),
        bullet("n8n-mcp: [TBD]"),
        bullet("comfyui-mcp: [TBD]"),
        
        heading2("MCP Servers"),
        bullet("Port 9300 (Ohm): [TBD]"),
        bullet("Port 9301 (RAWRity): [TBD]"),
        bullet("Port 9302 (Sigma): [TBD]"),
        bullet("Port 9100 (n8n): [TBD]"),
        bullet("Port 9101 (ComfyUI): [TBD]"),
        
        divider(),
        
        heading1("Recent Issues"),
        paragraph("Log of recent errors, warnings, and anomalies detected during diagnostics.", bold=True),
        bullet("[2026-03-03] Agent spawn timeout - investigating model override issue"),
        
        divider(),
        
        heading1("Tool Ideas Queue"),
        heading2("High Priority"),
        bullet("[ ] Multi-agent orchestration framework"),
        bullet("[ ] Sub-agent model routing (local vs cloud)"),
        
        heading2("Medium Priority"),
        bullet("[ ] Automated wallpaper health checks via vision"),
        bullet("[ ] System resource monitoring dashboard"),
        
        heading2("Low Priority"),
        bullet("[ ] Notion-to-MCP sync for ideas"),
        
        divider(),
        
        heading1("Completed Improvements"),
        paragraph("Archive of implemented improvements with completion dates.", bold=True),
        bullet("[2026-03-03] Created System Health Dashboard in Notion"),
        
        divider(),
        paragraph("Maintained by: Notion System Diagnostics Agent"),
        paragraph("Next update: [Scheduled via cron]")
    ]

    print(f"Adding {len(blocks)} blocks to page...")
    result = add_blocks(page_id, blocks)
    print(f"Added {len(result.get('results', []))} blocks successfully!")

if __name__ == '__main__':
    main()
