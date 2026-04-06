#!/usr/bin/env python3
"""
Discord Message Sender Tool
Sends messages to Discord channels via bot

Usage:
    python send_discord_message.py <channel_id> <message>
    
Example:
    python send_discord_message.py 1468088770996867228 "Hello Sigma!"
"""

import discord
import asyncio
import sys
import json
from pathlib import Path

def load_discord_token():
    """Load Discord bot token from openclaw.json"""
    config_path = Path(r"C:\Users\OHM\.openclaw\openclaw.json")
    
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        token = config.get("channels", {}).get("discord", {}).get("token")
        if not token:
            print("Error: Discord token not found in openclaw.json")
            return None
        
        return token
    except Exception as e:
        print(f"Error reading config: {e}")
        return None

async def send_to_channel(channel_id: str, message: str):
    """Send message to Discord channel"""
    token = load_discord_token()
    if not token:
        return False
    
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.messages = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        try:
            channel = client.get_channel(int(channel_id))
            
            if channel:
                # Split long messages (Discord 2000 char limit)
                if len(message) > 2000:
                    chunks = [message[i:i+2000] for i in range(0, len(message), 2000)]
                    for chunk in chunks:
                        await channel.send(chunk)
                else:
                    await channel.send(message)
                
                print(f"✓ Message sent to channel {channel_id}")
                print(f"  Channel: {channel.name} (type: {type(channel).__name__})")
            else:
                print(f"✗ Channel {channel_id} not found")
                print(f"  Bot is in {len(client.guilds)} guilds:")
                for guild in client.guilds:
                    print(f"    - {guild.name} (ID: {guild.id})")
        except Exception as e:
            print(f"✗ Error sending message: {e}")
        finally:
            await client.close()
    
    try:
        await client.start(token)
        return True
    except Exception as e:
        print(f"✗ Client error: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Discord Message Sender")
        print("=" * 60)
        print("\nUsage:")
        print("  python send_discord_message.py <channel_id> <message>")
        print("\nExamples:")
        print("  python send_discord_message.py 1468088770996867228 \"Hello Sigma!\"")
        print("  python send_discord_message.py 1468027295670206545 \"Test message\"")
        print("\nKnown Channels:")
        print("  - Sigma's chat: 1468088770996867228")
        print("  - RAWRity's chat: 1468088770065862822")
        print("  - Server channel: 1468027295670206545")
        sys.exit(1)
    
    channel_id = sys.argv[1]
    message = " ".join(sys.argv[2:])
    
    print(f"Sending to channel {channel_id}...")
    # Encode message for safe printing (Windows console emoji issues)
    safe_message = message.encode('cp1252', errors='replace').decode('cp1252')
    print(f"Message: {safe_message[:100]}...")
    print()
    
    success = asyncio.run(send_to_channel(channel_id, message))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
