---
name: hello-world
description: Use when testing the skill-creator TDD methodology with a minimal example
---

# Hello World

## Overview

**Test skill for validating the TDD methodology.**

This skill exists solely to test the `skill-creator` workflow. It has no real functionality.

## When to Use

**Use when:**
- Testing the TDD cycle end-to-end
- Validating git-workspace automation
- Demonstrating skill structure

**When NOT to use:**
- Production work (this is a test skill)
- Real tasks (use actual skills)

## Core Pattern

```
1. Write baseline test (RED)
2. Write minimal skill (GREEN)
3. Verify test passes (GREEN)
4. Delete or keep as example (REFACTOR)
```

## Test Commands

```bash
# Test git-workspace commit
node git-workspace/scripts/git-commit.js --skill hello-world --message "add test skill"

# Test git-workspace push
node git-workspace/scripts/git-push.js
```

## Expected Outcome

- ✅ Commit created with conventional format
- ✅ Push succeeds (with auth)
- ✅ Skill appears in OHM_Skills repo
- ✅ TDD cycle validated

---

*Updated: 2026-04-06 — Test skill for TDD methodology validation.*
