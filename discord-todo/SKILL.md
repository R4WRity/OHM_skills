# Discord To-Do Skill

Manage your personal to-do list via Discord commands

## Commands

- `/todo add [description] [project:name] [due:date] [priority:level] [tags:tags]` - Add new task
- `/todo list [filter]` - List tasks (all, by project, by priority, overdue)
- `/todo update [task] [status] [notes]` - Update task status or notes
- `/todo done [task]` - Mark task as complete
- `/todo stats [project]` - Show task statistics

## Usage

Type commands in Discord. Bot will respond with confirmation and task details.

## Examples

```
/todo add Build n8n workflow project:Image Generation due:2026-04-15 priority:high tags:n8n,workflow
/todo list project:Image Generation
/todo update "Build n8n workflow" status:in-progress
/todo done "Build n8n workflow"
```
