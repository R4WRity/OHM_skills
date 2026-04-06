#!/usr/bin/env node
/**
 * Tunnel Status Command - /tunnel_status
 * 
 * Shows current tunnel status: URL, uptime, requests, etc.
 * 
 * Usage: node tunnel-status.js
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

const STATE_FILE = path.join(__dirname, '..', 'active-tunnels.json');

function loadState() {
  if (fs.existsSync(STATE_FILE)) {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  }
  return null;
}

function getTunnelDetails(name) {
  return new Promise((resolve, reject) => {
    const req = http.get(`http://localhost:4040/api/tunnels/${name}`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error('Failed to parse tunnel data'));
          }
        } else {
          resolve(null);
        }
      });
    });
    
    req.on('error', () => resolve(null));
    req.setTimeout(3000, () => {
      req.destroy();
      resolve(null);
    });
  });
}

function getRequestMetrics() {
  return new Promise((resolve) => {
    const req = http.get('http://localhost:4040/api/requests/http', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const metrics = JSON.parse(data);
            resolve(metrics.requests || []);
          } catch (e) {
            resolve([]);
          }
        } else {
          resolve([]);
        }
      });
    });
    
    req.on('error', () => resolve([]));
    req.setTimeout(3000, () => {
      req.destroy();
      resolve([]);
    });
  });
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

async function main() {
  const state = loadState();
  
  if (!state || !state.active) {
    console.log('ℹ️ No active tunnel.');
    console.log('Start one with: /tunnel <folder_path>');
    return;
  }
  
  // Get live tunnel details from ngrok agent
  const tunnel = await getTunnelDetails(state.name);
  const requests = await getRequestMetrics();
  
  // Count requests for this tunnel
  const tunnelRequests = requests.filter(r => r.tunnel_name === state.name);
  
  console.log(`📡 Active Tunnel`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log();
  console.log(`📁 Folder: ${state.folder}`);
  console.log(`🔗 Public URL: ${state.publicUrl}`);
  console.log(`🌐 Local: http://localhost:${state.port}`);
  console.log(`🎭 Subdomain: ${state.subdomain}`);
  console.log(`⏱️ Uptime: ${calculateDuration(state.startedAt)}`);
  console.log(`📈 Requests: ${tunnelRequests.length}`);
  console.log();
  
  if (tunnel) {
    const config = tunnel.config || {};
    console.log(`🔧 Configuration:`);
    console.log(`   Protocol: ${tunnel.proto || 'http'}`);
    console.log(`   Forwarding to: ${config.addr || 'unknown'}`);
    console.log(`   Region: ${config.region || 'us'}`);
    
    if (tunnel.metrics) {
      const m = tunnel.metrics;
      console.log();
      console.log(`📊 Metrics:`);
      if (m.conns) console.log(`   Connections: ${m.conns.count || 0}`);
      if (m.http) console.log(`   HTTP: ${m.http.count || 0}`);
    }
  }
  
  console.log();
  console.log(`🌐 Web Interface: http://localhost:4040`);
  console.log(`🛑 Stop with: /tunnel_stop`);
  
  // Recent request log (last 3)
  if (tunnelRequests.length > 0) {
    console.log();
    console.log(`📋 Recent Requests (last 3):`);
    const recent = tunnelRequests.slice(-3).reverse();
    recent.forEach((req, i) => {
      const method = req.request?.method || 'GET';
      const uri = req.request?.uri || '/';
      const status = req.response?.status_code || '-';
      const time = new Date(req.start).toLocaleTimeString();
      console.log(`   ${i + 1}. ${method} ${uri} → ${status} (${time})`);
    });
  }
}

main().catch(err => {
  console.error(`❌ Error: ${err.message}`);
  process.exit(1);
});
