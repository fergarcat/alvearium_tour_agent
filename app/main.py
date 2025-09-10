from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

# --- 1. Modelo de entrada ---
class UserPrompt(BaseModel):
    text: str


# --- 5. Endpoint principal ---
@app.post("/plan")
def generate_plan(user_prompt: UserPrompt):
    category = classify_prompt(user_prompt.text)
    story = build_story(category, user_prompt.text)
    return {
        "category": category,
        "story": story
    }
