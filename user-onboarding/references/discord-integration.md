# Discord Integration Example

This shows how to integrate the onboarding skill into OpenClaw/Discord.

## Option 1: Direct Skill Trigger

Add a command handler that triggers the onboarding skill:

```python
# In your Discord bot command handler

from skills.user_onboarding.scripts.onboard_bot import OnboardingBot
from projects.personal-memory-mcp-docker.bridge import rawrity, sigma

# Map Discord users to MCP clients
USER_CLIENTS = {
    'rawrity_': rawrity,
    'sigma': sigma,
}

async def handle_onboard_command(message, user_id):
    """Handle /onboard command"""
    client = USER_CLIENTS.get(user_id)
    if not client:
        await message.channel.send("Unknown user. Are you registered?")
        return
    
    bot = OnboardingBot(mcp_client=client)
    
    # Get a question flow
    questions = bot.get_suggested_question_flow(5)
    
    # Send first question
    q = questions[0]
    await message.channel.send(
        f"**Let's get to know you better!** (Question 1 of 5)\n\n"
        f"*{q['text']}*\n\n"
        f"Reply with your answer, or type 'skip' to move on."
    )
    
    # Store state for continuing the conversation
    # (You'd need to track which question number and the question data)
```

## Option 2: Natural Conversation Trigger

Instead of a formal /onboard command, trigger onboarding naturally:

```python
# When a new user sends their first message
async def on_first_message(message):
    # Check if user has any personal info stored
    client = get_client_for_user(message.author)
    stats = client.get_stats()
    
    if stats['personal_info_count'] == 0:
        # No data yet - offer onboarding
        await message.channel.send(
            "Hey! I don't know much about you yet. "
            "Want to do a quick onboarding? Just reply 'yes' and I'll ask a few fun questions!"
        )
        # ... handle their response
```

## Option 3: Category-Specific Questions

For more targeted information gathering:

```python
async def ask_about_travel(message, user_id):
    """Ask travel-related questions"""
    client = USER_CLIENTS.get(user_id)
    bot = OnboardingBot(mcp_client=client)
    
    # Get a travel question
    q = bot.get_question(category='travel')
    
    await message.channel.send(f"Speaking of travel... {q['text']}")
    
    # Wait for response, then store it
    # ... message handling logic
    answer = message.content
    bot.store_answer(q, answer)
```

## Option 4: Periodic Check-ins

Use heartbeats to periodically ask new questions:

```yaml
# In heartbeat configuration
onboarding:
  check_interval: 7 days
  max_questions_per_session: 2
  categories_to_rotate:
    - food
    - entertainment
    - travel
    - goals
```

```python
# In heartbeat handler
def heartbeat_onboarding_check(user_id):
    client = USER_CLIENTS.get(user_id)
    bot = OnboardingBot(mcp_client=client)
    
    # Pick a random category
    import random
    category = random.choice(['food', 'travel', 'goals', 'entertainment'])
    
    # Get question
    q = bot.get_question(category=category)
    
    return f"Random check-in: {q['text']}"
```

## Storing Answers

Once you have a user's answer:

```python
from skills.user_onboarding.scripts.onboard_bot import OnboardingBot

# The question data includes everything needed to store properly
q = {
    'text': "What's your favorite food?",
    'category': 'food',
    'storage_key': 'cuisine_preferences',
    'type': 'preference'
}

answer = "Sushi, especially salmon"

bot = OnboardingBot(mcp_client=client)
result = bot.store_answer(q, answer)

# result will be the MCP server response
# {'status': 'success', 'category': 'food', ...}
```

## Available Categories for Targeted Questions

```python
bot = OnboardingBot(mcp_client=client)
categories = bot.get_categories()
# Returns: ['entertainment', 'food', 'goals', 'identity', 
#           'lifestyle', 'preferences', 'professional', 
#           'quirks', 'relationships', 'tech', 'travel']
```

## Quick Demo Command

```python
async def demo_question(message):
    """Show a random question as a demo"""
    bot = OnboardingBot()
    q = bot.get_question()
    
    await message.channel.send(
        f"**Sample onboarding question:**\n"
        f"Category: {q['category']}\n"
        f"Key: {q['storage_key']}\n\n"
        f"> {q['text']}"
    )
```
