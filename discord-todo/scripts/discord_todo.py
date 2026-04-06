#!/usr/bin/env python3
"""
Discord To-Do Command Handler
Processes Discord commands for todo management
"""

import requests
import json
import re
from datetime import datetime, timedelta

class KnowledgeGraphClient:
    def __init__(self, base_url="http://localhost:9301", group_id="rawrity"):
        self.base_url = base_url
        self.mcp_url = f"{self.base_url}/mcp"
        self.group_id = group_id
        self.msg_id = 0
    
    def _call(self, method, params):
        self.msg_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": {**params, "group_id": self.group_id},
            "id": f"req_{self.msg_id}"
        }
        try:
            resp = requests.post(self.mcp_url, json=payload, timeout=30)
            return resp.json().get("result", {})
        except Exception as e:
            return {"error": str(e)}
    
    def add_entity(self, name, entity_type, properties=None):
        params = {"name": name, "entity_type": entity_type}
        if properties:
            params["properties"] = properties
        return self._call("add_entity", params)
    
    def add_relation(self, from_entity, to_entity, relation_type):
        return self._call("add_relation", {
            "from_entity": from_entity,
            "to_entity": to_entity,
            "relation_type": relation_type
        })
    
    def search_text(self, query, limit=50):
        return self._call("search_text", {"query": query, "limit": limit})

def parse_command(message):
    """Parse Discord todo command"""
    message = message.strip()
    
    if not message.startswith("/todo"):
        return None
    
    parts = message.split(maxsplit=2)
    if len(parts) < 2:
        return {"command": "help"}
    
    command = parts[1].lower()
    args = parts[2] if len(parts) > 2 else ""
    
    # Parse key:value pairs
    params = {}
    # Extract quoted strings first
    quoted = re.findall(r'"([^"]+)"', args)
    args_no_quotes = re.sub(r'"[^"]+"', '', args)
    
    # Parse remaining key:value pairs
    for match in re.finditer(r'(\w+):(\S+)', args_no_quotes):
        key, value = match.groups()
        params[key.lower()] = value
    
    # Add quoted strings as description if present
    if quoted:
        params['description'] = quoted[0]
    
    return {
        "command": command,
        "params": params
    }

def handle_add(params):
    """Handle /todo add command"""
    description = params.get('description', params.get('task', 'Unnamed Task'))
    project = params.get('project')
    due = params.get('due')
    priority = params.get('priority', 'medium')
    tags = params.get('tags')
    notes = params.get('notes')
    
    graph = KnowledgeGraphClient("http://localhost:9301", "rawrity")
    
    properties = {
        "description": description,
        "status": "backlog",
        "priority": priority,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
    }
    
    if project:
        properties["project"] = project
    if due:
        properties["due_date"] = due
    if tags:
        properties["tags"] = tags.split(",")
    if notes:
        properties["notes"] = notes
    
    result = graph.add_entity(description, "Task", properties)
    
    if result.get("success"):
        response = f"✅ **Task Created**\n\n"
        response += f"**{description}**\n"
        if project:
            response += f"📁 Project: {project}\n"
            graph.add_entity(project, "Project", {"created": datetime.now().isoformat()})
            graph.add_relation(project, description, "has_task")
        if due:
            response += f"📅 Due: {due}\n"
        response += f"🎯 Priority: {priority}\n"
        if tags:
            response += f"🏷️ Tags: {tags}\n"
        response += f"📋 Status: backlog"
        return response
    else:
        return f"❌ Error creating task: {result}"

def handle_list(params):
    """Handle /todo list command"""
    graph = KnowledgeGraphClient("http://localhost:9301", "rawrity")
    
    filter_type = params.get('filter', 'all')
    project = params.get('project')
    priority = params.get('priority')
    
    search_query = "Task"
    if project:
        search_query += f" {project}"
    if priority:
        search_query += f" {priority}"
    
    result = graph.search_text(search_query, limit=100)
    
    if not result.get("results"):
        return "📋 No tasks found."
    
    tasks = []
    for r in result["results"]:
        props = r.get("properties", {})
        
        # Skip done tasks unless specifically requested
        if props.get("status") == "done" and filter_type != "done":
            continue
        
        # Filter logic
        if filter_type == "overdue":
            due = props.get("due_date")
            if due and due < datetime.now().strftime("%Y-%m-%d"):
                tasks.append((r, "overdue"))
        elif filter_type == "today":
            due = props.get("due_date")
            if due and due == datetime.now().strftime("%Y-%m-%d"):
                tasks.append((r, "today"))
        elif project and props.get("project") != project:
            continue
        elif priority and props.get("priority") != priority:
            continue
        else:
            # Determine status
            due = props.get("due_date")
            if due and due < datetime.now().strftime("%Y-%m-%d") and props.get("status") != "done":
                tasks.append((r, "overdue"))
            elif due and due == datetime.now().strftime("%Y-%m-%d"):
                tasks.append((r, "today"))
            else:
                tasks.append((r, "normal"))
    
    if not tasks:
        return "📋 No tasks match your filters."
    
    # Sort by priority + due date
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    tasks.sort(key=lambda t: (
        priority_order.get(t[0].get("properties", {}).get("priority", "medium"), 2),
        t[0].get("properties", {}).get("due_date", "9999-99-99")
    ))
    
    # Build response
    response = f"📋 **To-Do List** ({len(tasks)} tasks)\n\n"
    
    for i, (task, status_type) in enumerate(tasks[:20], 1):  # Limit to 20 for Discord
        props = task.get("properties", {})
        name = task.get("name", "Unknown")
        
        # Status emoji
        status_emoji = {
            "backlog": "📋",
            "todo": "⏳",
            "in-progress": "🔄",
            "blocked": "⛔",
            "done": "✅"
        }.get(props.get("status", "backlog"), "📋")
        
        # Priority emoji
        priority_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(props.get("priority", "medium"), "⚪")
        
        # Due date
        due = props.get("due_date")
        if status_type == "overdue":
            due_display = f"🚨 **OVERDUE:** {due}"
        elif status_type == "today":
            due_display = f"⏰ **DUE TODAY:** {due}"
        elif due:
            due_display = f"📅 Due: {due}"
        else:
            due_display = ""
        
        response += f"{i}. {status_emoji} {priority_emoji} **{name}**\n"
        if due_display:
            response += f"   {due_display}\n"
        if props.get('project'):
            response += f"   📁 {props.get('project')}\n"
        response += "\n"
    
    if len(tasks) > 20:
        response += f"... and {len(tasks) - 20} more tasks.\n"
        response += "Use `/todo list priority:high` to filter."
    
    return response

def handle_update(params, done=False):
    """Handle /todo update or /todo done command"""
    # Find task by name or ID
    task_identifier = params.get('description') or params.get('task')
    
    if not task_identifier:
        return "❌ Please specify a task name or ID."
    
    graph = KnowledgeGraphClient("http://localhost:9301", "rawrity")
    
    # Search for task
    result = graph.search_text(task_identifier, limit=10)
    
    if not result.get("results"):
        return f"❌ Task not found: {task_identifier}"
    
    # Get first match
    task = result["results"][0]
    task_name = task.get("name")
    
    if done:
        # Mark as done
        new_status = "done"
        response = f"✅ **Task Completed:** {task_name}\n\nGreat job! 🎉"
    else:
        # Update status/notes
        new_status = params.get('status')
        notes = params.get('notes')
        
        response = f"🔄 **Task Updated:** {task_name}\n\n"
        if new_status:
            response += f"Status: {new_status}\n"
        if notes:
            response += f"Notes: {notes}\n"
    
    return response

def handle_stats(params):
    """Handle /todo stats command"""
    graph = KnowledgeGraphClient("http://localhost:9301", "rawrity")
    
    result = graph.search_text("Task", limit=200)
    
    if not result.get("results"):
        return "📊 No tasks found."
    
    tasks = result["results"]
    total = len(tasks)
    
    # Count by status
    by_status = {}
    by_priority = {}
    overdue = 0
    today = datetime.now().strftime("%Y-%m-%d")
    
    for task in tasks:
        props = task.get("properties", {})
        status = props.get("status", "backlog")
        priority = props.get("priority", "medium")
        due = props.get("due_date")
        
        by_status[status] = by_status.get(status, 0) + 1
        by_priority[priority] = by_priority.get(priority, 0) + 1
        
        if due and due < today and status != "done":
            overdue += 1
    
    response = "📊 **Task Statistics**\n\n"
    response += f"**Total Tasks:** {total}\n\n"
    
    response += "**By Status:**\n"
    for status, count in sorted(by_status.items()):
        emoji = {"backlog": "📋", "todo": "⏳", "in-progress": "🔄", "blocked": "⛔", "done": "✅"}.get(status, "")
        response += f"{emoji} {status}: {count}\n"
    
    response += f"\n**By Priority:**\n"
    for priority, count in sorted(by_priority.items(), key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x[0], 4)):
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "")
        response += f"{emoji} {priority}: {count}\n"
    
    if overdue > 0:
        response += f"\n🚨 **Overdue:** {overdue}"
    
    return response

def process_discord_command(message):
    """Main entry point for Discord commands"""
    command = parse_command(message)
    
    if not command:
        return None
    
    cmd = command["command"]
    params = command.get("params", {})
    
    if cmd == "add":
        return handle_add(params)
    elif cmd == "list":
        return handle_list(params)
    elif cmd == "update":
        return handle_update(params)
    elif cmd == "done":
        return handle_update(params, done=True)
    elif cmd == "stats":
        return handle_stats(params)
    elif cmd == "help":
        return """📋 **To-Do Commands**

`/todo add [description] [project:name] [due:date] [priority:level] [tags:tags]`
  Add a new task

`/todo list [filter:all|project:name|priority:high|overdue]`
  List tasks with optional filter

`/todo update [task] [status:status] [notes:text]`
  Update task status or notes

`/todo done [task]`
  Mark task as complete

`/todo stats`
  Show task statistics

**Examples:**
`/todo add Build workflow project:Image Generation due:2026-04-15 priority:high tags:n8n,workflow`
`/todo list project:Image Generation`
`/todo done "Build workflow"`"""
    else:
        return f"❓ Unknown command: {cmd}. Use `/todo help` for available commands."

if __name__ == "__main__":
    # Test with sample commands
    import sys
    test_commands = [
        "/todo add Build n8n workflow project:Image Generation due:2026-04-15 priority:high tags:n8n,workflow",
        "/todo list",
        "/todo stats",
    ]
    
    for cmd in test_commands:
        sys.stdout.write(f"\nCommand: {cmd}\n")
        sys.stdout.write("-" * 80 + "\n")
        response = process_discord_command(cmd)
        sys.stdout.write(response + "\n")
        sys.stdout.flush()
