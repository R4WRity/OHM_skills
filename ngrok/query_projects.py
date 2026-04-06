#!/usr/bin/env python3
"""Search for more project/achievement data."""

import sys
sys.path.insert(0, 'projects/personal-memory-mcp-docker')
from bridge import rawrity
import json

def main():
    # Search for various keywords
    searches = ['FNAF', 'Five Nights', 'VR', 'game', 'character', 'exhibit', 'published', 'released']
    
    found_memories = []
    
    for term in searches:
        try:
            results = rawrity.search_memories(query=term, limit=5)
            if results:
                for r in results:
                    key = r.get('key', '')
                    if key and key not in [m['key'] for m in found_memories]:
                        found_memories.append(r)
        except:
            pass
    
    print(f"Found {len(found_memories)} unique memories:\n")
    
    for m in found_memories:
        key = m.get('key', '')
        val = m.get('value', '')
        print(f"{key}:")
        if isinstance(val, str):
            print(f"  {val[:300]}..." if len(val) > 300 else f"  {val}")
        else:
            print(f"  {json.dumps(val, indent=2)}")
        print()

if __name__ == "__main__":
    main()
