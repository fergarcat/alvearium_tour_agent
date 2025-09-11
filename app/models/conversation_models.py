# app/models/conversation_models.py
"""
Модели для управления состоянием разговора в чате
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

class ConversationState(BaseModel):
    """Состояние разговора для интерактивного чата"""
    conversation_id: str
    family_id: str
    current_step: str = "kids_ages"  # Текущий шаг сбора данных
    collected_data: Dict[str, Any] = {}  # Собранные данные
    is_collecting: bool = True  # Флаг сбора данных
    profile_complete: bool = False  # Профиль собран
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def update_step(self, step: str, data: Dict[str, Any] = None):
        """Обновляет текущий шаг и данные"""
        self.current_step = step
        if data:
            self.collected_data.update(data)
        self.updated_at = datetime.now()
    
    def mark_profile_complete(self):
        """Отмечает профиль как собранный"""
        self.is_collecting = False
        self.profile_complete = True
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует в словарь для сериализации"""
        return {
            "conversation_id": self.conversation_id,
            "family_id": self.family_id,
            "current_step": self.current_step,
            "collected_data": self.collected_data,
            "is_collecting": self.is_collecting,
            "profile_complete": self.profile_complete,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationState':
        """Создает из словаря"""
        return cls(
            conversation_id=data["conversation_id"],
            family_id=data["family_id"],
            current_step=data.get("current_step", "kids_ages"),
            collected_data=data.get("collected_data", {}),
            is_collecting=data.get("is_collecting", True),
            profile_complete=data.get("profile_complete", False),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

class CollectionStepResponse(BaseModel):
    """Ответ на шаг сбора данных"""
    response: str
    next_step: Optional[str] = None
    profile_complete: bool = False
    collected_info: Dict[str, Any] = {}
    action: str  # "ask_next_question", "create_profile", "ask_clarification", "error"

class ConversationManager:
    """Менеджер состояний разговоров"""
    
    def __init__(self):
        # В реальном приложении это должно быть Redis или база данных
        self.conversations: Dict[str, ConversationState] = {}
    
    def get_conversation_state(self, conversation_id: str, family_id: str) -> ConversationState:
        """Получает или создает состояние разговора"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationState(
                conversation_id=conversation_id,
                family_id=family_id
            )
        return self.conversations[conversation_id]
    
    def update_conversation_state(self, conversation_id: str, state: ConversationState):
        """Обновляет состояние разговора"""
        self.conversations[conversation_id] = state
    
    def delete_conversation_state(self, conversation_id: str):
        """Удаляет состояние разговора"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_all_conversations(self) -> List[ConversationState]:
        """Получает все активные разговоры"""
        return list(self.conversations.values())

# Глобальный менеджер состояний
conversation_manager = ConversationManager()
