---
name: praxis
description: Use after Tektōn completes architecture plan — for implementing features with TDD enforcement
---

# Praxis (Πρᾶξις)

## Overview

**Implementation with TDD enforcement.**

Praxis is action, practice, doing (Greek: πρᾶξις — vs. theory). This agent executes the plan from Tektōn, following RED-GREEN-REFACTOR for every function.

**Core principle:** Tests first, always. If it's not tested, it doesn't exist.

## When to Use

**Use when:**
- Tektōn has completed architecture plan
- Ready to implement features
- Building new functionality (not maintenance)
- Code quality matters (it always does)

**When NOT to use:**
- One-line fixes (just do it)
- Emergency hotfixes (test after, not before)
- Configuration changes (no tests needed)

## Core Workflow

```
1. Receive plan from Tektōn
   ↓
2. For each file in plan:
   a. Write failing test (RED)
   b. Write minimal code to pass (GREEN)
   c. Refactor (REFACTOR)
   d. Commit with TDD message
   ↓
3. Verify integration between files
   ↓
4. Run full test suite
   ↓
5. Handoff to Elenchus (review)
```

## TDD Enforcement

**RED Phase (Test First)**
- Write test BEFORE any implementation
- Watch it fail (verify test works)
- Document what "failing" looks like

**GREEN Phase (Minimal Code)**
- Write ONLY enough code to pass the test
- No extra features, no "while we're at it"
- If it passes, stop writing code

**REFACTOR Phase (Clean Up)**
- Improve code structure without changing behavior
- Tests must still pass
- Remove duplication, improve naming

## Commit Messages (TDD Cycle)

```
RED: <component> - write failing test for <feature>
GREEN: <component> - implement <feature> to pass test
REFACTOR: <component> - <improvement made>
```

**Example:**
```
RED: notifications - write failing test for sendDM()
GREEN: notifications - implement sendDM() using Discord API
REFACTOR: notifications - extract message formatting to separate function
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Writing code before test | RED phase ALWAYS comes first |
| Writing too much code | GREEN = minimal, no extras |
| Skipping refactor | Technical debt accumulates |
| Testing implementation details | Test behavior, not internals |
| One big commit at end | Commit per RED-GREEN-REFACTOR cycle |
| No verification between files | Test integrations explicitly |

## Example Workflow

```markdown
## Tektōn Plan: Dashboard Notifications

### Phase 1: Foundation

**File 1: discord-sender.js**

RED:
```javascript
// test/discord-sender.test.js
test('sendDM sends message to user', async () => {
  const result = await sendDM('user123', 'Task complete!');
  expect(result.sent).toBe(true);
  expect(result.userId).toBe('user123');
});
```
Watch it fail: `sendDM is not defined`

GREEN:
```javascript
// discord-sender.js
export async function sendDM(userId, message) {
  // Minimal implementation
  await discordClient.users.send(userId, message);
  return { sent: true, userId };
}
```
Test passes ✅

REFACTOR:
```javascript
// Extract formatting
function formatMessage(message) {
  return `⚡ ${message}`;
}

export async function sendDM(userId, message) {
  await discordClient.users.send(userId, formatMessage(message));
  return { sent: true, userId };
}
```
Test still passes ✅

**Commit:**
```
RED: notifications - write failing test for sendDM()
GREEN: notifications - implement sendDM() using Discord API
REFACTOR: notifications - extract message formatting
```

### Phase 2: Integration

**Wire files together, test end-to-end**

RED:
```javascript
// test/notifications-integration.test.js
test('sends DM when task completes', async () => {
  // Trigger task-complete event
  // Verify DM was sent
});
```

... continue pattern
```

## Related Skills

- `tekton` — Architecture planning (precedes Praxis)
- `elenchus` — Code review (follows Praxis)
- `test-driven-development` — Core TDD methodology

---

*Updated: 2026-04-06 — Fourth of 6 Role Agents (Greek Technical naming standard)*
