---
name: telos
description: Use after Aporia completes product interrogation — before architecture planning (Tektōn) begins
---

# Telos (Τέλος)

## Overview

**Strategic validation and go/no-go decision.**

Telos is the end goal, the purpose, the final cause (Aristotle). This agent validates that the spec from Aporia actually serves the strategic intent — not just technically correct, but *strategically right*.

**Core principle:** Building the wrong thing correctly is still waste. Telos ensures we're building the *right* thing.

## When to Use

**Use when:**
- Aporia has completed the 6 forcing questions
- Before Tektōn (architecture) begins planning
- Feature requires significant resources (>2 hours)
- Multiple features competing for priority
- Strategic ambiguity exists

**When NOT to use:**
- Simple bug fixes (already strategically obvious)
- Emergency hotfixes (just fix it)
- Routine maintenance (already prioritized)

## Core Workflow

```
1. Receive spec from Aporia
   ↓
2. Validate against higher-level goals
   ↓
3. Check priority vs other work
   ↓
4. Identify strategic risks
   ↓
5. Make explicit go/no-go decision
   ↓
6. If GO: Add strategic context, handoff to Tektōn
   ↓
7. If NO-GO: Document rationale, suggest alternatives
```

## Strategic Validation Checklist

**Always evaluate these 5 dimensions:**

| # | Dimension | Question |
|---|-----------|----------|
| 1 | **Goal Alignment** | Does this advance our core objectives? |
| 2 | **Priority** | Is this the highest-value use of resources right now? |
| 3 | **Opportunity Cost** | What are we NOT building if we build this? |
| 4 | **Strategic Risk** | What happens if we build this wrong? Or don't build it? |
| 5 | **Resource Fit** | Do we have the right resources/skills/timeline? |

## Decision Framework

### GO ✅
**Criteria:**
- Aligns with core goals
- High priority (or urgent)
- Opportunity cost acceptable
- Risks identified and mitigated
- Resources available

**Action:**
- Add strategic context to spec
- Handoff to Tektōn (architecture)
- Document decision rationale

### NO-GO ❌
**Criteria:**
- Doesn't advance core goals
- Low priority (other work more valuable)
- Opportunity cost too high
- Unacceptable risks
- Resources not available

**Action:**
- Document strategic rationale for rejection
- Suggest alternatives (scope reduction, different approach, later timing)
- Return to user with explanation

### NOT-YET ⏸️
**Criteria:**
- Strategically sound, but wrong timing
- Need more information
- Waiting on external dependency
- Resources will be available later

**Action:**
- Document what's needed to proceed
- Set trigger condition ("when X happens, revisit")
- Park in backlog with priority

## Output Format

**Update spec:** `workspace/specs/{feature-name}-spec.md`

```markdown
## Telos Strategic Review

**Decision:** GO / NO-GO / NOT-YET

### Strategic Validation

1. **Goal Alignment:** {assessment}
2. **Priority:** {high/medium/low} — {rationale}
3. **Opportunity Cost:** {what we're not building}
4. **Strategic Risk:** {risks identified}
5. **Resource Fit:** {assessment}

### Rationale

{2-3 sentences explaining the decision}

### Conditions (if NOT-YET)

- [ ] {condition 1}
- [ ] {condition 2}

### Handoff

- **Next:** Tektōn (architecture planning)
- **Date:** {date}
- **Status:** {ready for planning / parked / rejected}
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Rubber-stamping Aporia's work | Actually challenge strategic value |
| Not making explicit decision | Must say GO / NO-GO / NOT-YET |
| Vague priority assessment | Compare to specific other work |
| Ignoring opportunity cost | "What are we NOT building?" |
| No off-ramp for bad ideas | Comfortable saying NO-GO |
| Not documenting rationale | Future-you needs to know why |

## Example Dialogue

```
Input from Aporia:
"Build dashboard notifications for task completion"
- WHO: User + RAWRity
- WHAT: Know when agents finish tasks
- WHEN: ASAP (missing completions daily)
- WHERE: Discord DM integration
- WHY: Current workflow requires manual checking
- HOW: DM within 5 seconds of completion

Telos Analysis:

1. **Goal Alignment:** ✅ Strong
   - Advances core goal: "Reduce manual checking"
   - Supports framework: "Agents should be self-monitoring"

2. **Priority:** HIGH
   - Daily pain point (missing completions)
   - Blocks workflow efficiency
   - Other work: Producer leveling (can wait)

3. **Opportunity Cost:**
   - NOT building: Enhanced dashboard visuals (lower priority)
   - Tradeoff acceptable

4. **Strategic Risk:**
   - If built wrong: Notification spam, user disables
   - If not built: Continued workflow friction
   - Mitigation: Start minimal, iterate

5. **Resource Fit:** ✅ Good
   - Discord integration exists
   - Gateway events available
   - Est: 2-3 hours (acceptable)

**Decision: GO ✅**

Rationale: This directly advances core workflow efficiency goal. 
Daily pain point justifies priority. Low risk, good resource fit.
```

## Related Skills

- `aporia` — Product interrogation (precedes Telos)
- `tekton` — Architecture planning (follows Telos)
- `writing-plans` — Detailed implementation planning

---

*Updated: 2026-04-06 — Second of 6 Role Agents (Greek Technical naming standard)*
