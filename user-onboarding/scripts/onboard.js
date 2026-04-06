#!/usr/bin/env node
/**
 * Onboard Command for Discord/OpenClaw
 * 
 * Usage:
 *   /onboard              - Start quick onboarding (5 questions)
 *   /onboard quick        - Same as above
 *   /onboard full         - Comprehensive onboarding (all categories)
 *   /onboard custom       - Ask for specific categories
 *   /onboard [category]   - One question from specific category
 * 
 * Examples:
 *   /onboard food         - Ask a food preference question
 *   /onboard travel       - Ask a travel question
 *   /onboard goals        - Ask about goals
 */

const { execSync } = require('child_process');
const path = require('path');

// User mapping (Discord ID -> user config)
const USER_MAP = {
  '85131474184986624': { name: 'rawrity', port: 9001, container: 'memory-rawrity' },
  '296511082745298944': { name: 'sigma', port: 9002, container: 'memory-sigma' },
};

// Get user from environment (set by OpenClaw)
function getCurrentUser() {
  const discordUserId = process.env.DISCORD_USER_ID || process.env.USER_ID;
  if (!discordUserId) {
    // Default to rawrity for testing
    return USER_MAP['85131474184986624'];
  }
  return USER_MAP[discordUserId];
}

// Check MCP server health
function checkMCP(port) {
  try {
    execSync(`curl -s http://localhost:${port}/health >nul 2>&1`, { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

// Start MCP container if needed
function startMCP(container) {
  try {
    const composeFile = path.join(__dirname, '..', '..', '..', 'projects', 'personal-memory-mcp-docker', 'docker-compose.yml');
    execSync(`docker-compose -f "${composeFile}" up -d ${container}`, { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

// Get a question using the Python backend
function getQuestion(port, category = null, mode = 'single') {
  const scriptPath = path.join(__dirname, '..', 'scripts', 'onboard_bot.py');
  const args = category ? `--category ${category}` : mode === 'flow' ? '--flow 1' : '--random';
  
  try {
    const result = execSync(
      `python "${scriptPath}" ${args} --port ${port}`,
      { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }
    );
    return result.trim();
  } catch (e) {
    return null;
  }
}

// Get categories list
function getCategories() {
  const scriptPath = path.join(__dirname, '..', 'scripts', 'onboard_bot.py');
  try {
    const result = execSync(
      `python "${scriptPath}" --categories`,
      { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }
    );
    return result.trim();
  } catch (e) {
    return null;
  }
}

// Main execution
function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'quick';
  
  const user = getCurrentUser();
  if (!user) {
    console.log('❌ Unknown user. Cannot start onboarding.');
    process.exit(1);
  }

  // Check MCP server
  let mcpStatus = checkMCP(user.port) ? '✅ Running' : '⚠️ Not running';
  
  if (!checkMCP(user.port)) {
    console.log(`🔌 MCP Server: ${mcpStatus}`);
    console.log(`   Attempting to start ${user.container}...`);
    if (startMCP(user.container)) {
      // Wait a moment for startup
      setTimeout(() => {}, 2000);
      mcpStatus = checkMCP(user.port) ? '✅ Started' : '❌ Failed to start';
    }
  }
  
  console.log(`🔌 MCP Server: ${mcpStatus} (port ${user.port})`);
  
  if (!checkMCP(user.port)) {
    console.log('\n❌ Cannot start onboarding — MCP server is not available.');
    console.log(`   Run: docker-compose up -d ${user.container}`);
    process.exit(1);
  }

  // Handle different modes
  switch (mode) {
    case 'quick':
      console.log('\n🚀 Starting QUICK onboarding (5 essential questions)');
      console.log('='.repeat(50));
      console.log('\nI\'ll ask you 5 questions one at a time.');
      console.log('Reply with your answer, or type "skip" to move on.\n');
      console.log('Starting with question 1...\n');
      
      // Get first question from identity category
      const q1 = getQuestion(user.port, 'identity');
      if (q1) {
        console.log(q1);
        console.log('\n💡 Tip: After you answer, I\'ll continue with the next question.');
      } else {
        console.log('❌ Could not load questions. Check the skill installation.');
      }
      break;
      
    case 'full':
      console.log('\n📚 Starting FULL onboarding (comprehensive — takes ~10-15 min)');
      console.log('='.repeat(50));
      console.log('\nThis will cover all categories:');
      console.log('  • Identity, Food, Entertainment, Professional');
      console.log('  • Travel, Lifestyle, Relationships, Goals');
      console.log('  • Preferences, Quirks, Tech\n');
      console.log('Type "done" anytime to finish early.\n');
      console.log('Starting...\n');
      
      const fq = getQuestion(user.port, 'identity');
      if (fq) {
        console.log(fq);
      }
      break;
      
    case 'custom':
      console.log('\n🎯 CUSTOM onboarding — Choose your categories');
      console.log('='.repeat(50));
      console.log('\nAvailable categories:');
      console.log(getCategories());
      console.log('\nTo start, reply with categories you want (space-separated):');
      console.log('Example: `/onboard food travel goals`\n');
      break;
      
    case 'categories':
    case 'list':
      console.log('\n📋 Available onboarding categories:\n');
      console.log(getCategories());
      console.log('\nUsage: `/onboard [category]` for a single question');
      console.log('       `/onboard quick` for 5 essential questions');
      console.log('       `/onboard full` for comprehensive onboarding');
      break;
      
    default:
      // Treat as category name
      const category = mode.toLowerCase();
      console.log(`\n🎲 Random question from: ${category}\n`);
      const q = getQuestion(user.port, category);
      if (q) {
        console.log(q);
        console.log('\n💡 Reply with your answer and I\'ll save it to your memory.');
      } else {
        console.log(`❌ Unknown category: ${category}`);
        console.log('Run `/onboard categories` to see available options.');
      }
  }
}

main();
