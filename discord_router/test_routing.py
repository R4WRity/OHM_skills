#!/usr/bin/env python3
"""Test Discord channel routing"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from skills.discord_router.router import route_message, get_router

print("=== Channel Routing Test ===\n")

# Test 1: Empty Set Chat (RAWRity)
print("Test 1: #empty-set-chat -> RAWRity")
result = route_message(
    channel_id="1468088770065862822",
    message="What's in my Notion recipes?",
    author_id="85131474184986624"
)
assert result["routed"] == True
assert result["agent_label"] == "RAWRity"
assert "9a13a3da" in result["agent_session"]
print(f"  Result: {result['agent_label']} ({result['channel_name']})")
print(f"  Session: {result['agent_session'][:30]}...")

# Test 2: Sigma Chat (Sigma)
print("\nTest 2: #sigma-chat -> Sigma")
result = route_message(
    channel_id="1468088770996867228",
    message="Add a new task",
    author_id="296511082745298944"
)
assert result["routed"] == True
assert result["agent_label"] == "Sigma"
assert "5480d04d" in result["agent_session"]
print(f"  Result: {result['agent_label']} ({result['channel_name']})")
print(f"  Session: {result['agent_session'][:30]}...")

# Test 3: Unknown channel -> main
print("\nTest 3: #general -> main")
result = route_message(
    channel_id="1423444490689056939",
    message="Hello everyone"
)
assert result["routed"] == False
assert result["fallback_to"] == "main"
print(f"  Result: fallback to {result['fallback_to']}")

print("\n=== All tests passed! ===")
print("\nRouting Summary:")
print("  #empty-set-chat (1468088770065862822) -> RAWRity's agent")
print("  #sigma-chat (1468088770996867228) -> Sigma's agent")
print("  Other channels -> Main OpenClaw")
