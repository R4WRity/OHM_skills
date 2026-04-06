#!/usr/bin/env python3
"""Discord channel-based agent router"""
import json
import os
from typing import Dict, Any, Optional

ROUTING_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config", "channel-routing.json"
)

class ChannelRouter:
    """Routes Discord messages to appropriate agent based on channel"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or ROUTING_CONFIG_PATH
        self.config = self._load_config()
        self.routes = {r["channel_id"]: r for r in self.config.get("routing", [])}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load routing configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load routing config: {e}")
            return {"routing": [], "default": {"agent": "main"}}
    
    def get_route(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get routing info for a channel"""
        return self.routes.get(str(channel_id))
    
    def should_route(self, channel_id: str, author_id: str = None) -> Dict[str, Any]:
        """
        Determine if message should be routed to a sub-agent
        
        Returns:
            {
                "route": bool,
                "agent_label": str,
                "agent_session": str,
                "user_id": str,
                "channel_name": str
            }
        """
        route_info = self.get_route(channel_id)
        
        if not route_info:
            return {
                "route": False,
                "reason": "no_route_configured",
                "fallback_to": "main"
            }
        
        # Check author matches (optional - for verification)
        if author_id and author_id != route_info.get("user_id"):
            # Allow but log - could be someone else in the channel
            pass
        
        return {
            "route": True,
            "agent_label": route_info["agent_label"],
            "agent_session": route_info["agent_session"],
            "user_id": route_info["user_id"],
            "channel_name": route_info["channel_name"]
        }

# Global instance
_router = None

def get_router() -> ChannelRouter:
    """Get or create router singleton"""
    global _router
    if _router is None:
        _router = ChannelRouter()
    return _router

def route_message(channel_id: str, message: str, author_id: str = None) -> Dict[str, Any]:
    """
    Route a Discord message to the appropriate agent
    
    Usage in OpenClaw:
        result = route_message(
            channel_id=discord_channel_id,
            message=user_message,
            author_id=user_id
        )
        if result["route"]:
            # Send to sub-agent
            sessions_send(
                result["agent_session"],
                f"[{result['channel_name']}] {message}"
            )
    """
    router = get_router()
    routing = router.should_route(channel_id, author_id)
    
    if routing["route"]:
        return {
            "routed": True,
            "agent_label": routing["agent_label"],
            "agent_session": routing["agent_session"],
            "channel_name": routing["channel_name"],
            "message": message
        }
    
    return {
        "routed": False,
        "fallback_to": "main",
        "message": message
    }

# Predefined exports
AGENT_RAWWRITY = "agent:main:subagent:9a13a3da-c78b-4ead-be6c-d7db0449fc48"
AGENT_SIGMA = "agent:main:subagent:5480d04d-64bd-43df-94b9-49c915254909"

CHANNEL_EMPTY_SET = "1468088770065862822"
CHANNEL_SIGMA = "1468088770996867228"

__all__ = [
    'ChannelRouter',
    'get_router',
    'route_message',
    'AGENT_RAWWRITY',
    'AGENT_SIGMA',
    'CHANNEL_EMPTY_SET',
    'CHANNEL_SIGMA'
]
