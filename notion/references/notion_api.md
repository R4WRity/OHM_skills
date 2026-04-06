# Notion API Reference

## Authentication

All requests require:
- `Authorization: Bearer <token>` header
- `Notion-Version: 2022-06-28` header
- `Content-Type: application/json` header for POST/PUT

## Common Operations

### Search
```
POST /v1/search
{
  "query": "search text",
  "page_size": 10
}
```

### Get Page
```
GET /v1/pages/{page_id}
```

### Get Page Content (Blocks)
```
GET /v1/blocks/{page_id}/children
```

### Create Page
```
POST /v1/pages
{
  "parent": {"page_id": "parent-page-id"},
  "properties": {
    "title": {"title": [{"text": {"content": "Page Title"}}]}
  },
  "children": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [{"type": "text", "text": {"content": "Content here"}}]
      }
    }
  ]
}
```

### Query Database
```
POST /v1/databases/{database_id}/query
{
  "filter": {
    "property": "Status",
    "select": {"equals": "Done"}
  }
}
```

### Create Page in Database
```
POST /v1/pages
{
  "parent": {"database_id": "database-id"},
  "properties": {
    "Name": {"title": [{"text": {"content": "Entry Title"}}]},
    "Status": {"select": {"name": "Idea"}}
  }
}
```

## Block Types

Common block types when reading/writing page content:

- `paragraph` — Regular text
- `heading_1`, `heading_2`, `heading_3` — Headings
- `bulleted_list_item` — Bullet list
- `numbered_list_item` — Numbered list
- `to_do` — Checkbox item
- `code` — Code block
- `quote` — Quote block
- `divider` — Horizontal line

## Property Types for Databases

- `title` — Page title
- `rich_text` — Text field
- `select` — Single select dropdown
- `multi_select` — Multi-select tags
- `status` — Status column
- `number` — Numeric value
- `date` — Date/datetime
- `relation` — Link to another database
- `formula` — Computed value
- `url` — URL link

## Rate Limits

- 3 requests per second (sustained)
- Burst: ~100 requests

If rate limited, wait and retry with exponential backoff.
