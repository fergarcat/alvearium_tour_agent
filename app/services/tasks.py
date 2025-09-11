# tasks.py
from crewai import Task
from app.services.agents import (
    hotel_agent,
    restaurant_agent,
    activities_agent,
    transport_agent,
    itinerary_agent,
)

# -----------------------------
# Hotels
# -----------------------------
hotel_task = Task(
    description=(
        "Based on the trip information provided: {input}, "
        "suggest family-friendly hotels in Madrid. "
        "Consider the number of adults ({input[adults]}), "
        "children ({input[children]}), trip duration ({input[trip_duration]}), "
        "and hotel preferences ({input[hotels]}). "
        "Focus on hotels that accommodate families with young children."
    ),
    agent=hotel_agent,
    expected_output=(
        "JSON with structure: { 'hotels': [ { 'name': str, 'category': str, "
        "'price_range': str, 'location': str, 'family_friendly_features': [str] } ] }"
    ),
    output_file="hotels.json"
)

# -----------------------------
# Restaurants
# -----------------------------
restaurant_task = Task(
    description=(
        "Based on the trip information: {input}, "
        "recommend suitable restaurants in Madrid. "
        "Consider the family size ({input[adults]} adults, {input[children]} children), "
        "preferred cuisine type ({input[restaurants]}), "
        "and that there's a {input[children_age]} child in the group. "
        "Focus on family-friendly establishments."
    ),
    agent=restaurant_agent,
    expected_output=(
        "JSON with structure: { 'restaurants': [ { 'name': str, 'cuisine': str, "
        "'price_range': str, 'location': str, 'family_friendly': bool } ] }"
    ),
    output_file="restaurants.json"
)

# -----------------------------
# Activities
# -----------------------------
activities_task = Task(
    description=(
        "Based on the trip information: {input}, "
        "suggest cultural, outdoor and music activities in Madrid. "
        "Consider the family composition ({input[adults]} adults, {input[children]} children aged {input[children_age]}), "
        "trip duration ({input[trip_duration]}), "
        "and activity preferences ({input[activities]}). "
        "Ensure activities are suitable for families with young children."
    ),
    agent=activities_agent,
    expected_output=(
        "JSON with structure: { 'activities': [ { 'name': str, 'type': str, "
        "'location': str, 'duration': str, 'age_suitability': str } ] }"
    ),
    output_file="activities.json"
)

# -----------------------------
# Transportation
# -----------------------------
transport_task = Task(
    description=(
        "Based on the trip information: {input}, "
        "recommend transport options in Madrid. "
        "Consider the family size ({input[adults]} adults, {input[children]} children), "
        "preferred transportation ({input[transportation]}), "
        "and the presence of a {input[children_age]} child. "
        "Focus on family-friendly and practical options."
    ),
    agent=transport_agent,
    expected_output=(
        "JSON with structure: { 'transportary': [ { 'mode': str, 'provider': str, "
        "'price_range': str, 'duration': str, 'family_friendly': bool } ] }"
    ),
    output_file="transportation.json"
)

# -----------------------------
# Itinerary - Returns formatted text for web display
# -----------------------------
itinerary_task = Task(
    description=(
        "Based on all the trip information: {input}, and the recommendations from other agents, "
        "create a beautifully formatted daily itinerary for {input[trip_duration]} in Madrid. "
        "Use the hotel recommendations from the Hotel Agent, "
        "restaurant recommendations from the Restaurant Agent, "
        "activity recommendations from the Activities Agent, "
        "and transportation options from the Transport Agent. "
        "Combine these into a cohesive itinerary suitable for a family with "
        "{input[adults]} adults, {input[children]} children ({input[children_age]}).\n\n"
        "Format the output as clean, readable text with:\n"
        "- Clear day headings (Day 1, Day 2, etc.)\n"
        "- Morning, afternoon, and evening sections for each day\n"
        "- Include specific times where appropriate\n"
        "- Mention transportation methods between locations\n"
        "- Include practical tips for families with young children\n"
        "- Make it engaging and easy to read in a web browser\n\n"
        "Ensure the itinerary is practical, logical, and family-friendly, "
        "considering travel times between locations and appropriate timing for meals and activities."
    ),
    agent=itinerary_agent,
    expected_output=(
        "A beautifully formatted text itinerary ready for web display with:\n"
        "- Clear day sections\n"
        "- Morning, afternoon, evening activities\n"
        "- Transportation details\n"
        "- Family-friendly tips\n"
        "- Engaging and readable format"
    ),
    context=[hotel_task, restaurant_task, activities_task, transport_task]
)