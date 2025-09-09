import os
from dotenv import load_dotenv
from app.services.prompts import read_prompt
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.router import MultiPromptChain

# -----------------------------
# 1. Load environment variables
# -----------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -----------------------------
# 2. Initialize Groq LLM
# -----------------------------
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",  # supported model
    temperature=0
)

# -----------------------------
# 3. Define specialized prompts (prompt_template as string)
# -----------------------------
prompt_infos = [
    {
        "name": "hotels",
        "description": "Questions about hotels and accommodations",
        "prompt_template": "You are a tourist agent specialized in hotel recommendations.\nQuestion: {input}\nAnswer like a local expert."
    },
    {
        "name": "restaurants",
        "description": "Questions about restaurants and dining",
        "prompt_template": "You are a culinary guide specialized in restaurant recommendations.\nQuestion: {input}\nProvide the best options."
    },
    {
        "name": "activities",
        "description": "Questions about activities, sightseeing, and excursions",
        "prompt_template": "You are a tourist activities expert.\nQuestion: {input}\nSuggest fun excursions and attractions."
    },
    {
        "name": "transportation",
        "description": "Questions about taxis, buses, trains, and rentals",
        "prompt_template": "You are a travel transportation expert.\nQuestion: {input}\nProvide practical transport options."
    },
    {
        "name": "all",
        "description": "Full trip plan including hotels, restaurants, activities, and transport",
        "prompt_template": "You are a comprehensive tourist assistant.\nQuestion: {input}\nProvide hotels, restaurants, activities, and transportation recommendations in one response."
    }
]

# -----------------------------
# 4. General prompt
# -----------------------------
general_prompt_text = read_prompt("general_prompt.txt")
general_prompt = PromptTemplate(
    template=general_prompt_text,
    input_variables=["input"]
)

general_chain = LLMChain(
    llm=llm,
    prompt=general_prompt
)

# -----------------------------
# 5. Create MultiPromptChain (routing)
# -----------------------------
multi_prompt_chain = MultiPromptChain.from_prompts(
    llm=llm,
    prompt_infos=prompt_infos  # strings for prompt_template
)

# -----------------------------
# 6. Routing function
# -----------------------------
def route_trip_query(user_input: str) -> str:
    """
    Process the user input with a general prompt first,
    then route it to the appropriate specialized prompt.
    """
    processed_input = general_chain.run(user_input)
    return multi_prompt_chain.run(processed_input)

# -----------------------------
# 7. Example usage
# -----------------------------
if __name__ == "__main__":
    print("=== Tourist Agent Chatbot ===")
    while True:
        query = input("\nAsk me about your trip (or type 'exit'): ")
        if query.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break
        response = route_trip_query(query)
        print("\nAgent:", response)
