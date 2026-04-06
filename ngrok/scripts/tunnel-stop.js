#!/usr/bin/env node
/**
 * Tunnel Stop Command - /tunnel_stop
 * 
 * Stops the active ngrok tunnel and kills the local HTTP server.
 * 
 * Usage: node tunnel-stop.js [tunnel_name]
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const { exec } = require('child_process');

const STATE_FILE = path.join(__dirname, '..', 'active-tunnels.json');

function loadState() {
  if (fs.existsSync(STATE_FILE)) {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  }
  return null;
}

function clearState() {
  fs.writeFileSync(STATE_FILE, JSON.stringify({}, null, 2), 'utf8');
}

function stopNgrokTunnel(name) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: 4040,
      path: `/api/tunnels/${name}`,
      method: 'DELETE'
    };
    
    const req = http.request(options, (res) => {
      resolve(res.statusCode === 204 || res.statusCode === 200);
    });
    
    req.on('error', () => resolve(false));
    req.end();
  });
}

function killServer(pid, port) {
  return new Promise((resolve) => {
    const platform = process.platform;
    let cmd;
    
    if (platform === 'win32') {
      // On Windows, if pid is 'powershell-bg', find and kill by port
      if (pid === 'powershell-bg' && port) {
        // Find process using the port and kill it
        cmd = `powershell.exe -Command "Get-NetTCPConnection -LocalPort ${port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"`;
      } else {
        cmd = `taskkill /PID ${pid} /F`;
      }
    } else {
      cmd = `kill -9 ${pid}`;
    }
    
    exec(cmd, (err) => {
      resolve(!err);
    });
  });
}

async function main() {
  const state = loadState();
  
  if (!state || !state.active) {
    console.log('ℹ️ No active tunnel to stop.');
    console.log('Start one with: /tunnel <folder_path>');
    return;
  }
  
  console.log(`🛑 Stopping tunnel: ${state.name}`);
  console.log(`   🔗 ${state.publicUrl}`);
  
  // Stop ngrok tunnel
  console.log(`   Closing ngrok tunnel...`);
  const tunnelStopped = await stopNgrokTunnel(state.name);
  
  // Kill Python server
  console.log(`   Stopping HTTP server (PID ${state.serverPid})...`);
  const serverStopped = await killServer(state.serverPid, state.port);
  
  // Clear state
  clearState();
  
  // Report results
  console.log(`\n✅ Tunnel stopped`);
  if (tunnelStopped) {
    console.log(`   🔗 ${state.publicUrl} (offline)`);
  }
  if (serverStopped) {
    console.log(`   📁 Server on port ${state.port} killed`);
  }
  
  console.log(`\n📊 Served: ${state.folder}`);
  console.log(`⏱️ Duration: ${calculateDuration(state.startedAt)}`);
}

function calculateDuration(startedAt) {
  const start = new Date(startedAt);
  const now = new Date();
  const diff = Math.floor((now - start) / 1000);
  
  const hours = Math.floor(diff / 3600);
  const minutes = Math.floor((diff % 3600) / 60);
  const seconds = diff % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${seconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  } else {
    return `${seconds}s`;
  }
}

main().catch(err => {
  console.error(`❌ Error: ${err.message}`);
  process.exit(1);
});
