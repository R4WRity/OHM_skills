---
name: user-onboarding
description: "Engage new users in conversational onboarding to populate their Simple Graph MCP knowledge graph. Use when a new user joins the system, when /onboard is triggered, or when explicit onboarding is needed. Supports quick (5 questions), full (comprehensive), and custom (category-specific) modes with stop/resume support. Integrates with Dockerized Simple Graph MCP servers via HTTP bridge. Discord commands: /onboard, /onboard quick, /onboard full, /onboard custom, /onboard [category], /onboard_stop, /onboard_resume"
---

# User Onboarding Skill

Conversational onboarding system that asks witty, engaging questions to populate a user's **Simple Graph MCP** knowledge graph with useful information.

**IMPORTANT:** This skill now uses **Simple Graph MCP** (ports 9300-9302) instead of the legacy Personal Memory MCP. The onboarding adapter translates answers into entities and relationships for the graph visualization.

**NEW: Structured Mode** — Now supports dual storage (raw text + extracted entities) for better queryability and graph visualization.

## Architecture

Onboarding data flows as follows:
```
Onboarding Question → Answer → Simple Graph Adapter → Entities + Relationships
```

| User | Simple Graph Port | Neo4j Port | Purpose |
|------|-------------------|------------|---------|
| Set (∅ / rawrity) | 9301 | 7687 | Gerald's knowledge graph |
| Sigma (Σ) | 9302 | 7787 | Uthara's knowledge graph |
| Ohm (Ω / default) | 9300 | 7887 | System knowledge graph |

## Discord Commands

| Command | Description |
|---------|-------------|
| `/onboard` or `/onboard quick` | 5 essential questions (identity, food, professional, entertainment, lifestyle) |
| `/onboard full` | Comprehensive onboarding (all 11 categories, ~10-15 min) |
| `/onboard custom` | Show available categories, let user pick |
| `/onboard [category]` | Single question from specific category (e.g., `/onboard food`) |
| `/onboard categories` | List available categories |
| `/onboard_stop` | Pause onboarding and save progress (use anytime) |
| `/onboard_resume` | Continue from where you left off |
| `/onboard_status` | Check current onboarding progress |
| `/onboard_restart` | Clear progress and start fresh (asks for confirmation) |

### Structured Mode (Agent-Enabled)
When the agent runs onboarding with structured extraction enabled, each answer is stored **three ways**:
- `answer_raw` — Full original response preserved
- `answer_structured` — LLM-extracted fields (cuisines, activities, dishes, etc.)
- `answer` — Reference pointer to structured data

This enables queries like:
- "What Japanese foods does Set like?" → Query structured fields
- "Show me Set's exact words about their morning routine" → Query raw
- "Does Set have a sweet tooth?" → Query boolean in structured

### Usage Flow

**Quick onboarding (multi-turn conversation):**
```
User: /onboard
Bot: "First things first — what should I actually call you?..."
User: "Call me Set"
Bot: [saves, asks question 2]
User: [answers]
Bot: [saves, asks question 3]
...
Bot: "Quick onboarding complete! 5 things learned about you."
```

**Single category (one-shot):**
```
User: /onboard travel
Bot: "Favorite place you've ever been?"
User: "Japan — the food and culture were incredible"
Bot: [saves to memory, confirms]
```

## Agent Implementation (Simple Graph MCP)

When a user replies to an onboarding question, the agent should use the **Simple Graph Adapter**:

1. **Parse the question data** from the context (category, key, type stored in memory)
2. **Store the answer** using the `simple_graph_adapter.py` script:
   ```bash
   # Store onboarding answer as entities/relationships
   python skills/user-onboarding/scripts/simple_graph_adapter.py store \
     --user rawrity \
     --category food \
     --key cuisine_preferences \
     --answer "I love Japanese ramen and sushi" \
     --type preference
   ```
   
   This creates:
   - A **Memory** entity with the full answer
   - **Person** entity linked to the memory (if not exists)
   - Extracted entities (e.g., Cuisine nodes for "Japanese")
   - Relationships connecting person to extracted entities

3. **Save progress** after each answer (for stop/resume support):
   ```bash
   python skills/user-onboarding/scripts/simple_graph_adapter.py progress save \
     --user rawrity --mode full --question-num 3 \
     --completed '["identity", "food", "travel"]' \
     --remaining '["professional", "entertainment", "lifestyle"]' \
     --status active
   ```

4. **Continue or conclude** based on mode:
   - `quick` mode: Ask next of 5 questions, or finish after #5
   - `full` mode: Ask next question, or finish if user says "done"
   - Single category: Confirm save and stop

### Handling Stop/Resume Commands

**When user says `/onboard_stop`:**
1. Save current progress with `status: paused`
2. Reply: "⏸️ Onboarding paused. You've answered {N} questions, {M} remaining. Your progress is saved — just type `/onboard resume` to continue anytime."

**When user says `/onboard_resume`:**
1. Check for active progress: `simple_graph_adapter.py progress check --mode full`
2. If found:
   - Load `remaining_categories`
   - Reply: "▶️ Resuming onboarding... Question {N+1}: {question_text}"
   - Skip already-completed categories
3. If not found: "No paused onboarding found. Start with `/onboard full`"

**When user says `/onboard_status`:**
1. Get progress: `simple_graph_adapter.py progress get --mode full`
2. Reply: "📊 Onboarding status: {status} — {completed} categories done, {remaining} remaining. Last question: {N}."

**When user says `/onboard_restart`:**
1. Check for existing progress
2. Ask: "You have a paused session ({N} questions done). Resume or restart fresh?"
3. If restart: `simple_graph_adapter.py progress clear --mode full` then start from question 1

**When starting new onboarding with existing progress:**
```
User: /onboard full
Bot: "You have a paused full onboarding session (7/15 questions done). 
      Type '/onboard resume' to continue, or reply 'restart' to start fresh."
```

### State Tracking & Progress Persistence

The agent tracks onboarding state in conversation context:
- `onboarding_mode`: quick, full, or category name
- `onboarding_question_num`: Current question (for quick/full modes)
- `onboarding_question_data`: {category, key, type} for storing answer
- `onboarding_remaining`: List of categories/questions left (for full mode)
- `structured_mode`: Whether to extract and store structured fields

**Persistent Progress:** Progress is automatically saved to Simple Graph MCP after each answer. This enables:
- `/onboard_stop` — Pause anytime, progress is preserved
- `/onboard_resume` — Continue from where you left off
- `/onboard_status` — See how many questions remain

#### How Progress Works

```cypher
(Person)-[:HAS_ONBOARDING_PROGRESS]->(OnboardingProgress {
  mode: "full",
  last_question_num: 7,
  completed_categories: "[\"identity\", \"food\", \"travel\"]",
  remaining_categories: "[\"professional\", \"entertainment\", ...]",
  status: "paused"  // or "active", "completed"
})
```

**On each answer:**
1. Answer is stored to MCP (already happens)
2. Progress node is updated with current position

**On `/onboard_stop`:**
- Progress status → `paused`
- User gets: "Onboarding paused. 7 questions answered, 8 remaining. Type `/onboard resume` to continue."

**On `/onboard_resume`:**
1. Check for paused session → load `remaining_categories`
2. Resume from next question (skip completed ones)
3. If no paused session → "No paused onboarding found. Start with `/onboard full`"

**On `/onboard_restart`:**
- Ask: "You have a paused session (7/15 done). Resume or restart fresh?"
- If restart → clear progress, start from question 1

**Edge Cases:**

| Scenario | Behavior |
|----------|----------|
| Start new `/onboard full` while paused exists | Prompt: "Resume existing (7 done) or restart fresh?" |
| Switch modes (`quick` while `full` is paused) | Treat as separate — each mode has its own progress |
| Complete after pause | Progress → `completed`, can be archived |
| Multiple users | Progress keyed by user automatically |

### Structured Data Extraction

When `--structured` is enabled, the system parses natural language answers into queryable fields:

**Architecture:**
1. **Raw storage** — Full answer preserved as `key_raw` (never lost)
2. **Rule-based extraction** — Smart parsing using regex/patterns (current implementation)
3. **Structured storage** — Extracted fields saved as `key_structured`

**Current Extractors:**
- `extract_food_fields()` — Cuisines, dishes, ingredients, modifiers
- `extract_morning_routine_fields()` — Activities, phases, emotional tone, evolution narrative
- `extract_movie_fields()` — Titles, directors, genres, rewatchability
- `extract_professional_fields()` — Role, company, activities, relationships
- `extract_name_fields()` — Preferred name, legal name, handles, symbols

**Future: LLM-based extraction** — Replace rule-based with actual LLM calls for more intelligent parsing

**Query examples with structured data:**
```bash
# Query structured cuisine preferences
python -c "from projects.personal_memory_mcp_docker.bridge import rawrity; 
           prefs = rawrity.get_preferences('food'); 
           print(prefs['preferences']['cuisine_preferences_structured']['cuisines'])"
# Output: ['japanese']

# Check for sweet tooth
python -c "from projects.personal_memory_mcp_docker.bridge import rawrity; 
           prefs = rawrity.get_preferences('food'); 
           print(prefs['preferences']['cuisine_preferences_structured']['sweet_tooth'])"
# Output: True
```

## CLI Usage (Direct)

```bash
# Quick 5-question onboarding (default)
python skills/user-onboarding/scripts/onboard.py --user rawrity --mode quick

# Full comprehensive onboarding with structured extraction
python skills/user-onboarding/scripts/onboard.py --user rawrity --mode full --structured

# Custom category focus
python skills/user-onboarding/scripts/onboard.py --user rawrity --mode custom --categories food travel

# Single category with structured extraction
python skills/user-onboarding/scripts/onboard.py --user rawrity --mode custom --categories food --structured

# Progress management via adapter
python skills/user-onboarding/scripts/simple_graph_adapter.py --user rawrity progress save \
  --mode full --question-num 5 \
  --completed '["identity", "food"]' \
  --remaining '["travel", "professional", "entertainment"]' \
  --status paused

# Check progress status
python skills/user-onboarding/scripts/simple_graph_adapter.py --user rawrity progress get --mode full

# List all progress for user
python skills/user-onboarding/scripts/simple_graph_adapter.py --user rawrity progress list

# Mark as completed
python skills/user-onboarding/scripts/simple_graph_adapter.py --user rawrity progress complete --mode full

# Clear progress (start fresh)
python skills/user-onboarding/scripts/simple_graph_adapter.py --user rawrity progress clear --mode full
```

## Available Categories

The questions catalog (`references/onboarding-questions.yaml`) organizes questions into these categories:

| Category | What We Learn | Storage Type | Structured Extraction |
|----------|---------------|--------------|---------------------|
| `identity` | Name, age, location, occupation | `personal_info` | ✅ Name variants, handles, symbols |
| `food` | Cuisine preferences, restrictions, favorites | `preferences` | ✅ Cuisines, dishes, ingredients, modifiers |
| `entertainment` | Movies, TV, music, games, books | `memories` | ✅ Titles, directors, genres, rewatchability |
| `professional` | Role, skills, career goals, learning interests | `personal_info`, `goals` | ✅ Role, company, activities, relationships |
| `travel` | Favorite destinations, bucket list, travel style | `memories`, `goals` | ✅ Destinations, activities, disruptions, journey arc |
| `lifestyle` | Morning routine, hobbies, exercise, sleep | `preferences` | ✅ Activities, phases, emotional tone, evolution |
| `relationships` | Family, pets, emergency contacts | `relationships` | ✅ People, pets, dynamics, timeline, origins |
| `goals` | Short-term, long-term, current projects | `goals` | ✅ (passthrough with summary) |
| `preferences` | Communication style, productivity, decisions | `preferences` | ✅ (passthrough with summary) |
| `quirks` | Pet peeves, happy triggers | `memories` | ✅ (passthrough with summary) |
| `tech` | Devices, apps, workflow tools | `personal_info`, `preferences` | ✅ (passthrough with summary) |

**All 11 categories support structured mode.** The extractors for identity, food, entertainment, professional, travel, lifestyle, and relationships do deep parsing. Goals, preferences, quirks, and tech store the raw text with a summary (ready for LLM extraction upgrade).

## Question Catalog Format

Each question entry in the YAML file follows this structure:

```yaml
- category: "food"
  storage_key: "cuisine_preferences"
  type: "preference"
  questions:
    - "If I were to surprise you with takeout..."
    - "Pizza or sushi? Tacos or Thai?"
    - "Desert island cuisine — you can only eat one..."
```

**Fields:**
- `category`: Logical grouping for the question
- `storage_key`: Where in MCP to store the answer (e.g., `food.cuisine_preferences`)
- `type`: Storage mechanism — `personal_info`, `preference`, `memory`, `goal`, or `relationship`
- `questions`: Array of witty variants (script picks randomly)

## Storage Mapping

| Type | MCP Method | Use Case |
|------|-----------|----------|
| `personal_info` | `store_personal_info()` | Core facts (name, age, job) |
| `preference` | `store_preference()` | Categorical preferences (food, lifestyle) |
| `memory` | `add_memory()` | Experiences, favorites, stories |
| `goal` | `add_goal()` | Aspirations, projects, targets |
| `relationship` | `store_relationship()` | People, pets, contacts |

## For Discord/OpenClaw Integration

The onboarding script is designed to work with conversational interfaces. Key behaviors:

1. **Random question selection**: Each category has multiple witty variants — keeps it fresh
2. **Skip-friendly**: Users can type 'skip', 'pass', or hit Enter to skip any question
3. **Early exit**: Type 'done' during full mode to wrap up early
4. **Confirmation**: Shows what's been saved after each answer
5. **Structured mode available**: Agent can enable `--structured` for dual storage (raw + extracted fields)

### Agent Workflow for Structured Mode

```
User: /onboard quick
Agent: Q1 question...
User: [long conversational answer]
Agent: @exec python skills/user-onboarding/scripts/simple_graph_adapter.py store \
       --user rawrity --category travel --key favorite_destinations \
       --answer "[user text]" --type memory
Agent: @exec python skills/user-onboarding/scripts/simple_graph_adapter.py progress save \
       --user rawrity --mode quick --question-num 1 \
       --completed '["identity"]' --remaining '["food", "professional", "entertainment", "lifestyle"]'
Agent: [OK] Saved raw + 12 extracted fields
Agent: Q2 question...
```

## Multi-User Support

Onboarding works across all configured Simple Graph MCP users:

| User | Username | Simple Graph Port | Neo4j Port |
|------|----------|-------------------|------------|
| Set (∅) | `rawrity` | 9301 | 7687 |
| Sigma (Σ) | `sigma` | 9302 | 7787 |
| Ohm (Ω) | `default` | 9300 | 7887 |

**Example commands:**
```bash
# Onboard Set (rawrity)
python simple_graph_adapter.py --user rawrity --category food --key cuisine --answer "Sushi"

# Onboard Sigma
python simple_graph_adapter.py --user sigma --category travel --key destinations --answer "Japan, Iceland"
```

**Data Storage:**
Each user's Simple Graph MCP server stores their onboarding data as entities and relationships independently. The DATAVIZ wallpaper will show the combined graph with color-coded servers (green=rawrity, magenta=sigma, cyan=default).

## Extending Questions

To add new questions, edit `references/onboarding-questions.yaml`:

1. Add a new entry with unique `storage_key`
2. Choose appropriate `category` and `type`
3. Write 2-3 question variants (witty, direct, thoughtful)
4. Restart onboarding to see new questions immediately

## Programmatic Usage (Simple Graph MCP)

```python
from skills.user_onboarding.scripts.simple_graph_adapter import SimpleGraphOnboardingAdapter

# Create adapter for user
adapter = SimpleGraphOnboardingAdapter("rawrity")

# Store onboarding answer
adapter.store_answer(
    category="food",
    key="cuisine_preferences",
    answer="I love Japanese ramen with black garlic",
    answer_type="preference"
)

# This creates:
# - Person entity: "Gerald Hardin"
# - Memory entity: "Gerald Hardin - cuisine_preferences" with full answer
# - Cuisine entity: "Cuisine - Japanese" linked to person
# - Dish entity: "Dish - Ramen" linked to person
# - Relationships: Person --HAS_MEMORY--> Memory, Person --LIKES_CUISINE--> Cuisine
```

**Query the onboarded data:**
```cypher
// Neo4j Browser: http://localhost:7474

// What memories does Gerald have?
MATCH (p:Person {name: "Gerald Hardin"})-[:HAS_MEMORY]->(m)
RETURN m.name, m.answer

// What cuisines does Gerald like?
MATCH (p:Person {name: "Gerald Hardin"})-[:LIKES_CUISINE]->(c)
RETURN c.name
```
