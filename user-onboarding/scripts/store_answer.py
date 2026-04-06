#!/usr/bin/env python3
"""
Store an onboarding answer to the MCP server.
Called by the agent after the user answers an onboarding question.
Supports both raw and structured storage.
"""

import argparse
import json
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "projects" / "personal-memory-mcp-docker"))
sys.path.insert(0, str(Path(__file__).parent))  # For structured_extractor

from bridge import MemoryClient
from structured_extractor import extract_structured_fields


def main():
    parser = argparse.ArgumentParser(description='Store an onboarding answer')
    parser.add_argument('--port', '-p', type=int, default=9001, help='MCP server port')
    parser.add_argument('--category', '-c', required=True, help='Question category')
    parser.add_argument('--key', '-k', required=True, help='Storage key')
    parser.add_argument('--type', '-t', required=True, 
                        choices=['personal_info', 'preference', 'memory', 'goal', 'relationship'],
                        help='Storage type')
    parser.add_argument('--answer', '-a', required=True, help='User answer')
    parser.add_argument('--structured', '-s', action='store_true', 
                        help='Also extract and store structured fields')
    parser.add_argument('--schema', type=str, help='JSON schema for structured extraction (optional)')
    
    args = parser.parse_args()
    
    client = MemoryClient(f"http://localhost:{args.port}")
    
    # Check health
    if not client.health_check():
        print(f"[ERROR] MCP server not responding on port {args.port}")
        sys.exit(1)
    
    # Store the RAW answer
    raw_result = {}
    raw_key = f"{args.key}_raw"  # Store raw with _raw suffix
    
    if args.type == 'personal_info':
        # Store raw in personal_info with _raw suffix
        client.store_personal_info(raw_key, args.answer)
        # Store the main structured version in the main key if structured mode
        if args.structured:
            result = client.store_personal_info(args.key, f"[STRUCTURED] See {args.key}_structured")
        else:
            result = client.store_personal_info(args.key, args.answer)
    elif args.type == 'preference':
        # Store raw in preferences
        client.store_preference(args.category, raw_key, args.answer)
        if args.structured:
            result = client.store_preference(args.category, args.key, f"[STRUCTURED] See {args.key}_structured")
        else:
            result = client.store_preference(args.category, args.key, args.answer)
    elif args.type == 'memory':
        # Store raw as a memory
        client.add_memory(
            content=f"{args.key}_raw: {args.answer}",
            tags=['onboarding', args.category, 'raw_response'],
            context=f"Raw user onboarding response about {args.key}"
        )
        if args.structured:
            result = client.add_memory(
                content=f"{args.key}: [STRUCTURED] See {args.key}_structured",
                tags=['onboarding', args.category, 'structured'],
                context=f"Structured user onboarding response about {args.key}"
            )
        else:
            result = client.add_memory(
                content=f"{args.key}: {args.answer}",
                tags=['onboarding', args.category],
                context=f"User onboarding response about {args.key}"
            )
    elif args.type == 'goal':
        client.add_goal(
            description=f"{args.key}_raw: {args.answer}",
            category=f"{args.category}_raw"
        )
        if args.structured:
            result = client.add_goal(
                description=f"{args.key}: [STRUCTURED] See {args.key}_structured",
                category=args.category
            )
        else:
            result = client.add_goal(
                description=f"{args.key}: {args.answer}",
                category=args.category
            )
    elif args.type == 'relationship':
        # For relationships, store details differently
        raw_details = {'info': args.answer, 'type': 'raw_response'}
        client.store_relationship(
            name=f"{args.key}_raw",
            relationship_type=args.category,
            details=raw_details
        )
        if args.structured:
            result = client.store_relationship(
                name=args.key,
                relationship_type=args.category,
                details={'info': '[STRUCTURED]', 'type': 'structured_reference'}
            )
        else:
            result = client.store_relationship(
                name=args.key,
                relationship_type=args.category,
                details={'info': args.answer}
            )
    
    # If structured mode, also extract and store structured fields
    structured_result = None
    if args.structured:
        # Parse schema if provided
        schema = {}
        if args.schema:
            try:
                schema = json.loads(args.schema)
            except:
                schema = {}
        
        # Extract structured fields
        structured_data = extract_structured_fields(args.answer, args.category, args.key, schema)
        
        # Store structured fields
        structured_key = f"{args.key}_structured"
        
        # Store in the appropriate location
        if args.type == 'personal_info':
            structured_result = client.store_personal_info(structured_key, structured_data)
        elif args.type == 'preference':
            structured_result = client.store_preference(args.category, structured_key, structured_data)
        elif args.type == 'memory':
            structured_result = client.add_memory(
                content=f"{structured_key}: {json.dumps(structured_data)}",
                tags=['onboarding', args.category, 'structured_extraction'],
                context=f"Structured extraction for {args.key}"
            )
        elif args.type == 'goal':
            structured_result = client.add_goal(
                description=f"{structured_key}: {json.dumps(structured_data)}",
                category=f"{args.category}_structured"
            )
        elif args.type == 'relationship':
            structured_result = client.store_relationship(
                name=structured_key,
                relationship_type=f"{args.category}_structured",
                details={'structured_data': structured_data}
            )
    
    # Output results
    if 'error' in result:
        print(f"[ERROR] Failed to save main entry: {result['error']}")
        sys.exit(1)
    else:
        print(f"[OK] Saved raw to {args.type}: {args.key}_raw")
        if args.structured and structured_result:
            if 'error' in structured_result:
                print(f"[WARN] Raw saved, but structured extraction failed: {structured_result['error']}")
            else:
                print(f"[OK] Saved structured to {args.type}: {args.key}_structured")
                print(f"[INFO] Extracted {len([k for k in structured_data.keys() if not k.startswith('_')])} fields")


if __name__ == "__main__":
    main()
