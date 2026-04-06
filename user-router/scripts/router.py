#!/usr/bin/env python3
"""
User Router - Route Discord messages to user-specific agent sessions.

Since OpenClaw bindings don't support userId matching for Discord,
this skill provides user-based routing at the application level.
"""

import json
import os
from pathlib import Path

# User ID to agent/workspace mapping
USER_MAP = {
    "85131474184986624": {
        "agent_id": "rawrity",
        "workspace": ".",  # Root workspace
        "name": "RAWRity",
        "graph_port": 9301
    },
    "296511082745298944": {
        "agent_id": "sigma",
        "workspace": "users/sigma",
        "name": "Sigma",
        "graph_port": 9302
    }
}


def get_user_context(user_id: str) -> dict:
    """Get the agent context for a Discord user ID."""
    return USER_MAP.get(user_id, USER_MAP["85131474184986624"])  # Default to rawrity


def route_message(user_id: str, message: str, channel: str = "discord") -> dict:
    """
    Route a message to the appropriate user agent.
    
    Args:
        user_id: Discord user ID (e.g., "85131474184986624")
        message: The message content
        channel: Channel type (discord, etc.)
    
    Returns:
        dict with routing info
    """
    context = get_user_context(user_id)
    
    return {
        "routed_to": context["agent_id"],
        "workspace": context["workspace"],
        "user_name": context["name"],
        "graph_port": context["graph_port"],
        "message": message,
        "action": f"Use /load-user {context['agent_id']} or spawn sub-agent"
    }


def should_handle_as_user(user_id: str) -> bool:
    """Check if this user has a dedicated agent/workspace."""
    return user_id in USER_MAP


def get_routing_instructions(user_id: str, message_content: str) -> str:
    """
    Get instructions for handling this user's message.
    
    Returns a command string that can be executed.
    """
    if not should_handle_as_user(user_id):
        return f"User {user_id} not in map. Handle as default (rawrity)."
    
    context = get_user_context(user_id)
    
    return f"""User Routing Instructions:
- Discord User ID: {user_id}
- Mapped to: {context['name']} ({context['agent_id']})
- Workspace: {context['workspace']}
- Simple Graph Port: {context['graph_port']}

To process this message properly:
1. Run: /load-user {context['agent_id']}
2. Or use sessions_spawn to create isolated sub-agent:
   sessions_spawn(task="{message_content}", label="{context['agent_id']}")
3. Access their Simple Graph at http://localhost:{context['graph_port']}
"""


def get_current_user_from_context() -> dict:
    """
    Attempt to read the current Discord user from OpenClaw context.
    This works when called from within an OpenClaw session.
    """
    # In OpenClaw, the user ID is injected in the message context
    # This is a placeholder - the actual ID comes from the runtime
    return {
        "note": "Call get_routing_instructions(user_id, message) with the actual Discord user ID"
    }


if __name__ == "__main__":
    # Test usage
    print("Testing user router...")
    
    # Test RAWRity
    result = route_message("85131474184986624", "Hello from RAWRity")
    print(f"\nRAWRity route: {json.dumps(result, indent=2)}")
    
    # Test Sigma
    result = route_message("296511082745298944", "Hello from Sigma")
    print(f"\nSigma route: {json.dumps(result, indent=2)}")
    
    # Test unknown user
    result = route_message("999999999999999999", "Hello from unknown")
    print(f"\nUnknown route: {json.dumps(result, indent=2)}")
