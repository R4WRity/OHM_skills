---
name: git-workspace
description: Use when committing workspace changes, pushing to GitHub, or managing git branches for skills and infrastructure
---

# Git Workspace

## Overview

**Automated git workflow for OpenClaw skills and infrastructure.**

This skill ensures consistent, recoverable version control with meaningful commits, proper branching, and automated push/pull operations.

**Core principle:** Every change should be recoverable, traceable, and follow a consistent pattern that makes future work easier.

## When to Use

**Use when:**
- Committing skill changes (new skills, updates, refactors)
- Pushing to GitHub repos (OHM_Skills, OHM_Stack, OHM_Superpowers, OHM_Compound)
- Creating feature branches for skills (`skill/{name}`)
- Rolling back to known-good state after failures
- Checking git status before operations
- Handling authentication errors

**When NOT to use:**
- Quick local experiments (use git directly)
- One-off file edits (skill auto-commits on deploy)
- Merging upstream changes (manual review needed)

## Core Workflow

```
1. Check status     → git status --short
2. Stage changes    → git add <paths>
3. Verify .gitignore → Ensure no tracked junk
4. Commit message   → <type>: <description>
5. Commit           → git commit -m "..."
6. Push             → git push origin <branch>
7. Confirm          → Verify remote updated
```

## Commit Message Format

**Convention:** Conventional Commits

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` — New skill or feature
- `fix` — Bug fix
- `docs` — Documentation only
- `refactor` — Code change that's neither feat nor fix
- `test` — Adding or updating tests
- `chore` — Maintenance (gitignore, config, etc.)

**Examples:**
```
feat(skill-creator): add TDD methodology with pressure testing
fix(git-workspace): handle index.lock cleanup on Windows
docs(readme): add installation instructions
refactor(user-onboarding): extract answer storage to separate module
test(load-user): add skill propagation test cases
chore(skills): update .gitignore for __pycache__
```

## Branch Strategy

**Main branch:** `main` — Always deployable, tested skills

**Feature branches:** `skill/{name}` — One skill per branch

```bash
# Create skill branch
git checkout -b skill/git-workspace

# Work on skill
# ...

# Merge to main after testing
git checkout main
git merge skill/git-workspace
git push origin main
```

## Commands

### Commit Skill Changes

```bash
node scripts/git-commit.js --skill <name> --message "<description>"
```

**Auto-formats commit message:**
```
feat(<skill-name>): <description>
```

### Push to GitHub

```bash
node scripts/git-push.js [--branch <name>]
```

**Defaults:** Current branch, origin remote

### Create Skill Branch

```bash
node scripts/git-branch.js --create --skill <name>
```

**Creates:** `skill/<name>` from `main`

### Rollback

```bash
node scripts/git-rollback.js [--commit <hash>]
```

**Reverts to:** Last known-good commit or specified hash

### Status Check

```bash
node scripts/git-status.js [--verbose]
```

**Shows:** Modified files, staged files, untracked files

## Implementation

**Location:** `skills/git-workspace/scripts/`

| Script | Purpose |
|--------|---------|
| `git-commit.js` | Stage, format message, commit |
| `git-push.js` | Push with confirmation |
| `git-branch.js` | Create/manage skill branches |
| `git-rollback.js` | Revert to known-good state |
| `git-status.js` | Enhanced status display |
| `git-auth.js` | Handle auth errors, token refresh |

## TDD Integration

**Commit at each TDD stage:**

```bash
# RED phase
git commit -m "RED: <skill> baseline fails - <specific violation>"

# GREEN phase
git commit -m "GREEN: <skill> tests pass - <compliance verified>"

# REFACTOR phase
git commit -m "REFACTOR: <skill> - <loophole closed>"
```

**Example:**
```bash
# Baseline test fails
git commit -m "RED: git-workspace baseline fails - no index.lock handling"

# Skill written, tests pass
git commit -m "GREEN: git-workspace tests pass - handles index.lock cleanup"

# Refined skill
git commit -m "REFACTOR: git-workspace - add safe.directory auto-config"
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Vague commit messages | Use conventional commits: `feat(skill): description` |
| Committing to main directly | Use `skill/{name}` branches |
| Not checking .gitignore | Run `git status` before staging |
| Pushing without confirmation | Script confirms remote updated |
| Ignoring auth errors | Use `git-auth.js` for token refresh |
| No rollback plan | Always know last known-good commit |

## Authentication

**Windows Credential Manager:**
```bash
git config --global credential.helper wincred
```

**Personal Access Token:**
1. https://github.com/settings/tokens
2. Generate token with `repo` scope
3. Use as password when prompted
4. Store in Credential Manager

**SSH Keys (alternative):**
```bash
ssh-keygen -t ed25519 -C "github@ohm"
# Add to GitHub: Settings → SSH and GPG keys
```

## Error Handling

### index.lock Exists
```bash
# Skill auto-clears stale locks
node scripts/git-commit.js --skill <name>
# If fails: Remove-Item .git/index.lock -Force
```

### Ownership Errors (Windows)
```bash
# Skill auto-configures safe.directory
git config --global --add safe.directory <path>
```

### Push Hung on Auth
```bash
# Timeout after 30s, prompt for token
node scripts/git-push.js --timeout 30000
```

### Remote Not Found
```bash
# Skill verifies remote exists before push
git remote -v
# If missing: git remote add origin <url>
```

## Real-World Impact

**Before git-workspace:**
- Manual git operations
- Inconsistent commit messages
- No branch strategy
- Auth errors blocked progress
- No rollback capability

**After git-workspace:**
- Automated commits with meaningful messages
- Skill branches for isolation
- Graceful auth handling
- Rollback to known-good state
- TDD cycle tracked in git history

## Related Skills

- `skill-creator` — TDD methodology (uses git-workspace for commits)
- `test-driven-development` — Core TDD cycle
- `writing-plans` — Breaking work into commits

---

*Updated: 2026-04-06 — First skill built using skill-creator TDD methodology.*
