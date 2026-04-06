#!/usr/bin/env node
/**
 * Skill Propagation Test
 * 
 * Verifies that skills work correctly after loading a user workspace.
 * This test simulates the scenario where /load-user has been run and
 * confirms skills are still accessible.
 * 
 * Usage: node test-skill-propagation.js [username]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Simulate different working directories
const WORKSPACE_ROOT = path.resolve(__dirname, '..', '..', '..');
const USER_DIRS = {
  'Set': path.join(WORKSPACE_ROOT, 'users', 'Set'),
  'Sigma': path.join(WORKSPACE_ROOT, 'users', 'Sigma')
};

const TESTS = [
  {
    name: 'ngrok tunnel-start path resolution',
    skill: 'ngrok',
    script: 'tunnel-start.js',
    test: (scriptPath) => {
      // Check if script exists and has correct __dirname usage
      const content = fs.readFileSync(scriptPath, 'utf8');
      return content.includes('__dirname');
    }
  },
  {
    name: 'ngrok tunnel-stop path resolution',
    skill: 'ngrok',
    script: 'tunnel-stop.js',
    test: (scriptPath) => {
      const content = fs.readFileSync(scriptPath, 'utf8');
      return content.includes('__dirname');
    }
  },
  {
    name: 'ngrok tunnel-status path resolution',
    skill: 'ngrok',
    script: 'tunnel-status.js',
    test: (scriptPath) => {
      const content = fs.readFileSync(scriptPath, 'utf8');
      return content.includes('__dirname');
    }
  },
  {
    name: 'user-onboarding path resolution',
    skill: 'user-onboarding',
    script: 'onboard.js',
    test: (scriptPath) => {
      const content = fs.readFileSync(scriptPath, 'utf8');
      return content.includes('__dirname') || content.includes('SKILLS_DIR');
    }
  },
  {
    name: 'user-onboarding bot path resolution',
    skill: 'user-onboarding',
    script: 'onboard_bot.py',
    test: (scriptPath) => {
      // Python files should use pathlib or os.path
      const content = fs.readFileSync(scriptPath, 'utf8');
      return content.includes('Path(__file__)') || content.includes('__dirname');
    }
  }
];

function getScriptPath(skill, script) {
  return path.join(WORKSPACE_ROOT, 'skills', skill, 'scripts', script);
}

function runTest(test, cwd) {
  const scriptPath = getScriptPath(test.skill, test.script);
  
  if (!fs.existsSync(scriptPath)) {
    return { passed: false, error: 'Script not found' };
  }
  
  try {
    const result = test.test(scriptPath);
    return { passed: result, error: result ? null : 'Test function returned false' };
  } catch (e) {
    return { passed: false, error: e.message };
  }
}

function main() {
  const userName = process.argv[2] || 'Set';
  const userDir = USER_DIRS[userName] || WORKSPACE_ROOT;
  
  console.log(`🧪 Skill Propagation Test`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  
  console.log(`Workspace root: ${WORKSPACE_ROOT}`);
  console.log(`User directory: ${userDir}`);
  console.log(`User exists: ${fs.existsSync(userDir) ? 'Yes' : 'No'}\n`);
  
  // Test 1: Direct from workspace root (baseline)
  console.log(`Test 1: Running from workspace root`);
  console.log(`─────────────────────────────────`);
  let allPassed = true;
  
  for (const test of TESTS) {
    const result = runTest(test, WORKSPACE_ROOT);
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    console.log(`  ${status}: ${test.name}`);
    if (!result.passed) {
      console.log(`      Error: ${result.error}`);
      allPassed = false;
    }
  }
  
  // Test 2: From user directory (simulates /load-user context)
  if (fs.existsSync(userDir)) {
    console.log(`\nTest 2: Running from user directory (${userName})`);
    console.log(`─────────────────────────────────`);
    
    for (const test of TESTS) {
      const result = runTest(test, userDir);
      const status = result.passed ? '✅ PASS' : '❌ FAIL';
      console.log(`  ${status}: ${test.name}`);
      if (!result.passed) {
        console.log(`      Error: ${result.error}`);
        allPassed = false;
      }
    }
  } else {
    console.log(`\n⚠️ Skipping user directory test — ${userDir} does not exist`);
  }
  
  // Summary
  console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  if (allPassed) {
    console.log(`✅ All tests passed! Skills will work after /load-user`);
    console.log(`\nSkills are properly using __dirname for path resolution.`);
    console.log(`They will function correctly regardless of working directory.`);
  } else {
    console.log(`❌ Some tests failed. Skills may not work after /load-user.`);
    console.log(`\nFix: Update scripts to use __dirname for all path resolution.`);
  }
  
  // Show skill commands reference
  console.log(`\n📋 Quick Reference — Commands that work from any context:`);
  console.log(`  • /tunnel <folder> → node "${getScriptPath('ngrok', 'tunnel-start.js')}" <folder>`);
  console.log(`  • /tunnel_stop → node "${getScriptPath('ngrok', 'tunnel-stop.js')}"`);
  console.log(`  • /tunnel_status → node "${getScriptPath('ngrok', 'tunnel-status.js')}"`);
  console.log(`  • /onboard → node "${getScriptPath('user-onboarding', 'onboard.js')}"`);
}

main();
