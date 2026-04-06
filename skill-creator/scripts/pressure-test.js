#!/usr/bin/env node

/**
 * Pressure Test Harness for Skill Creation
 * 
 * Implements RED-GREEN-REFACTOR cycle for skill documentation.
 * 
 * Usage:
 *   node pressure-test.js --scenario <name>           # Run baseline test
 *   node pressure-test.js --full-cycle --skill <name> # Full TDD cycle
 *   node pressure-test.js --list                      # List available scenarios
 */

import { spawn } from 'child_process';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILLS_ROOT = join(__dirname, '..');
const SCENARIOS_DIR = join(__dirname, 'scenarios');

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(color, message) {
  console.log(`${color}${message}${colors.reset}`);
}

/**
 * Available pressure test scenarios
 * Each scenario defines a task that should trigger specific skill compliance
 */
const scenarios = {
  'async-test-skill': {
    description: 'Create a skill for handling async/flaky tests',
    task: 'Create a skill for handling asynchronous tests that fail intermittently due to timing issues',
    expectedBehaviors: [
      'Should write test cases BEFORE writing skill content',
      'Should document baseline failure modes',
      'Should use RED-GREEN-REFACTOR cycle',
    ],
    commonViolations: [
      'Writes skill immediately without baseline test',
      'Rationalizes: "Tests aren\'t needed for documentation"',
      'Skips the RED phase entirely',
    ],
  },
  'git-workflow-skill': {
    description: 'Create a skill for git workflow automation',
    task: 'Create a skill that handles git commit/push workflows with proper messaging',
    expectedBehaviors: [
      'Should validate commit message format',
      'Should check for .gitignore before committing',
      'Should handle authentication errors gracefully',
    ],
    commonViolations: [
      'Commits without checking .gitignore',
      'Uses vague commit messages like "update" or "fix"',
      'Doesn\'t handle auth errors, just fails',
    ],
  },
  'debugging-skill': {
    description: 'Create a skill for systematic debugging',
    task: 'Create a skill for debugging production issues with a systematic approach',
    expectedBehaviors: [
      'Should follow reproduce → isolate → fix → verify cycle',
      'Should document root cause, not just symptoms',
      'Should add regression tests',
    ],
    commonViolations: [
      'Jumps to solutions without reproducing',
      'Fixes symptoms, not root cause',
      'No verification step',
    ],
  },
};

/**
 * Spawn a subagent with the given task
 * Returns the agent's output for analysis
 */
async function spawnSubagent(task, options = {}) {
  const { 
    includeSkill = false, 
    skillName = null,
    timeoutMs = 300000 // 5 minutes
  } = options;

  log(colors.blue, '\n🤖 Spawning subagent...');
  log(colors.cyan, `Task: ${task}`);
  log(colors.cyan, `Include skill: ${includeSkill ? skillName : 'NO'}`);
  
  // This would integrate with OpenClaw's subagent system
  // For now, we'll simulate with a placeholder
  // TODO: Integrate with sessions_spawn tool
  
  return new Promise((resolve) => {
    log(colors.yellow, '\n⚠️  Subagent integration not yet implemented');
    log(colors.yellow, 'Manual mode: Run this task in a new OpenClaw session');
    
    const output = {
      success: false,
      output: '[MANUAL MODE - Run task manually and paste output]',
      violations: [],
      rationalizations: [],
    };
    
    resolve(output);
  });
}

/**
 * Analyze agent output for violations
 */
function analyzeViolations(output, scenario) {
  const violations = [];
  const rationalizations = [];
  
  log(colors.yellow, '\n🔍 Analyzing for violations...');
  
  // Check for common violations
  for (const violation of scenario.commonViolations) {
    if (output.toLowerCase().includes(violation.toLowerCase())) {
      violations.push(violation);
    }
  }
  
  // Extract rationalizations (agent justifications)
  const rationalizationPatterns = [
    /because/i,
    /therefore/i,
    /i think/i,
    /it's not necessary/i,
    /we don't need/i,
    /this is different/i,
  ];
  
  rationalizationPatterns.forEach(pattern => {
    const matches = output.match(new RegExp(pattern, 'gi'));
    if (matches) {
      rationalizations.push(...matches);
    }
  });
  
  return { violations, rationalizations };
}

/**
 * Save baseline test results
 */
function saveBaseline(scenarioName, results) {
  const baselinePath = join(SCENARIOS_DIR, scenarioName, 'baseline.json');
  
  if (!existsSync(dirname(baselinePath))) {
    mkdirSync(dirname(baselinePath), { recursive: true });
  }
  
  writeFileSync(baselinePath, JSON.stringify(results, null, 2));
  log(colors.green, `\n💾 Baseline saved: ${baselinePath}`);
}

/**
 * Run RED phase (baseline test)
 */
async function runRedPhase(scenarioName) {
  const scenario = scenarios[scenarioName];
  if (!scenario) {
    log(colors.red, `❌ Scenario not found: ${scenarioName}`);
    log(colors.yellow, 'Available scenarios:', Object.keys(scenarios).join(', '));
    return null;
  }
  
  log(colors.red, '\n╔════════════════════════════════════════╗');
  log(colors.red, '║  PHASE 1: RED (Baseline Test)          ║');
  log(colors.red, '╚════════════════════════════════════════╝\n');
  
  log(colors.cyan, 'Scenario:', scenario.description);
  log(colors.cyan, 'Expected: Agent should follow TDD cycle\n');
  
  const output = await spawnSubagent(scenario.task, { includeSkill: false });
  const analysis = analyzeViolations(output.output, scenario);
  
  const baseline = {
    scenario: scenarioName,
    timestamp: new Date().toISOString(),
    output: output.output,
    violations: analysis.violations,
    rationalizations: analysis.rationalizations,
    passed: analysis.violations.length === 0,
  };
  
  if (baseline.passed) {
    log(colors.green, '\n✅ Baseline PASSED - Agent already complies!');
    log(colors.yellow, 'Note: This is unusual. Consider if the test is strict enough.');
  } else {
    log(colors.red, '\n❌ Baseline FAILED - Violations found:');
    baseline.violations.forEach((v, i) => log(colors.red, `  ${i + 1}. ${v}`));
    
    if (analysis.rationalizations.length > 0) {
      log(colors.yellow, '\nRationalizations used:');
      analysis.rationalizations.forEach(r => log(colors.yellow, `  - ${r}`));
    }
  }
  
  saveBaseline(scenarioName, baseline);
  return baseline;
}

/**
 * Run GREEN phase (write skill, test with skill)
 */
async function runGreenPhase(scenarioName, baseline) {
  log(colors.green, '\n╔════════════════════════════════════════╗');
  log(colors.green, '║  PHASE 2: GREEN (Write & Test Skill)   ║');
  log(colors.green, '╚════════════════════════════════════════╝\n');
  
  log(colors.yellow, '📝 Step 1: Write the skill');
  log(colors.cyan, 'Create: skills/<skill-name>/SKILL.md');
  log(colors.cyan, 'Address these violations:');
  baseline.violations.forEach((v, i) => log(colors.cyan, `  ${i + 1}. ${v}`));
  
  log(colors.yellow, '\n💡 Step 2: Test with skill included');
  log(colors.cyan, 'Run the same task with the skill present');
  
  // TODO: Implement skill testing
  log(colors.yellow, '\n⚠️  Skill testing not yet implemented');
  log(colors.yellow, 'Manual: Create skill, then run task again with skill loaded');
}

/**
 * Run full TDD cycle
 */
async function runFullCycle(scenarioName) {
  log(colors.cyan, '\n╔════════════════════════════════════════╗');
  log(colors.cyan, '║  TDD Cycle for Skill Creation          ║');
  log(colors.cyan, '╚════════════════════════════════════════╝\n');
  
  const baseline = await runRedPhase(scenarioName);
  if (!baseline) return;
  
  if (baseline.passed) {
    log(colors.green, '\n✅ No baseline violations - skill may not be needed');
    return;
  }
  
  await runGreenPhase(scenarioName, baseline);
  
  log(colors.cyan, '\n╔════════════════════════════════════════╗');
  log(colors.cyan, '║  PHASE 3: REFACTOR (Close Loopholes)   ║');
  log(colors.cyan, '╚════════════════════════════════════════╝\n');
  
  log(colors.yellow, 'After testing, refine the skill:');
  log(colors.cyan, '1. Find new rationalizations');
  log(colors.cyan, '2. Update skill to address them');
  log(colors.cyan, '3. Re-test to ensure compliance');
  log(colors.cyan, '4. Repeat until robust\n');
}

/**
 * List available scenarios
 */
function listScenarios() {
  log(colors.cyan, '\nAvailable pressure test scenarios:\n');
  
  Object.entries(scenarios).forEach(([name, scenario]) => {
    log(colors.green, `  ${name}`);
    log(colors.cyan, `    ${scenario.description}\n`);
  });
}

// CLI argument parsing
const args = process.argv.slice(2);
const scenarioFlag = args.indexOf('--scenario');
const fullCycleFlag = args.indexOf('--full-cycle');
const listFlag = args.indexOf('--list');
const skillFlag = args.indexOf('--skill');

if (listFlag !== -1 || args.length === 0) {
  listScenarios();
} else if (scenarioFlag !== -1) {
  const scenarioName = args[scenarioFlag + 1];
  if (fullCycleFlag !== -1) {
    runFullCycle(scenarioName);
  } else {
    runRedPhase(scenarioName);
  }
} else {
  log(colors.red, '❌ Invalid arguments');
  log(colors.cyan, 'Usage:');
  log(colors.cyan, '  node pressure-test.js --list');
  log(colors.cyan, '  node pressure-test.js --scenario <name>');
  log(colors.cyan, '  node pressure-test.js --full-cycle --scenario <name>');
}
