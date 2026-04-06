---
name: notion
description: Interact with Notion workspaces via the Notion API. Use when creating, reading, updating, or searching pages and databases in Notion. Supports note-taking, document building, and database operations for personal or team workspaces.
---

# Notion Integration

This skill provides tools to interact with your Notion workspace.

## Prerequisites

- Notion integration token must be configured in OpenClaw gateway settings under `notion.token`
- The Notion integration must be shared with relevant pages/databases in your workspace

## Quick Start

### Search Content
```python
python scripts/notion_search.py "game design ideas"
```

### Create a New Page
```python
python scripts/notion_create_page.py --parent <page_or_database_id> --title "New Game Concept" --content "Ideas here..."
```

### Read a Page
```python
python scripts/notion_get_page.py <page_id>
```

### List Databases
```python
python scripts/notion_list_databases.py
```

### Query a Database
```python
python scripts/notion_query_database.py <database_id> --filter '{"property":"Status","select":{"equals":"Idea"}}'
```

## Common Workflows

### Note Taking
1. Search for existing notes on a topic
2. If found, read and append new thoughts
3. If not, create a new page in your notes database/parent page

### Document Building
1. Create a structured page with headings and content blocks
2. Add content incrementally
3. Organize with tags/properties if using databases

### Game Development Ideas
- Create pages for each game concept
- Track ideas in a database with properties like Status, Genre, Priority
- Use the API to query and surface relevant ideas

## API Reference

See [references/notion_api.md](references/notion_api.md) for complete Notion API documentation and examples.
