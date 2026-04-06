#!/usr/bin/env node

/**
 * Git Push Script for OpenClaw Skills
 * 
 * Automates: push to remote, confirmation, auth handling
 * 
 * Usage:
 *   node git-push.js [--branch <name>] [--timeout <ms>]
 */

import { execSync } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILLS_ROOT = join(__dirname, '..');

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

function exec(command, options = {}) {
  try {
    return execSync(command, { 
      cwd: SKILLS_ROOT, 
      encoding: 'utf8',
      stdio: 'pipe',
      ...options 
    });
  } catch (error) {
    throw {
      command,
      message: error.message,
      stderr: error.stderr?.toString(),
      stdout: error.stdout?.toString(),
    };
  }
}

/**
 * Get current branch
 */
function getCurrentBranch() {
  return exec('git branch --show-current').trim();
}

/**
 * Check if remote exists
 */
function remoteExists(remote = 'origin') {
  try {
    const remotes = exec(`git remote -v`);
    return remotes.includes(remote);
  } catch {
    return false;
  }
}

/**
 * Push to remote with timeout and confirmation
 */
function push(branch, remote = 'origin', timeoutMs = 30000) {
  log(colors.blue, `\n🚀 Pushing to ${remote}/${branch}...`);
  
  // Check remote exists
  if (!remoteExists(remote)) {
    log(colors.red, `❌ Remote '${remote}' not found`);
    log(colors.yellow, 'Add remote: git remote add origin <url>');
    return false;
  }
  
  // Push with timeout
  try {
    log(colors.cyan, `Timeout: ${timeoutMs / 1000}s`);
    const result = exec(`git push -u ${remote} ${branch}`, { 
      timeout: timeoutMs / 1000 
    });
    
    log(colors.green, '\n✅ Push successful!');
    
    // Confirm remote updated
    const status = exec('git status --porcelain --branch');
    const match = status.match(/## (\S+)\.\.\.(\S+)/);
    if (match && match[2]) {
      log(colors.green, `Remote: ${match[2]} is up to date`);
    }
    
    return true;
    
  } catch (e) {
    if (e.message.includes('timed out')) {
      log(colors.red, '\n❌ Push timed out - likely waiting for authentication');
      log(colors.yellow, '\nFix:');
      log(colors.cyan, '1. Generate GitHub token: https://github.com/settings/tokens');
      log(colors.cyan, '2. Use token as password when prompted');
      log(colors.cyan, '3. Or configure credential helper: git config --global credential.helper wincred');
    } else if (e.stderr?.includes('Authentication failed')) {
      log(colors.red, '\n❌ Authentication failed');
      log(colors.yellow, '\nFix:');
      log(colors.cyan, '1. Check token is valid');
      log(colors.cyan, '2. Regenerate if needed');
      log(colors.cyan, '3. Update stored credentials in Windows Credential Manager');
    } else if (e.stderr?.includes('doesn\'t match')) {
      log(colors.yellow, '\n⚠️  Branch not tracking remote');
      log(colors.cyan, 'Setting upstream...');
      try {
        exec(`git push -u ${remote} ${branch}`);
        log(colors.green, '✅ Upstream set and pushed');
        return true;
      } catch (e2) {
        log(colors.red, '❌ Failed to set upstream');
        throw e2;
      }
    } else {
      log(colors.red, '\n❌ Push failed');
      log(colors.red, `Error: ${e.message}`);
      if (e.stderr) {
        log(colors.red, `Details: ${e.stderr}`);
      }
    }
    return false;
  }
}

// CLI argument parsing
const args = process.argv.slice(2);
const branchFlag = args.indexOf('--branch');
const timeoutFlag = args.indexOf('--timeout');
const helpFlag = args.indexOf('--help');

if (helpFlag !== -1 || args.length === 0) {
  log(colors.cyan, '\nGit Push for OpenClaw Skills\n');
  log(colors.cyan, 'Usage:');
  log(colors.cyan, '  node git-push.js [--branch <name>] [--timeout <ms>]');
  log(colors.cyan, '\nOptions:');
  log(colors.cyan, '  --branch <name>  Push to specific branch (default: current)');
  log(colors.cyan, '  --timeout <ms>   Timeout in ms (default: 30000)');
  log(colors.cyan, '\nExamples:');
  log(colors.cyan, '  node git-push.js');
  log(colors.cyan, '  node git-push.js --branch skill/my-skill');
  log(colors.cyan, '  node git-push.js --timeout 60000');
  process.exit(0);
}

try {
  const branch = branchFlag !== -1 ? args[branchFlag + 1] : getCurrentBranch();
  const timeout = timeoutFlag !== -1 ? parseInt(args[timeoutFlag + 1]) : 30000;
  
  if (!branch) {
    log(colors.red, '❌ Could not determine branch');
    log(colors.yellow, 'Specify with --branch <name>');
    process.exit(1);
  }
  
  const success = push(branch, 'origin', timeout);
  process.exit(success ? 0 : 1);
  
} catch (e) {
  log(colors.red, '\n❌ Push operation failed');
  log(colors.red, `Error: ${e.message}`);
  if (e.stderr) {
    log(colors.red, `Details: ${e.stderr}`);
  }
  process.exit(1);
}
