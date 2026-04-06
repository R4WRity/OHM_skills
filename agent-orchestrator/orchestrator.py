#!/usr/bin/env python3
"""
Agent Orchestrator
Manages sub-agents as permanent infrastructure with health monitoring and auto-recovery.
"""

import json
import os
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import signal
import sys

AGENTS_DIR = Path("skills/agent-orchestrator/agents")
LOG_DIR = Path("skills/agent-orchestrator/logs")
STATE_FILE = Path("skills/agent-orchestrator/state.json")

def load_agent_config(agent_id: str) -> Optional[Dict]:
    """Load agent configuration from JSON file"""
    config_path = AGENTS_DIR / f"{agent_id}.json"
    if not config_path.exists():
        return None
    with open(config_path) as f:
        return json.load(f)

def load_all_agents() -> List[Dict]:
    """Load all agent configurations"""
    agents = []
    if AGENTS_DIR.exists():
        for config_file in AGENTS_DIR.glob("*.json"):
            try:
                with open(config_file) as f:
                    agent = json.load(f)
                    agent["_file"] = config_file.name
                    agents.append(agent)
            except Exception as e:
                print(f"Error loading {config_file}: {e}")
    return agents

def load_state() -> Dict:
    """Load orchestrator state"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"agents": {}, "last_check": None}

def save_state(state: Dict):
    """Save orchestrator state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def spawn_agent(agent_config: Dict) -> Dict:
    """Spawn a sub-agent and track its session"""
    agent_id = agent_config["agent_id"]
    
    # Load prompt template
    prompt_path = Path(agent_config["prompt_template"])
    if not prompt_path.exists():
        return {"status": "error", "error": f"Prompt template not found: {prompt_path}"}
    
    with open(prompt_path) as f:
        prompt = f.read()
    
    # Build environment variables
    env_vars = {}
    for key, value in agent_config.get("environment", {}).items():
        if value.startswith("${VAULT}"):
            # Load from vault
            vault_path = value.replace("${VAULT}", os.path.expanduser("~/.openclaw/vault"))
            vault_path = vault_path.replace("/${", "/").replace("}", "")
            try:
                with open(vault_path) as f:
                    env_vars[key] = f.read().strip()
            except:
                env_vars[key] = os.environ.get(key, "")
        else:
            env_vars[key] = value
    
    # Model configuration
    model = agent_config.get("model", {})
    model_str = f"ollama/{model.get('model', 'gemma3:1b')}"
    
    # Build the spawn command (simulated - actually uses sessions_spawn API)
    spawn_info = {
        "agent_id": "main",
        "task": prompt,
        "model": model_str,
        "label": agent_id,
        "runTimeoutSeconds": agent_config.get("resources", {}).get("timeout_seconds", 300),
        "environment": env_vars
    }
    
    # Log the spawn
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "action": "spawn",
            "config": agent_config,
            "spawn_params": spawn_info
        }, f, indent=2)
    
    # Note: In actual implementation, this would call the sessions_spawn tool
    # For now, we just record the intent
    return {
        "status": "spawned",
        "agent_id": agent_id,
        "log_file": str(log_path),
        "params": spawn_info
    }

def check_agent_health(agent_id: str) -> Dict:
    """Check health of a running agent"""
    # This would check if the agent's session is still active
    # For now, stub implementation
    return {
        "status": "unknown",
        "agent_id": agent_id,
        "last_seen": None,
        "is_responsive": False
    }

def restart_agent(agent_id: str) -> Dict:
    """Restart an agent that has failed or frozen"""
    config = load_agent_config(agent_id)
    if not config:
        return {"status": "error", "error": f"Agent {agent_id} not found"}
    
    # Kill existing session if any
    try:
        # Find and kill existing Python process for this agent
        subprocess.run(
            ["taskkill", "/F", "/FI", f"WINDOWTITLE eq *{agent_id}*"],
            capture_output=True
        )
    except:
        pass
    
    # Respawn
    time.sleep(2)
    result = spawn_agent(config)
    result["action"] = "restart"
    
    # Log restart
    log_path = LOG_DIR / f"{agent_id}_restart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "action": "restart",
            "agent_id": agent_id,
            "result": result
        }, f, indent=2)
    
    return result

def run_health_checks():
    """Run health checks on all agents and restart if needed"""
    state = load_state()
    agents = load_all_agents()
    
    alerts = []
    restarts = []
    
    for agent in agents:
        agent_id = agent["agent_id"]
        
        if not agent.get("enabled", False):
            continue
        
        if not agent.get("health_checks", {}).get("enabled", True):
            continue
        
        health = check_agent_health(agent_id)
        state["agents"][agent_id] = {
            **state["agents"].get(agent_id, {}),
            "last_check": datetime.now().isoformat(),
            **health
        }
        
        # Check if we need to restart
        unhealthy_count = state["agents"][agent_id].get("unhealthy_count", 0)
        max_unhealthy = agent.get("health_checks", {}).get("max_unhealthy_count", 2)
        
        if health["status"] in ["error", "frozen", "unresponsive"]:
            unhealthy_count += 1
            state["agents"][agent_id]["unhealthy_count"] = unhealthy_count
            
            if unhealthy_count >= max_unhealthy and agent.get("health_checks", {}).get("auto_restart", True):
                print(f"[ORCHESTRATOR] Agent {agent_id} unhealthy ({unhealthy_count}/{max_unhealthy}), restarting...")
                result = restart_agent(agent_id)
                restarts.append({
                    "agent_id": agent_id,
                    "reason": f"unhealthy {unhealthy_count} times",
                    "result": result
                })
                state["agents"][agent_id]["unhealthy_count"] = 0
                state["agents"][agent_id]["last_restart"] = datetime.now().isoformat()
        else:
            # Reset counter on healthy check
            state["agents"][agent_id]["unhealthy_count"] = 0
    
    state["last_check"] = datetime.now().isoformat()
    save_state(state)
    
    return {
        "checks_run": len(agents),
        "restarts": restarts,
        "alerts": alerts
    }

def run_agent_now(agent_id: str) -> Dict:
    """Manually trigger an agent run"""
    config = load_agent_config(agent_id)
    if not config:
        return {"status": "error", "error": f"Agent {agent_id} not found"}
    
    return spawn_agent(config)

def cli_main():
    """Command-line interface for orchestrator"""
    import argparse
    parser = argparse.ArgumentParser(description="Agent Orchestrator")
    parser.add_argument("command", choices=["check", "run", "status", "restart"])
    parser.add_argument("--agent", help="Agent ID for run/restart commands")
    args = parser.parse_args()
    
    if args.command == "check":
        result = run_health_checks()
        print(json.dumps(result, indent=2))
    
    elif args.command == "run":
        if not args.agent:
            print("Error: --agent required for run command", file=sys.stderr)
            sys.exit(1)
        result = run_agent_now(args.agent)
        print(json.dumps(result, indent=2))
    
    elif args.command == "restart":
        if not args.agent:
            print("Error: --agent required for restart command", file=sys.stderr)
            sys.exit(1)
        result = restart_agent(args.agent)
        print(json.dumps(result, indent=2))
    
    elif args.command == "status":
        state = load_state()
        agents = load_all_agents()
        print(f"Registered agents: {len(agents)}")
        print(f"Last check: {state.get('last_check', 'never')}")
        for agent_id, agent_state in state.get("agents", {}).items():
            print(f"  {agent_id}: {agent_state.get('status', 'unknown')}")

if __name__ == "__main__":
    cli_main()
