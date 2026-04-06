#!/usr/bin/env python3
"""Debug the user stats calculation"""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent.parent / "projects" / "simple-graph-mcp"))
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))

from simple_graph_adapter import SimpleGraphOnboardingAdapter

for username in ['rawrity', 'sigma']:
    print(f"\n{'='*60}")
    print(f"Testing: {username}")
    print('='*60)
    
    adapter = SimpleGraphOnboardingAdapter(username)
    
    # Test get_user_stats
    stats = adapter.get_user_stats()
    print(f"Stats: {stats}")
    
    # Get config
    config = adapter._get_leveling_config()
    scoring = config.get('scoring', {})
    type_weights = scoring.get('node_type_weights', {})
    
    # Calculate score
    score = adapter.calculate_weighted_score(
        stats['nodes_by_type'],
        stats['relationships_count'],
        type_weights
    )
    print(f"Calculated score: {score}")
