#!/usr/bin/env node
/**
 * Skill Path Resolver
 * 
 * Ensures skills can be found regardless of user workspace context.
 * This script returns absolute paths to skills for use in Discord commands.
 * 
 * Usage:
 *   node resolve-skill-path.js <skill-name> [script-name]
 * 
 * Examples:
 *   node resolve-skill-path.js ngrok tunnel-start.js
 *   // Returns: C:\Users\愛\.openclaw\workspace\skills\ngrok\scripts\tunnel-start.js
 */

const fs = require('fs');
const path = require('path');

// Skills directory is always at workspace root
const SKILLS_DIR = path.join(__dirname, '..', '..', '..', 'skills');

function resolveSkillPath(skillName, scriptName = null) {
  const skillPath = path.join(SKILLS_DIR, skillName);
  
  // Verify skill exists
  if (!fs.existsSync(skillPath)) {
    return { error: `Skill not found: ${skillName}` };
  }
  
  const skillFile = path.join(skillPath, 'SKILL.md');
  if (!fs.existsSync(skillFile)) {
    return { error: `Invalid skill (no SKILL.md): ${skillName}` };
  }
  
  if (scriptName) {
    // Check scripts directory
    const scriptsDir = path.join(skillPath, 'scripts');
    const scriptPath = path.join(scriptsDir, scriptName);
    
    if (!fs.existsSync(scriptPath)) {
      return { error: `Script not found: ${scriptName} in ${skillName}` };
    }
    
    return {
      skill: skillName,
      script: scriptName,
      fullPath: scriptPath,
      relativePath: path.relative(process.cwd(), scriptPath)
    };
  }
  
  return {
    skill: skillName,
    path: skillPath,
    skillFile: skillFile
  };
}

function listSkills() {
  const skills = fs.readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name)
    .filter(name => {
      const skillFile = path.join(SKILLS_DIR, name, 'SKILL.md');
      return fs.existsSync(skillFile);
    });
  
  return skills;
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Available skills:');
    listSkills().forEach(skill => {
      console.log(`  - ${skill}`);
    });
    console.log('\nUsage: node resolve-skill-path.js <skill> [script]');
    return;
  }
  
  const [skillName, scriptName] = args;
  const result = resolveSkillPath(skillName, scriptName);
  
  if (result.error) {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }
  
  if (scriptName) {
    // Output just the full path for easy use in commands
    console.log(result.fullPath);
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
}

main();
