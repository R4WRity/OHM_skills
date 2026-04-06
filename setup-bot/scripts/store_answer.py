#!/usr/bin/env python3
"""
Store single setup-bot answer and update appropriate file section.

Used by Discord/conversational interfaces to update one answer at a time.

Usage:
    python store_answer.py --category communication --key directness --value direct
    python store_answer.py --category identity --key name --value "Omega"
    python store_answer.py --category proactivity --key check_in_frequency --value daily
"""

import os
import sys
import yaml
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

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
    
    def find_section(self, header: str) -> tuple:
        """Find a section in the content. Returns (found, start, end)."""
        content = self.original_content
        header_text = header.lstrip('#').strip()
        
        for level in range(2, 7):
            pattern = rf'(^|\n)(#{{{level}}}\s+{re.escape(header_text)}\s*\n+)(.*?)(?=\n#{{2,6}}\s|\Z)'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return True, match.start(), match.end()
        
        return False, -1, -1
    
    def update_or_insert_section(self, section_header: str, new_content: str, insert_after: str = "") -> bool:
        """Update existing section or insert new section after a reference header."""
        content = self.original_content
        section_content = f"\n{section_header}\n\n{new_content}\n"
        
        # Try to find and replace existing section
        found, start, end = self.find_section(section_header)
        if found:
            content = content[:start] + section_content + content[end:]
        else:
            # Section doesn't exist - need to insert
            if insert_after:
                ref_found, ref_start, ref_end = self.find_section(insert_after)
                if ref_found:
                    content = content[:ref_end] + section_content + content[ref_end:]
                else:
                    content = content.rstrip() + section_content
            else:
                content = content.rstrip() + section_content
        
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.original_content = content
            return True
        except Exception as e:
            print(f"[ERR] Failed to write {self.filepath.name}: {e}", file=sys.stderr)
            return False
    
    def update_frontmatter_field(self, field_name: str, new_value: str) -> bool:
        """Update a field like - **Field:** value in IDENTITY.md."""
        content = self.original_content
        field_pattern = rf'(-\s*\*\*{re.escape(field_name)}:\*\*\s*)(.*?)(\n|$)'
        
        match = re.search(field_pattern, content, re.IGNORECASE)
        
        if match:
            old_line = match.group(0)
            new_line = f"{match.group(1)}{new_value}{match.group(3)}"
            content = content.replace(old_line, new_line)
        else:
            # Field doesn't exist - find the list and add it
            list_match = re.search(r'(-\s*\*\*\w+:\*\*.*?\n)', content)
            if list_match:
                insert_pos = list_match.end()
                content = content[:insert_pos] + f"- **{field_name}:** {new_value}\n" + content[insert_pos:]
            else:
                content = content.rstrip() + f"\n\n- **{field_name}:** {new_value}\n"
        
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.original_content = content
            return True
        except Exception as e:
            print(f"[ERR] Failed to write {self.filepath.name}: {e}", file=sys.stderr)
            return False
    
    def update_date(self, new_date: str) -> bool:
        """Update the date in the header line."""
        content = self.original_content
        new_content = re.sub(
            r'(\*Assigned by .*? on )\d{4}-\d{2}-\d{2}(\*\s*\n)',
            rf'\g<1>{new_date}\g<2>',
            content
        )
        if new_content != content:
            try:
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.original_content = new_content
                return True
            except Exception as e:
                print(f"[ERR] Failed to write {self.filepath.name}: {e}", file=sys.stderr)
                return False
        return True


class SetupBotStore:
    """Handles storing individual answers to appropriate files."""
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or workspace_root
        self.questions_file = Path(__file__).parent.parent / "references" / "setup-bot-questions.yaml"
        
        with open(self.questions_file, 'r', encoding='utf-8') as f:
            self.questions = yaml.safe_load(f)
    
    def get_question_data(self, category: str, mode: str = "quick") -> Optional[Dict]:
        """Get question definition for a category."""
        questions = self.questions.get(mode, [])
        for q in questions:
            if q.get('category') == category:
                return q
        # Also check full mode for inherited questions
        if mode == "quick":
            questions = self.questions.get('full', [])
            for q in questions:
                if q.get('category') == category:
                    return q
        return None
    
    def get_choice_description(self, category: str, key: str, value: str, mode: str = "quick") -> str:
        """Get description for a choice value."""
        q_data = self.get_question_data(category, mode)
        if not q_data:
            return ""
        
        for option in q_data.get('options', []):
            if option.get('key') == key:
                for choice in option.get('choices', []):
                    if choice['value'] == value:
                        return choice.get('description', '')
        return ""
    
    def store_answer(self, category: str, key: str, value: str, mode: str = "quick") -> Dict:
        """Store a single answer and update the appropriate file."""
        result = {
            'category': category,
            'key': key,
            'value': value,
            'updated': False,
            'file': None,
            'message': ""
        }
        
        q_data = self.get_question_data(category, mode)
        if not q_data:
            result['message'] = f"Unknown category: {category}"
            return result
        
        target_file = q_data.get('file')
        if not target_file:
            result['message'] = f"No target file for category: {category}"
            return result
        
        file_path = self.workspace_dir / target_file
        
        if not file_path.exists():
            result['message'] = f"File not found: {target_file} (run load-user first)"
            return result
        
        updater = SectionUpdater(file_path)
        updated = False
        description = self.get_choice_description(category, key, value, mode)
        date = datetime.now().strftime('%Y-%m-%d')
        
        # Handle specific category/key combinations
        if category == "communication":
            if key == "directness":
                content = f"**Directness:** {value}\n\n{description}"
                updated = updater.update_or_insert_section(
                    "## Communication Style", content, insert_after="## Core Truths"
                )
                result['message'] = f"Updated Communication Style: {value}"
        
        elif category == "tone":
            if key == "tone":
                content = f"**Tone:** {value}\n\n{description}"
                # Check if Communication Style exists to insert after it
                comm_found, _, _ = updater.find_section("## Communication Style")
                if comm_found:
                    updated = updater.update_or_insert_section(
                        "## Tone / Voice", content, insert_after="## Communication Style"
                    )
                else:
                    updated = updater.update_or_insert_section(
                        "## Tone / Voice", content, insert_after="## Core Truths"
                    )
                result['message'] = f"Updated Tone/Voice: {value}"
        
        elif category == "identity":
            updater.update_date(date)
            if key == "name":
                updated = updater.update_frontmatter_field("Name", value)
                result['message'] = f"Updated bot name to: {value}"
            elif key == "emoji":
                updated = updater.update_frontmatter_field("Emoji", value)
                result['message'] = f"Updated bot emoji to: {value}"
            elif key == "creature":
                updated = updater.update_frontmatter_field("Creature", value)
                result['message'] = f"Updated bot creature to: {value}"
            elif key == "vibe":
                updated = updater.update_frontmatter_field("Vibe", value)
                result['message'] = f"Updated bot vibe to: {value}"
            elif key == "notes":
                # Notes go under **Notes:** section
                content = updater.original_content
                notes_pattern = r'(\*\*Notes:\*\*\s*\n)'
                match = re.search(notes_pattern, content)
                if match:
                    insert_pos = match.end()
                    new_content = content[:insert_pos] + f"\n{value}\n" + content[insert_pos:]
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated = True
                    except Exception as e:
                        result['message'] = f"Failed to update notes: {e}"
                else:
                    # Append Notes section at end
                    new_content = content.rstrip() + f"\n\n**Notes:**\n\n{value}\n"
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated = True
                    except Exception as e:
                        result['message'] = f"Failed to add notes: {e}"
                result['message'] = f"Updated bot notes"
        
        elif category == "proactivity":
            if key == "check_in_frequency":
                content = f"**Check-in Frequency:** {value}\n\n{description}"
                updated = updater.update_or_insert_section(
                    "## Proactivity Rules", content
                )
                result['message'] = f"Updated heartbeat frequency: {value}"
            elif key == "suggestions":
                content = f"**Suggestions:** {value}\n\n{description}"
                # Find and append to Proactivity section
                found, start, end = updater.find_section("## Proactivity Rules")
                if found:
                    section = updater.original_content[start:end]
                    new_section = section.rstrip() + f"\n\n**Suggestions:** {value}\n\n{description}\n"
                    content = updater.original_content[:start] + new_section + updater.original_content[end:]
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        updated = True
                    except Exception as e:
                        result['message'] = f"Failed to update suggestions: {e}"
                else:
                    content = f"**Suggestions:** {value}\n\n{description}\n"
                    updated = updater.update_or_insert_section("## Proactivity Rules", content)
                result['message'] = f"Updated suggestion mode: {value}"
        
        result['updated'] = updated
        result['file'] = target_file
        return result


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Store single setup-bot answer')
    parser.add_argument('--category', required=True,
                       help='Question category (communication, tone, identity, etc.)')
    parser.add_argument('--key', required=True,
                       help='Answer key (directness, tone, name, etc.)')
    parser.add_argument('--value', required=True,
                       help='Answer value')
    parser.add_argument('--mode', default='quick',
                       help='Configuration mode (quick or full)')
    parser.add_argument('--workspace', type=Path, default=None,
                       help='Workspace directory')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    
    args = parser.parse_args()
    
    store = SetupBotStore(workspace_dir=args.workspace)
    result = store.store_answer(args.category, args.key, args.value, args.mode)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result['updated']:
            print(f"[OK] {result['file']}: {result['message']}")
        else:
            print(f"[ERR] {result['message']}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
