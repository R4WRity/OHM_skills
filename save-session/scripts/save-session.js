#!/usr/bin/env node
/**
 * Save-Session Skill Implementation
 * Saves current conversation session to docs/saved-session.md
 */

const fs = require('fs');
const path = require('path');

function getCurrentDateTime() {
  const now = new Date();
  return now.toISOString().replace('T', ' ').split('.')[0] + ' PST';
}

function getTodayFile() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}.md`;
}

const note = process.argv[2] || '';

const sessionTemplate = `# Saved Session
*Saved: ${getCurrentDateTime()}*

## Session Context Snapshot

**Active User:** Set (∅) — users/Set/  
**Today:** ${getTodayFile()}  
**Current Directory:** C:\\AI\\_BOT\\.openclaw\\workspace  

## Conversation Summary
<!-- Agent: Summarize the key discussion points here -->

${note ? `**User Note:** ${note}\n\n` : ''}## Recent Actions
- Ngrok Discord skill created with /tunnel, /tunnel_stop, /tunnel_status commands
- Baltimore wedding trip dashboard website built (baltimore-trip/index.html)
- Trip docs updated with current flight pricing and status

## Active Projects
1. **Ngrok Tunnel Skill** — Discord commands ready for testing
2. **Baltimore Trip Planning** — Dashboard created, need to book flights

## Decisions Made
- Ngrok skill uses witty subdomain generation based on folder type
- Single tunnel at a time (Hobbyist plan)
- Trip dashboard includes budget calculator and action items

## Next Steps / TODO
- [ ] Test /tunnel command from Discord with baltimore-trip folder
- [ ] Book Lynn's flight (wedding party priority)
- [ ] Book Alex's flight (Fort Smith → Baltimore)
- [ ] Confirm Sigma's surgery status
- [ ] Decide on kids' travel method (road trip likely)

## Files Created/Modified
- skills/ngrok/scripts/tunnel-start.js — Discord /tunnel command
- skills/ngrok/scripts/tunnel-stop.js — Discord /tunnel_stop command
- skills/ngrok/scripts/tunnel-status.js — Discord /tunnel_status command
- baltimore-trip/index.html — Trip dashboard website
- docs/wedding-trip-baltimore-aug2025.md — Updated status
- docs/trip-planning-baltimore-wedding-aug2025.md — Updated with website link

## Memory References
- Daily memory: users/Set/memory/${getTodayFile()}
- User config: users/Set/AGENTS.md, users/Set/USER.md

---
**Restored:** false  
*Load this session with: /load-session*
`;

const workspaceRoot = process.env.OPENCLAW_WORKSPACE || process.cwd();
const savePath = path.join(workspaceRoot, 'docs', 'saved-session.md');

// Ensure docs directory exists
const docsDir = path.dirname(savePath);
if (!fs.existsSync(docsDir)) {
  fs.mkdirSync(docsDir, { recursive: true });
}

// Write the session file
fs.writeFileSync(savePath, sessionTemplate, 'utf8');

console.log('✅ Session saved');
console.log(`📁 Location: docs/saved-session.md`);
console.log(`⏰ Time: ${getCurrentDateTime()}`);
console.log(`📝 Content: Summary | Decisions | Next Steps`);
console.log('');
console.log('@reference docs/saved-session.md');
