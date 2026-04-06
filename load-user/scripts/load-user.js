#!/usr/bin/env node
/**
 * Load-User Skill Implementation
 * Loads user-specific workspace context for multi-user OpenClaw sessions
 * Includes Docker-based MCP server health check and auto-start
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const http = require('http');

// User mapping configuration (Discord ID → User config)
const USER_MAP = {
  'Set': {
    discordId: '85131474184986624',
    nickname: 'Set',
    symbol: '∅',
    path: 'users/Set/',
    composeFile: 'simple-graph-mcp/docker-compose-rawrity.yml',
    mcpService: 'mcp',
    mcpPort: 9301,
    neo4jPort: 7474
  },
  'Sigma': {
    discordId: '296511082745298944',
    nickname: 'Sigma',
    symbol: 'Σ',
    path: 'users/Sigma/',
    composeFile: 'simple-graph-mcp/docker-compose-sigma.yml',
    mcpService: 'mcp',
    mcpPort: 9302,
    neo4jPort: 7574
  }
};

const DOCKER_COMPOSE_DIR = 'projects';

function getTodayFileName() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}.md`;
}

async function httpHealthCheck(port) {
  return new Promise((resolve) => {
    const req = http.get(`http://localhost:${port}/health`, (res) => {
      resolve({ ok: res.statusCode === 200, statusCode: res.statusCode });
    });
    req.on('error', () => resolve({ ok: false, statusCode: null }));
    req.setTimeout(3000, () => {
      req.destroy();
      resolve({ ok: false, statusCode: null });
    });
  });
}

function checkDockerContainer(user, workspaceRoot) {
  const composePath = path.join(workspaceRoot, DOCKER_COMPOSE_DIR, user.composeFile);
  
  if (!fs.existsSync(composePath)) {
    return { containerExists: false, isRunning: false, error: `docker-compose file not found: ${user.composeFile}` };
  }
  
  try {
    // Check if service is running using docker compose (new CLI)
    const cmd = `docker compose -f "${composePath}" ps -q ${user.mcpService}`;
    const containerId = execSync(cmd, { encoding: 'utf8', windowsHide: true }).trim();
    
    if (!containerId) {
      return { containerExists: false, isRunning: false, error: null };
    }
    
    // Check if actually running (not just created)
    const statusCmd = `docker inspect -f '{{.State.Running}}' ${containerId}`;
    const isRunning = execSync(statusCmd, { encoding: 'utf8', windowsHide: true }).trim() === 'true';
    
    return { containerExists: true, isRunning, error: null };
  } catch (e) {
    // Try old docker-compose command if docker compose fails
    try {
      const cmd = `docker-compose -f "${composePath}" ps -q ${user.mcpService}`;
      const containerId = execSync(cmd, { encoding: 'utf8', windowsHide: true }).trim();
      
      if (!containerId) {
        return { containerExists: false, isRunning: false, error: null };
      }
      
      const statusCmd = `docker inspect -f '{{.State.Running}}' ${containerId}`;
      const isRunning = execSync(statusCmd, { encoding: 'utf8', windowsHide: true }).trim() === 'true';
      
      return { containerExists: true, isRunning, error: null };
    } catch (e2) {
      return { containerExists: false, isRunning: false, error: e2.message };
    }
  }
}

async function checkMcpStatus(user, workspaceRoot) {
  // First check Docker container
  const dockerStatus = checkDockerContainer(user, workspaceRoot);
  
  // Then verify HTTP endpoint responds
  const httpStatus = await httpHealthCheck(user.mcpPort);
  
  const isHealthy = dockerStatus.isRunning && httpStatus.ok;
  
  return {
    isHealthy,
    containerRunning: dockerStatus.isRunning,
    httpResponding: httpStatus.ok,
    containerExists: dockerStatus.containerExists,
    error: dockerStatus.error
  };
}

async function getStorageStats(port) {
  // For Simple Graph MCP, fetch stats from health endpoint
  try {
    const response = await fetch(`http://localhost:${port}/health`);
    if (response.ok) {
      const data = await response.json();
      return { 
        itemCount: data.entities || 0, 
        relationships: data.relationships || 0,
        error: null 
      };
    }
    return { itemCount: 0, relationships: 0, error: 'Health check failed' };
  } catch (e) {
    return { itemCount: 0, relationships: 0, error: e.message };
  }
}

function checkOnboardingStatus(storagePath, workspaceRoot) {
  const fullPath = path.join(workspaceRoot, storagePath);
  
  try {
    if (!fs.existsSync(fullPath)) {
      return { 
        hasCompletedOnboarding: false, 
        hasBasicIdentity: false,
        identityKeys: [],
        totalDataPoints: 0
      };
    }
    
    const data = JSON.parse(fs.readFileSync(fullPath, 'utf8'));
    const personalInfo = data.personal_info || {};
    const preferences = data.preferences || {};
    const memories = data.memories || [];
    const relationships = data.relationships || {};
    
    // Check for identity indicators
    const hasName = !!(personalInfo.basic?.name || personalInfo.identity?.full_name || personalInfo.misc?.Uthara);
    const hasNickname = !!(personalInfo.identity?.nickname || personalInfo.misc?.current_title);
    const hasCareerInfo = !!(personalInfo.career || personalInfo.work);
    
    // Count data richness indicators
    const identityKeys = Object.keys(personalInfo);
    const prefCategories = Object.keys(preferences);
    const relationshipCount = Object.keys(relationships).length;
    
    const totalDataPoints = identityKeys.length + prefCategories.length + memories.length + relationshipCount;
    
    // Onboarding is "complete" if they have:
    // 1. Basic identity (name/nickname), AND
    // 2. Either career info OR relationship data OR multiple preference categories
    const hasBasicIdentity = hasName || hasNickname;
    const hasExtendedData = hasCareerInfo || relationshipCount > 0 || prefCategories.length > 0 || memories.length > 0;
    
    const hasCompletedOnboarding = hasBasicIdentity && hasExtendedData;
    
    return {
      hasCompletedOnboarding,
      hasBasicIdentity,
      identityKeys,
      totalDataPoints,
      dataSummary: {
        personalInfoCategories: identityKeys.length,
        preferenceCategories: prefCategories.length,
        memories: memories.length,
        relationships: relationshipCount
      }
    };
  } catch (e) {
    return { 
      hasCompletedOnboarding: false, 
      hasBasicIdentity: false,
      identityKeys: [],
      totalDataPoints: 0,
      error: e.message
    };
  }
}

function startMcpContainer(user, workspaceRoot) {
  const composePath = path.join(workspaceRoot, DOCKER_COMPOSE_DIR, user.composeFile);
  
  if (!fs.existsSync(composePath)) {
    return { started: false, error: `docker-compose file not found: ${user.composeFile}` };
  }
  
  try {
    // Start the service (using docker compose new CLI, fallback to docker-compose)
    let cmd = `docker compose -f "${composePath}" up -d ${user.mcpService}`;
    try {
      execSync(cmd, { windowsHide: true, stdio: 'pipe' });
    } catch (e) {
      // Fallback to old docker-compose
      cmd = `docker-compose -f "${composePath}" up -d ${user.mcpService}`;
      execSync(cmd, { windowsHide: true, stdio: 'pipe' });
    }
    
    return { started: true, error: null };
  } catch (e) {
    return { started: false, error: e.message };
  }
}

async function loadUser(userName) {
  const user = USER_MAP[userName];
  
  if (!user) {
    console.error(`❌ Unknown user: ${userName}`);
    console.error('Available users: Set, Sigma');
    process.exit(1);
  }

  const workspaceRoot = process.env.OPENCLAW_WORKSPACE || process.cwd();
  const userPath = path.join(workspaceRoot, user.path);
  const memoryPath = path.join(userPath, 'memory');
  const todayFile = path.join(memoryPath, getTodayFileName());
  const composePath = path.join(workspaceRoot, DOCKER_COMPOSE_DIR, user.composeFile);

  // Check if user workspace exists
  if (!fs.existsSync(userPath)) {
    console.error(`❌ User workspace not found: ${user.path}`);
    console.error('Run: mkdir -p ' + user.path);
    process.exit(1);
  }

  // Check MCP Docker container status
  const mcpStatus = await checkMcpStatus(user, workspaceRoot);
  const storageStats = await getStorageStats(user.mcpPort);
  
  let autoStarted = false;
  let startError = null;
  
  // Auto-start if container doesn't exist or isn't running
  if (!mcpStatus.containerExists || !mcpStatus.containerRunning) {
    if (fs.existsSync(composePath)) {
      const startResult = startMcpContainer(user, workspaceRoot);
      autoStarted = startResult.started;
      startError = startResult.error;
      
      // Wait a moment for container to start, then recheck
      if (autoStarted) {
        await new Promise(r => setTimeout(r, 3000));
        const recheck = await checkMcpStatus(user, workspaceRoot);
        mcpStatus.isHealthy = recheck.isHealthy;
        mcpStatus.containerRunning = recheck.containerRunning;
        mcpStatus.httpResponding = recheck.httpResponding;
      }
    } else {
      startError = 'Docker compose not configured';
    }
  }

  // Ensure memory directory exists
  if (!fs.existsSync(memoryPath)) {
    fs.mkdirSync(memoryPath, { recursive: true });
  }

  // Create today's memory file if it doesn't exist
  if (!fs.existsSync(todayFile)) {
    const dateHeader = `# ${getTodayFileName().replace('.md', '')}\n\n`;
    fs.writeFileSync(todayFile, dateHeader, 'utf8');
  }

  // Check onboarding status (simplified - no longer uses JSON file)
  const onboardingStatus = { hasCompletedOnboarding: true, hasBasicIdentity: true, totalDataPoints: storageStats.itemCount };
  
  // Output success message (this will be parsed by OpenClaw)
  console.log(`✅ Loaded user: ${user.nickname} (${user.symbol})`);
  console.log(`📁 Workspace: ${user.path}`);
  console.log(`📝 Context: AGENTS.md, USER.md, MEMORY.md, memory/${getTodayFileName()}`);
  
  // Output MCP status
  const containerName = `simple-graph-mcp-${user.nickname.toLowerCase()}`;
  if (mcpStatus.isHealthy) {
    console.log(`🔌 MCP Server: ✅ Running`);
    console.log(`   ├─ Container: ${containerName}`);
    console.log(`   ├─ Port: ${user.mcpPort}`);
    console.log(`   └─ Storage: ${storageStats.itemCount} entities, ${storageStats.relationships} relationships`);
    if (autoStarted) {
      console.log(`   └─ Note: Auto-started for this session`);
    }
  } else if (mcpStatus.containerRunning && !mcpStatus.httpResponding) {
    // Container running but HTTP not responding
    console.log(`🔌 MCP Server: ⚠️ Container running, HTTP not responding`);
    console.log(`   ├─ Container: ${containerName}`);
    console.log(`   ├─ Port: ${user.mcpPort}`);
    console.log(`   └─ 📝 Check: docker compose -f projects/${user.composeFile} logs`);
  } else if (autoStarted) {
    console.log(`🔌 MCP Server: ⚠️ Auto-started (starting up)`);
    console.log(`   ├─ Container: ${containerName}`);
    console.log(`   ├─ Port: ${user.mcpPort}`);
    if (startError) {
      console.log(`   ├─ Error: ${startError}`);
    }
    console.log(`   └─ 📝 Note: Container was stopped — may need a moment`);
    console.log(`      Check: docker compose -f projects/${user.composeFile} ps`);
  } else if (!fs.existsSync(composePath)) {
    console.log(`🔌 MCP Server: ℹ️ Docker not configured`);
    console.log(`   ├─ Path: projects/${user.composeFile}`);
    console.log(`   └─ 📝 Run: docker compose -f projects/${user.composeFile} up -d`);
  } else {
    console.log(`🔌 MCP Server: ❌ Not running`);
    console.log(`   ├─ Container: ${containerName}`);
    console.log(`   ├─ Port: ${user.mcpPort}`);
    if (startError) {
      console.log(`   ├─ Start error: ${startError}`);
    }
    console.log(`   └─ 📝 Run: docker compose -f projects/${user.composeFile} up -d`);
  }
  
  // Output onboarding status
  if (!onboardingStatus.hasCompletedOnboarding) {
    console.log(`\n🆕 Onboarding Status: Not completed`);
    if (!onboardingStatus.hasBasicIdentity) {
      console.log(`   └─ ⚠️  No identity information found`);
    } else {
      console.log(`   └─ ℹ️  Basic info present, but minimal data (${onboardingStatus.totalDataPoints} data points)`);
    }
    console.log(`\n💡 Run onboarding to populate your memory:`);
    console.log(`   /onboard quick     — 5 essential questions (2-3 min)`);
    console.log(`   /onboard full      — Comprehensive (10-15 min)`);
    console.log(`   /onboard [category] — Single topic (food, travel, etc.)`);
  } else {
    console.log(`\n✅ MCP Graph: Active (${onboardingStatus.totalDataPoints} entities)`);
  }
  
  // Output file references for OpenClaw to load
  const filesToLoad = [
    path.join(userPath, 'AGENTS.md'),
    path.join(userPath, 'USER.md'),
    path.join(userPath, 'MEMORY.md'),
    todayFile
  ].filter(f => fs.existsSync(f));

  // Signal files to load via special output format
  filesToLoad.forEach(file => {
    console.log(`@reference ${path.relative(workspaceRoot, file)}`);
  });
  
  // Output skill propagation info
  console.log(`\n🛠️  Available Skills (use from any context):`);
  console.log(`   ngrok: /tunnel, /tunnel_stop, /tunnel_status`);
  console.log(`   user-onboarding: /onboard, /onboard quick, /onboard full`);
  console.log(`   load-session: /load-session`);
  console.log(`   save-session: /save-session`);
  console.log(`   discord-user-bridge: /send-to`);
  console.log(`\n   All skills resolve paths via __dirname — they work regardless of user context.`);
  console.log(`   Run: node skills/load-user/scripts/validate-skills.js ${userName}`);
}

// Main entry point
const userName = process.argv[2];

if (!userName) {
  console.error('Usage: load-user.js <Set|Sigma>');
  process.exit(1);
}

loadUser(userName);
