# Task Shelve Skill - Context Persistence for Human-AI Collaboration

**Purpose:** Capture active work context to Nerve's Kanban board when life interrupts, enabling seamless resumption later.

**Trigger Phrases:**

**Shelve/Pause (for later resumption):**
- "Shelve this"
- "Pause this"
- "Save to tasks"
- "Add to the board"
- "I need to stop"
- "Let's continue later"
- "Life is interrupting"
- "Need to handle [responsibility]"

**Add to To-Do (for future execution):**
- "Add this to my to-do list"
- "Put this on the todo"
- "Add to the to-do"
- "Make this a task"
- "Queue this up"

**Execute Now (start working immediately):**
- "Let's get to it"
- "Do this now"
- "Start working on this"
- "Execute this"

**Also triggers:** When agent detects conversation wrapping up or user indicating they need to leave

---

## What Gets Captured

**Task Structure:**
```
Title: [Active Work] <what we were working on>
Status: In Progress → Shelved → Ready to Resume

Context:
- What we were doing: <activity description>
- Where we left off: <last completed step/discussion point>
- Files involved: <paths to relevant files>
- Decisions made: <key decisions reached>
- Next steps: <numbered list of immediate next actions>
- Related tasks: <links to parent/child tasks if applicable>

Priority: <High|Medium|Low>
Assigned: <Unassigned|Ohm|RAWRity|Sigma>
Labels: <development|research|config|caretaker|etc>
```

**MEMORY.md Backup:**
- Log task creation to `memory/YYYY-MM-DD.md`
- Include task ID for reference
- Note: "Task shelved for later resumption"

---

## Execution Flow

1. **Detect trigger** (explicit phrase or contextual cue)
2. **Determine intent** from trigger type:
   - **Shelve/Pause** → Status: `in-progress` or `todo` (context-dependent), priority: preserve for resumption
   - **Add to To-Do** → Status: `todo`, priority: `normal` (or inferred from context)
   - **Execute Now** → Status: `in-progress`, priority: `high`, optionally spawn subagent immediately
3. **Summarize current context** from conversation
4. **Create task in Nerve Kanban** via API
5. **Log to MEMORY.md** as backup
6. **Confirm to user** with task details, status, and next steps

---

## API Endpoints (Nerve Kanban)

```bash
# Create task
curl -X POST http://localhost:3080/api/kanban/tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "...",
    "description": "...",
    "status": "shelved",
    "priority": "medium"
  }'

# List tasks
curl http://localhost:3080/api/kanban/tasks

# Update task
curl -X PUT http://localhost:3080/api/kanban/tasks/<id> \
  -H 'Content-Type: application/json' \
  -d '{"status": "ready-to-resume"}'
```

---

## Examples

**Example 1: Shelve for Later (Life Interrupts)**
```
User: "Need to shelve this — caretaker responsibilities"

Agent creates task:
Title: [Active Work] Nerve Cockpit Customization
Status: in-progress (ready to resume)
Context:
- What: Exploring Nerve theme options and customization paths
- Left off: Just finished reading CONFIGURATION.md, discussing 14 built-in themes
- Files: Ohm-nerve/docs/, workspace SOUL.md/TOOLS.md
- Decisions: Shelve deep customization until infrastructure complete
- Next: Try built-in themes in Settings, configure monospace font
Priority: normal
```

**Example 2: Add to To-Do (Future Execution)**
```
User: "Add this to my to-do list: test the new voice interface with 
different background noise levels"

Agent creates task:
Title: Test Voice Interface - Background Noise Robustness
Status: todo (queued for execution)
Context:
- What: Quality testing for voice STT accuracy
- Requirements: Test with various noise levels (quiet room, traffic, 
  music, multiple speakers)
- Success criteria: >90% transcription accuracy in moderate noise
Priority: normal
```

**Example 3: Execute Now (Immediate Action)**
```
User: "Let's get to it - check if the OpenClaw gateway is healthy 
and restart it if needed"

Agent creates task AND executes immediately:
Title: Gateway Health Check & Restart
Status: in-progress (actively executing)
Priority: high
Action: Spawns subagent or executes directly

[Agent performs the check, reports back with results]
```

**Example 4: Proactive Suggestion**
```
Agent: "I notice you've been working on this for 2 hours and mentioned 
an appointment coming up. Want me to shelve this to the Tasks board 
so you can pick it up later without losing context?"

User: "Yeah, add it to my to-do list"

Agent: "Done — added to your todo queue. Task ID: [id]. It'll be here 
when you're ready to resume."
```

---

## Task Breakdown Pattern

For large tasks, suggest decomposition:

```
Original: "Build complete voice interface"

Suggested breakdown:
- [ ] Research STT options (Whisper, ElevenLabs, browser STT)
- [ ] Research TTS options (ElevenLabs, Edge TTS, local)
- [ ] Design push-to-talk UI flow
- [ ] Implement WebSocket streaming for low latency
- [ ] Add wake word detection
- [ ] Test with real voice conversations
- [ ] Document setup and troubleshooting
```

---

## Failure Modes & Fallbacks

**If Nerve API unavailable:**
- Create task in `memory/pending-tasks.md` as fallback
- Notify user: "Nerve unavailable, saved to pending-tasks.md"
- Retry on next heartbeat

**If gateway down:**
- Log to daily memory file with `[TASK-PENDING]` prefix
- Set cron to retry when gateway back online

**If network error:**
- Local file backup always created first
- Sync to Nerve when connection restored

---

## Integration Points

**Heartbeat Integration:**
- Check for shelved tasks during heartbeat
- Prompt user: "You have 3 shelved tasks — want to resume any?"
- Auto-resume if user indicates availability

**Discord Integration:**
- When user returns via Discord, check for shelved tasks
- Offer: "Welcome back! You have shelved tasks from [date]. Resume?"

**Session Startup:**
- On new session, check for tasks assigned to current user
- Surface in opening message if found

---

## Memory Backup Format

In `memory/YYYY-MM-DD.md`:

```markdown
## Tasks Shelved

**Task ID:** task-2026-04-03-001
**Title:** Nerve Cockpit Customization
**When:** 2026-04-03 15:00 PDT
**Reason:** User caretaker responsibilities
**Context:** [brief summary]
**Next:** [immediate next step]
```

---

## Testing & Iteration

**Track:**
- How often tasks are shelved
- How often they're resumed
- Time between shelve and resume
- User satisfaction with resumption flow

**Iterate on:**
- Task description detail level (too much? too little?)
- Trigger phrase recognition
- Proactive suggestion timing
- Integration with other Project Prometheus patterns

---

**Created:** 2026-04-03  
**Pattern:** Context Persistence for Human-AI Collaboration  
**Part of:** Project Prometheus - Human-Centered AI Framework
