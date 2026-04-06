#!/usr/bin/env python3
"""Query RAWRity's personal memory for portfolio content."""

import sys
sys.path.insert(0, 'projects/personal-memory-mcp-docker')
from bridge import rawrity
import json

def main():
    # Career info
    print("=== CAREER SUMMARY ===")
    career = rawrity.get_personal_info('career')
    if career.get('found'):
        print(json.dumps(career['value'], indent=2))
    
    # Work history
    print("\n=== WORK HISTORY ===")
    work = rawrity.get_personal_info('work')
    if work.get('found'):
        print(json.dumps(work['value'], indent=2))
    
    # Skills
    print("\n=== SKILLS ===")
    skills = rawrity.get_personal_info('skills')
    if skills.get('found'):
        print(json.dumps(skills['value'], indent=2))
    
    # Search for project-related memories
    print("\n=== PROJECT MEMORIES ===")
    try:
        all_memories = rawrity.get_all_memories(limit=50)
        if isinstance(all_memories, list):
            for m in all_memories:
                key = m.get('key', '')
                if any(word in key.lower() for word in ['project', 'work', 'job', 'company', 'studio']):
                    print(f"\n{key}:")
                    val = m.get('value', '')
                    if isinstance(val, str):
                        print(f"  {val[:200]}" if len(val) > 200 else f"  {val}")
                    else:
                        print(f"  {json.dumps(val, indent=2)}")
    except Exception as e:
        print(f"Error listing memories: {e}")
    
    # Relationships
    print("\n=== RELATIONSHIPS ===")
    try:
        rels = rawrity.get_relationships('Steel Wool Studios')
        print(json.dumps(rels, indent=2) if rels else "No relationships found")
    except:
        pass

if __name__ == "__main__":
    main()
