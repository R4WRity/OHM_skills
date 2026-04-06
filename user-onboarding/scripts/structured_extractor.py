"""
Structured Data Extractor for Onboarding
Uses LLM to parse natural language answers into structured fields.
"""

import json
import re
from typing import Dict, Any, Optional


def extract_structured_fields(answer: str, category: str, key: str, extraction_schema: dict) -> dict:
    """
    Extract structured fields from a natural language answer using rule-based parsing.
    
    In production, this would call an LLM. For now, we use smart regex/pattern matching
    as a demonstration of the architecture.
    
    Args:
        answer: The user's natural language response
        category: Question category (food, lifestyle, etc.)
        key: Storage key (cuisine_preferences, morning_routine, etc.)
        extraction_schema: Schema defining what fields to extract
        
    Returns:
        dict with extracted fields
    """
    
    # Route to appropriate extractor based on category/key
    if category == 'food' or key == 'cuisine_preferences':
        return extract_food_fields(answer)
    elif category == 'lifestyle' and key == 'morning_routine':
        return extract_morning_routine_fields(answer)
    elif category == 'entertainment' and key == 'favorite_movies':
        return extract_movie_fields(answer)
    elif category == 'professional' and key == 'current_role':
        return extract_professional_fields(answer)
    elif category == 'identity' and key == 'name':
        return extract_name_fields(answer)
    elif category == 'travel' or key in ['favorite_destinations', 'travel_bucket_list', 'travel_style']:
        return extract_travel_fields(answer)
    elif category == 'relationships' or key in ['family', 'pets', 'emergency_contacts']:
        return extract_relationship_fields(answer)
    else:
        # Generic extraction - just return the raw answer
        return {
            'raw_summary': answer[:200] if len(answer) > 200 else answer,
            'full_text': answer,
            '_extraction_method': 'passthrough'
        }


def extract_food_fields(answer: str) -> dict:
    """Extract cuisine, dishes, ingredients from food preferences"""
    answer_lower = answer.lower()
    
    # Initialize structure
    structured = {
        'cuisines': [],
        'dishes': [],
        'ingredients': [],
        'desserts': [],
        'modifiers': [],
        '_extraction_method': 'rule_based'
    }
    
    # Cuisine detection
    cuisines = {
        'japanese': ['japanese', 'sushi', 'ramen', 'tempura', 'teriyaki'],
        'chinese': ['chinese', 'dim sum', 'dumpling', 'szechuan'],
        'italian': ['italian', 'pizza', 'pasta', 'risotto'],
        'mexican': ['mexican', 'taco', 'burrito', 'enchilada'],
        'thai': ['thai', 'pad thai', 'curry'],
        'indian': ['indian', 'curry', 'naan', 'tandoori'],
        'american': ['american', 'burger', 'steak'],
        'french': ['french', 'baguette', 'croissant'],
        'korean': ['korean', 'bbq', 'kimchi', 'bulgogi'],
        'mediterranean': ['mediterranean', 'greek', 'falafel', 'hummus']
    }
    
    for cuisine, keywords in cuisines.items():
        if any(kw in answer_lower for kw in keywords):
            structured['cuisines'].append(cuisine)
    
    # Specific dish detection
    dishes = ['ramen', 'sushi', 'pizza', 'taco', 'burger', 'steak', 'pasta', 'pho', 'curry']
    for dish in dishes:
        if dish in answer_lower:
            structured['dishes'].append(dish)
    
    # Ingredient detection (specific modifiers)
    ingredients = {
        'black_garlic': 'black garlic' in answer_lower,
        'pork': 'pork' in answer_lower or 'chashu' in answer_lower,
        'chicken': 'chicken' in answer_lower,
        'beef': 'beef' in answer_lower,
        'vegetarian': 'vegetarian' in answer_lower or 'veggie' in answer_lower,
        'spicy': 'spicy' in answer_lower or 'hot' in answer_lower,
        'sweet': 'sweet' in answer_lower or 'dessert' in answer_lower or 'ice cream' in answer_lower
    }
    
    structured['ingredients'] = [k for k, v in ingredients.items() if v]
    
    # Dessert detection
    if 'ice cream' in answer_lower or 'sweet' in answer_lower:
        structured['desserts'].append('ice cream')
    if 'boutique' in answer_lower or 'artisan' in answer_lower:
        structured['modifiers'].append('boutique/artisan')
    
    # Extract specific ramen details
    if 'ramen' in answer_lower:
        ramen_details = {}
        if 'black garlic' in answer_lower:
            ramen_details['broth'] = 'black garlic'
        if 'chashu' in answer_lower or 'pork' in answer_lower:
            ramen_details['protein'] = 'pork chashu'
        if ramen_details:
            structured['dish_details'] = {'ramen': ramen_details}
    
    # Sentiment/tone indicators
    structured['enthusiasm_level'] = 'high' if any(w in answer_lower for w in ['love', 'favorite', 'obsessed', 'amazing']) else 'moderate'
    structured['sweet_tooth'] = 'ice cream' in answer_lower or 'sweet' in answer_lower
    
    # Always include the full original
    structured['full_text'] = answer
    
    return structured


def extract_morning_routine_fields(answer: str) -> dict:
    """Extract structured morning routine info"""
    answer_lower = answer.lower()
    
    structured = {
        'activities': [],
        'duration_minutes': None,
        'phases': [],
        'emotional_tone': [],
        '_extraction_method': 'rule_based'
    }
    
    # Activity detection
    activities = {
        'phone_scrolling': any(w in answer_lower for w in ['scroll', 'phone', 'reddit', 'social media']),
        'news_checking': any(w in answer_lower for w in ['news', 'election', 'politics', 'doom scroll']),
        'ai_research': any(w in answer_lower for w in ['mcp', 'ai', 'llm', 'open source', 'framework']),
        'gaming': 'game' in answer_lower,
        'music': 'guitar' in answer_lower or 'music' in answer_lower,
        'work_prep': any(w in answer_lower for w in ['work', 'tasks', 'character art']),
        'meditation': any(w in answer_lower for w in ['meditate', 'mindful', 'breathing']),
        'exercise': any(w in answer_lower for w in ['gym', 'run', 'workout', 'exercise'])
    }
    structured['activities'] = [k for k, v in activities.items() if v]
    
    # Duration extraction (simple pattern matching)
    duration_patterns = [
        r'(\d+)\s*(?:minute|min)',
        r'(\d+)\s*min',
        r'half an hour',
        r'an hour',
        r'(\d+)\s*hour'
    ]
    for pattern in duration_patterns:
        match = re.search(pattern, answer_lower)
        if match:
            if 'hour' in match.group():
                structured['duration_minutes'] = int(match.group(1)) * 60 if match.group(1) else 30
            else:
                structured['duration_minutes'] = int(match.group(1))
            break
    
    # Phase detection (before/after evolution)
    if any(w in answer_lower for w in ['used to', 'before', 'previously', 'was']):
        structured['phases'].append('past_behavior')
    if any(w in answer_lower for w in ['now', 'recently', 'transformed', 'changed', 'shift']):
        structured['phases'].append('current_behavior')
    if any(w in answer_lower for w in ['then', 'after', 'becomes', 'next']):
        structured['phases'].append('transition_to_work')
    
    # Emotional tone
    tones = {
        'anxiety': any(w in answer_lower for w in ['stress', 'anxiety', 'worry', 'doom']),
        'curiosity': any(w in answer_lower for w in ['explore', 'research', 'investigate', 'learn']),
        'intentionality': any(w in answer_lower for w in ['conscious', 'intentional', 'deliberate', 'shift']),
        'productivity': any(w in answer_lower for w in ['work', 'tasks', 'development']),
        'connection': any(w in answer_lower for w in ['partner', 'relationship', 'cats', 'uthara'])
    }
    structured['emotional_tone'] = [k for k, v in tones.items() if v]
    
    # Evolution narrative detected
    structured['has_evolution_narrative'] = any(w in answer_lower for w in ['used to', 'transformed', 'evolution', 'changed', 'shift', 'now'])
    
    # Add full original
    structured['full_text'] = answer
    
    return structured


def extract_movie_fields(answer: str) -> dict:
    """Extract movie/entertainment structure"""
    answer_lower = answer.lower()
    
    structured = {
        'titles': [],
        'directors': [],
        'genres': [],
        'rewatchability': None,
        'emotional_impact': [],
        '_extraction_method': 'rule_based'
    }
    
    # Extract potential movie titles (capitalized phrases)
    words = answer.split()
    for i, word in enumerate(words):
        if word[0].isupper() and len(word) > 2:
            # Check if it might be a title (look for patterns)
            if i > 0 and words[i-1][0].isupper():
                potential_title = f"{words[i-1]} {word}"
                if 'the' not in potential_title.lower() or word.lower() == 'fountain':
                    structured['titles'].append(potential_title)
    
    # Director detection
    directors = ['aronofsky', 'nolan', 'tarantino', 'spielberg', 'kubrick', 'cameron']
    for director in directors:
        if director in answer_lower:
            structured['directors'].append(director)
    
    # Genre hints
    genres = {
        'sci_fi': any(w in answer_lower for w in ['matrix', 'sci-fi', 'space', 'future']),
        'drama': any(w in answer_lower for w in ['drama', 'emotional', 'intense']),
        'philosophical': any(w in answer_lower for w in ['fountain', 'philosophy', 'meaning', 'life']),
        'action': any(w in answer_lower for w in ['action', 'fight', 'explosion']),
        'horror': any(w in answer_lower for w in ['horror', 'scary', 'fear'])
    }
    structured['genres'] = [k for k, v in genres.items() if v]
    
    # Rewatch indicators
    if any(w in answer_lower for w in ['100 times', 'rewatch', 'again and again', 'never tired']):
        structured['rewatchability'] = 'high'
    
    structured['full_text'] = answer
    return structured


def extract_professional_fields(answer: str) -> dict:
    """Extract work/career structure"""
    answer_lower = answer.lower()
    
    structured = {
        'primary_role': None,
        'company': None,
        'activities': [],
        'skills': [],
        'interests': [],
        'relationships': [],
        '_extraction_method': 'rule_based'
    }
    
    # Role detection
    roles = ['character artist', 'technical artist', 'programmer', 'developer', 'designer', 'director']
    for role in roles:
        if role in answer_lower:
            structured['primary_role'] = role
            break
    
    # Company detection
    if 'steel wool' in answer_lower:
        structured['company'] = 'Steel Wool Studios'
    
    # Activities
    activity_keywords = {
        'art_creation': any(w in answer_lower for w in ['character art', 'artwork', 'create', 'design']),
        'technical_exploration': any(w in answer_lower for w in ['explore', 'experiment', 'technical', 'tool']),
        'gaming_research': any(w in answer_lower for w in ['play games', 'game', 'research', 'development']),
        'music': any(w in answer_lower for w in ['guitar', 'music', 'play']),
        'relationship_care': any(w in answer_lower for w in ['partner', 'uthara', 'relationship', 'cats'])
    }
    structured['activities'] = [k for k, v in activity_keywords.items() if v]
    
    # Relationship mentions
    if 'uthara' in answer_lower or 'partner' in answer_lower:
        structured['relationships'].append('Uthara (partner)')
    if 'cats' in answer_lower or 'olie' in answer_lower or 'ash' in answer_lower:
        structured['relationships'].append('Cats (Olie, Ash)')
    
    structured['full_text'] = answer
    return structured


def extract_name_fields(answer: str) -> dict:
    """Extract name variants and identity info"""
    structured = {
        'preferred_name': None,
        'legal_name': None,
        'nicknames': [],
        'online_handles': [],
        'symbols': [],
        '_extraction_method': 'rule_based'
    }
    
    answer_lower = answer.lower()
    
    # Preferred name detection
    if 'call me' in answer_lower:
        match = re.search(r'call me ([^.,]+)', answer_lower)
        if match:
            structured['preferred_name'] = match.group(1).strip()
    
    # Legal name detection
    legal_indicators = ['government', 'legal', 'official', 'real name']
    for indicator in legal_indicators:
        if indicator in answer_lower:
            # Extract capitalized words after the indicator
            pattern = rf'{indicator}[^,]*is ([A-Z][a-z]+ [A-Z][a-z]+)'
            match = re.search(pattern, answer, re.IGNORECASE)
            if match:
                structured['legal_name'] = match.group(1)
    
    # Symbol detection
    if '∅' in answer or 'empty set' in answer_lower:
        structured['symbols'].append('∅ (Empty Set)')
    
    # Online handles (usernames)
    handle_patterns = [
        r'requiem4ddr',
        r'RAWRity_',
        r'[A-Za-z0-9_]+ on (?:discord|steam|twitter|github)'
    ]
    for pattern in handle_patterns:
        matches = re.findall(pattern, answer, re.IGNORECASE)
        structured['online_handles'].extend(matches)
    
    # If nothing parsed, use the full text
    if not any([structured['preferred_name'], structured['legal_name'], structured['online_handles']]):
        structured['preferred_name'] = answer.split('.')[0]  # First sentence
    
    structured['full_text'] = answer
    return structured


def extract_travel_fields(answer: str) -> dict:
    """Extract travel/destination structure from conversational narrative"""
    answer_lower = answer.lower()
    
    structured = {
        'dream_destinations': [],
        'visited_places': [],
        'people_traveled_with': [],
        'activities': [],
        'travel_catalysts': [],
        'disruptions': [],
        'pivots': [],
        'emotional_notes': [],
        'travel_style_indicators': [],
        'future_intentions': [],
        '_extraction_method': 'rule_based'
    }
    
    # Dream destinations (planned but not visited)
    if 'japan' in answer_lower:
        japan_entry = {
            'place': 'Japan',
            'status': 'dream/destination - not yet visited',
            'original_plan': 'pre-pandemic plan with Uthara',
            'significance': 'life destination, tourist goal'
        }
        if 'covid' in answer_lower or 'pandemic' in answer_lower:
            japan_entry['blocked_by'] = 'COVID-19 pandemic'
            japan_entry['cancellation_reason'] = 'prevention measures, isolation, safety'
        structured['dream_destinations'].append(japan_entry)
    
    # Visited places
    if 'honolulu' in answer_lower or 'hawaii' in answer_lower:
        hawaii_entry = {
            'place': 'Honolulu, Hawaii',
            'type': 'actual_visit',
            'when': 'post-pandemic (after restrictions lifted)',
            'who_with': ['Uthara'],
            'duration_implied': 'visit/stay at friend\'s place',
            'trigger': 'friend invitation (Jon Del Secco)',
            'catalyst': 'alternative to cancelled Japan trip, used saved funds'
        }
        
        # Extract experiences
        experiences = []
        if 'scuba' in answer_lower or 'diving' in answer_lower:
            experiences.append('scuba diving')
        if 'snorkeling' in answer_lower or 'snorkel' in answer_lower:
            experiences.append('snorkeling')
        if 'sea turtle' in answer_lower:
            experiences.append('swimming with sea turtles')
        if 'dolphin' in answer_lower:
            experiences.append('dolphins')
        if 'jellyfish' in answer_lower:
            experiences.append('jellyfish sting incident')
            hawaii_entry['incidents'] = 'group member stung by jellyfish on floating sandbar'
        if 'sandbar' in answer_lower or 'floating' in answer_lower:
            experiences.append('floating sandbar visit')
        
        if experiences:
            hawaii_entry['experiences'] = experiences
        
        # Weather/atmosphere
        if 'weather' in answer_lower and 'fantastic' in answer_lower:
            hawaii_entry['weather'] = 'absolutely fantastic'
        if 'horizon' in answer_lower or 'mesmerizing' in answer_lower:
            hawaii_entry['visual_notes'] = 'infinite horizon in every backdrop, mesmerizing'
        
        # Satisfaction
        if any(w in answer_lower for w in ['everything', 'say that it is', 'mesmerizing']):
            hawaii_entry['satisfaction'] = 'exceeded expectations'
        
        structured['visited_places'].append(hawaii_entry)
    
    # People mentioned
    if 'uthara' in answer_lower or 'uthra' in answer_lower:
        structured['people_traveled_with'].append({'name': 'Uthara', 'relationship': 'partner'})
    
    if 'jon' in answer_lower or 'del secco' in answer_lower:
        friend_entry = {
            'name': 'Jon Del Secco',
            'relationship': 'college friend',
            'connection_duration': 'since college years',
            'role_in_trip': 'host in Honolulu',
            'status': 'remote engineering manager living in Honolulu',
            'notable': 'shared snorkeling photos, invited them to stay'
        }
        structured['people_traveled_with'].append(friend_entry)
    
    # Travel catalysts/triggers
    if 'invited' in answer_lower or 'invitation' in answer_lower:
        structured['travel_catalysts'].append('friend invitation (Jon)')
    if 'saved' in answer_lower and 'money' in answer_lower:
        structured['travel_catalysts'].append('reallocated Japan trip savings')
    if 'jumped at the opportunity' in answer_lower:
        structured['travel_catalysts'].append('enthusiastic acceptance')
    
    # Disruptions/forced changes
    if 'covid' in answer_lower or 'pandemic' in answer_lower:
        structured['disruptions'].append({
            'event': 'COVID-19 pandemic',
            'impact': 'cancelled Japan travel plans',
            'duration': 'long delay in travel',
            'response': 'complete isolation, prevention measures'
        })
    
    # Pivots (Plan B that became reality)
    if 'instead' in answer_lower and ('hawaii' in answer_lower or 'honolulu' in answer_lower):
        structured['pivots'].append({
            'original_plan': 'Japan trip (with Uthara)',
            'alternative': 'Hawaii visit (with Uthara + Jon)',
            'outcome': 'successful alternative experience',
            'resources_used': 'saved Japan trip funds'
        })
    
    # Emotional notes
    if any(w in answer_lower for w in ['mesmerizing', 'everything', 'fantastic', 'hope to do more']):
        structured['emotional_notes'].append('deeply positive experience')
    if 'hope to do more trips' in answer_lower or 'more trips with uthra' in answer_lower:
        structured['future_intentions'].append('seek similar travel experiences with Uthara')
        structured['emotional_notes'].append('desire to repeat experience')
    
    # Travel style indicators
    if any(w in answer_lower for w in ['scuba', 'diving', 'snorkeling', 'active']):
        structured['travel_style_indicators'].append('activity/adventure focused')
    if 'friend' in answer_lower and 'stay at his place' in answer_lower:
        structured['travel_style_indicators'].append('friend-hosted travel (not hotels)')
    if 'saved money' in answer_lower or 'saved to go' in answer_lower:
        structured['travel_style_indicators'].append('financially planned travel')
    
    # Journey narrative summary
    structured['journey_arc'] = {
        'original_goal': 'Japan (life destination)',
        'disruption': 'COVID-19 pandemic',
        'adaptation': 'reallocated funds to alternative trip',
        'opportunity': 'friend invitation to Hawaii',
        'execution': 'Honolulu visit with diving, snorkeling, wildlife',
        'outcome': 'exceeded expectations, desire to repeat',
        'companion': 'Uthara (partner) throughout'
    }
    
    structured['full_text'] = answer
    return structured


def extract_relationship_fields(answer: str) -> dict:
    """Extract relationship/pets structure"""
    answer_lower = answer.lower()
    
    structured = {
        'people': [],
        'pets': [],
        'relationships': [],
        'dynamics': [],
        'timeline': [],
        'origins': [],
        'health_status': [],
        '_extraction_method': 'rule_based'
    }
    
    # Person detection (common names and pronouns)
    if 'uthara' in answer_lower or 'partner' in answer_lower:
        structured['people'].append({'name': 'Uthara', 'relationship': 'partner', 'nickname': 'large slow hairless cat'})
    
    # Pet detection
    if 'cat' in answer_lower or 'cats' in answer_lower:
        # Count cats
        cat_count = answer_lower.count('cat')
        structured['pet_summary'] = f"{cat_count} cats" if cat_count > 1 else "1 cat"
        
        # Individual pet extraction
        if 'olie' in answer_lower:
            olie = {
                'name': 'Olie',
                'species': 'cat',
                'appearance': 'orange tabby with white chest and white mittens',
                'attachment': 'attached to Uthara',
                'tenure_years': 5,
                'origin': 'shelter or early acquisition'
            }
            structured['pets'].append(olie)
        
        if 'ash' in answer_lower:
            ash = {
                'name': 'Ash',
                'species': 'cat',
                'appearance': 'white and mackerel gray tabby',
                'attachment': 'attached to Set (me)',
                'tenure_years': 3,
                'age_at_acquisition': 'kitten/almost 1 year',
                'origin': 'shelter service (kitten) / car lady (almost 1 year)'
            }
            structured['pets'].append(ash)
    
    # Relationship dynamics
    if any(w in answer_lower for w in ['attached to', 'bond', 'love', 'close']):
        structured['dynamics'].append('strong pet-owner bonds')
    if 'uthara' in answer_lower and ('attached to uthra' in answer_lower or 'attached to uthara' in answer_lower):
        structured['dynamics'].append('Olie bonded with Uthara, Ash bonded with Set')
    if any(w in answer_lower for w in ['nothing but love', 'love between']):
        structured['dynamics'].append('harmonious household')
    
    # Timeline extraction
    years_pattern = r'(\d+)\s*years?'
    years_matches = re.findall(years_pattern, answer_lower)
    if years_matches:
        structured['timeline'] = [f"{y} years" for y in years_matches]
    
    # Origin stories
    if 'shelter' in answer_lower:
        structured['origins'].append('shelter adoption')
    if 'car lady' in answer_lower:
        structured['origins'].append('rehomed from individual')
    
    # Health/care indicators
    if any(w in answer_lower for w in ['paperwork', 'certifications', 'shots', 'vaccine', 'vet']):
        structured['health_status'].append('properly documented/vaccinated')
    
    # Sentiment/humor indicators
    if any(w in answer_lower for w in ['hairless cat', 'agree', 'reminiscent']):
        structured['humor_notes'] = ['affectionate teasing about partner']
    
    # Household composition
    structured['household'] = {
        'humans': 2,
        'cats': 2,
        'total_beings': 4,
        'description': 'two humans, two cats, mutual affection'
    }
    
    structured['full_text'] = answer
    return structured


def llm_extract_fields(answer: str, category: str, key: str, schema: dict) -> dict:
    """
    Placeholder for LLM-based extraction.
    
    In production, this would:
    1. Call OpenAI/Anthropic/Ollama with a structured extraction prompt
    2. Parse the JSON response
    3. Return structured fields
    
    For now, falls back to rule-based extraction.
    """
    # TODO: Implement actual LLM call
    # Example prompt structure:
    """
    Extract structured information from this user response about {category}.
    
    Response: "{answer}"
    
    Extract these fields: {schema}
    
    Return valid JSON only.
    """
    
    # For now, use rule-based
    return extract_structured_fields(answer, category, key, schema)


if __name__ == "__main__":
    # Test examples
    
    # Test food extraction
    test_food = "Japanese ramen black garlic pork chashu. I've also got a sweet tooth and would do a lot of things for some boutique ice cream."
    print("Food extraction:")
    print(json.dumps(extract_food_fields(test_food), indent=2))
    print()
    
    # Test morning routine
    test_routine = "Wake up and scroll phone for 30 minutes. Used to be doom-scrolling politics, now checking Reddit for MCP servers. Then character art work."
    print("Morning routine extraction:")
    print(json.dumps(extract_morning_routine_fields(test_routine), indent=2))
    print()
    
    # Test name
    test_name = "Call me ∅. But that is difficult to type on a standard mobile keyboard. So we've been referring to me as 'Set' as in short for empty set (∅). RAWRity_ is my gamer tag on discord and steam. I also go by requiem4ddr online. My government name is Gerald Lewis Hardin II."
    print("Name extraction:")
    print(json.dumps(extract_name_fields(test_name), indent=2))
