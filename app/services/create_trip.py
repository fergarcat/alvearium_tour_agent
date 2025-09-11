# services/create_trip.py
import json
import time
from typing import Optional
from crewai import Crew
from .agents import (
    hotel_agent,
    restaurant_agent,
    activities_agent,
    transport_agent,
    itinerary_agent
)
from .tasks import (
    hotel_task,
    restaurant_task,
    activities_task,
    transport_task,
    itinerary_task,
    get_rag_context
)
from . import get_vectorstore, initialize_rag_system

# -----------------------------
# Rate limit handling utilities
# -----------------------------
def extract_wait_time_from_error(error_msg: str) -> Optional[int]:
    """Extract wait time from rate limit error message."""
    try:
        import re
        pattern = r'Please try again in (\d+)ms'
        match = re.search(pattern, error_msg)
        if match:
            return int(match.group(1))
        
        pattern_seconds = r'Please try again in ([\d.]+)s'
        match_seconds = re.search(pattern_seconds, error_msg)
        if match_seconds:
            return int(float(match_seconds.group(1)) * 1000)
            
    except (ValueError, AttributeError):
        pass
    return None

def execute_with_retry(operation, max_retries=5, initial_delay=1000, backoff_factor=2):
    """Execute operation with retry logic for rate limiting."""
    for attempt in range(max_retries + 1):
        try:
            return operation()
            
        except Exception as e:
            error_msg = str(e)
            
            if "Rate limit reached" in error_msg or "rate limit" in error_msg.lower():
                wait_time_ms = extract_wait_time_from_error(error_msg)
                
                if wait_time_ms is None:
                    wait_time_ms = initial_delay * (backoff_factor ** attempt)
                
                wait_time_seconds = (wait_time_ms / 1000) + 0.1
                time.sleep(wait_time_seconds)
                
            else:
                raise e
                
    raise Exception(f"Operation failed after {max_retries + 1} attempts due to rate limiting")

# -----------------------------
# Create Crew with proper template variables
# -----------------------------
def create_crew_with_rag(conversation_state: dict):
    """Create crew with properly formatted inputs for template variables"""
    
    # Try to get RAG context, but fall back gracefully if not available
    rag_contexts = {
        'hotels': "",
        'restaurants': "",
        'activities': "",
        'transportation': "",
        'general': ""
    }
    
    # Only try to get RAG context if the system is initialized
    vectorstore = get_vectorstore()
    if vectorstore:
        try:
            rag_contexts = {
                'hotels': get_rag_context("family friendly hotels Madrid children"),
                'restaurants': get_rag_context("family restaurants Madrid children friendly"),
                'activities': get_rag_context("activities Madrid children family"),
                'transportation': get_rag_context("transportation Madrid family children"),
                'general': get_rag_context("Madrid tourism family children guide")
            }
        except Exception as e:
            print(f"⚠️  Error getting RAG context: {e}")
    
    # Create the inputs dictionary with all template variables
    inputs = {
        'input': conversation_state,  # This provides {input} for template variables
        'rag_context': rag_contexts['general'],
        'rag_hotels': rag_contexts['hotels'],
        'rag_restaurants': rag_contexts['restaurants'],
        'rag_activities': rag_contexts['activities'],
        'rag_transportation': rag_contexts['transportation']
    }
    
    # Also add individual conversation state fields for direct access
    inputs.update(conversation_state)
    
    return Crew(
        name="Trip Planning Crew with RAG",
        agents=[
            hotel_agent,
            restaurant_agent,
            activities_agent,
            transport_agent,
            itinerary_agent
        ],
        tasks=[
            hotel_task,
            restaurant_task,
            activities_task,
            transport_task,
            itinerary_task
        ],
        verbose=False
    ), inputs

# -----------------------------
# Create trip function with RAG (graceful fallback)
# -----------------------------
def create_trip(conversation_state: dict) -> str:
    """Orchestrates trip planning with RAG context and returns formatted itinerary."""
    try:
        # Try to get the vectorstore, initialize if not available
        vectorstore = get_vectorstore()
        if not vectorstore:
            print("⏳ RAG system not initialized, attempting to initialize...")
            vectorstore = initialize_rag_system()
            if not vectorstore:
                print("⚠️  RAG system could not be initialized, continuing without RAG context")
        
        # Create crew with properly formatted inputs (will work even without RAG)
        crew, inputs = create_crew_with_rag(conversation_state)
        
        def kickoff_operation():
            return crew.kickoff(inputs=inputs)
        
        crew_results = execute_with_retry(kickoff_operation)
        
        itinerary_text = ""

        # Extract itinerary text from results
        if hasattr(crew_results, 'tasks_output') and crew_results.tasks_output:
            for task_output in enumerate(crew_results.tasks_output):
                try:
                    if hasattr(task_output, 'dict'):
                        task_dict = task_output.dict()
                    elif isinstance(task_output, dict):
                        task_dict = task_output
                    else:
                        continue
                    
                    agent_name = task_dict.get('agent', '')
                    raw_output = task_dict.get('raw', '')
                    
                    if agent_name == 'Itinerary Agent' and raw_output:
                        itinerary_text = raw_output
                        break
                    
                except Exception:
                    continue

        # Fallback to raw output
        if not itinerary_text and hasattr(crew_results, 'raw'):
            itinerary_text = crew_results.raw

        # Clean JSON artifacts if present
        if itinerary_text and itinerary_text.strip().startswith('{') and '"itinerary":' in itinerary_text:
            try:
                json_data = json.loads(itinerary_text)
                if isinstance(json_data, dict) and 'itinerary' in json_data:
                    itinerary_text = format_itinerary_from_json(json_data['itinerary'])
            except json.JSONDecodeError:
                pass

        return itinerary_text or "No itinerary could be generated. Please try again."

    except Exception as e:
        return f"Error generating itinerary: {str(e)}"

def format_itinerary_from_json(itinerary_data: list) -> str:
    """Convert JSON itinerary data to formatted text."""
    if not isinstance(itinerary_data, list):
        return str(itinerary_data)
    
    formatted_text = "# 🗺️ Your Madrid Family Itinerary\n\n"
    
    for day in itinerary_data:
        day_num = day.get('day', '')
        formatted_text += f"## 📅 Day {day_num}\n\n"
        
        if morning := day.get('morning'):
            formatted_text += f"**🌅 Morning:**\n{morning}\n\n"
        
        if afternoon := day.get('afternoon'):
            formatted_text += f"**☀️ Afternoon:**\n{afternoon}\n\n"
        
        if evening := day.get('evening'):
            formatted_text += f"**🌙 Evening:**\n{evening}\n\n"
        
        formatted_text += "---\n\n"
    
    formatted_text += "### 🎯 Travel Tips\n"
    formatted_text += "- All times are approximate and may vary based on your pace\n"
    formatted_text += "- Consider nap times for your 2-year-old when planning activities\n"
    formatted_text += "- Madrid's metro system is stroller-friendly\n"
    formatted_text += "- Many restaurants offer early dining options suitable for families\n\n"
    
    formatted_text += "*Enjoy your family adventure in Madrid!* ✨"
    
    return formatted_text

# -----------------------------
# Main execution
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

    itinerary = create_trip(conversation_state_example)
    print(itinerary)