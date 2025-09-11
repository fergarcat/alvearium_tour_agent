# llm_conversation.py
import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from app.services.prompt_templates import PLAN_PROMPT, TOOTH_FAIRY_PROMPT, GUIDE_PROMPT
#from app.services.create_trip import create_trip

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -----------------------------
# Initialize Groq LLM
# -----------------------------
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0
)

# Create Tooth Fairy Chain
tooth_fairy_chain = LLMChain(llm=llm, prompt=TOOTH_FAIRY_PROMPT)

# -----------------------------
# Global conversation memory
# -----------------------------
conversation_state = {}

# Define REQUIRED fields
REQUIRED_FIELDS = [
    "adults",
    "children",
    "children_age",
    "trip_duration",
    "hotels",
    "restaurants",
    "transportation",
    "activities"
]

def update_conversation_state(new_data: dict):
    """Merge new extracted data with existing conversation state."""
    for key, value in new_data.items():
        if value and value != "Not specified":
            conversation_state[key] = value

# -----------------------------
# Temperature adjustment
# -----------------------------
def set_temperature(temp: float):
    llm.temperature = temp

# ------------------------------
# Mouse Iterative Talking
# ------------------------------
def mouse_talking(conversation_state, follow_up_question):
    set_temperature(0.7)  # Make Tooth Fairy more conversational
    conversation_str = json.dumps(conversation_state, indent=2)
    tooth_fairy_output = tooth_fairy_chain.run({
        "conversation_state": conversation_str,
        "follow_up_question": follow_up_question
    })
    return tooth_fairy_output.strip()

def mouse_greeting(language="Spanish"):
    set_temperature(0.7)  # Make Tooth Fairy more conversational
    conversation_str = json.dumps(conversation_state, indent=2)
    tooth_fairy_output = tooth_fairy_chain.run({
        "conversation_state": "",
        "follow_up_question": "Introduce yourself briefly and greet the user in " + language + " and offer help with trip planning."
    })
    return tooth_fairy_output.strip()

def mouse_trip_creation(conversation_state):
    set_temperature(0.7)  # Make Tooth Fairy more conversational
    return mouse_talking(conversation_state,"")

# -----------------------------
# JSON extraction helper
# -----------------------------
def extract_json_from_response(response: str) -> dict:
    try:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("No valid JSON found in response")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

# -----------------------------
# Check for missing required fields
# -----------------------------
def get_first_missing_required_field() -> str:
    """Return the first required field that is still missing."""
    for field in REQUIRED_FIELDS:
        if conversation_state.get(field, "Not specified") == "Not specified":
            return field
    return None

# -----------------------------
# Query processing
# -----------------------------
def process_user_input(user_input: str, conversation_state):
    """Extract structured trip info and update conversation state."""
    
    try:
        # Build prompt with current state
        prompt_input = (
            f"Current conversation state: {json.dumps(conversation_state, indent=2)}\n"
            f"New user input: {user_input}"
        )

        # Run main planning chain
        set_temperature(0)  # Keep extraction deterministic
        raw_response = LLMChain(llm=llm, prompt=PLAN_PROMPT).run(prompt_input).strip()
        trip_data = extract_json_from_response(raw_response)

        # Merge new data
        update_conversation_state(trip_data)

        # Print conversation state
        print("\n=== Conversation State ===")
        print(json.dumps(conversation_state, indent=2))
        print("==========================")

        # Check required fields first
        missing_required = get_first_missing_required_field()
        if missing_required:
            # Always prioritize missing REQUIRED fields
            follow_up_question = f"Could you please provide details for '{missing_required}'?"
        else:
            # If all required fields are filled, force the follow-up to be empty
            follow_up_question = None


        # Ask a follow-up if needed
        if follow_up_question:
            return mouse_talking(conversation_state, follow_up_question)
        else:
            set_temperature(0) 
            guide_chain = LLMChain(llm=llm, prompt=GUIDE_PROMPT)
            guide_output = guide_chain.run({
                "preferences": json.dumps(conversation_state, indent=2)
            })
            return guide_output.strip()
            #print("FIN")


            return mouse_trip_creation(conversation_state)
            return create_trip(conversation_state)  # Finalize trip creation

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"Error processing input: {str(e)}"

# -----------------------------
# Main loop
# -----------------------------
if __name__ == "__main__":
    print("=== Tooth Fairy Tourist Chatbot ===\n")
    print(mouse_greeting())

    while True:
        query = input("\nAsk me about your trip (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break

        follow_up = process_user_input(query)
        if follow_up:
            print(follow_up)
        else:
            print("✅ All required information gathered! You can now generate your plan.")
