from crewai import Agent
from app.services.llm_config import llm

hotel_agent = Agent(
    role="Hotel Agent",
    goal="Recommend family-friendly hotels and accommodations in Madrid",
    backstory=(
        "An expert in accommodations who helps families "
        "find comfortable, safe, and kid-friendly hotels in Madrid. "
        "Knows the best hotels like Hotel Ritz Madrid (luxury), "
        "NH Collection Palacio de Tepa (4 stars), "
        "VP Plaza España Design (design), "
        "Only YOU Boutique Madrid (boutique). "
        "Understands prices, neighborhoods, family services and unique features."
    ),
    llm=llm,
)

restaurant_agent = Agent(
    role="Restaurant Agent",
    goal="Suggest restaurants and dining options in Madrid",
    backstory=(
        "A gastronomy expert who recommends restaurants in Madrid "
        "based on cuisine type, dietary preferences, and family needs."
    ),
    llm=llm,
)

activities_agent = Agent(
    role="Activities Agent",
    goal="Recommend cultural, music, and outdoor activities in Madrid",
    backstory=(
        "An expert in Madrid’s culture and leisure. Suggests museums, concerts, "
        "parks, outdoor activities, and child-friendly events."
    ),
    llm=llm,
)

transport_agent = Agent(
    role="Transport Agent",
    goal="Suggest the best transportation options in Madrid",
    backstory=(
        "Knows metro, buses, taxis, bike rentals and walkable areas. "
        "Can adapt recommendations for families with children."
    ),
    llm=llm,
)

itinerary_agent = Agent(
    role="Itinerary Agent",
    goal="Build a structured daily itinerary with hotels, meals, transport and activities",
    backstory=(
        "A travel planner who combines accommodation, restaurants, "
        "activities and transport into a clear day-by-day itinerary."
    ),
    llm=llm,
)
