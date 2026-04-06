---
name: skill-creator
description: Use when creating new skills, editing existing skills, or verifying skills work before deployment
---

# Skill Creator

## Overview

**Skill creation IS Test-Driven Development applied to process documentation.**

You write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**REQUIRED BACKGROUND:** You MUST understand test-driven-development before using this skill. That methodology defines the fundamental RED-GREEN-REFACTOR cycle. This skill adapts TDD to documentation.

## What is a Skill?

A **skill** is a reference guide for proven techniques, patterns, or tools. Skills help future agent instances find and apply effective approaches.

**Skills are:** Reusable techniques, patterns, tools, reference guides

**Skills are NOT:** Narratives about how you solved a problem once

## TDD Mapping for Skills

| TDD Concept | Skill Creation |
|-------------|----------------|
| **Test case** | Pressure scenario with subagent |
| **Production code** | Skill document (SKILL.md) |
| **Test fails (RED)** | Agent violates rule without skill (baseline) |
| **Test passes (GREEN)** | Agent complies with skill present |
| **Refactor** | Close loopholes while maintaining compliance |
| **Write test first** | Run baseline scenario BEFORE writing skill |
| **Watch it fail** | Document exact rationalizations agent uses |
| **Minimal code** | Write skill addressing those specific violations |
| **Watch it pass** | Verify agent now complies |
| **Refactor cycle** | Find new rationalizations → plug → re-verify |

The entire skill creation process follows RED-GREEN-REFACTOR.

## When to Create a Skill

**Create when:**
- Technique wasn't intuitively obvious to you
- You'd reference this again across projects
- Pattern applies broadly (not project-specific)
- Others would benefit

**Don't create for:**
- One-off solutions
- Standard practices well-documented elsewhere
- Project-specific conventions (put in AGENTS.md)
- Mechanical constraints (if it's enforceable with regex/validation, automate it—save documentation for judgment calls)

## Skill Types

### Technique
Concrete method with steps to follow (condition-based-waiting, root-cause-tracing)

### Pattern
Way of thinking about problems (flatten-with-flags, test-invariants)

### Reference
API docs, syntax guides, tool documentation (office docs)

## Directory Structure

```
skills/
  skill-name/
    SKILL.md              # Main reference (required)
    scripts/              # Only if needed
      test-harness.js     # Pressure testing
      example-tool.py     # Reusable utility
    references/           # Heavy reference material
      api-docs.md
```

**Flat namespace** - all skills in one searchable namespace

**Separate files for:**
1. **Heavy reference** (100+ lines) - API docs, comprehensive syntax
2. **Reusable tools** - Scripts, utilities, templates

**Keep inline:**
- Principles and concepts
- Code patterns (< 50 lines)
- Everything else

## SKILL.md Structure

**Frontmatter (YAML):**
- Two required fields: `name` and `description`
- Max 1024 characters total
- `name`: Use letters, numbers, and hyphens only (no parentheses, special chars)
- `description`: Third-person, describes ONLY when to use (NOT what it does)
  - Start with "Use when..." to focus on triggering conditions
  - Include specific symptoms, situations, and contexts
  - **NEVER summarize the skill's process or workflow** (see CSO section for why)
  - Keep under 500 characters if possible

```markdown
---
name: Skill-Name-With-Hyphens
description: Use when [specific triggering conditions and symptoms]
---

# Skill Name

## Overview
What is this? Core principle in 1-2 sentences.

## When to Use
- Bullet list with SYMPTOMS and use cases
- When NOT to use
- [Inline flowchart IF decision non-obvious]

## Core Pattern (for techniques/patterns)
Before/after code comparison

## Quick Reference
Table or bullets for scanning common operations

## Implementation
Inline code for simple patterns
Link to file for heavy reference or reusable tools

## Common Mistakes
What goes wrong + fixes

## Real-World Impact (optional)
Concrete results
```

## Claude Search Optimization (CSO)

**Critical for discovery:** Future agent needs to FIND your skill

### 1. Rich Description Field

**Purpose:** Agent reads description to decide which skills to load for a given task. Make it answer: "Should I read this skill right now?"

**Format:** Start with "Use when..." to focus on triggering conditions

**CRITICAL: Description = When to Use, NOT What the Skill Does**

The description should ONLY describe triggering conditions. Do NOT summarize the skill's process or workflow in the description.

**Why this matters:** Testing revealed that when a description summarizes the workflow, the agent may follow the description instead of reading the full skill content. A description saying "code review between tasks" caused the agent to do ONE review, even though the skill's flowchart clearly showed TWO reviews (spec compliance then code quality).

When the description was changed to just "Use when executing implementation plans with independent tasks" (no workflow summary), the agent correctly read the flowchart and followed the two-stage review process.

**The trap:** Descriptions that summarize workflow create a shortcut the agent will take. The skill body becomes documentation the agent skips.

```yaml
# ❌ BAD: Summarizes workflow - agent may follow this instead of reading skill
description: Use when executing plans - dispatches subagent per task with code review between tasks

# ❌ BAD: Too much process detail
description: Use for TDD - write test first, watch it fail, write minimal code, refactor

# ✅ GOOD: Just triggering conditions, no workflow summary
description: Use when executing implementation plans with independent tasks in the current session

# ✅ GOOD: Triggering conditions only
description: Use when implementing any feature or bugfix, before writing implementation code
```

**Content:**
- Use concrete triggers, symptoms, and situations that signal this skill applies
- Describe the *problem* (race conditions, inconsistent behavior) not *language-specific symptoms* (setTimeout, sleep)
- Keep triggers technology-agnostic unless the skill itself is technology-specific
- If skill is technology-specific, make that explicit in the trigger
- Write in third person (injected into system prompt)
- **NEVER summarize the skill's process or workflow**

```yaml
# ❌ BAD: Too abstract, vague, doesn't include when to use
description: For async testing

# ❌ BAD: First person
description: I can help you with async tests when they're flaky

# ❌ BAD: Mentions technology but skill isn't specific to it
description: Use when tests use setTimeout/sleep and are flaky

# ✅ GOOD: Starts with "Use when", describes problem, no workflow
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently

# ✅ GOOD: Technology-specific skill with explicit trigger
description: Use when using React Router and handling authentication redirects
```

### 2. Keyword Coverage

Use words the agent would search for:
- Error messages: "Hook timed out", "ENOTEMPTY", "race condition"
- Symptoms: "flaky", "hanging", "zombie", "pollution"
- Synonyms: "timeout/hang/freeze", "cleanup/teardown/afterEach"
- Tools: Actual commands, library names, file types

### 3. Descriptive Naming

**Use active voice, verb-first:**
- ✅ `creating-skills` not `skill-creation`
- ✅ `condition-based-waiting` not `async-test-helpers`

### 4. Token Efficiency (Critical)

**Problem:** Frequently-loaded skills load into EVERY conversation. Every token counts.

**Target word counts:**
- Getting-started workflows: <150 words each
- Frequently-loaded skills: <200 words total
- Other skills: <500 words (still be concise)

**Techniques:**

**Move details to tool help:**
```bash
# ❌ BAD: Document all flags in SKILL.md
search-conversations supports --text, --both, --after DATE, --before DATE, --limit N

# ✅ GOOD: Reference --help
search-conversations supports multiple modes and filters. Run --help for details.
```

**Use cross-references:**
```markdown
# ❌ BAD: Repeat workflow details
When searching, dispatch subagent with template...
[20 lines of repeated instructions]

# ✅ GOOD: Reference other skill
Always use subagents (50-100x context savings). REQUIRED: Use [other-skill-name] for workflow.
```

**Compress examples:**
```markdown
# ❌ BAD: Verbose example (42 words)
your human partner: "How did we handle authentication errors in React Router before?"
You: I'll search past conversations for React Router authentication p...

# ✅ GOOD: Compressed (12 words)
Example: "Search for React Router auth errors in past conversations"
```

## The TDD Cycle for Skills

### Phase 1: RED (Baseline Test)

**Goal:** Watch the agent fail WITHOUT the skill

1. **Define pressure scenario** - What should the skill prevent?
2. **Spawn subagent** - Give it the task WITHOUT the skill
3. **Document violations** - What rationalizations does it use?
4. **Save baseline** - Record exact failure modes

**Example:**
```
Task: "Create a new skill for handling async tests"
Expected: Agent should write test cases first, then skill
Actual: Agent writes skill immediately, no tests
Rationalization: "Tests aren't needed for documentation"
```

### Phase 2: GREEN (Write Skill)

**Goal:** Write minimal skill that addresses documented violations

1. **Address each violation** - Directly counter the rationalizations
2. **Keep it minimal** - Only what's needed to pass the test
3. **Include examples** - Show the right way
4. **Test immediately** - Run the same scenario WITH the skill

**Example:**
```markdown
## Core Principle
If you didn't watch an agent fail without the skill, you don't know if it teaches the right thing.

## Required First Step
BEFORE writing any skill content:
1. Spawn subagent with the task
2. Document what it does wrong
3. Save the baseline violations
```

### Phase 3: REFACTOR (Close Loopholes)

**Goal:** Improve skill without breaking compliance

1. **Find new rationalizations** - Agent finds creative ways to violate
2. **Plug holes** - Update skill to address them
3. **Re-verify** - Ensure original test still passes
4. **Repeat** - Until skill is robust

**Example:**
```
New rationalization: "This skill is different, it doesn't need tests"
Fix: Add "When This Applies" section with examples
Re-verify: Original test passes, new edge case covered
```

## Test Harness

**Location:** `skills/skill-creator/scripts/pressure-test.js`

**Usage:**
```bash
# Test a skill creation scenario
node scripts/pressure-test.js --scenario "async-test-skill"

# Run full TDD cycle
node scripts/pressure-test.js --full-cycle --skill-name "condition-based-waiting"
```

**What it does:**
1. Spawns subagent WITHOUT skill → documents violations
2. Prompts you to write skill
3. Spawns subagent WITH skill → verifies compliance
4. Reports loopholes found

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Writing skill before baseline test | Always run RED phase first |
| Summarizing workflow in description | Description = triggers ONLY |
| Too verbose (>500 words) | Use cross-references, move details to tool help |
| No keyword coverage | Add error messages, symptoms, synonyms |
| First-person voice | Write in third person (system prompt injection) |
| Vague triggering conditions | Be specific: symptoms, situations, contexts |

## Real-World Impact

**Before TDD for skills:**
- Skills written based on assumptions
- Agents found loopholes immediately
- Constant skill revisions
- No way to verify improvements

**After TDD for skills:**
- Skills address documented failures
- Loopholes caught in testing
- Confident in skill quality
- Measurable compliance rates

## Related Skills

- `test-driven-development` - Core TDD methodology (REQUIRED)
- `writing-plans` - Breaking work into testable tasks
- `requesting-code-review` - Review methodology for skills

---

*Updated: 2026-04-06 — Adapted from superpowers writing-skills for OpenClaw architecture.*
