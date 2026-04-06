#!/usr/bin/env python3
"""
User Router Bridge - OpenClaw Integration

Provides functions that can be called from OpenClaw agents to route
messages to user-specific contexts.
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from router import USER_MAP, get_user_context, should_handle_as_user


def check_user_and_advise(user_id: str, message_content: str = "") -> str:
    """
    Check which user sent the message and return appropriate advice.
    
    Call this from OpenClaw when you receive a Discord message.
    Returns instructions on how to handle the message properly.
    
    Example usage in OpenClaw:
        from skills.user_router.scripts.bridge import check_user_and_advise
        advice = check_user_and_advise("296511082745298944", "user message here")
    """
    if not should_handle_as_user(user_id):
        return f"User ID {user_id} not in routing map. Handle with current context."
    
    context = get_user_context(user_id)
    
    # Different advice based on who the user is
    if context["agent_id"] == "rawrity":
        return f"Message from RAWRity (owner). Continue with current workspace context."
    
    elif context["agent_id"] == "sigma":
        return f"""Message from Sigma (user: 296511082745298944).

To handle this properly, you have two options:

OPTION 1 - Spawn isolated sub-agent (RECOMMENDED):
  sessions_spawn(
      task="{message_content}",
      label="sigma",
      agent_id="sigma"
  )
  This creates a completely isolated session with Sigma's workspace.

OPTION 2 - Switch context in current session:
  /load-user sigma
  Then process the message.

CURRENT SETUP NOTE:
All Discord messages currently route to the rawrity agent due to guild-based binding.
The Discord user ID is available in the message metadata.
"""
    
    return f"Unknown routing for user {user_id}"


def get_user_info(user_id: str) -> dict:
    """
    Get information about a Discord user.
    
    Returns dict with agent_id, workspace, name, graph_port
    """
    return get_user_context(user_id)


def list_users() -> list:
    """List all configured users."""
    return [
        {
            "user_id": uid,
            "name": info["name"],
            "agent_id": info["agent_id"],
            "workspace": info["workspace"]
        }
        for uid, info in USER_MAP.items()
    ]


def format_routing_summary() -> str:
    """Return a formatted summary of the routing configuration."""
    lines = ["User Router Configuration", "=" * 40, ""]
    
    for user_id, info in USER_MAP.items():
        lines.append(f"User: {info['name']}")
        lines.append(f"  Discord ID: {user_id}")
        lines.append(f"  Agent ID: {info['agent_id']}")
        lines.append(f"  Workspace: {info['workspace']}")
        lines.append(f"  Simple Graph: http://localhost:{info['graph_port']}")
        lines.append("")
    
    lines.append("Usage:")
    lines.append("  from skills.user_router.scripts.bridge import check_user_and_advise")
    lines.append("  advice = check_user_and_advise(user_id, message)")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    print(format_routing_summary())
    print("\n" + "=" * 40)
    
    print("\nSimulating RAWRity message:")
    print(check_user_and_advise("85131474184986624", "Test message"))
    
    print("\nSimulating Sigma message:")
    print(check_user_and_advise("296511082745298944", "Create cover letters"))
