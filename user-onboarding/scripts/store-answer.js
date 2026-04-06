#!/usr/bin/env node
/**
 * Store Onboarding Answer
 * 
 * Usage:
 *   node store-answer.js [category] [storage_key] [type] "answer text"
 * 
 * Example:
 *   node store-answer.js food cuisine_preferences preference "I love sushi"
 */

const { execSync } = require('child_path');
const path = require('path');

// User mapping
const USER_MAP = {
  '85131474184986624': { name: 'rawrity', port: 9001 },
  '296511082745298944': { name: 'sigma', port: 9002 },
};

function getCurrentUser() {
  const discordUserId = process.env.DISCORD_USER_ID || process.env.USER_ID;
  return USER_MAP[discordUserId] || USER_MAP['85131474184986624'];
}

function storeAnswer(port, category, storageKey, type, answer) {
  const scriptPath = path.join(__dirname, '..', 'scripts', 'store_answer.py');
  
  try {
    const result = execSync(
      `python "${scriptPath}" --port ${port} --category "${category}" --key "${storageKey}" --type "${type}" --answer "${answer}"`,
      { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }
    );
    return { success: true, output: result.trim() };
  } catch (e) {
    return { success: false, error: e.stderr || e.message };
  }
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 4) {
    console.log('Usage: node store-answer.js [category] [storage_key] [type] "answer"');
    console.log('  type: personal_info | preference | memory | goal | relationship');
    process.exit(1);
  }
  
  const [category, storageKey, type, ...answerParts] = args;
  const answer = answerParts.join(' ');
  
  const user = getCurrentUser();
  const result = storeAnswer(user.port, category, storageKey, type, answer);
  
  if (result.success) {
    console.log('✅ Answer saved to your memory.');
  } else {
    console.log('❌ Failed to save:', result.error);
  }
}

main();
