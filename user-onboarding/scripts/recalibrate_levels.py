#!/usr/bin/env python3
"""
Level Recalibration Script

Recalculates all users' levels based on current leveling configuration.
Useful when thresholds change or when adopting the leveling system retroactively.

Usage:
    python recalibrate_levels.py [--dry-run] [--users rawrity sigma default]
"""

import sys
import json
from pathlib import Path

# Add Simple Graph MCP to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "projects" / "simple-graph-mcp"))
sys.path.insert(0, str(Path(__file__).parent))

from simple_graph_adapter import SimpleGraphOnboardingAdapter, load_leveling_config


def recalibrate_user(username, dry_run=False):
    """
    Recalculate level for a single user
    
    Args:
        username: User to recalibrate
        dry_run: If True, only show what would change, don't apply
    
    Returns:
        dict: Recalibration results
    """
    print(f"\n{'='*60}")
    print(f"Recalibrating: {username}")
    print(f"{'='*60}")
    
    adapter = SimpleGraphOnboardingAdapter(username)
    
    # Get current stats
    stats = adapter.get_user_stats()
    config = load_leveling_config()
    scoring = config.get('scoring', {})
    type_weights = scoring.get('node_type_weights', {})
    
    # Calculate new score
    score = adapter.calculate_weighted_score(
        stats['nodes_by_type'],
        stats['relationships_count'],
        type_weights
    )
    
    # Calculate new level
    new_level, new_title, new_desc, next_threshold = adapter.calculate_level(score)
    
    # Get current level - use get_entity for exact name match instead of search_text
    person_name = adapter._get_person_name()
    result = adapter.client.get_entity(person_name)
    
    if result.get("error"):
        print(f"[ERROR] Person entity not found for {username}: {result.get('error')}")
        return None
    
    props = result.get("properties", {})
    current_level = props.get("level", 1)
    current_title = props.get("level_title", "Seeker")
    
    print(f"Current: Level {current_level} — {current_title}")
    print(f"New:     Level {new_level} — {new_title}")
    print(f"Score:   {score:.1f} points")
    
    # Check retroactive settings
    retro_config = config.get('retroactive', {})
    preserve_highest = retro_config.get('preserve_highest', True)
    
    # Determine final level
    if preserve_highest and current_level > new_level:
        final_level = current_level
        final_title = current_title
        action = "PRESERVED (no demotion)"
    elif new_level > current_level:
        final_level = new_level
        final_title = new_title
        action = "LEVEL UP"
    else:
        final_level = new_level
        final_title = new_title
        action = "UNCHANGED"
    
    print(f"Action:  {action}")
    
    if not dry_run and action != "UNCHANGED":
        # Apply changes
        adapter.client.add_entity(
            person_name,
            "Person",
            {
                **props,
                "level": final_level,
                "level_title": final_title,
                "score": score,
                "nodes_by_type": json.dumps(stats['nodes_by_type']),
                "relationships_count": stats['relationships_count'],
                "leveling_version": config.get("version", "1.0")
            }
        )
        print(f"[OK] Updated {username} to Level {final_level}")
    elif dry_run:
        print(f"[DRY RUN] Would update {username} to Level {final_level}")
    else:
        print(f"[OK] No changes needed")
    
    return {
        "username": username,
        "previous_level": current_level,
        "new_level": final_level,
        "action": action,
        "score": score,
        "nodes": sum(stats['nodes_by_type'].values()),
        "relationships": stats['relationships_count']
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Recalculate user levels based on current configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python recalibrate_levels.py --dry-run
      Show what would change without applying
      
  python recalibrate_levels.py --users rawrity sigma
      Recalibrate specific users
      
  python recalibrate_levels.py
      Recalibrate all users (rawrity, sigma, default)
        """
    )
    
    parser.add_argument('--dry-run', '-n', action='store_true',
                        help='Show changes without applying')
    parser.add_argument('--users', '-u', nargs='+',
                        default=['rawrity', 'sigma', 'default'],
                        help='Users to recalibrate (default: all)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("LEVEL RECALIBRATION")
    print("="*60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Users: {', '.join(args.users)}")
    
    # Load and display config
    config = load_leveling_config()
    print(f"Config version: {config.get('version', 'unknown')}")
    
    results = []
    for username in args.users:
        result = recalibrate_user(username, dry_run=args.dry_run)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    level_ups = [r for r in results if r['action'] == "LEVEL UP"]
    preserved = [r for r in results if r['action'] == "PRESERVED (no demotion)"]
    unchanged = [r for r in results if r['action'] == "UNCHANGED"]
    
    print(f"Level ups: {len(level_ups)}")
    for r in level_ups:
        print(f"  {r['username']}: Level {r['previous_level']} -> {r['new_level']}")
    
    print(f"Preserved (no demotion): {len(preserved)}")
    for r in preserved:
        print(f"  {r['username']}: Level {r['previous_level']} (would have been {r['new_level']})")
    
    print(f"Unchanged: {len(unchanged)}")
    for r in unchanged:
        print(f"  {r['username']}: Level {r['new_level']}")
    
    print("\n" + "="*60)
    if args.dry_run:
        print("This was a DRY RUN. No changes were made.")
        print("Run without --dry-run to apply changes.")
    else:
        print("Recalibration complete.")
    print("="*60)


if __name__ == "__main__":
    main()
