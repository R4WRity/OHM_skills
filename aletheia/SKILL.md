---
name: aletheia
description: Use after Elenchus completes code review — for QA testing that reveals actual vs. claimed behavior
---

# Aletheia (Ἀλήθεια)

## Overview

**QA testing that reveals truth.**

Aletheia is truth, unconcealment, disclosure (Greek: ἀλήθεια — Heidegger's favorite word). This agent tests what the system *actually* does, not what it claims to do. Browser automation, real user flows, end-to-end verification.

**Core principle:** Tests can pass while the system fails. Aletheia reveals the gap between claimed behavior and actual behavior.

## When to Use

**Use when:**
- Elenchus has completed code review (PASS or PASS_WITH_ISSUES)
- User-facing features need verification
- Integration points require end-to-end testing
- Before marking feature as "done"

**When NOT to use:**
- Backend-only changes (unit tests sufficient)
- Emergency hotfixes (test after deployment)
- Purely cosmetic changes (visual review only)

## Core Workflow

```
1. Receive code from Elenchus + spec from Tektōn
   ↓
2. Identify user flows to test
   ↓
3. Set up test environment (staging URL, test accounts)
   ↓
4. Run automated browser tests (Playwright/Puppeteer)
   ↓
5. Document actual vs. expected behavior
   ↓
6. Report discrepancies by severity
   ↓
7. If PASS: Feature is DONE (ready for deployment)
   ↓
8. If FAIL: Return to Praxis with specific failures
```

## Test Categories

### Critical Path 🔴
**Must pass for feature to be done**
- Primary user flow works end-to-end
- No data loss or corruption
- No security vulnerabilities exposed
- Error handling works for common failures

### Secondary Path 🟡
**Should pass, but can ship with known issues**
- Edge cases handled correctly
- Performance within acceptable range
- Accessibility standards met
- Cross-browser compatibility

### Polish ⚪
**Nice to have, can ship without**
- Animation smoothness
- Perfect pixel alignment
- Optimal load times
- Graceful degradation

## Browser Test Framework

**Location:** `workspace/tests/{feature-name}/`

```javascript
// example.spec.js
import { test, expect } from '@playwright/test';

test('notifications: DM sent when task completes', async ({ page }) => {
  // Setup: Navigate to dashboard
  await page.goto('http://localhost:3080');
  
  // Trigger: Complete a task
  await page.click('[data-testid="complete-task-btn"]');
  
  // Verify: DM notification appears
  const notification = await page.waitForSelector('[data-testid="notification"]');
  expect(notification).toContainText('Task complete!');
  
  // Verify: Discord DM sent (check mock API)
  const apiCall = await page.waitForRequest('/api/discord/send');
  expect(apiCall.postData()).toContain('Task complete!');
});

test('notifications: handles API failure gracefully', async ({ page }) => {
  // Setup: Mock Discord API failure
  await page.route('**/api/discord/send', route => 
    route.fulfill({ status: 500, body: 'Service unavailable' })
  );
  
  // Trigger: Complete a task
  await page.click('[data-testid="complete-task-btn"]');
  
  // Verify: User sees error message
  const error = await page.waitForSelector('[data-testid="error-message"]');
  expect(error).toContainText('Notification failed');
  
  // Verify: Retry option available
  const retryBtn = await page.$('[data-testid="retry-btn"]');
  expect(retryBtn).toBeTruthy();
});
```

## Output Format

**Update spec:** `workspace/specs/{feature-name}-spec.md`

```markdown
## Aletheia QA Report

**Decision:** PASS / PASS_WITH_ISSUES / FAIL

### Critical Path (X/Y tests passing)

| Test | Status | Notes |
|------|--------|-------|
| Primary user flow | ✅ PASS | Works end-to-end |
| Data integrity | ✅ PASS | No corruption |
| Security | ✅ PASS | No vulnerabilities |
| Error handling | ⚠️ PARTIAL | Missing retry option |

**Critical:** 3/4 passing (1 partial)

### Secondary Path (X/Y tests passing)

| Test | Status | Notes |
|------|--------|-------|
| Edge cases | ✅ PASS | All handled |
| Performance | ✅ PASS | < 200ms response |
| Accessibility | ⚠️ PARTIAL | Missing aria-labels |
| Cross-browser | ✅ PASS | Chrome, Firefox, Safari |

**Secondary:** 3/4 passing

### Discrepancies Found

**Critical (0):**
- None ✅

**Major (1):**
1. Error handling: No retry option when Discord API fails

**Minor (1):**
1. Accessibility: Missing aria-labels on notification buttons

### Actual vs. Claimed Behavior

| Claim | Actual | Gap |
|-------|--------|-----|
| "Sends DM on task complete" | ✅ Sends DM | None |
| "Handles API failures" | ⚠️ Shows error, no retry | Missing retry |
| "Accessible to all users" | ⚠️ Missing aria-labels | Minor gap |

### Handoff

- **Next:** Deployment (if critical path passes)
- **Status:** PASS_WITH_ISSUES
- **Follow-up:** Fix major issues in next sprint
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Testing only happy path | Test failures, edge cases |
| Relying on unit tests only | Browser tests reveal integration issues |
| Not testing actual behavior | Run real flows, not mocks |
| Missing performance tests | Measure actual load times |
| Skipping accessibility | Test with screen readers |
| No cross-browser testing | Test Chrome, Firefox, Safari |

## Related Skills

- `elenchus` — Code review (precedes Aletheia)
- `test-driven-development` — Core TDD methodology
- `requesting-code-review` — Review best practices

---

*Updated: 2026-04-06 — Sixth of 6 Role Agents (Greek Technical naming standard)*
