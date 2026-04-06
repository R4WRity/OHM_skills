#!/usr/bin/env node
/**
 * Load-Session Skill Implementation
 * Loads saved session from docs/saved-session.md
 */

const fs = require('fs');
const path = require('path');

const workspaceRoot = process.env.OPENCLAW_WORKSPACE || process.cwd();
const loadPath = path.join(workspaceRoot, 'docs', 'saved-session.md');
const activeSessionPath = path.join(workspaceRoot, 'docs', 'active-session.md');

// Check if saved session exists
if (!fs.existsSync(loadPath)) {
  console.error('❌ No saved session found');
  console.error('📁 Expected: docs/saved-session.md');
  console.error('💡 Run /save-session first');
  process.exit(1);
}

// Read the saved session
const sessionContent = fs.readFileSync(loadPath, 'utf8');

// Extract timestamp from the file
const timestampMatch = sessionContent.match(/Saved: (.+?)$/m);
const savedAt = timestampMatch ? timestampMatch[1] : 'unknown';

// Mark as restored
const restoredContent = sessionContent.replace(
  /\*\*Restored:\*\* false/,
  '**Restored:** true (just now)'
);

// Also save to active-session.md
fs.writeFileSync(activeSessionPath, restoredContent, 'utf8');
fs.writeFileSync(loadPath, restoredContent, 'utf8');

console.log('✅ Session loaded');
console.log(`📁 Source: docs/saved-session.md`);
console.log(`⏰ Saved: ${savedAt}`);
console.log('📝 Restored: Summary | Projects | Next Steps');
console.log('');
console.log('@reference docs/saved-session.md');
console.log('');
console.log('---');
console.log('Session content restored. Ready to continue.');
