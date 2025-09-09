import os
from dotenv import load_dotenv
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
    model="llama-3.3-70b-versatile",
    temperature=0
)

# -----------------------------
# 3. Define prompt infos (prompt_template as string)
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
# 4. Build router chain
# -----------------------------
categories_list = "\n".join([f"- {p['name']}: {p['description']}" for p in prompt_infos])

router_template = f"""
You are a tourist assistant. Classify the following user question into one of the categories below:
{categories_list}

Question: {{input}}
Return ONLY the name of the category.
"""

router_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(template=router_template, input_variables=["input"])
)

# -----------------------------
# 5. Create MultiPromptChain
# -----------------------------
multi_prompt_chain = MultiPromptChain.from_prompts(
    llm=llm,
    prompt_infos=prompt_infos  # list of dicts with name, description, prompt_template (string)
)


# -----------------------------
# 6. Routing function
# -----------------------------
def route_trip_query(user_input: str) -> str:
    """Route the user query to the appropriate specialized prompt."""
    return multi_prompt_chain.run(user_input)

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
