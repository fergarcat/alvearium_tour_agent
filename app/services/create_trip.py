import json
from app.services.accommodation_agent import hotel_agent
from app.services.restaurant_agent import restaurant_agent
from app.services.activities_agent import activities_agent
from app.services.transport_agent import transport_agent
from app.services.itinerary_agent import itinerary_agent


def create_trip(conversation_state: dict) -> dict:
    """
    Orchestrates trip planning by passing conversation_state to all CrewAI agents,
    collecting their responses, and returning a final aggregated JSON.
    """
    try:
        aggregated_results = {}

        # -----------------------------
        # 1. Hotels
        # -----------------------------
        if conversation_state.get("hotels") and conversation_state["hotels"] != "Not specified":
            aggregated_results["hotels"] = hotel_agent.execute({"hotels": conversation_state["hotels"]})
        else:
            aggregated_results["hotels"] = {}

        # -----------------------------
        # 2. Restaurants
        # -----------------------------
        if conversation_state.get("restaurants") and conversation_state["restaurants"] != "Not specified":
            aggregated_results["restaurants"] = restaurant_agent.execute({"restaurants": conversation_state["restaurants"]})
        else:
            aggregated_results["restaurants"] = {}

        # -----------------------------
        # 3. Activities
        # -----------------------------
        if conversation_state.get("activities") and conversation_state["activities"] != "Not specified":
            aggregated_results["activities"] = activities_agent.execute({"activities": conversation_state["activities"]})
        else:
            aggregated_results["activities"] = {}

        # -----------------------------
        # 4. Transportation
        # -----------------------------
        if conversation_state.get("transportation") and conversation_state["transportation"] != "Not specified":
            aggregated_results["transportation"] = transport_agent.execute({"transportation": conversation_state["transportation"]})
        else:
            aggregated_results["transportation"] = {}

        # -----------------------------
        # 5. Itinerary
        # -----------------------------
        aggregated_results["itinerary"] = itinerary_agent.execute(conversation_state)

        return aggregated_results

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    conversation_state_example = {
        "adults": "2",
        "children": "1",
        "children_age": "2 years",
        "trip_duration": "3 days",
        "hotels": "budget hotel",
        "restaurants": "Italian cuisine",
        "transportation": "metro",
        "activities": "outdoor activities, music events",
        "user_language": "Spanish"
    }

    final_plan = create_trip(conversation_state_example)
    print(json.dumps(final_plan, indent=2, ensure_ascii=False))
