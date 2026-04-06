#!/usr/bin/env python3
"""
Update THE GEAR page with comprehensive content.
Usage: python notion_update_gear.py <page_id>
"""

import argparse
import json
import os
import sys
import urllib.request

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

def get_token():
    token = os.environ.get('NOTION_TOKEN')
    if token:
        return token
    config_path = os.path.expanduser('~/.openclaw/openclaw.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('notion', {}).get('token')
        except Exception:
            pass
    print("Error: Notion token not configured.", file=sys.stderr)
    sys.exit(1)

def add_blocks(page_id, blocks):
    token = get_token()
    url = f"{NOTION_API_BASE}/blocks/{page_id}/children"
    
    data = json.dumps({"children": blocks}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Notion-Version': NOTION_VERSION,
            'Content-Type': 'application/json'
        },
        method='PATCH'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"API Error: {e.code} - {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)

def heading1(text):
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def heading2(text):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def heading3(text):
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def paragraph(text, bold=False):
    rt = {"type": "text", "text": {"content": text}}
    if bold:
        rt["annotations"] = {"bold": True}
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [rt]}}

def bullet(text):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def callout(text, emoji="💡"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": text}}], "icon": {"type": "emoji", "emoji": emoji}}}

def main():
    parser = argparse.ArgumentParser(description='Update THE GEAR page')
    parser.add_argument('--page-id', default='e8a125eb-b866-4571-ade7-cb932b1229b0', help='Page ID')
    args = parser.parse_args()
    
    page_id = args.page_id.replace('-', '')
    total_added = 0
    
    # Batch 1: Overview + EHX Tuner + Slammi
    batch1 = [
        divider(),
        heading2("📊 Signal Chain Overview"),
        paragraph("Signal flow: Tuner → Octaver/Wah → Compressor → Overdrive → Delay → Reverb → Looper"),
        paragraph("Total current draw: ~487mA"),
        heading3("Recommended Signal Chain Order"),
        bullet("Tuner first for clean entry and mute functionality"),
        bullet("Pitch effects (Slammi) early for tracking clarity"),
        bullet("Compression before drive for singing sustain"),
        bullet("Modulation/time-based effects after dirt (cleaner repeats)"),
        bullet("Reverb after delay for washing effect"),
        bullet("Looper last to capture full effected signal"),
        
        divider(),
        
        # EHX Tuner
        heading2("1. Electro Harmonix Tuner"),
        paragraph("Type: Chromatic Tuner | Position: First in chain", bold=True),
        heading3("Purpose"),
        bullet("Clean signal entry point for accurate tuning"),
        bullet("Mutes signal when tuning active (true bypass)"),
        bullet("Reference pitch standard (A440)"),
        heading3("Key Features"),
        bullet("Chromatic range: A0 to C8"),
        bullet("LED display with cents deviation"),
        bullet("True bypass switching"),
        callout("Always stays in standby until needed. First position ensures cleanest signal."),
        
        divider(),
        
        # EHX Slammi
        heading2("2. Electro Harmonix Slammi Plus"),
        paragraph("Type: Polyphonic Octaver / Expression Wah", bold=True),
        heading3("Purpose"),
        bullet("Pitch manipulation (octave up/down)"),
        bullet("Expression-controlled filter sweeps"),
        bullet("Synthetic textures and organ-like sounds"),
        heading3("Three Modes"),
        bullet("Up: Adds octave above"),
        bullet("Down: Adds octave below"),
        bullet("Both: Simultaneous up+down octaves (organ effect)"),
        heading3("Key Controls"),
        bullet("Blend: Dry/wet mix ratio"),
        bullet("Range: Sweep width for expression"),
        bullet("Expression pedal input for real-time control"),
        callout("Excellent before reverb/delay for cavernous drones. Polyphonic tracking handles chords."),
    ]
    
    print(f"Adding batch 1 ({len(batch1)} blocks)...")
    result = add_blocks(page_id, batch1)
    total_added += len(result.get('results', []))
    print(f"✓ Added {len(result.get('results', []))} blocks")
    
    # Batch 2: Walrus Mira + 385
    batch2 = [
        divider(),
        
        # Walrus Mira
        heading2("3. Walrus Audio Mira"),
        paragraph("Type: Optical Studio-Grade Compressor", bold=True),
        heading3("Purpose"),
        bullet("Dynamic control and sustain enhancement"),
        bullet("Evening out attack for fingerstyle"),
        bullet("Adds subtle sustain without squashing"),
        heading3("Controls"),
        bullet("Sustain: Amount of compression (threshold + ratio)"),
        bullet("Attack: Speed compression engages"),
        bullet("Release: Speed compression lets go"),
        bullet("Blend: Parallel compression mix (dry/compressed)"),
        bullet("Volume: Output level makeup"),
        callout("Smooth, musical compression. Works as an 'always-on' pedal. Pairs beautifully with 385 for singing leads."),
        
        divider(),
        
        # Walrus 385
        heading2("4. Walrus Audio 385 Overdrive"),
        paragraph("Type: Medium-Gain Overdrive | Inspired by Bell & Howell 385 film projector", bold=True),
        heading3("Purpose"),
        bullet("Core dirt tone from edge of breakup to saturation"),
        bullet("Textured harmonics unique to this circuit"),
        heading3("Controls"),
        bullet("Gain: Overdrive amount"),
        bullet("Bass/Gain Toggle: Left=Low cut mode, Right=Secondary gain stage"),
        bullet("Tone: High-frequency roll-off"),
        bullet("Volume: Output level"),
        heading3("Recommended Settings"),
        bullet("Edge of breakup: Gain at 9-10 o'clock"),
        bullet("Mid-gain rhythm: Gain at 1-2 o'clock with Bass boost"),
        bullet("Sustained lead: Gain maxed, compressor feeding hot signal"),
        callout("Warm, slightly grainy overdrive that responds to guitar volume. Articulate chords stay clear."),
    ]
    
    print(f"Adding batch 2 ({len(batch2)} blocks)...")
    result = add_blocks(page_id, batch2)
    total_added += len(result.get('results', []))
    print(f"✓ Added {len(result.get('results', []))} blocks")
    
    # Batch 3: ARP-87 + Slö
    batch3 = [
        divider(),
        
        # ARP-87
        heading2("5. Walrus Audio ARP-87"),
        paragraph("Type: Multi-Mode Digital Delay | Tap Tempo", bold=True),
        heading3("Five Delay Modes"),
        bullet("Digital: Clean, pristine repeats"),
        bullet("Analog: Warm degradation with each repeat (tape-like)"),
        bullet("Lo-Fi: Bitcrushed, degraded texture"),
        bullet("Reverse: Backwards echo effect"),
        bullet("Slap: Short delay for rockabilly/country tones"),
        heading3("Key Controls"),
        bullet("Time: Delay time or tap tempo"),
        bullet("Repeats: Feedback (1 repeat to self-oscillation)"),
        bullet("Mix: Wet/dry blend"),
        bullet("Dampen: High-frequency roll-off on repeats"),
        bullet("Tails switch: Continue trails after bypass"),
        callout("Lo-Fi + Slö Dark mode = degraded tape ambiance. Reverse for rhythmic patterns. Trails ON for ambient decays."),
        
        divider(),
        
        # Slö
        heading2("6. Walrus Audio Slö Multi-Texture Reverb"),
        paragraph("Type: Multi-Algorithm Reverb | Shimmer & Ambient Specialist", bold=True),
        heading3("Three Reverb Algorithms"),
        bullet("Dark: Lower octave added to tail (sub-octave shimmer)"),
        bullet("Rise: Auto-swell reverb (attack blooms to full volume)"),
        bullet("Dream: Upper octave shimmer with infinite pad capability"),
        heading3("Controls"),
        bullet("Depth: Modulation intensity"),
        bullet("Blend: Wet/dry mix"),
        bullet("Time: Decay length"),
        bullet("Filter: Tone shaping for tail"),
        bullet("X: Mode-specific (octave blend / swell time / shimmer interval)"),
        heading3("Hidden Feature"),
        bullet("Hold footswitch in Dream mode to latch infinite pad"),
        callout("Dream mode = 'church organ in space.' Rise mode for swells. Layer with ARP-87 for cavernous depth."),
    ]
    
    print(f"Adding batch 3 ({len(batch3)} blocks)...")
    result = add_blocks(page_id, batch3)
    total_added += len(result.get('results', []))
    print(f"✓ Added {len(result.get('results', []))} blocks")
    
    # Batch 4: Looper + Power + Wishlist + Combinations
    batch4 = [
        divider(),
        
        # 360 Looper
        heading2("7. Electro Harmonix 360 Looper"),
        paragraph("Type: Stereo Looper | 6 Minutes Recording", bold=True),
        heading3("Specifications"),
        bullet("6 minutes stereo recording time"),
        bullet("Unlimited overdubs"),
        bullet("Half-speed and reverse playback"),
        bullet("Undo/Redo functionality"),
        bullet("Stereo in/out"),
        heading3("Operation"),
        bullet("Tap once: Record"),
        bullet("Tap again: Stop recording, start playback"),
        bullet("Tap again: Overdub layer"),
        bullet("Hold: Undo last layer"),
        bullet("Double-tap: Stop"),
        callout("Perfect for ambient layering with Slö + ARP-87. Half-speed = octave-down texture."),
        
        divider(),
        
        # Power Section
        heading2("⚡ Power Requirements"),
        paragraph("Current draw breakdown:", bold=True),
        bullet("EHX Tuner: ~50mA"),
        bullet("EHX Slammi: ~100mA"),
        bullet("Walrus Mira: ~45mA"),
        bullet("Walrus 385: ~22mA"),
        bullet("ARP-87: ~70mA"),
        bullet("Slö: ~100mA"),
        bullet("360 Looper: ~100mA"),
        paragraph("Total: ~487mA"),
        heading3("Power Solution"),
        bullet("Current: Daisy chain wall wart (potentially noisy)"),
        bullet("Upgrade needed: Isolated power supply"),
        bullet("Recommended: EHX Power Brick, Voodoo Lab, or Strymon"),
        callout("Isolated power eliminates ground loops and reduces noise. Essential for a clean 7-pedal board."),
    ]
    
    print(f"Adding batch 4 ({len(batch4)} blocks)...")
    result = add_blocks(page_id, batch4)
    total_added += len(result.get('results', []))
    print(f"✓ Added {len(result.get('results', []))} blocks")
    
    # Batch 5: Wishlist + Combinations + Footer
    batch5 = [
        divider(),
        
        # Wishlist
        heading2("🛍️ Wishlist"),
        heading3("Walrus Audio Fable (Granular Delay)"),
        bullet("Granular synthesis: chops audio into micro-samples"),
        bullet("Stutter effects and time manipulation"),
        bullet("Glitchy textures that complement ARP-87"),
        heading3("Chroma Console"),
        bullet("Multi-effect tone shaper"),
        bullet("Color/saturation/compression in one unit"),
        
        divider(),
        
        # Favorite Combinations
        heading2("🎛️ Notable Combinations"),
        bullet("Mira + 385: Singing lead tones with enhanced sustain"),
        bullet("Slammi (octave both) + Slö (Dream): Organ pad textures"),
        bullet("ARP-87 (Lo-Fi) + Slö (Dark): Degraded tape ambiance"),
        bullet("385 (edge of breakup) + ARP-87 (Analog): Classic rock slapback"),
        bullet("Everything + Looper: Ambient soundscape layering"),
        
        divider(),
        
        # Maintenance
        heading2("🔧 Maintenance Notes"),
        bullet("All Walrus pedals use soft-touch relay bypass (no pop)"),
        bullet("Keep pedals away from excessive heat"),
        bullet("Clean footswitches with contact cleaner annually"),
        bullet("Check patch cables quarterly for noise"),
        bullet("Verify power supply voltage and current capacity regularly"),
        
        divider(),
        
        paragraph("📅 Last Updated: February 26, 2026"),
        paragraph("📝 Document compiled from product manuals, reviews, and technical research."),
    ]
    
    print(f"Adding batch 5 ({len(batch5)} blocks)...")
    result = add_blocks(page_id, batch5)
    total_added += len(result.get('results', []))
    print(f"✓ Added {len(result.get('results', []))} blocks")
    
    print(f"\n✅ Success! Total blocks added: {total_added}")

if __name__ == '__main__':
    main()
