# app/api/dependencies.py
"""
Зависимости для API endpoints
"""

from fastapi import Depends, HTTPException, status
from typing import Generator
import os

def get_supabase_config():
    """Получает конфигурацию Supabase"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration not found"
        )
    
    return {"url": url, "key": key}


def get_openai_config():
    """Получает конфигурацию OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not found"
        )
    
    return {"api_key": api_key}