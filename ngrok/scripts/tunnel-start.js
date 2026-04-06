#!/usr/bin/env node
/**
 * Tunnel Start Command - /tunnel <folder_path>
 * 
 * Starts a local HTTP server for a folder and creates an ngrok tunnel.
 * Generates witty subdomains based on the folder content.
 * 
 * Usage: node tunnel-start.js <folder_path>
 * Example: node tunnel-start.js portfolio
 *          node tunnel-start.js docs/report-2025
 */

const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const http = require('http');

// Configuration
const STATE_FILE = path.join(__dirname, '..', 'active-tunnels.json');
const START_PORT = 8000;
const MAX_PORT = 9000;

// Witty subdomain generators based on folder name patterns
const SUBDOMAIN_GENERATORS = {
  // Portfolio/creative work
  portfolio: () => pickOne([
    'masterpiece-in-progress',
    'hired-please',
    'look-ma-im-creative',
    'pixels-and-paychecks',
    'art-but-make-it-money',
    'hire-me-im-pretty',
    'portfolio-polish',
    'creative-cashflow',
    'rawrity-showcase'
  ]),
  
  // Documentation/reports
  docs: () => pickOne([
    'the-paper-trail',
    'boring-but-important',
    'read-me-or-else',
    'official-business',
    'doc-u-ment',
    'evidence-of-work',
    'paperwork-party'
  ]),
  
  // Projects
  project: () => pickOne([
    'work-in-prog',
    'probably-works',
    'certified-fresh-code',
    'it-compiles-ship-it',
    'feature-not-bug',
    'will-debug-later',
    'commit-and-pray'
  ]),
  
  // Data/analysis
  data: () => pickOne([
    'numbers-and-stuff',
    'excel-but-cooler',
    'big-data-little-effort',
    'trust-me-im-data',
    'stats-stats-stats',
    'graph-me-daddy'
  ]),
  
  // Personal/random
  personal: () => pickOne([
    'my-stuff-dont-touch',
    'organized-chaos',
    'life-in-folders',
    'me-myself-and-files',
    'digital-hoard',
    'my-mess-my-rules'
  ]),
  
  // Default fallback
  default: (folder) => {
    // Clean the folder name for subdomain use (alphanumeric + hyphens only)
    const clean = folder.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
    const wittySuffixes = [
      'live-and-direct',
      'now-with-wifi',
      'world-wide-wonder',
      'internet-magic',
      'click-if-you-dare',
      'hosted-with-love',
      'tunnel-vision',
      'rawrity-special',
      'fresh-from-laptop'
    ];
    return `${clean}-${pickOne(wittySuffixes)}`;
  }
};

function pickOne(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function generateSubdomain(folderPath) {
  const folder = path.basename(folderPath).toLowerCase();
  
  // Check for exact matches
  if (SUBDOMAIN_GENERATORS[folder]) {
    return SUBDOMAIN_GENERATORS[folder]();
  }
  
  // Check for partial matches
  for (const [key, generator] of Object.entries(SUBDOMAIN_GENERATORS)) {
    if (folder.includes(key)) {
      return generator();
    }
  }
  
  // Fallback to folder-based name
  return SUBDOMAIN_GENERATORS.default(folder);
}

function findAvailablePort() {
  return new Promise((resolve, reject) => {
    const testPort = (port) => {
      if (port > MAX_PORT) {
        reject(new Error('No available ports found'));
        return;
      }
      
      const server = http.createServer();
      server.listen(port, () => {
        server.close(() => resolve(port));
      });
      server.on('error', () => testPort(port + 1));
    };
    
    testPort(START_PORT);
  });
}

function checkNgrokAgent() {
  return new Promise((resolve) => {
    const req = http.get('http://localhost:4040/api/tunnels', (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(3000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

function startNgrokAgent() {
  return new Promise((resolve, reject) => {
    const skillDir = path.join(__dirname, '..');
    const docker = spawn('docker-compose', ['up', '-d'], { 
      cwd: skillDir,
      detached: true,
      stdio: 'ignore'
    });
    
    docker.on('error', (err) => reject(err));
    
    // Wait for agent to be ready
    setTimeout(async () => {
      let attempts = 0;
      const check = async () => {
        if (await checkNgrokAgent()) {
          resolve();
        } else if (attempts++ > 10) {
          reject(new Error('Agent failed to start'));
        } else {
          setTimeout(check, 1000);
        }
      };
      check();
    }, 3000);
  });
}

function startPythonServer(folderPath, port) {
  return new Promise((resolve, reject) => {
    // Resolve full path
    const workspaceRoot = process.env.OPENCLAW_WORKSPACE || process.cwd();
    const fullPath = path.resolve(workspaceRoot, folderPath);
    
    // Verify folder exists
    if (!fs.existsSync(fullPath)) {
      reject(new Error(`Folder not found: ${folderPath}`));
      return;
    }
    
    // Check for index.html
    const indexPath = path.join(fullPath, 'index.html');
    if (!fs.existsSync(indexPath)) {
      // List HTML files
      const files = fs.readdirSync(fullPath);
      const htmlFiles = files.filter(f => f.endsWith('.html'));
      
      if (htmlFiles.length === 0) {
        reject(new Error(`No index.html found in ${folderPath}. Create an index.html file first.`));
        return;
      }
      
      // Use first HTML file but warn
      console.log(`⚠️ No index.html found, using ${htmlFiles[0]}`);
    }
    
    // Start Python HTTP server with proper detachment for the platform
    const isWindows = process.platform === 'win32';
    let python;
    
    if (isWindows) {
      // On Windows, use PowerShell Start-Process for true background execution
      const psCmd = `Start-Process -FilePath "python" -ArgumentList "-m","http.server","${port}","--bind","0.0.0.0" -WindowStyle Hidden -WorkingDirectory "${fullPath}"`;
      python = spawn('powershell.exe', ['-Command', psCmd], {
        detached: false,
        stdio: 'ignore'
      });
    } else {
      // On Unix, use detached process
      python = spawn('python', [
        '-m', 'http.server',
        port.toString(),
        '--bind', '0.0.0.0'
      ], {
        cwd: fullPath,
        detached: true,
        stdio: 'ignore'
      });
    }
    
    python.on('error', (err) => reject(err));
    
    // Give it a moment to start and verify it's running
    setTimeout(() => {
      // Verify server is responding
      http.get(`http://127.0.0.1:${port}`, (res) => {
        if (res.statusCode === 200) {
          // On Windows, we can't easily get the PID, so return a placeholder
          resolve(isWindows ? 'powershell-bg' : python.pid);
        } else {
          reject(new Error(`Server started but returned status ${res.statusCode}`));
        }
      }).on('error', (err) => {
        // Try again after a moment
        setTimeout(() => {
          http.get(`http://127.0.0.1:${port}`, (res) => {
            resolve(isWindows ? 'powershell-bg' : python.pid);
          }).on('error', reject);
        }, 1000);
      });
    }, 2000);
  });
}

function getHostIp() {
  // For Docker Desktop on Windows/Mac, host.docker.internal is the reliable way
  // The container can reach the host via this special DNS name
  // The Python server binds to 0.0.0.0 so it's accessible from Docker
  return 'host.docker.internal';
}

function createNgrokTunnel(name, port, subdomain) {
  return new Promise((resolve, reject) => {
    const hostIp = getHostIp();
    const tunnelData = JSON.stringify({
      name: name,
      proto: 'http',
      addr: `${hostIp}:${port}`,
      subdomain: subdomain
    });
    
    const options = {
      hostname: 'localhost',
      port: 4040,
      path: '/api/tunnels',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(tunnelData)
      }
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 201) {
          try {
            const tunnel = JSON.parse(data);
            resolve(tunnel);
          } catch (e) {
            reject(new Error('Failed to parse tunnel response'));
          }
        } else {
          reject(new Error(`Ngrok API error: ${res.statusCode} - ${data}`));
        }
      });
    });
    
    req.on('error', reject);
    req.write(tunnelData);
    req.end();
  });
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
}

function loadState() {
  if (fs.existsSync(STATE_FILE)) {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  }
  return {};
}

async function main() {
  const folderPath = process.argv[2];
  
  if (!folderPath) {
    console.error('❌ Usage: /tunnel <folder_path>');
    console.error('Example: /tunnel portfolio');
    process.exit(1);
  }
  
  // Check if there's already an active tunnel
  const state = loadState();
  if (state.active) {
    console.log(`⚠️ Tunnel already active: ${state.name}`);
    console.log(`   🔗 ${state.publicUrl}`);
    console.log(`   Stop it first with: /tunnel_stop`);
    process.exit(0);
  }
  
  console.log(`🚀 Starting tunnel for ${folderPath}...`);
  
  try {
    // Find available port
    const port = await findAvailablePort();
    console.log(`📡 Found available port: ${port}`);
    
    // Generate witty subdomain
    const subdomain = generateSubdomain(folderPath);
    console.log(`🎭 Generated subdomain: ${subdomain}`);
    
    // Ensure ngrok agent is running
    let agentRunning = await checkNgrokAgent();
    if (!agentRunning) {
      console.log(`🐳 Starting ngrok agent...`);
      await startNgrokAgent();
      agentRunning = true;
    }
    
    // Start local HTTP server
    console.log(`🌐 Starting HTTP server on port ${port}...`);
    const serverPid = await startPythonServer(folderPath, port);
    
    // Create ngrok tunnel
    console.log(`🔗 Creating ngrok tunnel...`);
    const tunnelName = `tunnel-${Date.now()}`;
    const tunnel = await createNgrokTunnel(tunnelName, port, subdomain);
    
    const publicUrl = tunnel.public_url;
    
    // Save state
    saveState({
      active: true,
      name: tunnelName,
      folder: folderPath,
      port: port,
      serverPid: serverPid,
      subdomain: subdomain,
      publicUrl: publicUrl,
      startedAt: new Date().toISOString()
    });
    
    // Output results
    console.log(`\n✅ Tunnel ready!`);
    console.log(`\n📁 Serving: ${folderPath}/index.html`);
    console.log(`🌐 Local: http://localhost:${port}`);
    console.log(`🔗 Public: ${publicUrl}`);
    console.log(`\n📊 Check status: /tunnel_status`);
    console.log(`🛑 Stop tunnel: /tunnel_stop`);
    
  } catch (err) {
    console.error(`\n❌ Error: ${err.message}`);
    process.exit(1);
  }
}

main();
