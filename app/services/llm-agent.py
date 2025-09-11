import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains.router import MultiPromptChain
from .prompt_templates import GENERAL_PROMPT, PROMPT_INFOS

# -----------------------------
# 1. Load environment variables
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------------
# 2. Initialize OpenAI LLM
# -----------------------------
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    temperature=0
)

# -----------------------------
# 3. General chain
# -----------------------------
general_chain = LLMChain(llm=llm, prompt=GENERAL_PROMPT)

# -----------------------------
# 4. MultiPromptChain for routing
# -----------------------------
multi_prompt_chain = MultiPromptChain.from_prompts(
    llm=llm,
    prompt_infos=PROMPT_INFOS
)

# -----------------------------
# 5. Routing function
# -----------------------------
def route_trip_query(user_input: str) -> str:
    """
    Preprocess user input with general prompt, then route it to the specialized prompt.
    """
    processed_input = general_chain.run(user_input)
    return multi_prompt_chain.run(processed_input)

# -----------------------------
# 6. Example usage
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
