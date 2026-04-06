#!/usr/bin/env python3
"""
Ngrok Tunnel Manager Bridge
CLI and API for managing ngrok tunnels via the local agent API.

This uses the ngrok agent's local API (localhost:4040) rather than the cloud API,
so it only requires the authtoken (not an API key).
"""

import argparse
import json
import os
import sys
import subprocess
from typing import Optional, Dict, List
from pathlib import Path

import requests


class NgrokManager:
    """Manage ngrok tunnels via the local agent API."""
    
    AGENT_API = "http://localhost:4040/api"
    
    def __init__(self, authtoken: Optional[str] = None):
        self.authtoken = authtoken or self._load_authtoken()
    
    def _load_authtoken(self) -> str:
        """Load authtoken from vault or environment."""
        token = os.getenv("NGROK_AUTHTOKEN")
        if token:
            return token
        
        vault_path = Path.home() / ".openclaw" / "vault" / "ngrok-auth-token"
        if vault_path.exists():
            return vault_path.read_text().strip()
        
        raise RuntimeError("NGROK_AUTHTOKEN not found in env or vault")
    
    def _api_get(self, endpoint: str) -> Dict:
        """Make GET request to ngrok agent API."""
        url = f"{self.AGENT_API}{endpoint}"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except requests.ConnectionError:
            return {"error": "Agent not running on localhost:4040"}
    
    def _api_post(self, endpoint: str, data: Dict) -> Dict:
        """Make POST request to ngrok agent API."""
        url = f"{self.AGENT_API}{endpoint}"
        resp = requests.post(url, json=data)
        resp.raise_for_status()
        return resp.json()
    
    def _api_delete(self, endpoint: str) -> None:
        """Make DELETE request to ngrok agent API."""
        url = f"{self.AGENT_API}{endpoint}"
        resp = requests.delete(url)
        resp.raise_for_status()
    
    # ==================== Public API ====================
    
    def list_tunnels(self) -> List[Dict]:
        """List all active tunnels from the agent."""
        data = self._api_get("/tunnels")
        if "error" in data:
            return []
        return data.get("tunnels", [])
    
    def get_tunnel(self, name: str) -> Optional[Dict]:
        """Get specific tunnel details."""
        data = self._api_get(f"/tunnels/{name}")
        if "error" in data:
            return None
        return data
    
    def start_tunnel(
        self,
        name: str,
        port: int,
        subdomain: Optional[str] = None,
        domain: Optional[str] = None,
        region: str = "us",
        proto: str = "http"
    ) -> Dict:
        """
        Start a new tunnel through the ngrok agent.
        
        Args:
            name: Identifier for this tunnel
            port: Local port to forward
            subdomain: Custom subdomain (paid feature, e.g., 'myapp')
            domain: Full custom domain (paid feature, e.g., 'api.mydomain.com')
            region: ngrok region (us, eu, ap, au, sa, jp, in)
            proto: Protocol (http, https, tcp)
        
        Returns:
            Created tunnel object
        """
        # Build tunnel configuration
        config = {
            "addr": str(port),
            "proto": proto,
            "name": name
        }
        
        # Add custom domain/subdomain if provided (paid features)
        if domain:
            config["domain"] = domain
            config["host_header"] = domain
        elif subdomain:
            config["subdomain"] = subdomain
        
        return self._api_post("/tunnels", config)
    
    def stop_tunnel(self, name: str) -> None:
        """Stop a running tunnel."""
        self._api_delete(f"/tunnels/{name}")
    
    def agent_status(self) -> Dict:
        """Check ngrok agent status and version."""
        try:
            resp = requests.get(f"{self.AGENT_API}/tunnels", timeout=5)
            resp.raise_for_status()
            return {"running": True, "tunnels": resp.json().get("tunnels", [])}
        except requests.ConnectionError:
            return {"error": "Agent not running on localhost:4040"}
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== Config Management ====================
    
    def save_tunnel_config(self, tunnel: Dict, filepath: Optional[Path] = None):
        """Save tunnel config to JSON file for reference."""
        endpoints_dir = Path(__file__).parent / "endpoints"
        endpoints_dir.mkdir(exist_ok=True)
        
        name = tunnel.get("name", "unnamed")
        
        config = {
            "name": name,
            "public_url": tunnel.get("public_url"),
            "proto": tunnel.get("proto"),
            "config": tunnel.get("config", {}),
            "metrics": tunnel.get("metrics", {})
        }
        
        save_path = filepath or endpoints_dir / f"{name}.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        return save_path
    
    def load_tunnel_config(self, name: str) -> Optional[Dict]:
        """Load tunnel config from JSON file."""
        config_path = Path(__file__).parent / "endpoints" / f"{name}.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


def check_agent() -> bool:
    """Check if ngrok agent is running."""
    try:
        resp = requests.get("http://localhost:4040/api/tunnels", timeout=3)
        return resp.status_code == 200
    except:
        return False


def cmd_start(args):
    """Start a new tunnel."""
    mgr = NgrokManager()
    
    # Check agent is running
    if not check_agent():
        print("[ERR] Ngrok agent not running on localhost:4040")
        print("\nStart it with:")
        print("  python bridge.py docker up")
        sys.exit(1)
    
    print(f"Starting tunnel '{args.name}' -> localhost:{args.port}...")
    
    try:
        tunnel = mgr.start_tunnel(
            name=args.name,
            port=args.port,
            subdomain=args.subdomain,
            domain=args.domain,
            region=args.region or "us",
            proto=args.proto or "http"
        )
        
        # Save config for reference
        config_path = mgr.save_tunnel_config(tunnel)
        
        print(f"\n[OK] Tunnel started: {tunnel.get('public_url')}")
        print(f"  Forwarding: {tunnel.get('config', {}).get('addr', 'N/A')}")
        print(f"  Config saved: {config_path}")
        
    except requests.HTTPError as e:
        error_data = e.response.json() if e.response.text else {}
        msg = error_data.get('error', e.response.text)
        print(f"[ERR] {msg}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERR] {e}")
        sys.exit(1)


def cmd_list(args):
    """List active tunnels."""
    mgr = NgrokManager()
    
    print("Active Tunnels:")
    print("-" * 60)
    
    tunnels = mgr.list_tunnels()
    
    if not tunnels:
        agent_status = mgr.agent_status()
        if "error" in agent_status:
            print(f"  [ERR] {agent_status['error']}")
        else:
            print("  No active tunnels.")
        return
    
    for tunnel in tunnels:
        name = tunnel.get("name", "unnamed")
        url = tunnel.get("public_url", "N/A")
        addr = tunnel.get("config", {}).get("addr", "N/A")
        proto = tunnel.get("proto", "http")
        
        print(f"  {name}")
        print(f"    Public URL: {url}")
        print(f"    Forwarding: {addr}")
        print(f"    Protocol: {proto}")
        print()


def cmd_stop(args):
    """Stop a tunnel by name."""
    mgr = NgrokManager()
    
    # Check if tunnel exists
    tunnels = mgr.list_tunnels()
    tunnel = next((t for t in tunnels if t.get("name") == args.name), None)
    
    if not tunnel:
        print(f"[ERR] Tunnel not found: {args.name}")
        sys.exit(1)
    
    if not args.yes:
        confirm = input(f"Stop tunnel '{args.name}' ({tunnel.get('public_url')})? [y/N]: ")
        if confirm.lower() != "y":
            print("Cancelled.")
            return
    
    try:
        mgr.stop_tunnel(args.name)
        print(f"[OK] Stopped: {args.name}")
        
        # Remove local config file
        config_path = Path(__file__).parent / "endpoints" / f"{args.name}.json"
        if config_path.exists():
            config_path.unlink()
            
    except requests.HTTPError as e:
        print(f"[ERR] {e.response.text}")


def cmd_status(args):
    """Check agent status."""
    mgr = NgrokManager()
    
    print("Ngrok Status Check")
    print("=" * 40)
    
    # Agent status
    status = mgr.agent_status()
    if "error" in status:
        print(f"[ERR] Agent: {status['error']}")
        print("\nTo start the agent:")
        print("  python bridge.py docker up")
    else:
        print(f"[OK] Agent running")
        
        # List active tunnels
        tunnels = mgr.list_tunnels()
        print(f"[OK] Active tunnels: {len(tunnels)}")
        for t in tunnels:
            print(f"  - {t.get('name')}: {t.get('public_url')} -> {t.get('config', {}).get('addr')}")


def cmd_docker(args):
    """Docker compose shortcuts."""
    skill_dir = Path(__file__).parent
    
    # Load authtoken
    vault_path = Path.home() / ".openclaw" / "vault" / "ngrok-auth-token"
    authtoken = vault_path.read_text().strip() if vault_path.exists() else ""
    
    env = os.environ.copy()
    env["NGROK_AUTHTOKEN"] = authtoken
    
    if args.action == "up":
        cmd = ["docker-compose", "up", "-d"]
    elif args.action == "down":
        cmd = ["docker-compose", "down"]
    elif args.action == "logs":
        cmd = ["docker-compose", "logs", "-f"]
    else:
        cmd = ["docker-compose", "ps"]
    
    subprocess.run(cmd, cwd=skill_dir, env=env)


def cmd_web(args):
    """Open ngrok web interface."""
    import webbrowser
    webbrowser.open("http://localhost:4040")
    print("Opened http://localhost:4040")


def main():
    parser = argparse.ArgumentParser(
        prog="ngrok-skill",
        description="Manage ngrok tunnels (Dockerized with local agent API)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Start
    start_parser = subparsers.add_parser("start", help="Start a new tunnel")
    start_parser.add_argument("--name", "-n", required=True, help="Tunnel name/identifier")
    start_parser.add_argument("--port", "-p", type=int, required=True, help="Local port to forward")
    start_parser.add_argument("--subdomain", "-s", help="Custom subdomain (paid: e.g., 'myapp')")
    start_parser.add_argument("--domain", "-d", help="Full custom domain (paid: requires dashboard)")
    start_parser.add_argument("--region", "-r", default="us", help="Region (us, eu, ap, au, sa, jp, in)")
    start_parser.add_argument("--proto", choices=["http", "https", "tcp"], default="http", help="Protocol")
    start_parser.set_defaults(func=cmd_start)
    
    # List
    list_parser = subparsers.add_parser("list", help="List active tunnels")
    list_parser.set_defaults(func=cmd_list)
    
    # Stop
    stop_parser = subparsers.add_parser("stop", help="Stop a tunnel")
    stop_parser.add_argument("name", help="Tunnel name")
    stop_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    stop_parser.set_defaults(func=cmd_stop)
    
    # Status
    status_parser = subparsers.add_parser("status", help="Check agent status")
    status_parser.set_defaults(func=cmd_status)
    
    # Docker
    docker_parser = subparsers.add_parser("docker", help="Docker compose shortcuts")
    docker_parser.add_argument("action", choices=["up", "down", "logs", "ps"], help="Docker action")
    docker_parser.set_defaults(func=cmd_docker)
    
    # Web
    web_parser = subparsers.add_parser("web", help="Open web interface")
    web_parser.set_defaults(func=cmd_web)
    
    args = parser.parse_args()
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
