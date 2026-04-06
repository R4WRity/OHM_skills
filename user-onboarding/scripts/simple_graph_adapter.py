#!/usr/bin/env python3
"""
Simple Graph MCP Onboarding Adapter
Translates onboarding answers into Simple Graph entities/relationships
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add Simple Graph MCP to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "projects" / "simple-graph-mcp"))

from bridge import SimpleGraphClient

# User port mapping (matches load-user skill)
USER_PORTS = {
    "rawrity": 9301,   # Port 7687 Neo4j
    "sigma": 9302,     # Port 7787 Neo4j
    "default": 9300,   # Port 7887 Neo4j (Ohm)
}

# Load leveling configuration
LEVELING_CONFIG = None

def load_leveling_config():
    """Load leveling configuration from YAML"""
    global LEVELING_CONFIG
    if LEVELING_CONFIG is None:
        config_path = Path(__file__).parent.parent / "references" / "leveling-config.yaml"
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                LEVELING_CONFIG = config.get('leveling_system', {})
        except Exception as e:
            print(f"[WARN] Could not load leveling config: {e}")
            LEVELING_CONFIG = {}
    return LEVELING_CONFIG

class SimpleGraphOnboardingAdapter:
    """Adapter that stores onboarding data as entities/relationships"""
    
    def __init__(self, username):
        self.username = username
        self.port = USER_PORTS.get(username, 9300)
        self.client = SimpleGraphClient(f"http://localhost:{self.port}", group_id="default")
        
        # Ensure Person entity exists for this user
        self._ensure_user_entity()
    
    def _ensure_user_entity(self):
        """Create the Person entity for this user if not exists"""
        # Map usernames to real names
        name_map = {
            "rawrity": "Gerald Hardin",
            "sigma": "Uthara Thelagar",
            "default": "Ohm"
        }
        
        person_name = name_map.get(self.username, self.username)
        
        # Check if exists using get_entity for exact match
        result = self.client.get_entity(person_name)
        if not result.get("error"):
            print(f"[OK] Person entity exists: {person_name}")
            # Check if Person has level fields, if not add them
            props = result.get("properties", {})
            if "level" not in props:
                # Initialize leveling fields
                self.client.add_entity(
                    person_name,
                    "Person",
                    {
                        "username": self.username,
                        "source": "onboarding",
                        "level": 1,
                        "level_title": "Seeker",
                        "score": 0,
                        "nodes_by_type": json.dumps({}),
                        "relationships_count": 0,
                        "leveling_version": "1.0"
                    }
                )
                print(f"[OK] Initialized leveling fields for {person_name}")
        else:
            # Create Person entity with leveling fields
            result = self.client.add_entity(
                person_name,
                "Person",
                {
                    "username": self.username,
                    "source": "onboarding",
                    "level": 1,
                    "level_title": "Seeker",
                    "score": 0,
                    "nodes_by_type": json.dumps({}),
                    "relationships_count": 0,
                    "leveling_version": "1.0"
                }
            )
            if "uuid" in result:
                print(f"[OK] Created Person entity: {person_name} (Level 1 - Seeker)")
            else:
                print(f"[FAIL] Could not create Person: {result}")
    
    def store_answer(self, category, key, answer, answer_type="preference"):
        """
        Store an onboarding answer as entities/relationships
        
        Args:
            category: Question category (food, travel, professional, etc.)
            key: Storage key (e.g., "cuisine_preferences")
            answer: User's answer text
            answer_type: Type of answer (preference, memory, goal, etc.)
        """
        person_name = self._get_person_name()
        
        # Create a Memory entity for this answer
        memory_name = f"{person_name} - {key}"
        memory_result = self.client.add_entity(
            memory_name,
            "Memory",
            {
                "category": category,
                "key": key,
                "answer": answer,
                "type": answer_type,
                "source": "onboarding"
            }
        )
        
        if "uuid" not in memory_result:
            print(f"[FAIL] Could not create memory: {memory_result}")
            return False
        
        # Link person to this memory
        self.client.add_relation(person_name, memory_name, "HAS_MEMORY")
        
        # Extract and create entities from the answer
        self._extract_and_link_entities(person_name, category, key, answer, answer_type)
        
        # Check for level up
        self.check_level_up()
        
        print(f"[OK] Stored {category}/{key} for {person_name}")
        return True
    
    def _get_person_name(self):
        """Get the person's real name from username"""
        name_map = {
            "rawrity": "Gerald Hardin",
            "sigma": "Uthara Thelagar",
            "default": "Ohm"
        }
        return name_map.get(self.username, self.username)
    
    # === PROGRESS TRACKING FOR STOP/RESUME ===
    
    def get_progress_entity_name(self, mode):
        """Get the unique entity name for onboarding progress"""
        person_name = self._get_person_name()
        return f"{person_name} - OnboardingProgress - {mode}"
    
    def save_progress(self, mode, current_question_num, completed_categories, remaining_categories, status='active'):
        """
        Save onboarding progress to Simple Graph MCP
        
        Args:
            mode: 'quick', 'full', or 'custom'
            current_question_num: Last question answered (0-indexed)
            completed_categories: List of categories completed
            remaining_categories: List of categories remaining
            status: 'active', 'paused', or 'completed'
        """
        entity_name = self.get_progress_entity_name(mode)
        person_name = self._get_person_name()
        
        # Create or update progress entity
        result = self.client.add_entity(
            entity_name,
            "OnboardingProgress",
            {
                "mode": mode,
                "username": self.username,
                "last_question_num": current_question_num,
                "completed_categories": json.dumps(completed_categories),
                "remaining_categories": json.dumps(remaining_categories),
                "status": status,
                "updated_at": json.dumps({"timestamp": str(__import__('datetime').datetime.now(__import__('datetime').timezone.utc))})
            }
        )
        
        # Ensure relationship to person exists
        self.client.add_relation(person_name, entity_name, "HAS_ONBOARDING_PROGRESS")
        
        if "uuid" in result:
            print(f"[OK] Progress saved: {mode} - question {current_question_num}, status: {status}")
            return True
        else:
            print(f"[FAIL] Could not save progress: {result}")
            return False
    
    def get_progress(self, mode):
        """
        Retrieve saved progress for a mode
        
        Returns:
            dict with progress data or None if not found
        """
        entity_name = self.get_progress_entity_name(mode)
        
        # Search for the progress entity
        result = self.client.search_text(entity_name, limit=1)
        
        if not result.get("results"):
            return None
        
        # Get the entity details
        entity = result["results"][0]
        properties = entity.get("properties", {})
        
        return {
            "mode": properties.get("mode", mode),
            "last_question_num": properties.get("last_question_num", 0),
            "completed_categories": json.loads(properties.get("completed_categories", "[]")),
            "remaining_categories": json.loads(properties.get("remaining_categories", "[]")),
            "status": properties.get("status", "unknown"),
            "entity_name": entity_name
        }
    
    def has_active_progress(self, mode):
        """Check if there's a paused/in-progress session for this mode"""
        progress = self.get_progress(mode)
        if not progress:
            return False
        return progress.get("status") in ["active", "paused"]
    
    def mark_completed(self, mode):
        """Mark an onboarding session as completed"""
        entity_name = self.get_progress_entity_name(mode)
        
        # Update the entity to mark as completed
        # Note: Simple Graph MCP may need an update_entity method
        # For now, we'll create a new entity with completed status
        progress = self.get_progress(mode)
        if progress:
            return self.save_progress(
                mode,
                progress.get("last_question_num", 0),
                progress.get("completed_categories", []),
                [],  # No remaining categories
                status="completed"
            )
        return False
    
    def clear_progress(self, mode):
        """Delete progress tracking for a mode (start fresh)"""
        entity_name = self.get_progress_entity_name(mode)
        # Note: This would require a delete_entity method in SimpleGraphClient
        # For now, we just mark it as abandoned
        progress = self.get_progress(mode)
        if progress:
            return self.save_progress(
                mode,
                progress.get("last_question_num", 0),
                progress.get("completed_categories", []),
                progress.get("remaining_categories", []),
                status="abandoned"
            )
        return True
    
    def get_all_progress(self):
        """Get all onboarding progress for this user across all modes"""
        person_name = self._get_person_name()
        
        # Search for all OnboardingProgress entities
        result = self.client.search_text("OnboardingProgress", limit=10)
        
        progress_list = []
        for entity in result.get("results", []):
            props = entity.get("properties", {})
            if props.get("username") == self.username:
                progress_list.append({
                    "mode": props.get("mode"),
                    "status": props.get("status"),
                    "completed_count": len(json.loads(props.get("completed_categories", "[]"))),
                    "remaining_count": len(json.loads(props.get("remaining_categories", "[]"))),
                    "entity_name": entity.get("name")
                })
        
        return progress_list
    
    # === LEVELING SYSTEM ===
    
    def _get_leveling_config(self):
        """Get loaded leveling configuration"""
        return load_leveling_config()
    
    def calculate_weighted_score(self, nodes_count, relationships_count, node_weights):
        """
        Calculate weighted score based on leveling configuration
        
        Args:
            nodes_count: Dict of {entity_type: count}
            relationships_count: Total relationships
            node_weights: Dict of entity_type weights
        
        Returns:
            float: Weighted score
        """
        config = self._get_leveling_config()
        scoring = config.get('scoring', {})
        type_weights = scoring.get('node_type_weights', {})
        rel_weight = scoring.get('relationship_weight', 0.75)
        
        # Calculate node score
        node_score = 0
        for entity_type, count in nodes_count.items():
            weight = type_weights.get(entity_type, 1.0)
            node_score += count * weight
        
        # Add relationship score
        relationship_score = relationships_count * rel_weight
        
        return node_score + relationship_score
    
    def get_user_stats(self):
        """
        Get entity counts for user from Neo4j
        
        Returns:
            dict: {nodes_by_type: {}, relationships_count: int}
        """
        person_name = self._get_person_name()
        
        # Query Neo4j directly via the bridge's underlying client
        # This requires Neo4j client access
        from neo4j import GraphDatabase
        
        # Get Neo4j connection info from environment or config
        # For now, use default Neo4j ports per user
        neo4j_ports = {
            "rawrity": 7687,
            "sigma": 7787,
            "default": 7887
        }
        neo4j_port = neo4j_ports.get(self.username, 7887)
        
        try:
            driver = GraphDatabase.driver(f"bolt://localhost:{neo4j_port}", 
                                         auth=("neo4j", "demodemo"))
            
            with driver.session() as session:
                # Count nodes by type linked to this person
                # Simple Graph MCP uses :Entity label with entity_type property
                result = session.run("""
                    MATCH (p:Entity {entity_type: 'Person', name: $person_name})-[r]-(n)
                    RETURN n.entity_type as node_type, count(n) as count
                """, person_name=person_name)
                
                nodes_by_type = {}
                for record in result:
                    node_type = record['node_type'] or 'Entity'
                    nodes_by_type[node_type] = nodes_by_type.get(node_type, 0) + record['count']
                
                # Count relationships
                result = session.run("""
                    MATCH (p:Entity {entity_type: 'Person', name: $person_name})-[r]-()
                    RETURN count(r) as rel_count
                """, person_name=person_name)
                
                relationships_count = result.single()['rel_count']
            
            driver.close()
            
            return {
                'nodes_by_type': nodes_by_type,
                'relationships_count': relationships_count
            }
            
        except Exception as e:
            print(f"[WARN] Could not query Neo4j stats: {e}")
            return {'nodes_by_type': {}, 'relationships_count': 0}
    
    def calculate_level(self, score):
        """
        Determine level based on score and thresholds
        
        Args:
            score: Weighted score
        
        Returns:
            tuple: (level, title, description, next_threshold)
        """
        config = self._get_leveling_config()
        thresholds = config.get('thresholds', [])
        
        current_level = 1
        current_title = "Seeker"
        current_desc = "Beginning the journey"
        next_threshold = 5
        
        for threshold in thresholds:
            if score >= threshold['min_score']:
                current_level = threshold['level']
                current_title = threshold['title']
                current_desc = threshold.get('description', '')
                # Next threshold is the next level's min_score, or None if max
                next_idx = thresholds.index(threshold) + 1
                if next_idx < len(thresholds):
                    next_threshold = thresholds[next_idx]['min_score']
                else:
                    next_threshold = None
        
        return current_level, current_title, current_desc, next_threshold
    
    def check_level_up(self):
        """
        Check if user has leveled up and update Person entity
        
        Returns:
            dict or None: Level up info if leveled up, None otherwise
        """
        person_name = self._get_person_name()
        
        # Get current stats
        stats = self.get_user_stats()
        nodes_by_type = stats['nodes_by_type']
        relationships_count = stats['relationships_count']
        
        # Calculate weighted score
        config = self._get_leveling_config()
        scoring = config.get('scoring', {})
        type_weights = scoring.get('node_type_weights', {})
        
        score = self.calculate_weighted_score(nodes_by_type, relationships_count, type_weights)
        
        # Calculate new level
        new_level, new_title, new_desc, next_threshold = self.calculate_level(score)
        
        # Get current level from Person entity
        result = self.client.search_text(person_name, limit=1)
        if result.get("results"):
            person = result["results"][0]
            props = person.get("properties", {})
            current_level = props.get("level", 1)
            
            # Check if leveled up
            if new_level > current_level:
                # Update Person entity with new level
                # Note: This creates a new entity with updated properties
                # In production, would want an update_entity method
                self.client.add_entity(
                    person_name,
                    "Person",
                    {
                        **props,
                        "level": new_level,
                        "level_title": new_title,
                        "score": score,
                        "nodes_by_type": json.dumps(nodes_by_type),
                        "relationships_count": relationships_count,
                        "last_level_up": str(datetime.now(timezone.utc)),
                        "leveling_version": config.get("version", "1.0")
                    }
                )
                
                level_up_info = {
                    "leveled_up": True,
                    "old_level": current_level,
                    "new_level": new_level,
                    "title": new_title,
                    "description": new_desc,
                    "score": score,
                    "next_threshold": next_threshold,
                    "nodes_by_type": nodes_by_type,
                    "relationships_count": relationships_count
                }
                
                # Print notification
                print(f"\nLEVEL UP! {person_name} reached Level {new_level} — {new_title}")
                print(f"   {new_desc}")
                print(f"   Score: {score:.1f} points")
                
                return level_up_info
        
        return None
    
    def get_level_progress(self):
        """
        Get current level progress for user
        
        Returns:
            dict: Level info and progress
        """
        stats = self.get_user_stats()
        score = self.calculate_weighted_score(
            stats['nodes_by_type'], 
            stats['relationships_count'],
            {}
        )
        
        level, title, desc, next_threshold = self.calculate_level(score)
        
        return {
            "level": level,
            "title": title,
            "description": desc,
            "score": score,
            "next_threshold": next_threshold,
            "nodes_by_type": stats['nodes_by_type'],
            "relationships_count": stats['relationships_count']
        }
    
    def _extract_and_link_entities(self, person_name, category, key, answer, answer_type):
        """Extract entities from answer and create relationships"""
        
        # Food category extraction
        if category == "food":
            # Extract cuisines
            cuisines = self._extract_cuisines(answer)
            for cuisine in cuisines:
                cuisine_entity = f"Cuisine - {cuisine}"
                self.client.add_entity(cuisine_entity, "Cuisine", {"name": cuisine})
                self.client.add_relation(person_name, cuisine_entity, "LIKES_CUISINE")
            
            # Extract dishes
            dishes = self._extract_dishes(answer)
            for dish in dishes:
                dish_entity = f"Dish - {dish}"
                self.client.add_entity(dish_entity, "Dish", {"name": dish})
                self.client.add_relation(person_name, dish_entity, "LIKES_DISH")
        
        # Travel category extraction
        elif category == "travel":
            places = self._extract_places(answer)
            for place in places:
                place_entity = f"Place - {place}"
                self.client.add_entity(place_entity, "Place", {"name": place})
                self.client.add_relation(person_name, place_entity, "VISITED")
        
        # Professional category
        elif category == "professional":
            # Could extract companies, roles, etc.
            pass
        
        # Trigger n8n leveling recalculation after adding entities
        self._trigger_n8n_leveling()
    
    def _trigger_n8n_leveling(self):
        """Trigger n8n workflow to recalculate levels for all users"""
        try:
            import httpx
            url = "http://localhost:5678/webhook/leveling-recalculate"
            response = httpx.post(url, timeout=10.0)
            if response.status_code == 200:
                print("[Leveling] Triggered recalculation for all users")
            else:
                print(f"[Leveling] Webhook returned {response.status_code}")
        except Exception as e:
            # Don't fail the operation if leveling trigger fails
            print(f"[Leveling] Could not trigger recalculation: {e}")
    
    def _extract_cuisines(self, text):
        """Extract cuisine types from text"""
        cuisines = []
        cuisine_keywords = [
            "japanese", "chinese", "italian", "mexican", "thai", "indian",
            "korean", "vietnamese", "french", "mediterranean", "greek",
            "middle eastern", "ethiopian", "brazilian", "peruvian"
        ]
        text_lower = text.lower()
        for cuisine in cuisine_keywords:
            if cuisine in text_lower:
                cuisines.append(cuisine.title())
        return cuisines
    
    def _extract_dishes(self, text):
        """Extract dish names from text"""
        # Simple extraction - could be enhanced with NLP
        dishes = []
        dish_keywords = [
            "sushi", "ramen", "pizza", "pasta", "tacos", "burrito",
            "curry", "pad thai", "pho", "burger", "steak", "salad"
        ]
        text_lower = text.lower()
        for dish in dish_keywords:
            if dish in text_lower:
                dishes.append(dish.title())
        return dishes
    
    def _extract_places(self, text):
        """Extract place names from text"""
        # Simple extraction - could use NER in production
        places = []
        # Look for capitalized phrases that might be places
        import re
        # Match patterns like "Tokyo, Japan" or "Paris"
        place_pattern = r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+)?)'
        matches = re.findall(place_pattern, text)
        for match in matches:
            if len(match) > 3 and match not in ['The', 'This', 'That', 'What', 'When', 'Where', 'There']:
                places.append(match)
        return list(set(places))[:5]  # Limit to 5 unique places


def main():
    """CLI for the adapter - supports storing answers and progress management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Graph Onboarding Adapter')
    parser.add_argument('--user', '-u', required=True, help='Username (rawrity, sigma, default)')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Store command (default/original behavior)
    store_parser = subparsers.add_parser('store', help='Store an onboarding answer')
    store_parser.add_argument('--category', '-c', required=True, help='Question category')
    store_parser.add_argument('--key', '-k', required=True, help='Storage key')
    store_parser.add_argument('--answer', '-a', required=True, help='User answer')
    store_parser.add_argument('--type', '-t', default='preference', help='Answer type')
    
    # Progress commands
    progress_parser = subparsers.add_parser('progress', help='Progress management commands')
    progress_subparsers = progress_parser.add_subparsers(dest='progress_command', help='Progress action')
    
    # Save progress
    save_prog = progress_subparsers.add_parser('save', help='Save current progress')
    save_prog.add_argument('--mode', '-m', required=True, choices=['quick', 'full', 'custom'], help='Onboarding mode')
    save_prog.add_argument('--question-num', '-n', type=int, required=True, help='Current question number')
    save_prog.add_argument('--completed', type=str, default='[]', help='JSON array of completed categories')
    save_prog.add_argument('--remaining', type=str, default='[]', help='JSON array of remaining categories')
    save_prog.add_argument('--status', '-s', default='active', choices=['active', 'paused', 'completed'], help='Progress status')
    
    # Get progress
    get_prog = progress_subparsers.add_parser('get', help='Get saved progress')
    get_prog.add_argument('--mode', '-m', required=True, choices=['quick', 'full', 'custom'], help='Onboarding mode')
    
    # List all progress
    progress_subparsers.add_parser('list', help='List all progress for user')
    
    # Check if active progress exists
    check_prog = progress_subparsers.add_parser('check', help='Check for active progress')
    check_prog.add_argument('--mode', '-m', required=True, choices=['quick', 'full', 'custom'], help='Onboarding mode')
    
    # Mark complete
    complete_prog = progress_subparsers.add_parser('complete', help='Mark onboarding as completed')
    complete_prog.add_argument('--mode', '-m', required=True, choices=['quick', 'full', 'custom'], help='Onboarding mode')
    
    # Clear progress
    clear_prog = progress_subparsers.add_parser('clear', help='Clear/abandon progress')
    clear_prog.add_argument('--mode', '-m', required=True, choices=['quick', 'full', 'custom'], help='Onboarding mode')
    
    # Level commands
    level_parser = subparsers.add_parser('level', help='Leveling system commands')
    level_subparsers = level_parser.add_subparsers(dest='level_command', help='Level action')
    
    # Check current level
    level_subparsers.add_parser('check', help='Check current level and progress')
    
    # Force recalculate
    level_subparsers.add_parser('recalc', help='Recalculate level based on current stats')
    
    args = parser.parse_args()
    
    # Initialize adapter
    adapter = SimpleGraphOnboardingAdapter(args.user)
    
    # Handle store command (default or explicit)
    if args.command == 'store' or args.command is None:
        if not hasattr(args, 'category') or args.category is None:
            parser.print_help()
            sys.exit(1)
        success = adapter.store_answer(args.category, args.key, args.answer, args.type)
        
        if success:
            print(f"\n[OK] Successfully stored onboarding data for {args.user}")
        else:
            print(f"\n[FAIL] Could not store onboarding data")
            sys.exit(1)
        return
    
    # Handle progress commands
    if args.command == 'progress':
        if args.progress_command == 'save':
            completed = json.loads(args.completed)
            remaining = json.loads(args.remaining)
            success = adapter.save_progress(args.mode, args.question_num, completed, remaining, args.status)
            if success:
                print(f"[OK] Progress saved for {args.mode} mode")
            else:
                sys.exit(1)
                
        elif args.progress_command == 'get':
            progress = adapter.get_progress(args.mode)
            if progress:
                print(json.dumps(progress, indent=2))
            else:
                print(f"[INFO] No progress found for {args.mode} mode")
                
        elif args.progress_command == 'list':
            all_prog = adapter.get_all_progress()
            if all_prog:
                print(f"[INFO] Onboarding progress for {args.user}:")
                for prog in all_prog:
                    print(f"  - {prog['mode']}: {prog['status']} ({prog['completed_count']} done, {prog['remaining_count']} remaining)")
            else:
                print(f"[INFO] No onboarding progress found for {args.user}")
                
        elif args.progress_command == 'check':
            has_active = adapter.has_active_progress(args.mode)
            print(json.dumps({"has_active_progress": has_active}))
            
        elif args.progress_command == 'complete':
            success = adapter.mark_completed(args.mode)
            if success:
                print(f"[OK] Marked {args.mode} as completed")
            else:
                print(f"[FAIL] Could not mark as completed")
                sys.exit(1)
                
        elif args.progress_command == 'clear':
            success = adapter.clear_progress(args.mode)
            if success:
                print(f"[OK] Cleared progress for {args.mode}")
            else:
                print(f"[FAIL] Could not clear progress")
                sys.exit(1)
        else:
            progress_parser.print_help()
    
    # Handle level commands
    if args.command == 'level':
        if args.level_command == 'check' or args.level_command is None:
            # Get level progress
            progress = adapter.get_level_progress()
            
            print(f"\nLevel Progress for {args.user}")
            print(f"   Level {progress['level']} — {progress['title']}")
            print(f"   {progress['description']}")
            print(f"\n   Score: {progress['score']:.1f} points")
            
            if progress['next_threshold']:
                remaining = progress['next_threshold'] - progress['score']
                print(f"   Next level: {progress['next_threshold']:.0f} points ({remaining:.1f} to go)")
            else:
                print(f"   Maximum level reached!")
            
            print(f"\n   Nodes by type:")
            for node_type, count in progress['nodes_by_type'].items():
                print(f"      {node_type}: {count}")
            print(f"   Relationships: {progress['relationships_count']}")
            
        elif args.level_command == 'recalc':
            # Force recalculation
            level_up = adapter.check_level_up()
            if level_up:
                print(f"\n🎉 Level recalculated!")
                print(f"   Level {level_up['new_level']} — {level_up['title']}")
                print(f"   Score: {level_up['score']:.1f} points")
            else:
                progress = adapter.get_level_progress()
                print(f"\n📊 Level unchanged: Level {progress['level']} — {progress['title']}")
                print(f"   Score: {progress['score']:.1f} points")
        else:
            level_parser.print_help()


if __name__ == "__main__":
    main()
