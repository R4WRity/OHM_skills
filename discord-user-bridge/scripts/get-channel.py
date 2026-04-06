#!/usr/bin/env python3
"""
Discord User Bridge - Helper script for cross-user messaging
Simple wrapper to validate and send messages between user channels
"""

import argparse
import sys

# Channel mappings
CHANNELS = {
    "RAWRity": "1468088770065862822",
    "rawrity": "1468088770065862822",
    "∅": "1468088770065862822",
    "Sigma": "1468088770996867228",
    "sigma": "1468088770996867228",
    "Σ": "1468088770996867228",
}

def get_channel_id(user: str) -> str | None:
    """Get channel ID for a user name/alias"""
    return CHANNELS.get(user)

def main():
    parser = argparse.ArgumentParser(description="Discord User Bridge Helper")
    parser.add_argument("user", help="Target user (RAWRity, Sigma, ∅, or Σ)")
    parser.add_argument("--validate", action="store_true", help="Just validate the user/channel")
    
    args = parser.parse_args()
    
    channel_id = get_channel_id(args.user)
    
    if not channel_id:
        print(f"Error: Unknown user '{args.user}'", file=sys.stderr)
        print(f"Known users: {', '.join(CHANNELS.keys())}", file=sys.stderr)
        sys.exit(1)
    
    if args.validate:
        print(f"OK: User '{args.user}' -> Channel {channel_id}")
        sys.exit(0)
    
    print(channel_id)

if __name__ == "__main__":
    main()
