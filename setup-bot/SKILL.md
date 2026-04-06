---
name: setup-bot
description: "Configure bot personality, communication style, and behavior via conversational questions. Updates SOUL.md, IDENTITY.md, and HEARTBEAT.md. Supports quick (3 questions) and full (6 questions) modes. Completely optional until user runs /setup-bot. Discord commands: /setup-bot quick, /setup-bot full"
---

# Setup Bot Skill

Configure your assistant's personality, communication style, and behavior via conversational interview. Populates SOUL.md, IDENTITY.md, and HEARTBEAT.md.

## Overview

**Optional until requested** — This skill is completely optional. Users can run `/setup-bot` at any time after creation to customize their bot's behavior. If not configured, bot uses sensible defaults.

**Separate from User Onboarding** — User onboarding learns about YOU (your preferences, stored in MCP). Setup-bot configures the BOT (how the bot behaves, stored in markdown files).

## Discord Commands

| Command | Description | Time |
|---------|-------------|------|
| `/setup-bot quick` | 3 questions (communication, tone, identity) | ~2 min |
| `/setup-bot full` | 6 questions (+ proactivity, boundaries, format prefs) | ~5 min |

### Multi-Turn Conversation Flow

**Quick mode (asked one at a time):**
```
User: /setup-bot quick
Bot: "When I communicate with you, should I be direct and concise, or conversational with context?"
User: "Direct"
Bot: [updates SOUL.md] "Got it. What tone feels right — professional, casual, witty, or warm?"
User: "Casual"
Bot: [updates SOUL.md] "What should I call myself?"
User: "Omega"
Bot: [updates IDENTITY.md] "Done! Your bot is now customized."
```

**After `load-user`:**
- User loads with `load-user`
- Sees default bot configuration
- **Optional**: Runs `/setup-bot` whenever they want to customize
- Changes take effect immediately

## Files Modified

| File | Sections Updated | When Updated |
|------|------------------|--------------|
| **SOUL.md** | Communication Style, Tone/Voice, Boundaries | During session |
| **IDENTITY.md** | Name, Emoji, Creature, Vibe | During session |
| **HEARTBEAT.md** | Proactivity Rules | Full mode only |

## How It Works

### State Tracking

The agent tracks setup-bot state in conversation context:
- `setup_bot_mode`: quick or full
- `setup_bot_question_num`: Current question number
- `setup_bot_question_data`: {category, key, file, section} for storing
- `setup_bot_remaining`: Questions still to ask

### Per-Question Update Flow

When user answers a setup-bot question:

1. **Parse the answer** using the question definition
2. **Update the appropriate file section** immediately:
   ```python
   from skills.setup_bot.scripts import update_config
   update_config.apply_answer(
       category="communication",
       key="directness",
       answer="direct",
       section_data=question_data
   )
   ```
3. **Show confirmation** (brief, no walls of text)
4. **Ask next question** or finish

### Question Format

Defined in `references/setup-bot-questions.yaml`:

```yaml
quick:
  - category: "communication"
    file: "SOUL.md"
    section: "Communication Style"
    order: 1
    questions:
      - "When I communicate with you, should I be direct and concise, or conversational with context?"
    options:
      - key: "directness"
        type: "choice"
        choices:
          - value: "direct"
            label: "Direct and concise"
          - value: "conversational"
            label: "Conversational with context"
```

## Section Update Logic

The skill **appends or updates** sections in existing files (doesn't overwrite whole file):

```python
# SOUL.md - Insert section after ## Core Truths
if file == "SOUL.md" and section == "Communication Style":
    insert_after("## Core Truths", "## Communication Style", content)

# IDENTITY.md - Update frontmatter fields
if file == "IDENTITY.md":
    update_field("Name", answer_value)
    update_field("Emoji", answer_value)
```

## CLI Usage

```bash
# Interactive mode (asks all questions)
python skills/setup-bot/scripts/setup-bot.py --mode quick
python skills/setup-bot/scripts/setup-bot.py --mode full

# Non-interactive with defaults
python skills/setup-bot/scripts/setup-bot.py --mode quick --defaults

# Update specific section only
python skills/setup-bot/scripts/update_section.py \
  --file SOUL.md \
  --section "Communication Style" \
  --content "**Directness:** direct"
```

## Quick vs Full Mode

### Quick Mode (3 Questions)

1. **Communication Style** → SOUL.md
   - Direct/concise vs conversational
   - Stored in `## Communication Style` section

2. **Tone/Voice** → SOUL.md
   - Professional, casual, witty, warm, neutral
   - Stored in `## Tone / Voice` section

3. **Bot Identity** → IDENTITY.md
   - Name, emoji, creature type
   - Updates frontmatter fields

### Full Mode (6 Questions)

Quick mode +:

4. **Proactivity Level** → HEARTBEAT.md
   - Check-in frequency
   - Suggestion mode
   - Trigger preferences
   - Stored in `## Proactivity Rules`

5. **Boundaries** → SOUL.md
   - Confirm before actions
   - Data handling preferences
   - Stored in `## Boundaries` section

6. **Format Preferences** → SOUL.md
   - Bullet points vs paragraphs
   - Markdown preferences
   - Pet peeves

## Architecture

```
skills/setup-bot/
├── SKILL.md                           # This file
├── scripts/
│   ├── setup-bot.py                   # Main interactive script
│   ├── store_answer.py                # Per-answer update (Discord use)
│   └── update_section.py              # Section manipulation utilities
├── references/
│   └── setup-bot-questions.yaml       # Question catalog
└── templates/                         # Section content templates
    ├── communication-section.md
    ├── tone-section.md
    └── heartbeat-proactivity.md
```

## Security / Privacy

- **No MCP storage** — Bot config stays in markdown files only
- **No Simple Graph** — Not added to knowledge graph
- **User-writable** — Users own their bot config files
- **Version controlled** — Changes visible in git diffs

## Comparison: Onboarding vs Bot Config

| | User Onboarding | Bot Configuration |
|--|-------------------|-------------------|
| **Purpose** | Learn about the user | Customize the bot |
| **Command** | `/onboard` | `/setup-bot` |
| **Storage** | Personal MCP server | Markdown files |
| **Scope** | What I know about you | How I behave |
| **Optional** | Recommended at start | Fully optional |

## Troubleshooting

**"File not found"**
- Run `load-user` first to create user files
- Then run `/setup-bot`

**"Section already exists"**
- This is normal — existing sections are updated, not duplicated

**"Want to redo configuration"**
- Run `/setup-bot` again — sections will be updated with new values

---
*Created: 2026-02-16*
