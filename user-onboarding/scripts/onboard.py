#!/usr/bin/env python3
"""
User Onboarding Script for Personal Memory MCP
Engages users in conversation to populate their personal memory servers.
Supports both raw and structured storage.
"""

import yaml
import random
import json
import sys
from pathlib import Path
from typing import Optional

# Add workspace to path for importing bridge and extractor
current_dir = Path(__file__).parent
workspace_root = current_dir.parent.parent.parent  # Go up to workspace root

# Add the projects directory directly
sys.path.insert(0, str(workspace_root / "projects" / "personal-memory-mcp-docker"))

from bridge import MemoryClient
from structured_extractor import extract_structured_fields


class OnboardingSession:
    """Manages a conversational onboarding session"""
    
    def __init__(self, mcp_client: MemoryClient, questions_file: str = None, structured: bool = False):
        self.client = mcp_client
        self.responses = {}
        self.structured = structured  # Enable structured extraction
        
        # Load questions from YAML
        if questions_file is None:
            questions_file = Path(__file__).parent.parent / "references" / "onboarding-questions.yaml"
        
        with open(questions_file, 'r', encoding='utf-8') as f:
            self.questions_catalog = yaml.safe_load(f)
    
    def get_random_question(self, category: str) -> Optional[dict]:
        """Get a random question from a category"""
        category_questions = [q for q in self.questions_catalog if q.get('category') == category]
        if not category_questions:
            return None
        
        question_data = random.choice(category_questions)
        question_text = random.choice(question_data['questions'])
        
        return {
            'text': question_text,
            'storage_key': question_data['storage_key'],
            'type': question_data['type'],
            'category': category
        }
    
    def store_answer(self, question_data: dict, answer: str) -> dict:
        """Store the answer in the appropriate MCP storage (raw + structured if enabled)"""
        storage_type = question_data['type']
        key = question_data['storage_key']
        category = question_data.get('category', 'general')
        
        results = {'raw': None, 'structured': None}
        
        # Always store the RAW answer with _raw suffix
        raw_key = f"{key}_raw"
        
        # Store raw based on type
        if storage_type == 'personal_info':
            results['raw'] = self.client.store_personal_info(raw_key, answer)
            if self.structured:
                # Placeholder for structured reference
                results['main'] = self.client.store_personal_info(key, f"[See {raw_key} for full, {key}_structured for extracted fields]")
            else:
                results['main'] = self.client.store_personal_info(key, answer)
        
        elif storage_type == 'preference':
            results['raw'] = self.client.store_preference(category, raw_key, answer)
            if self.structured:
                results['main'] = self.client.store_preference(category, key, f"[See {raw_key} for full, {key}_structured for extracted fields]")
            else:
                results['main'] = self.client.store_preference(category, key, answer)
        
        elif storage_type == 'memory':
            results['raw'] = self.client.add_memory(
                content=f"{raw_key}: {answer}",
                tags=['onboarding', category, 'raw_response'],
                context=f"Raw user onboarding response about {key}"
            )
            if self.structured:
                results['main'] = self.client.add_memory(
                    content=f"{key}: [See {raw_key} for full, {key}_structured for extracted fields]",
                    tags=['onboarding', category, 'structured_reference'],
                    context=f"Structured reference for {key}"
                )
            else:
                results['main'] = self.client.add_memory(
                    content=f"{key}: {answer}",
                    tags=['onboarding', category],
                    context=f"User onboarding response about {key}"
                )
        
        elif storage_type == 'goal':
            results['raw'] = self.client.add_goal(
                description=f"{raw_key}: {answer}",
                category=f"{category}_raw"
            )
            if self.structured:
                results['main'] = self.client.add_goal(
                    description=f"{key}: [See {raw_key} for full, {key}_structured for extracted fields]",
                    category=category
                )
            else:
                results['main'] = self.client.add_goal(
                    description=f"{key}: {answer}",
                    category=category
                )
        
        elif storage_type == 'relationship':
            results['raw'] = self.client.store_relationship(
                name=raw_key,
                relationship_type=category,
                details={'info': answer, 'type': 'raw_response'}
            )
            if self.structured:
                results['main'] = self.client.store_relationship(
                    name=key,
                    relationship_type=category,
                    details={'info': '[See structured data]', 'type': 'structured_reference'}
                )
            else:
                results['main'] = self.client.store_relationship(
                    name=key,
                    relationship_type=category,
                    details={'info': answer}
                )
        
        else:
            return {'error': f'Unknown storage type: {storage_type}'}
        
        # If structured mode enabled, also extract and store structured fields
        if self.structured:
            # Get extraction schema from question data if available
            schema = question_data.get('extraction_schema', {})
            
            # Extract structured fields
            structured_data = extract_structured_fields(answer, category, key, schema)
            
            # Store structured fields
            structured_key = f"{key}_structured"
            
            if storage_type == 'personal_info':
                results['structured'] = self.client.store_personal_info(structured_key, structured_data)
            elif storage_type == 'preference':
                results['structured'] = self.client.store_preference(category, structured_key, structured_data)
            elif storage_type == 'memory':
                results['structured'] = self.client.add_memory(
                    content=f"{structured_key}: {json.dumps(structured_data, indent=2)}",
                    tags=['onboarding', category, 'structured_extraction'],
                    context=f"Structured extraction for {key}"
                )
            elif storage_type == 'goal':
                results['structured'] = self.client.add_goal(
                    description=f"{structured_key}: {json.dumps(structured_data, indent=2)}",
                    category=f"{category}_structured"
                )
            elif storage_type == 'relationship':
                results['structured'] = self.client.store_relationship(
                    name=structured_key,
                    relationship_type=f"{category}_structured",
                    details={'structured_data': structured_data}
                )
            
            # Count extracted fields (excluding internal metadata)
            extracted_count = len([k for k in structured_data.keys() if not k.startswith('_')])
            print(f"   [STRUCTURED] Extracted {extracted_count} fields from your answer")
        
        return results['main'] if results['main'] else results['raw']
    
    def run_quick_onboarding(self) -> dict:
        """Run a quick 5-question onboarding"""
        print("\n" + "="*60)
        print("QUICK ONBOARDING — Let's get the essentials")
        if self.structured:
            print("[Structured mode ON: Storing raw answers + extracted fields]")
        print("="*60)
        print("(I'll ask 5 quick questions. Type 'skip' anytime to move on.)\n")
        
        # Core categories for quick mode
        core_categories = ['identity', 'food', 'professional', 'entertainment', 'lifestyle']
        
        for category in core_categories:
            q = self.get_random_question(category)
            if not q:
                continue
            
            print(f"\nQ: {q['text']}")
            answer = input("   Your answer: ").strip()
            
            if answer.lower() in ['skip', 'pass', '']:
                print("   (Skipped)")
                continue
            
            result = self.store_answer(q, answer)
            if 'error' in result:
                print(f"   [!] Couldn't save: {result['error']}")
            else:
                print(f"   [OK] Saved to your memory")
        
        print("\n" + "="*60)
        print("Quick onboarding complete!")
        print("="*60)
        
        return self.get_summary()
    
    def run_full_onboarding(self) -> dict:
        """Run a comprehensive full onboarding"""
        print("\n" + "="*60)
        print("FULL ONBOARDING — Deep dive into your brilliant mind")
        if self.structured:
            print("[Structured mode ON: Storing raw answers + extracted fields]")
        print("="*60)
        print("(This will take 10-15 minutes. Type 'skip' to skip a question,")
        print(" 'done' to finish early, or just hit Enter to skip.)\n")
        
        # Get all unique categories
        categories = list(set(q['category'] for q in self.questions_catalog))
        
        # Group by category for better flow
        for category in sorted(categories):
            category_questions = [q for q in self.questions_catalog if q['category'] == category]
            
            if not category_questions:
                continue
            
            print(f"\n{'='*60}")
            print(f"[{category.upper().replace('_', ' ')}]")
            print(f"{'='*60}")
            
            # Ask up to 2 questions per category
            for q_data in random.sample(category_questions, min(2, len(category_questions))):
                question_text = random.choice(q_data['questions'])
                
                print(f"\nQ: {question_text}")
                answer = input("   Your answer: ").strip()
                
                if answer.lower() == 'done':
                    print("\n[Ending onboarding early...]")
                    return self.get_summary()
                
                if answer.lower() in ['skip', 'pass', '']:
                    print("   (Skipped)")
                    continue
                
                result = self.store_answer({
                    'storage_key': q_data['storage_key'],
                    'type': q_data['type'],
                    'category': category
                }, answer)
                
                if 'error' in result:
                    print(f"   [!] Couldn't save: {result['error']}")
                else:
                    print(f"   [OK] Saved!")
        
        print("\n" + "="*60)
        print("Full onboarding complete! You magnificent creature.")
        print("="*60)
        
        return self.get_summary()
    
    def run_custom_onboarding(self, categories: list) -> dict:
        """Run onboarding for specific categories only"""
        print(f"\n{'='*60}")
        print(f"CUSTOM ONBOARDING — Focusing on: {', '.join(categories)}")
        print(f"{'='*60}\n")
        
        for category in categories:
            # Keep asking questions in this category until user says 'next'
            print(f"\n[{category.upper().replace('_', ' ')}]")
            print("-" * 40)
            
            while True:
                q = self.get_random_question(category)
                if not q:
                    print("   (No more questions in this category)")
                    break
                
                print(f"\nQ: {q['text']}")
                print("   (Type 'next' for new category, 'skip' to skip, or your answer)")
                answer = input("   Your answer: ").strip()
                
                if answer.lower() == 'next':
                    break
                
                if answer.lower() in ['skip', 'pass', '']:
                    print("   (Skipped)")
                    continue
                
                result = self.store_answer(q, answer)
                if 'error' in result:
                    print(f"   [!] Couldn't save: {result['error']}")
                else:
                    print(f"   [OK] Saved!")
        
        print("\n" + "="*60)
        print("Custom onboarding complete!")
        print("="*60)
        
        return self.get_summary()
    
    def get_summary(self) -> dict:
        """Get a summary of what was stored"""
        stats = self.client.get_stats()
        print("\n[Your Memory Stats]")
        print(f"   Personal info items: {stats.get('personal_info_count', 0)}")
        print(f"   Memories stored: {stats.get('memories_count', 0)}")
        print(f"   Relationships: {stats.get('relationships_count', 0)}")
        print(f"   Goals: {stats.get('goals_count', 0)}")
        return stats


def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Onboard a new user to the Personal Memory MCP system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --user rawrity --mode quick     # Quick 5-question onboarding
  %(prog)s --user sigma --mode full        # Full comprehensive onboarding
  %(prog)s --user rawrity --categories food travel  # Custom categories
  %(prog)s --port 9001 --mode quick        # Direct port connection
        """
    )
    
    parser.add_argument('--user', '-u', 
                        choices=['rawrity', 'sigma'],
                        help='User to onboard (rawrity or sigma)')
    
    parser.add_argument('--port', '-p', 
                        type=int,
                        help='MCP server port (overrides user)')
    
    parser.add_argument('--mode', '-m',
                        choices=['quick', 'full', 'custom'],
                        default='quick',
                        help='Onboarding mode (default: quick)')
    
    parser.add_argument('--categories', '-c',
                        nargs='+',
                        help='Categories for custom mode (space-separated)')
    
    parser.add_argument('--questions-file',
                        help='Path to custom questions YAML file')
    
    parser.add_argument('--structured', '-s', action='store_true',
                        help='Enable structured data extraction (stores raw + structured versions)')
    
    args = parser.parse_args()
    
    # Determine port
    if args.port:
        port = args.port
    elif args.user == 'rawrity':
        port = 9001
    elif args.user == 'sigma':
        port = 9002
    else:
        port = 9001  # default
    
    # Create MCP client
    client = MemoryClient(f"http://localhost:{port}")
    
    # Check health
    if not client.health_check():
        print(f"❌ Error: MCP server not running on port {port}")
        print(f"   Start it with: docker-compose up -d memory-{args.user or 'rawrity'}")
        sys.exit(1)
    
    # Create onboarding session
    session = OnboardingSession(
        mcp_client=client,
        questions_file=args.questions_file,
        structured=args.structured
    )
    
    # Run appropriate mode
    if args.mode == 'quick':
        session.run_quick_onboarding()
    elif args.mode == 'full':
        session.run_full_onboarding()
    elif args.mode == 'custom':
        if not args.categories:
            print("❌ Error: --categories required for custom mode")
            print("   Available categories:")
            cats = set(q['category'] for q in session.questions_catalog)
            for cat in sorted(cats):
                print(f"      - {cat}")
            sys.exit(1)
        session.run_custom_onboarding(args.categories)


if __name__ == "__main__":
    main()
