#!/usr/bin/env python3
"""
Bot Configuration Setup Script
Updates SOUL.md, IDENTITY.md, and HEARTBEAT.md sections based on user preferences.

Reads existing files and updates configured sections only.

Usage:
    python setup-bot.py --mode quick          # 3 questions
    python setup-bot.py --mode full           # 6 questions + HEARTBEAT
    python setup-bot.py --mode quick --user rawrity
    python setup-bot.py --mode full --user sigma
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(workspace_root))


class SectionUpdater:
    """Updates specific sections in markdown files while preserving other content."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.original_content = self._read_file()
    
    def _read_file(self) -> str:
        """Read file content or return empty string if not exists."""
        if not self.filepath.exists():
            return ""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def find_section(self, header: str) -> Tuple[bool, int, int]:
        """
        Find a section in the content.
        
        Returns:
            (found, start_pos, end_pos) - end_pos is exclusive
        """
        content = self.original_content
        header_text = header.lstrip('#').strip()
        # Match header with optional blank lines after
        # Pattern: ## Header\n followed by content until next ## or EOF
        
        # Try exact match first
        for level in range(2, 7):
            pattern = rf'(^|\n)(#{{{level}}}\s+{re.escape(header_text)}\s*\n+)(.*?)(?=\n#{{2,6}}\s|\Z)'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return True, match.start(), match.end()
        
        return False, -1, -1
    
    def update_or_insert_section(self, section_header: str, new_content: str, insert_after: Optional[str] = "") -> bool:
        """
        Update existing section or insert new section after a reference header.
        
        Args:
            section_header: The section header (e.g., "## Communication")
            new_content: The content to place in the section  
            insert_after: Reference header to insert after (e.g., "## Core Truths"). 
                         If empty, appends to end.
        
        Returns:
            True if file was modified
        """
        content = self.original_content
        section_content = f"\n{section_header}\n\n{new_content}\n"
        
        # Try to find and replace existing section
        found, start, end = self.find_section(section_header)
        if found:
            content = content[:start] + section_content + content[end:]
        else:
            # Section doesn't exist - need to insert
            if insert_after:
                # Find the reference section
                ref_found, ref_start, ref_end = self.find_section(insert_after)
                if ref_found:
                    # Insert after the reference section
                    content = content[:ref_end] + section_content + content[ref_end:]
                else:
                    # Reference not found, append to end
                    content = content.rstrip() + section_content
            else:
                # No reference, append to end
                content = content.rstrip() + section_content
        
        # Write back
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.original_content = content
            return True
        except Exception as e:
            print(f"  [ERR] Failed to write {self.filepath.name}: {e}")
            return False

    def insert_after_section_header(self, ref_header: str, new_header: str, new_content: str) -> bool:
        """Insert a new section immediately after the reference header."""
        content = self.original_content
        
        # Find the reference header
        header_pattern = re.escape(ref_header.lstrip('#').strip())
        # Match header and following content until next ##
        section_regex = rf'(^|\n)(#{1,6}\s*{header_pattern}\s*\n)(.*?)(?=\n#{1,6}\s|\Z)'
        
        match = re.search(section_regex, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            # Insert after this section
            insert_pos = match.end()
            new_section = f"\n\n{new_header}\n\n{new_content}\n"
            content = content[:insert_pos] + new_section + content[insert_pos:]
        else:
            # Reference not found, append
            content = content.rstrip() + f"\n\n{new_header}\n\n{new_content}\n"
        
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.original_content = content
            return True
        except Exception as e:
            print(f"  [ERR] Failed to write {self.filepath.name}: {e}")
            return False

    def update_frontmatter_field(self, field_name: str, new_value: str) -> bool:
        """
        Update a field in the frontmatter/list format like IDENTITY.md uses.
        Format: - **Field:** value
        """
        content = self.original_content
        
        # Pattern to match: - **Field:** value
        field_pattern = rf'(-\s*\*\*{re.escape(field_name)}:\*\*\s*)(.*?)(\n|$)'
        
        match = re.search(field_pattern, content, re.IGNORECASE)
        
        if match:
            # Field exists - update it
            old_line = match.group(0)
            new_line = f"{match.group(1)}{new_value}{match.group(3)}"
            content = content.replace(old_line, new_line)
        else:
            # Field doesn't exist - find the list and add it
            # Look for pattern like "- **Name:**" or "- **Creature:**"
            list_match = re.search(r'(-\s*\*\*\w+:\*\*.*?\n)', content)
            if list_match:
                # Insert after last field in list
                insert_pos = list_match.end()
                content = content[:insert_pos] + f"- **{field_name}:** {new_value}\n" + content[insert_pos:]
            else:
                # Can't find list, append to file
                content = content.rstrip() + f"\n\n- **{field_name}:** {new_value}\n"
        
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.original_content = content
            return True
        except Exception as e:
            print(f"  [ERR] Failed to write {self.filepath.name}: {e}")
            return False


class BotConfigurator:
    """Handles bot configuration interviews and file updates."""
    
    def __init__(self, user: str = "default", workspace_dir: Optional[Path] = None):
        self.user = user
        self.workspace_dir = workspace_dir or workspace_root
        self.questions_file = Path(__file__).parent.parent / "references" / "setup-bot-questions.yaml"
        self.answers = {}
        self.mode = None
        self.updated_files = []
        
        # Load questions
        with open(self.questions_file, 'r', encoding='utf-8') as f:
            self.questions = yaml.safe_load(f)
    
    def _get_default_answers(self, mode: str) -> Dict:
        """Get default answers for non-interactive mode."""
        defaults = {
            'communication.directness': {
                'value': 'direct',
                'label': 'Direct and concise - just the facts',
                'description': 'I get straight to the point. Short answers, bullet points, minimal fluff.'
            },
            'tone.tone': {
                'value': 'casual',
                'label': 'Casual',
                'description': 'Relaxed, friendly, like a helpful colleague.'
            },
            'identity.name': {
                'value': 'OHM',
                'raw': 'OHM'
            },
            'identity.emoji': {
                'value': 'O',
                'raw': 'O'
            },
            'identity.creature': {
                'value': 'AI assistant',
                'raw': 'AI assistant'
            }
        }
        
        if mode == 'full':
            defaults.update({
                'proactivity.check_in_frequency': {
                    'value': 'daily',
                    'label': 'Daily casual check-in',
                    'description': 'Once daily check-in with relevant updates.'
                },
                'proactivity.suggestions': {
                    'value': 'volunteer',
                    'label': 'Volunteer suggestions',
                    'description': 'If I think of something useful, I will share it.'
                }
            })
        
        return defaults
    
    def run_quick_config(self) -> Dict:
        """Run quick 3-question configuration."""
        print("=" * 60)
        print("[BOT] CONFIGURATION - QUICK MODE")
        print("=" * 60)
        print("\n3 questions to customize your bot's personality.")
        print("Existing files will be updated, not overwritten.\n")
        
        self.mode = "quick"
        quick_questions = self.questions.get('quick', [])
        
        for i, q in enumerate(quick_questions, 1):
            self._ask_question(q, i, len(quick_questions))
        
        return self.answers
        """Run quick 3-question configuration."""
        print("=" * 60)
        print("[BOT] CONFIGURATION - QUICK MODE")
        print("=" * 60)
        print("\n3 questions to customize your bot's personality.")
        print("Existing files will be updated, not overwritten.\n")
        
        self.mode = "quick"
        quick_questions = self.questions.get('quick', [])
        
        for i, q in enumerate(quick_questions, 1):
            self._ask_question(q, i, len(quick_questions))
        
        return self.answers
    
    def run_full_config(self) -> Dict:
        """Run full 6-question configuration."""
        print("=" * 60)
        print("[BOT] CONFIGURATION - FULL MODE")
        print("=" * 60)
        print("\n6 questions for complete bot customization.")
        print("Existing files will be updated, not overwritten.\n")
        
        self.mode = "full"
        full_questions = self.questions.get('full', [])
        
        for i, q in enumerate(full_questions, 1):
            # Check if question inherits from quick mode
            if 'inherits' in q:
                base = self._get_inherited_question(q['inherits'])
                if base:
                    # Merge with additional questions
                    merged = base.copy()
                    if 'additional_questions' in q:
                        merged['questions'].extend(q['additional_questions'])
                        # Merge options
                        if 'options' in q:
                            merged['options'] = merged.get('options', []) + q['options']
                    q = merged
            
            self._ask_question(q, i, len(full_questions))
        
        return self.answers
    
    def _get_inherited_question(self, inherit_path: str) -> Optional[Dict]:
        """Get a question from quick mode by path like 'quick.communication'."""
        parts = inherit_path.split('.')
        if len(parts) < 2:
            return None
        
        quick = self.questions.get('quick', [])
        category = parts[1]
        
        for q in quick:
            if q.get('category') == category:
                return q
        return None
    
    def _ask_question(self, question_data: Dict, current: int, total: int):
        """Ask a configuration question and store the answer."""
        category = question_data['category']
        file_target = question_data['file']
        
        print(f"[{current}/{total}] [{question_data['section'].upper()}]")
        print("-" * 40)
        
        # Show example questions
        for q in question_data.get('questions', []):
            print(f"  - {q}")
        print()
        
        # Process each option for this question
        for option in question_data.get('options', []):
            key = option['key']
            answer = self._ask_option(category, key, option)
            self.answers[f"{category}.{key}"] = answer
        
        print()
    
    def _ask_option(self, category: str, key: str, option: Dict) -> Dict:
        """Ask for a specific option value."""
        if 'choices' in option:
            # Multiple choice
            return self._ask_multiple_choice(category, key, option)
        elif option.get('type') == 'text':
            # Free text
            return self._ask_text(category, key, option)
        elif option.get('type') == 'multiselect':
            # Multi-select
            return self._ask_multiselect(category, key, option)
        else:
            # Default to text
            return self._ask_text(category, key, option)
    
    def _ask_multiple_choice(self, category: str, key: str, option: Dict) -> Dict:
        """Ask a multiple choice question."""
        choices = option['choices']
        
        print(f"  {option.get('description', key)}:")
        for i, choice in enumerate(choices, 1):
            print(f"    {i}. {choice['label']}")
            print(f"       -> {choice['description']}")
        print()
        
        # Get user selection
        while True:
            try:
                choice_str = input(f"  Select (1-{len(choices)}, or Enter for default): ").strip()
                
                if not choice_str:
                    # Use default (first option)
                    selected = choices[0]
                else:
                    idx = int(choice_str) - 1
                    if 0 <= idx < len(choices):
                        selected = choices[idx]
                    else:
                        raise ValueError()
                
                return {
                    'value': selected['value'],
                    'label': selected['label'],
                    'description': selected['description']
                }
                
            except (ValueError, IndexError):
                print(f"    Please enter a number 1-{len(choices)}")
            except KeyboardInterrupt:
                print("\n\nSkipped.")
                return {'value': 'default', 'label': 'Default', 'description': 'Using default setting'}
    
    def _ask_text(self, category: str, key: str, option: Dict) -> Dict:
        """Ask a free-text question."""
        default = option.get('default', '')
        description = option.get('description', key)
        multiline = option.get('multiline', False)
        
        print(f"  {description}")
        if default:
            print(f"  (Press Enter to accept default: '{default}')")
        print()
        
        if multiline:
            print("  (Enter multi-line text. Type 'DONE' on its own line when finished)")
            lines = []
            while True:
                try:
                    line = input("  > ")
                    if line.strip().upper() == 'DONE':
                        break
                    lines.append(line)
                except KeyboardInterrupt:
                    print("\n\nSkipped.")
                    return {'value': default or 'Not specified', 'raw': ''}
            value = '\n'.join(lines)
        else:
            try:
                value = input("  > ").strip()
                if not value and default:
                    value = default
            except KeyboardInterrupt:
                print("\n\nSkipped.")
                return {'value': default or 'Not specified', 'raw': ''}
        
        return {
            'value': value,
            'raw': value
        }
    
    def _ask_multiselect(self, category: str, key: str, option: Dict) -> Dict:
        """Ask a multi-select question."""
        choices = option['choices']
        
        print(f"  {option.get('description', key)}:")
        print("  (Enter numbers separated by commas, e.g., '1,3,5')")
        for i, choice in enumerate(choices, 1):
            print(f"    {i}. {choice['label']}")
        print()
        print("  Enter 'all' for all options, or press Enter to skip")
        print()
        
        try:
            selection = input("  > ").strip()
            
            if not selection:
                return {'values': [], 'selected': []}
            
            if selection.lower() == 'all':
                selected = choices
            else:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected = [choices[i] for i in indices if 0 <= i < len(choices)]
            
            return {
                'values': [s['value'] for s in selected],
                'selected': selected
            }
            
        except (ValueError, IndexError):
            print("    Invalid selection, skipping.")
            return {'values': [], 'selected': []}
        except KeyboardInterrupt:
            print("\n\nSkipped.")
            return {'values': [], 'selected': []}
    
    def update_files(self):
        """Update existing markdown files with new configuration."""
        print("\n" + "=" * 60)
        print("[UPDATE] CONFIGURING BOT FILES")
        print("=" * 60)
        print()
        
        # Add system date
        self.answers['system.date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Always update SOUL.md and IDENTITY.md
        self._update_soul()
        self._update_identity()
        
        # Update HEARTBEAT.md only in full mode
        if self.mode == "full":
            self._update_heartbeat()
        
        # Print summary
        print(f"\n[OK] Updated {len(self.updated_files)} file(s):")
        for f in self.updated_files:
            print(f"   - {f}")
    
    def _update_soul(self):
        """Update SOUL.md with communication style and tone."""
        soul_path = self.workspace_dir / 'SOUL.md'
        
        if not soul_path.exists():
            print(f"  [WARN] SOUL.md not found - skipping (run user creation first)")
            return
        
        updater = SectionUpdater(soul_path)
        updated = False
        
        # Update Communication Style section
        if 'communication.directness' in self.answers:
            directness = self.answers['communication.directness']
            content = f"**Directness:** {directness['value']}\n\n{directness['description']}"
            if updater.update_or_insert_section(
                "## Communication Style", content, insert_after="## Core Truths"
            ):
                updated = True
        
        # Update Tone/Voice section
        if 'tone.tone' in self.answers:
            tone = self.answers['tone.tone']
            content = f"**Tone:** {tone['value']}\n\n{tone['description']}"
            if updater.update_or_insert_section(
                "## Tone / Voice", content, insert_after="## Communication Style"
            ):
                updated = True
        
        if updated:
            self.updated_files.append("SOUL.md")
            print(f"  [OK] SOUL.md")
    
    def _update_identity(self):
        """Update IDENTITY.md with bot name, emoji, creature."""
        identity_path = self.workspace_dir / 'IDENTITY.md'
        
        if not identity_path.exists():
            print(f"  [WARN] IDENTITY.md not found - skipping (run user creation first)")
            return
        
        updater = SectionUpdater(identity_path)
        updated = False
        
        # Update date
        date = self.answers.get('system.date', datetime.now().strftime('%Y-%m-%d'))
        content = updater.original_content
        # Find and update the date line
        new_content = re.sub(
            r'(\*Assigned by .*? on )\d{4}-\d{2}-\d{2}(\*\s*\n)',
            rf'\g<1>{date}\g<2>',
            content
        )
        if new_content != content:
            with open(identity_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updater.original_content = new_content
            updated = True
        
        # Update fields
        if 'identity.name' in self.answers:
            updater.update_frontmatter_field("Name", self.answers['identity.name']['value'])
            updated = True
        
        if 'identity.emoji' in self.answers:
            updater.update_frontmatter_field("Emoji", self.answers['identity.emoji']['value'])
            updated = True
        
        if 'identity.creature' in self.answers:
            updater.update_frontmatter_field("Creature", self.answers['identity.creature']['value'])
            updated = True
        
        # Handle full mode extras
        if self.mode == "full":
            if 'identity.vibe' in self.answers:
                updater.update_frontmatter_field("Vibe", self.answers['identity.vibe']['value'])
                updated = True
        
        if updated:
            self.updated_files.append("IDENTITY.md")
            print(f"  [OK] IDENTITY.md")
    
    def _update_heartbeat(self):
        """Update HEARTBEAT.md with proactivity settings."""
        heartbeat_path = self.workspace_dir / 'HEARTBEAT.md'
        
        if not heartbeat_path.exists():
            print(f"  [WARN] HEARTBEAT.md not found - skipping (run user creation first)")
            return
        
        updater = SectionUpdater(heartbeat_path)
        updated = False
        
        # Build proactivity content
        content_lines = ["## Proactivity Rules", ""]
        
        if 'proactivity.check_in_frequency' in self.answers:
            freq = self.answers['proactivity.check_in_frequency']
            content_lines.extend([
                f"**Check-in Frequency:** {freq['label']}",
                "",
                freq['description'],
                ""
            ])
        
        if 'proactivity.suggestions' in self.answers:
            sugg = self.answers['proactivity.suggestions']
            content_lines.extend([
                f"**Suggestions:** {sugg['label']}",
                "",
                sugg['description'],
                ""
            ])
        
        if 'proactivity.triggers' in self.answers:
            triggers = self.answers['proactivity.triggers']
            if triggers.get('values'):
                content_lines.extend([
                    "**Proactive Triggers:**",
                    ""
                ])
                for t in triggers['values']:
                    content_lines.append(f"- {t}")
                content_lines.append("")
        
        content = "\n".join(content_lines)
        
        if updater.update_section("## Proactivity Rules", content):
            updated = True
        
        if updated:
            self.updated_files.append("HEARTBEAT.md")
            print(f"  [OK] HEARTBEAT.md")
    
    def save_answers_json(self):
        """Save answers to a JSON file for reference."""
        output_path = self.workspace_dir / '.bot-config-answers.json'
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.answers, f, indent=2, default=str)
            print(f"\n[OK] Answers saved to {output_path.name}")
        except Exception as e:
            print(f"\n[WARN] Could not save answers: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Configure bot personality and behavior')
    parser.add_argument('--mode', choices=['quick', 'full'], default='quick',
                       help='Configuration mode (default: quick)')
    parser.add_argument('--user', default='default',
                       help='User identifier (default: default)')
    parser.add_argument('--workspace', type=Path, default=None,
                       help='Workspace directory (default: current)')
    parser.add_argument('--answers', type=Path, default=None,
                       help='JSON file with pre-filled answers (non-interactive mode)')
    parser.add_argument('--defaults', action='store_true',
                       help='Use all default values (non-interactive mode)')
    
    args = parser.parse_args()
    
    # Create configurator
    configurator = BotConfigurator(
        user=args.user,
        workspace_dir=args.workspace
    )
    
    # Run configuration
    if args.answers:
        # Load answers from JSON file
        with open(args.answers, 'r') as f:
            configurator.answers = json.load(f)
        configurator.mode = args.mode
        print(f"[INFO] Loaded answers from {args.answers}")
    elif args.defaults:
        # Use defaults without prompting
        configurator.answers = configurator._get_default_answers(args.mode)
        configurator.mode = args.mode
        print("[INFO] Using default values")
    else:
        # Interactive mode
        if args.mode == 'quick':
            configurator.run_quick_config()
        else:
            configurator.run_full_config()
    
    # Update files (not generate)
    configurator.update_files()
    
    # Save answers
    configurator.save_answers_json()
    
    print("\n" + "=" * 60)
    print("[BOT] CONFIGURATION COMPLETE!")
    print("=" * 60)
    print("\nYour bot configuration has been updated.")
    print("Existing content was preserved.\n")


if __name__ == '__main__':
    main()
