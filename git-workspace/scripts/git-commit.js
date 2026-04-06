#!/usr/bin/env node

/**
 * Git Commit Script for OpenClaw Skills
 * 
 * Automates: status check, staging, commit message formatting, commit
 * 
 * Usage:
 *   node git-commit.js --skill <name> --message "<description>"
 *   node git-commit.js --all --message "<description>"
 *   node git-commit.js --status
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPTS_ROOT = join(__dirname, '..');
const SKILLS_ROOT = join(SCRIPTS_ROOT, '..');

// Color codes
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
 * Check for common issues before committing
 */
function preflightChecks() {
  log(colors.blue, '\n🔍 Preflight checks...\n');
  
  // Check for stale index.lock
  const lockPath = join(SKILLS_ROOT, '.git', 'index.lock');
  if (existsSync(lockPath)) {
    log(colors.yellow, '⚠️  Stale index.lock found - removing...');
    try {
      execSync(`powershell -Command "Remove-Item '${lockPath}' -Force"`);
      log(colors.green, '✅ index.lock cleared\n');
    } catch (e) {
      log(colors.red, '❌ Failed to remove index.lock - close git processes and retry');
      process.exit(1);
    }
  }
  
  // Check git status
  try {
    const status = exec('git status --porcelain');
    if (!status.trim()) {
      log(colors.yellow, '⚠️  No changes to commit\n');
      return false;
    }
  } catch (e) {
    if (e.stderr?.includes('not a git repository')) {
      log(colors.red, '❌ Not in a git repository');
      process.exit(1);
    }
  }
  
  return true;
}

/**
 * Format commit message using Conventional Commits
 */
function formatCommitMessage(type, scope, description, body = null) {
  let message = `${type}(${scope}): ${description}`;
  if (body) {
    message += `\n\n${body}`;
  }
  return message;
}

/**
 * Stage files for commit
 */
function stageFiles(paths) {
  log(colors.blue, '\n📦 Staging files...');
  
  if (paths === 'all') {
    exec('git add -A');
    log(colors.green, '✅ All changes staged');
  } else if (Array.isArray(paths)) {
    paths.forEach(path => exec(`git add "${path}"`));
    log(colors.green, `✅ Staged ${paths.length} path(s)`);
  }
}

/**
 * Commit staged changes
 */
function commit(message) {
  log(colors.blue, '\n💾 Committing...');
  log(colors.cyan, `Message: ${message.split('\n')[0]}`);
  
  try {
    exec(`git commit -m "${message.replace(/"/g, '\\"')}"`);
    log(colors.green, '✅ Commit successful');
    return true;
  } catch (e) {
    if (e.stderr?.includes('nothing to commit')) {
      log(colors.yellow, '⚠️  Nothing to commit - working tree clean');
      return false;
    }
    throw e;
  }
}

/**
 * Show git status
 */
function showStatus(verbose = false) {
  log(colors.blue, '\n📊 Git Status\n');
  
  const short = exec('git status --short');
  const branch = exec('git branch --show-current').trim();
  
  log(colors.cyan, `Branch: ${branch}\n`);
  
  if (!short.trim()) {
    log(colors.green, 'Working tree clean ✅');
  } else {
    log(colors.yellow, 'Changes:\n');
    console.log(short);
  }
  
  if (verbose) {
    const aheadBehind = exec('git status --porcelain --branch');
    const match = aheadBehind.match(/## (\S+)\.\.\.(\S+)(?: \[(?:ahead|behind) (\d+)\])?/);
    if (match) {
      log(colors.cyan, `\nRemote: ${match[2]}`);
      if (match[4]) {
        log(colors.yellow, `Ahead by ${match[4]} commit(s)`);
      }
    }
  }
}

// CLI argument parsing
const args = process.argv.slice(2);
const skillFlag = args.indexOf('--skill');
const messageFlag = args.indexOf('--message');
const allFlag = args.indexOf('--all');
const statusFlag = args.indexOf('--status');
const helpFlag = args.indexOf('--help');

if (helpFlag !== -1 || args.length === 0) {
  log(colors.cyan, '\nGit Commit for OpenClaw Skills\n');
  log(colors.cyan, 'Usage:');
  log(colors.cyan, '  node git-commit.js --skill <name> --message "<description>"');
  log(colors.cyan, '  node git-commit.js --all --message "<description>"');
  log(colors.cyan, '  node git-commit.js --status [--verbose]');
  log(colors.cyan, '\nExamples:');
  log(colors.cyan, '  node git-commit.js --skill git-workspace --message "add commit automation"');
  log(colors.cyan, '  node git-commit.js --all --message "update docs"');
  log(colors.cyan, '  node git-commit.js --status --verbose');
  process.exit(0);
}

if (statusFlag !== -1) {
  const verbose = args.includes('--verbose');
  showStatus(verbose);
  process.exit(0);
}

if (skillFlag === -1 && allFlag === -1) {
  log(colors.red, '❌ Missing required argument: --skill <name> or --all');
  log(colors.cyan, 'Run with --help for usage');
  process.exit(1);
}

if (messageFlag === -1) {
  log(colors.red, '❌ Missing required argument: --message "<description>"');
  log(colors.cyan, 'Run with --help for usage');
  process.exit(1);
}

try {
  // Preflight checks
  const hasChanges = preflightChecks();
  if (!hasChanges) {
    process.exit(0);
  }
  
  // Stage files
  const skillName = skillFlag !== -1 ? args[skillFlag + 1] : null;
  const paths = allFlag !== -1 ? 'all' : [`${skillName}/`];
  stageFiles(paths);
  
  // Format commit message
  const message = args[messageFlag + 1];
  const type = 'feat'; // Default to feat, could be smarter
  const scope = skillName || 'workspace';
  const commitMessage = formatCommitMessage(type, scope, message);
  
  // Commit
  const success = commit(commitMessage);
  
  if (success) {
    log(colors.green, '\n✅ Commit complete!');
    log(colors.cyan, 'Next: git push origin main');
  }
  
} catch (e) {
  log(colors.red, '\n❌ Git operation failed');
  log(colors.red, `Command: ${e.command}`);
  log(colors.red, `Error: ${e.message}`);
  if (e.stderr) {
    log(colors.red, `Details: ${e.stderr}`);
  }
  process.exit(1);
}
