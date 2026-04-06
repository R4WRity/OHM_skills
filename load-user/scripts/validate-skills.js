#!/usr/bin/env node
/**
 * Skill Propagation Validator
 * 
 * Ensures skills are accessible after loading a user workspace.
 * Run this after /load-user to verify skill paths and provide
 * working commands for the current user context.
 * 
 * This solves the issue where skills like /tunnel aren't available
 * after switching to a user workspace.
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE_ROOT = path.join(__dirname, '..', '..', '..');
const SKILLS_DIR = path.join(WORKSPACE_ROOT, 'skills');

// Alternative: resolve from current file location
const SKILLS_DIR_ALT = path.resolve(__dirname, '..', '..', '..', 'skills');

// Known Discord commands from skills
const SKILL_COMMANDS = {
  'ngrok': [
    { name: '/tunnel', script: 'tunnel-start.js', args: '<folder>' },
    { name: '/tunnel_stop', script: 'tunnel-stop.js', args: '' },
    { name: '/tunnel_status', script: 'tunnel-status.js', args: '' }
  ],
  'user-onboarding': [
    { name: '/onboard', script: 'onboard.js', args: '[mode|category]' },
    { name: '/onboard quick', script: 'onboard.js', args: '' },
    { name: '/onboard full', script: 'onboard.js', args: '' },
    { name: '/onboard custom', script: 'onboard.js', args: '' }
  ],
  'load-session': [
    { name: '/load-session', internal: true, description: 'Restores saved session from docs/saved-session.md' }
  ],
  'save-session': [
    { name: '/save-session', internal: true, description: 'Saves current session to docs/saved-session.md' }
  ],
  'discord-user-bridge': [
    { name: '/send-to [user]', internal: true, description: 'Send message to another user channel' }
  ]
};

function getSkillPath(skillName) {
  return path.join(SKILLS_DIR, skillName);
}

function getScriptPath(skillName, scriptName) {
  return path.join(SKILLS_DIR, skillName, 'scripts', scriptName);
}

function validateSkill(skillName) {
  const skillPath = getSkillPath(skillName);
  const skillFile = path.join(skillPath, 'SKILL.md');
  
  if (!fs.existsSync(skillFile)) {
    return { valid: false, error: 'Missing SKILL.md' };
  }
  
  const commands = SKILL_COMMANDS[skillName] || [];
  const validatedCommands = commands.map(cmd => {
    if (cmd.internal) {
      return { ...cmd, valid: true, path: null };
    }
    
    const scriptPath = getScriptPath(skillName, cmd.script);
    const exists = fs.existsSync(scriptPath);
    
    return {
      ...cmd,
      valid: exists,
      fullPath: scriptPath,
      execCommand: exists ? `node "${scriptPath}"` : null
    };
  });
  
  return {
    valid: true,
    name: skillName,
    path: skillPath,
    commands: validatedCommands
  };
}

function listAllSkills() {
  return fs.readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)
    .filter(name => fs.existsSync(path.join(SKILLS_DIR, name, 'SKILL.md')));
}

function generateSkillAliases(userName) {
  const skills = listAllSkills();
  const aliases = [];
  
  for (const skillName of skills) {
    const validation = validateSkill(skillName);
    if (!validation.valid) continue;
    
    for (const cmd of validation.commands) {
      if (cmd.internal || !cmd.valid) continue;
      
      // Generate alias that works from any context
      const aliasCmd = cmd.args 
        ? `${cmd.name.replace(/\[.*?\]/g, '')}{${cmd.args}}`
        : cmd.name;
      
      aliases.push({
        command: cmd.name,
        script: cmd.script,
        fullPath: cmd.fullPath,
        user: userName,
        working: `node "${cmd.fullPath}"${cmd.args ? ' ' + cmd.args : ''}`
      });
    }
  }
  
  return aliases;
}

function main() {
  const userName = process.argv[2] || 'current';
  const mode = process.argv[3] || 'summary';
  
  if (mode === 'aliases') {
    // Output just the aliases for shell integration
    const aliases = generateSkillAliases(userName);
    console.log(JSON.stringify(aliases, null, 2));
    return;
  }
  
  if (mode === 'validate') {
    // Validate all skills
    const skills = listAllSkills();
    let allValid = true;
    
    console.log(`🔍 Validating skills for user: ${userName}\n`);
    
    for (const skillName of skills) {
      const validation = validateSkill(skillName);
      
      if (!validation.valid) {
        console.log(`❌ ${skillName}: ${validation.error}`);
        allValid = false;
        continue;
      }
      
      console.log(`✅ ${skillName}`);
      
      for (const cmd of validation.commands) {
        if (cmd.internal) {
          console.log(`   ℹ️  ${cmd.name}: ${cmd.description}`);
        } else if (cmd.valid) {
          console.log(`   ✅ ${cmd.name} → ${cmd.script}`);
        } else {
          console.log(`   ❌ ${cmd.name} → script not found`);
          allValid = false;
        }
      }
    }
    
    console.log(`\n${allValid ? '✅ All skills validated' : '⚠️ Some skills have issues'}`);
    return;
  }
  
  // Default: summary with working directory info
  console.log(`📦 Skill Propagation Report for: ${userName}\n`);
  console.log(`Workspace root: ${WORKSPACE_ROOT}`);
  console.log(`Skills directory: ${SKILLS_DIR}\n`);
  
  const skills = listAllSkills();
  console.log(`Found ${skills.length} skills:\n`);
  
  for (const skillName of skills) {
    const validation = validateSkill(skillName);
    
    if (!validation.valid) {
      console.log(`❌ ${skillName}: ${validation.error}\n`);
      continue;
    }
    
    console.log(`📁 ${skillName}/`);
    
    for (const cmd of validation.commands) {
      if (cmd.internal) {
        console.log(`   ${cmd.name} (built-in)`);
      } else if (cmd.valid) {
        // Show the command that works regardless of current directory
        console.log(`   ${cmd.name}`);
        console.log(`      → node "${cmd.fullPath}"${cmd.args ? ' ' + cmd.args : ''}`);
      } else {
        console.log(`   ${cmd.name} (⚠️ script missing)`);
      }
    }
    console.log();
  }
  
  console.log('='.repeat(60));
  console.log('💡 Usage from any user workspace:\n');
  console.log('All skill scripts use absolute paths, so they work');
  console.log('regardless of which user context is loaded.\n');
  console.log('Example:');
  console.log('  @exec node "C:/Users/愛/.openclaw/workspace/skills/ngrok/scripts/tunnel-start.js" portfolio');
  console.log('\nOr simply use the Discord commands:');
  console.log('  /tunnel portfolio');
  console.log('  /tunnel_stop');
}

main();
