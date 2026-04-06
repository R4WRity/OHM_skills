#!/usr/bin/env python3
"""
Discord-friendly onboarding functions for OpenClaw integration.
Provides question retrieval and answer storage without interactive prompts.
"""

import yaml
import random
from pathlib import Path
from typing import Optional, List

# Add workspace to path
import sys
current_dir = Path(__file__).parent
workspace_root = current_dir.parent.parent.parent  # Go up to workspace root

# Add the projects directory directly
sys.path.insert(0, str(workspace_root / "projects" / "personal-memory-mcp-docker"))

try:
    from bridge import MemoryClient
except ImportError:
    MemoryClient = None


class OnboardingBot:
    """Non-interactive onboarding helper for Discord/OpenClaw"""
    
    QUESTIONS_FILE = Path(__file__).parent.parent / "references" / "onboarding-questions.yaml"
    
    def __init__(self, mcp_client=None, port: int = 9001):
        self.client = mcp_client
        if not self.client and MemoryClient:
            self.client = MemoryClient(f"http://localhost:{port}")
        
        # Load questions
        with open(self.QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            self.questions_catalog = yaml.safe_load(f)
    
    def get_question(self, category: str = None, storage_key: str = None) -> Optional[dict]:
        """
        Get a random question.
        
        Args:
            category: Filter by category (e.g., 'food', 'travel')
            storage_key: Filter by specific storage key
        
        Returns:
            Dict with 'text', 'category', 'storage_key', 'type', or None
        """
        candidates = self.questions_catalog
        
        if category:
            candidates = [q for q in candidates if q.get('category') == category]
        
        if storage_key:
            candidates = [q for q in candidates if q.get('storage_key') == storage_key]
        
        if not candidates:
            return None
        
        q = random.choice(candidates)
        return {
            'text': random.choice(q['questions']),
            'category': q['category'],
            'storage_key': q['storage_key'],
            'type': q['type']
        }
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return sorted(set(q['category'] for q in self.questions_catalog))
    
    def store_answer(self, question_data: dict, answer: str) -> dict:
        """
        Store an answer to the MCP server.
        
        Args:
            question_data: Dict with 'storage_key', 'type', 'category'
            answer: User's answer text
        
        Returns:
            Result dict from MCP server
        """
        if not self.client:
            return {'error': 'No MCP client configured'}
        
        storage_type = question_data['type']
        key = question_data['storage_key']
        category = question_data.get('category', 'general')
        
        try:
            if storage_type == 'personal_info':
                return self.client.store_personal_info(key, answer)
            
            elif storage_type == 'preference':
                return self.client.store_preference(category, key, answer)
            
            elif storage_type == 'memory':
                return self.client.add_memory(
                    content=f"{key}: {answer}",
                    tags=['onboarding', category],
                    context=f"User onboarding response about {key}"
                )
            
            elif storage_type == 'goal':
                return self.client.add_goal(
                    description=f"{key}: {answer}",
                    category=category
                )
            
            elif storage_type == 'relationship':
                return self.client.store_relationship(
                    name=key,
                    relationship_type=category,
                    details={'info': answer}
                )
            
            else:
                return {'error': f'Unknown storage type: {storage_type}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_random_question_text(self, category: str = None) -> str:
        """Just get the text of a random question"""
        q = self.get_question(category=category)
        return q['text'] if q else "No questions available for that category."
    
    def get_suggested_question_flow(self, num_questions: int = 5) -> List[dict]:
        """Get a suggested sequence of questions for onboarding"""
        # Prioritize core categories
        core_categories = ['identity', 'food', 'professional', 'entertainment', 'lifestyle']
        
        flow = []
        used_keys = set()
        
        for category in core_categories[:num_questions]:
            # Get questions for this category not already used
            available = [
                q for q in self.questions_catalog 
                if q['category'] == category and q['storage_key'] not in used_keys
            ]
            
            if available:
                q = random.choice(available)
                flow.append({
                    'text': random.choice(q['questions']),
                    'category': q['category'],
                    'storage_key': q['storage_key'],
                    'type': q['type']
                })
                used_keys.add(q['storage_key'])
        
        return flow


# Simple test interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Onboarding Bot - Get questions for users")
    parser.add_argument('--category', '-c', help='Get question from specific category')
    parser.add_argument('--random', '-r', action='store_true', help='Get completely random question')
    parser.add_argument('--categories', action='store_true', help='List all categories')
    parser.add_argument('--flow', '-f', type=int, default=5, help='Generate suggested question flow')
    parser.add_argument('--port', '-p', type=int, default=9001, help='MCP server port')
    
    args = parser.parse_args()
    
    bot = OnboardingBot(port=args.port)
    
    if args.categories:
        print("Available categories:")
        for cat in bot.get_categories():
            print(f"  - {cat}")
    
    elif args.random or args.category:
        q = bot.get_question(category=args.category)
        if q:
            print(f"\n[{q['category']}] {q['storage_key']}")
            print(f"Q: {q['text']}")
        else:
            print("No question found.")
    
    elif args.flow:
        print(f"\n[Suggested {args.flow}-question onboarding flow]\n")
        for i, q in enumerate(bot.get_suggested_question_flow(args.flow), 1):
            print(f"{i}. [{q['category']}] {q['storage_key']}")
            print(f"   Q: {q['text']}\n")
    
    else:
        # Default: get one random question
        q = bot.get_question()
        print(f"\n[{q['category']}] {q['storage_key']}")
        print(f"Q: {q['text']}")
