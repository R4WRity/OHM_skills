# Quick Integration Test for User Onboarding

## Test 1: List Categories
```bash
node skills/user-onboarding/scripts/onboard.js categories
```
Expected: Shows 11 categories

## Test 2: Single Question
```bash
node skills/user-onboarding/scripts/onboard.js food
```
Expected: Returns a food-related question with [food] tag

## Test 3: Store Answer
```bash
python skills/user-onboarding/scripts/store_answer.py \
  --port 9001 \
  --category food \
  --key cuisine_preferences \
  --type preference \
  --answer "Italian pasta"
```
Expected: [OK] Saved to preference: cuisine_preferences

## Test 4: Quick Mode Start
```bash
node skills/user-onboarding/scripts/onboard.js quick
```
Expected: Shows intro message + first identity question

## Test 5: Full Mode Start
```bash
node skills/user-onboarding/scripts/onboard.js full
```
Expected: Shows comprehensive intro + first question

## Test 6: Python Direct (Alternative)
```bash
# Get question
python skills/user-onboarding/scripts/onboard_bot.py --random

# Get from category
python skills/user-onboarding/scripts/onboard_bot.py --category travel

# Get question flow
python skills/user-onboarding/scripts/onboard_bot.py --flow 3
```

## Discord Command Mapping

| What User Types | What Runs | What Bot Does |
|-----------------|-----------|---------------|
| `/onboard` | `onboard.js quick` | Asks 5 questions sequentially |
| `/onboard quick` | `onboard.js quick` | Same as above |
| `/onboard full` | `onboard.js full` | Asks all categories, multiple per category |
| `/onboard food` | `onboard.js food` | Asks 1 food question |
| `/onboard categories` | `onboard.js categories` | Lists categories |

## Agent Response Flow

When user replies to an onboarding question:

1. Detect context (previous message was onboarding question)
2. Extract question metadata:
   - category: from [category] tag in previous message
   - storage_key: from question data or context
   - type: from question data
3. Call store_answer.py with:
   - port (from user mapping)
   - category, key, type
   - answer (user's message content)
4. Continue flow based on mode:
   - quick: Ask next question (or finish if 5 done)
   - full: Ask next question (or finish if user said "done")
   - single: Confirm save and end
