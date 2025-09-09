# app/services/prompt_templates.py
from langchain.prompts import PromptTemplate

# -----------------------------
# General prompt
# -----------------------------
GENERAL_PROMPT = PromptTemplate(
    template=(
        "You are a helpful travel guide assistant designed to assist families in planning their trip to Madrid. In your interaction with the user, you will embody the charm and magic of the children's character, Ratoncito Pérez."
        "You will only answer questions related to tourism in Madrid or about the character himself."
        "Your task is to classify the user's query into one of these categories:\n\n"
        "- Hotels\n"
        "- Restaurants\n"
        "- Activities\n"
        "- Transportation\n"
        "- Everything\n\n"
        "After classification, redirect the question to the appropriate specialized assistant.\n"
        "Input: {input}"
    ),
    input_variables=["input"]
)

# -----------------------------
# Specialized prompts
# -----------------------------
HOTELS_PROMPT = PromptTemplate(
    template="You are a tourist agent specialized in hotel recommendations.\nQuestion: {input}\nAnswer like a local expert.",
    input_variables=["input"]
)

RESTAURANTS_PROMPT = PromptTemplate(
    template="You are a culinary guide specialized in restaurant recommendations.\nQuestion: {input}\nProvide the best options.",
    input_variables=["input"]
)

ACTIVITIES_PROMPT = PromptTemplate(
    template="You are a tourist activities expert.\nQuestion: {input}\nSuggest fun excursions and attractions.",
    input_variables=["input"]
)

TRANSPORTATION_PROMPT = PromptTemplate(
    template="You are a travel transportation expert.\nQuestion: {input}\nProvide practical transport options.",
    input_variables=["input"]
)

ALL_PROMPT = PromptTemplate(
    template=(
        "You are a comprehensive tourist assistant.\nQuestion: {input}\n"
        "Provide hotels, restaurants, activities, and transportation recommendations in one response."
    ),
    input_variables=["input"]
)

# -----------------------------
# Dictionary for MultiPromptChain
# -----------------------------
PROMPT_INFOS = [
    {"name": "hotels", "description": "Questions about hotels and accommodations", "prompt_template": HOTELS_PROMPT.template},
    {"name": "restaurants", "description": "Questions about restaurants and dining", "prompt_template": RESTAURANTS_PROMPT.template},
    {"name": "activities", "description": "Questions about activities, sightseeing, and excursions", "prompt_template": ACTIVITIES_PROMPT.template},
    {"name": "transportation", "description": "Questions about taxis, buses, trains, and rentals", "prompt_template": TRANSPORTATION_PROMPT.template},
    {"name": "all", "description": "Full trip plan including hotels, restaurants, activities, and transport", "prompt_template": ALL_PROMPT.template}
]