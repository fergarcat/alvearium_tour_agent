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
        itinerary_task  # This should be last since it depends on others
    ],
    verbose=True  # Add verbose for better debugging
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
        # Look for patterns like "Please try again in 775ms"
        import re
        pattern = r'Please try again in (\d+)ms'
        match = re.search(pattern, error_msg)
        if match:
            return int(match.group(1))
        
        # Also check for seconds format if needed
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
    
    Args:
        operation: Function to execute
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in milliseconds if no wait time is specified
        backoff_factor: Factor to multiply delay by on each retry
    
    Returns:
        Result of the operation if successful
    
    Raises:
        Exception: If all retries fail
    """
    for attempt in range(max_retries + 1):
        try:
            return operation()
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if this is a rate limit error
            if "Rate limit reached" in error_msg or "rate limit" in error_msg.lower():
                # Extract suggested wait time from error message
                wait_time_ms = extract_wait_time_from_error(error_msg)
                
                if wait_time_ms is None:
                    # Use exponential backoff if no specific wait time is provided
                    wait_time_ms = initial_delay * (backoff_factor ** attempt)
                
                # Convert to seconds and add a small buffer
                wait_time_seconds = (wait_time_ms / 1000) + 0.1
                
                print(f"Rate limit encountered. Waiting {wait_time_seconds:.2f} seconds (attempt {attempt + 1}/{max_retries + 1})...")
                time.sleep(wait_time_seconds)
                
            else:
                # Re-raise if it's not a rate limit error
                raise e
                
    # If we've exhausted all retries
    raise Exception(f"Operation failed after {max_retries + 1} attempts due to rate limiting")

# -----------------------------
# Create trip function with rate limiting
# -----------------------------
def create_trip(conversation_state: dict) -> dict:
    """
    Orchestrates trip planning by passing conversation_state to all tasks,
    collecting their outputs, and returning a final aggregated JSON.
    """
    try:
        # Define the operation to execute with retry logic
        def kickoff_operation():
            return crew.kickoff(inputs={"input": conversation_state})
        
        # Execute with retry logic for rate limiting
        crew_results = execute_with_retry(kickoff_operation)
        
        print("Crew Results (raw):", crew_results.raw if hasattr(crew_results, 'raw') else 'No raw')
        
        # Convert CrewOutput to dict
        crew_dict = crew_results.dict()
        print("Crew Results (dict keys):", list(crew_dict.keys()))
        
        aggregated_results = {}

        # Check if all outputs are "safe" (filtered content)
        all_safe = True
        
        # Process tasks_output from crew_results
        if hasattr(crew_results, 'tasks_output') and crew_results.tasks_output:
            print(f"Processing {len(crew_results.tasks_output)} tasks...")
            
            for i, task_output in enumerate(crew_results.tasks_output):
                try:
                    # Convert TaskOutput to dict safely
                    if hasattr(task_output, 'dict'):
                        task_dict = task_output.dict()
                    elif isinstance(task_output, dict):
                        task_dict = task_output
                    else:
                        task_dict = {}
                    
                    # Extract task information
                    agent_name = task_dict.get('agent', f'Agent_{i}')
                    raw_output = task_dict.get('raw', 'No output')
                    description = task_dict.get('description', 'No description')
                    
                    print(f"Task {i} - Agent: {agent_name}, Description: {description[:100]}...")
                    print(f"Task {i} - Raw output: {str(raw_output)[:200]}...")
                    
                    # Check if output is meaningful
                    if raw_output != 'safe':
                        all_safe = False
                    
                    # Map agent names to result keys
                    agent_key_map = {
                        'Hotel Agent': 'hotels',
                        'Restaurant Agent': 'restaurants', 
                        'Activities Agent': 'activities',
                        'Transport Agent': 'transportation',
                        'Itinerary Agent': 'itinerary'
                    }
                    
                    result_key = agent_key_map.get(agent_name, f'task_{i}')
                    
                    # Try to parse JSON if it's a string and not "safe"
                    output_value = raw_output
                    if isinstance(raw_output, str) and raw_output != 'safe':
                        try:
                            output_value = json.loads(raw_output)
                        except json.JSONDecodeError:
                            # Keep as string if not valid JSON
                            pass
                    
                    aggregated_results[result_key] = output_value
                    
                except Exception as task_error:
                    print(f"Error processing task {i}: {task_error}")
                    aggregated_results[f'task_{i}_error'] = str(task_error)
        
        # If no tasks_output, try to get from crew_dict
        elif 'tasks_output' in crew_dict and isinstance(crew_dict['tasks_output'], list):
            print("Processing tasks from crew_dict...")
            
            for i, task_data in enumerate(crew_dict['tasks_output']):
                if isinstance(task_data, dict):
                    agent_name = task_data.get('agent', f'Agent_{i}')
                    raw_output = task_data.get('raw', 'No output')
                    
                    agent_key_map = {
                        'Hotel Agent': 'hotels',
                        'Restaurant Agent': 'restaurants', 
                        'Activities Agent': 'activities',
                        'Transport Agent': 'transportation',
                        'Itinerary Agent': 'itinerary'
                    }
                    
                    result_key = agent_key_map.get(agent_name, f'task_{i}')
                    aggregated_results[result_key] = raw_output
        
        # Add warning if all outputs are filtered
        if all_safe:
            aggregated_results['warning'] = 'All agent outputs were filtered as "safe". Check your agent configurations and prompts.'
        
        # Include original conversation_state
        aggregated_results["trip_data"] = conversation_state
        
        # Include token usage if available
        if 'token_usage' in crew_dict:
            aggregated_results["token_usage"] = crew_dict['token_usage']

        return aggregated_results

    except Exception as e:
        import traceback
        print("Error details:")
        print(traceback.format_exc())
        return {
            "error": str(e),
            "trip_data": conversation_state,
            "debug_info": {
                "crew_results_type": str(type(crew_results)) if 'crew_results' in locals() else 'not_available',
                "crew_dict_keys": list(crew_dict.keys()) if 'crew_dict' in locals() else 'not_available'
            }
        }

# -----------------------------
# Debug helper function with rate limiting
# -----------------------------
def debug_crew_results(conversation_state: dict):
    """
    Helper function to understand the structure of crew results
    """
    try:
        def debug_operation():
            return crew.kickoff(inputs={"input": conversation_state})
        
        crew_results = execute_with_retry(debug_operation)
        
        print("=== DEBUGGING CREW RESULTS ===")
        print(f"Type: {type(crew_results)}")
        print(f"Dir: {[attr for attr in dir(crew_results) if not attr.startswith('_')]}")
        
        if hasattr(crew_results, 'dict'):
            crew_dict = crew_results.dict()
            print(f"Dict keys: {list(crew_dict.keys()) if isinstance(crew_dict, dict) else 'Not a dict'}")
            
            if isinstance(crew_dict, dict):
                for key, value in crew_dict.items():
                    print(f"  {key}: {type(value)} - {str(value)[:100]}...")
        
        if hasattr(crew_results, 'tasks_output'):
            print(f"Tasks output length: {len(crew_results.tasks_output)}")
            for i, task_output in enumerate(crew_results.tasks_output):
                # Get task info safely
                if isinstance(task_output, dict):
                    task_dict = task_output
                else:
                    task_dict = task_output.dict() if hasattr(task_output, 'dict') else {}
                
                print(f"  Task {i} - Agent: {task_dict.get('agent', 'Unknown')}")
                print(f"  Task {i} - Description: {task_dict.get('description', 'No description')[:100]}...")
                print(f"  Task {i} - Raw output: {str(task_dict.get('raw', 'No output'))[:200]}...")
                print(f"  Task {i} - Keys: {list(task_dict.keys())}")
                print("---")
        
        return crew_results
        
    except Exception as e:
        print(f"Debug error: {e}")
        import traceback
        traceback.print_exc()

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

    # First debug to understand structure
    print("=== DEBUGGING ===")
    debug_crew_results(conversation_state_example)
    
    print("\n=== CREATING TRIP ===")
    final_plan = create_trip(conversation_state_example)
    print(json.dumps(final_plan, indent=2, ensure_ascii=False))