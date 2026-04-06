---
name: tekton
description: Use after Telos gives GO decision — before Builder (Praxis) begins implementation
---

# Tektōn (Τέκτων)

## Overview

**Architecture planning and file-by-file specification.**

Tektōn is the master builder, the architect, the designer (Greek: τέκτων — root of "technology", "technique"). This agent creates the implementation plan that Builder (Praxis) will execute.

**Core principle:** A clear plan prevents thrashing. Every file, every function, every dependency mapped before a single line is written.

## When to Use

**Use when:**
- Telos has given GO decision
- Feature requires multiple files/changes
- Before spawning Builder (Praxis) agent
- Complex integration points exist
- Multiple approaches possible

**When NOT to use:**
- Single-file changes (Builder can plan inline)
- Emergency hotfixes (just fix it)
- Trivial updates (typo fixes, config changes)

## Core Workflow

```
1. Receive spec from Telos (with GO decision)
   ↓
2. Analyze existing system structure
   ↓
3. Identify all files to create/modify
   ↓
4. For each file: define purpose, functions, dependencies
   ↓
5. Sequence the work (order of implementation)
   ↓
6. Define verification steps per file
   ↓
7. Handoff to Praxis (Builder) with complete plan
```

## Implementation Plan Format

**Update spec:** `workspace/specs/{feature-name}-spec.md`

```markdown
## Tektōn Architecture Plan

### Files to Create

| File | Purpose | Key Functions | Dependencies |
|------|---------|---------------|--------------|
| `path/to/file.js` | What it does | func1, func2 | module1, module2 |

### Files to Modify

| File | Changes | Reason | Risk |
|------|---------|--------|------|
| `path/to/file.js` | Add function X | Enable Y feature | Low |

### Implementation Sequence

1. **Phase 1:** Foundation (files A, B)
   - Create `path/A.js`
   - Create `path/B.js`
   - Verify: [test steps]

2. **Phase 2:** Integration (files C, D)
   - Modify `path/C.js`
   - Create `path/D.js`
   - Verify: [test steps]

3. **Phase 3:** Polish (files E)
   - Update `path/E.js`
   - Verify: [test steps]

### Dependencies

- **External:** {npm packages, APIs}
- **Internal:** {existing modules}
- **Blocking:** {must exist before we start}

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {risk} | Low/Med/High | Low/Med/High | {how to reduce} |
```

## Planning Heuristics

### YAGNI (You Aren't Gonna Need It)
**Don't plan for hypothetical futures.** Only what's needed for this spec.

### DRY (Don't Repeat Yourself)
**Identify shared logic.** Plan abstractions where duplication exists.

### Separation of Concerns
**One responsibility per file.** Don't mix concerns.

### Testability
**Plan tests alongside implementation.** Each file should have verification steps.

### Incremental Verification
**Verify after each phase.** Don't wait until the end.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Over-engineering | Apply YAGNI — only what's needed |
| Vague file descriptions | Be specific: functions, dependencies |
| No verification steps | Define how to verify each file |
| Wrong sequence | Dependencies first, polish last |
| Missing risks | Identify and mitigate upfront |
| Planning in isolation | Reference existing patterns |

## Example Plan

```markdown
## Tektōn Architecture Plan: Dashboard Notifications

### Files to Create

| File | Purpose | Key Functions | Dependencies |
|------|---------|---------------|--------------|
| `skills/notifications/discord-sender.js` | Send DM via Discord API | sendDM(), formatMessage() | discord.js, config |
| `skills/notifications/event-listener.js` | Listen for task completion | onTaskComplete(), filterEvents() | gateway-events |

### Files to Modify

| File | Changes | Reason | Risk |
|------|---------|--------|------|
| `skills/gateway/events.js` | Add task-complete event | Emit when task done | Low |
| `workspace/config.json` | Add Discord bot token | Auth for DM sending | Low |

### Implementation Sequence

**Phase 1: Foundation** (30 min)
1. Create `discord-sender.js`
   - Export: `sendDM(userId, message)`
   - Use: Discord.js REST API
   - Verify: Mock test, send test DM

2. Create `event-listener.js`
   - Export: `onTaskComplete(callback)`
   - Use: Gateway event subscription
   - Verify: Trigger manually, verify callback

**Phase 2: Integration** (30 min)
3. Modify `gateway/events.js`
   - Add: `task-complete` event emission
   - Trigger: When task status = complete
   - Verify: Event appears in log

4. Wire together
   - Import event-listener in discord-sender
   - Subscribe to task-complete events
   - Verify: End-to-end test

**Phase 3: Configuration** (15 min)
5. Update `config.json`
   - Add: `discord.botToken`
   - Add: `notifications.enabled`
   - Verify: Config loads without error

### Dependencies

- **External:** discord.js (^14.0.0)
- **Internal:** gateway-events module
- **Blocking:** Discord bot token (user provides)

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Discord API rate limits | Low | Medium | Add retry logic, exponential backoff |
| Event spam (multiple completions) | Medium | Low | Debounce: 1 DM per task |
| Token security | Low | High | Store in .env, never commit |
```

## Related Skills

- `telos` — Strategic validation (precedes Tektōn)
- `praxis` — Implementation (follows Tektōn)
- `writing-plans` — Detailed task breakdown

---

*Updated: 2026-04-06 — Third of 6 Role Agents (Greek Technical naming standard)*
