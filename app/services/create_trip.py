# create_trip.py
import json
import time
from typing import Optional
from crewai import Crew
from app.services.agents import (
    hotel_agent,
    restaurant_agent,
    activities_agent,
    transport_agent,
    itinerary_agent
)
from app.services.tasks import (
    hotel_task,
    restaurant_task,
    activities_task,
    transport_task,
    itinerary_task
)

# -----------------------------
# Create Crew
# -----------------------------
crew = Crew(
    name="Trip Planning Crew",
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
)

# -----------------------------
# Rate limit handling utilities
# -----------------------------
def extract_wait_time_from_error(error_msg: str) -> Optional[int]:
    """
    Extract the suggested wait time from the rate limit error message.
    Returns wait time in milliseconds, or None if not found.
    """
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
    """
    Execute an operation with retry logic for rate limiting.
    """
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
# Create trip function with rate limiting
# -----------------------------
def create_trip(conversation_state: dict) -> str:
    """
    Orchestrates trip planning and returns formatted itinerary text for web display.
    """
    try:
        def kickoff_operation():
            return crew.kickoff(inputs={"input": conversation_state})
        
        crew_results = execute_with_retry(kickoff_operation)
        crew_dict = crew_results.dict()
        
        itinerary_text = ""

        # Process tasks_output to find the itinerary text
        if hasattr(crew_results, 'tasks_output') and crew_results.tasks_output:
            for i, task_output in enumerate(crew_results.tasks_output):
                try:
                    if hasattr(task_output, 'dict'):
                        task_dict = task_output.dict()
                    elif isinstance(task_output, dict):
                        task_dict = task_output
                    else:
                        task_dict = {}
                    
                    agent_name = task_dict.get('agent', f'Agent_{i}')
                    raw_output = task_dict.get('raw', '')
                    
                    if agent_name == 'Itinerary Agent' and raw_output:
                        itinerary_text = raw_output
                        break
                    
                except Exception:
                    continue
        
        # If not found in tasks_output, try crew_dict
        elif 'tasks_output' in crew_dict and isinstance(crew_dict['tasks_output'], list):
            for i, task_data in enumerate(crew_dict['tasks_output']):
                if isinstance(task_data, dict):
                    agent_name = task_data.get('agent', f'Agent_{i}')
                    raw_output = task_data.get('raw', '')
                    
                    if agent_name == 'Itinerary Agent' and raw_output:
                        itinerary_text = raw_output
                        break

        # If still not found, try raw output
        if not itinerary_text and hasattr(crew_results, 'raw'):
            itinerary_text = crew_results.raw

        # Clean up the text if it contains JSON artifacts
        if itinerary_text:
            # Remove any JSON wrapping if present
            if itinerary_text.strip().startswith('{') and '"itinerary":' in itinerary_text:
                try:
                    json_data = json.loads(itinerary_text)
                    if isinstance(json_data, dict) and 'itinerary' in json_data:
                        # Convert JSON itinerary to formatted text
                        itinerary_text = format_itinerary_from_json(json_data['itinerary'])
                    elif isinstance(json_data, list):
                        itinerary_text = format_itinerary_from_json(json_data)
                except json.JSONDecodeError:
                    # If it's not valid JSON, keep as text
                    pass

        return itinerary_text or "No itinerary could be generated. Please try again."

    except Exception as e:
        return f"Error generating itinerary: {str(e)}"

def format_itinerary_from_json(itinerary_data: list) -> str:
    """
    Convert JSON itinerary data to formatted text.
    """
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
# Example usage (commented out)
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
