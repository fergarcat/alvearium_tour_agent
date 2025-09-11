# app/services/conversation_service.py
"""
Сервис для обработки интерактивного сбора данных в чате
"""

import json
from typing import Dict, Any, Optional
from models.conversation_models import ConversationState, CollectionStepResponse, conversation_manager
from tools.personalization_tools import sequential_question_tool, extract_family_info_tool
from models.family_models_supabase import FamilyProfileSupabase

class ConversationService:
    """Сервис для управления разговорами и сбором данных"""
    
    def __init__(self):
        self.conversation_manager = conversation_manager
    
    def process_chat_message(self, message: str, conversation_id: str, family_id: str) -> CollectionStepResponse:
        """
        Обрабатывает сообщение в контексте разговора
        
        Args:
            message: Сообщение пользователя
            conversation_id: ID разговора
            family_id: ID семьи
            
        Returns:
            CollectionStepResponse: Ответ с информацией о следующем шаге
        """
        try:
            # Получаем состояние разговора
            state = self.conversation_manager.get_conversation_state(conversation_id, family_id)
            
            # Если профиль уже собран, переходим к обычному чату
            if state.profile_complete:
                return CollectionStepResponse(
                    response="Профиль уже собран, переходим к обычному чату",
                    action="profile_complete",
                    profile_complete=True
                )
            
            # Обрабатываем ответ на текущий шаг сбора данных
            response_data = self._process_collection_step(message, state)
            
            # Обновляем состояние разговора
            self._update_conversation_state(state, response_data)
            
            return CollectionStepResponse(
                response=response_data["response"],
                next_step=response_data.get("next_step"),
                profile_complete=response_data.get("profile_complete", False),
                collected_info=response_data.get("collected_info", {}),
                action=response_data.get("action", "ask_next_question")
            )
            
        except Exception as e:
            return CollectionStepResponse(
                response=f"Lo siento, hubo un error al procesar tu mensaje: {str(e)}",
                action="error",
                profile_complete=False
            )
    
    def _process_collection_step(self, message: str, state: ConversationState) -> Dict[str, Any]:
        """
        Обрабатывает ответ на текущий шаг сбора данных
        
        Args:
            message: Сообщение пользователя
            state: Состояние разговора
            
        Returns:
            Dict с данными ответа
        """
        try:
            # Используем sequential_question_tool для обработки ответа
            result = sequential_question_tool(message, state.family_id, state.current_step)
            data = json.loads(result)
            
            print(f"🔍 ConversationService: Обработка шага '{state.current_step}'")
            print(f"   Ответ пользователя: {message[:50]}...")
            print(f"   Результат обработки: {data['action']}")
            
            if data["action"] == "ask_next_question":
                # Задаем следующий вопрос
                return {
                    "response": data["question"],
                    "next_step": data["next_step"],
                    "collected_info": data["collected_info"],
                    "profile_complete": False,
                    "action": "ask_next_question"
                }
                
            elif data["action"] == "create_profile":
                # Профиль собран, создаем его
                return self._create_family_profile(state, data["collected_info"])
                
            elif data["action"] == "ask_clarification":
                # Просим уточнить ответ
                return {
                    "response": data["question"],
                    "next_step": data["next_step"],
                    "collected_info": data["collected_info"],
                    "profile_complete": False,
                    "action": "ask_clarification"
                }
                
            else:
                # Ошибка обработки
                return {
                    "response": data.get("message", "Error al procesar tu respuesta"),
                    "next_step": state.current_step,
                    "collected_info": {},
                    "profile_complete": False,
                    "action": "error"
                }
                
        except Exception as e:
            print(f"❌ ConversationService: Ошибка обработки шага: {e}")
            return {
                "response": f"Lo siento, hubo un error al procesar tu respuesta: {str(e)}",
                "next_step": state.current_step,
                "collected_info": {},
                "profile_complete": False,
                "action": "error"
            }
    
    def _create_family_profile(self, state: ConversationState, collected_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создает профиль семьи из собранных данных
        
        Args:
            state: Состояние разговора
            collected_info: Собранная информация
            
        Returns:
            Dict с данными ответа
        """
        try:
            # Обновляем собранные данные
            state.collected_data.update(collected_info)
            
            # Создаем профиль семьи
            profile = FamilyProfileSupabase(
                family_id=state.family_id,
                kids_ages=state.collected_data.get("kids_ages", []),
                adults_count=state.collected_data.get("adults_count", 0),
                interests=state.collected_data.get("interests", []),
                origin_country=state.collected_data.get("origin_country", "Spain"),
                special_needs=state.collected_data.get("special_needs", []),
                language_preference=state.collected_data.get("language_preference", "es"),
                accommodation_type=state.collected_data.get("accommodation_type", "hotel"),
                transportation_preference=state.collected_data.get("transportation_preference", "public")
            )
            
            # Сохраняем профиль в Supabase
            print(f"🔍 ConversationService: Пытаемся сохранить профиль семьи {state.family_id}")
            print(f"🔍 Данные профиля: kids_ages={profile.kids_ages}, adults_count={profile.adults_count}, interests={profile.interests}")
            
            save_result = profile.save_to_supabase()
            print(f"🔍 Результат сохранения профиля: {save_result}")
            
            if save_result:
                print(f"✅ ConversationService: Профиль семьи {state.family_id} создан успешно")
                
                # Сохраняем budget_level в travel_requests
                budget_level = state.collected_data.get("budget_level", "medium")
                if budget_level:
                    # Получаем даты из собранных данных
                    travel_dates = state.collected_data.get("travel_dates", "")
                    start_date = ""
                    end_date = ""
                    
                    # Парсим даты из travel_dates
                    if travel_dates and " to " in travel_dates:
                        start_date, end_date = travel_dates.split(" to ")
                    elif travel_dates and " - " in travel_dates:
                        start_date, end_date = travel_dates.split(" - ")
                    
                    # Если даты не указаны, используем дефолтные
                    if not start_date or not end_date:
                        start_date = "2024-12-15"
                        end_date = "2024-12-20"
                    
                    profile.save_travel_request(
                        request_type="profile_creation",
                        request_data={
                            "family_profile": {
                                "kids_ages": state.collected_data.get("kids_ages", []),
                                "adults_count": state.collected_data.get("adults_count", 0),
                                "interests": state.collected_data.get("interests", []),
                                "special_needs": state.collected_data.get("special_needs", []),
                                "origin_country": state.collected_data.get("origin_country", "Spain")
                            }
                        },
                        budget_level=budget_level,
                        start_date=start_date,
                        end_date=end_date
                    )
                    print(f"✅ ConversationService: Budget level '{budget_level}' сохранен в travel_requests")
                
                # Отмечаем профиль как собранный
                state.mark_profile_complete()
                self.conversation_manager.update_conversation_state(state.conversation_id, state)
                
                # Генерируем персонализированный ответ через RouterAgent
                personalized_response = self._generate_personalized_response(profile, state.collected_data)
                
                return {
                    "response": personalized_response,
                    "next_step": None,
                    "collected_info": state.collected_data,
                    "profile_complete": True,
                    "action": "create_profile"
                }
            else:
                print(f"❌ ConversationService: Не удалось сохранить профиль семьи {state.family_id}")
                return {
                    "response": "Lo siento, hubo un error al guardar tu perfil. Inténtalo de nuevo.",
                    "next_step": state.current_step,
                    "collected_info": state.collected_data,
                    "profile_complete": False,
                    "action": "error"
                }
                
        except Exception as e:
            print(f"❌ ConversationService: Ошибка создания профиля: {e}")
            return {
                "response": f"Lo siento, hubo un error al crear tu perfil: {str(e)}",
                "next_step": state.current_step,
                "collected_info": state.collected_data,
                "profile_complete": False,
                "action": "error"
            }
    
    def _generate_personalized_response(self, profile: FamilyProfileSupabase, collected_data: Dict[str, Any]) -> str:
        """Генерирует персонализированный ответ через RouterAgent"""
        try:
            from services.router_agent import RouterAgent
            
            # Создаем данные для RouterAgent
            routing_data = {
                "query": "planificar viaje a Madrid",
                "family_id": profile.family_id,
                "profile": {
                    "kids_ages": profile.kids_ages,
                    "adults_count": profile.adults_count,
                    "interests": profile.interests,
                    "origin_country": profile.origin_country,
                    "special_needs": profile.special_needs or [],
                    "budget_level": collected_data.get("budget_level", "medium"),
                    "travel_dates": collected_data.get("travel_dates", "")
                }
            }
            
            # Инициализируем RouterAgent
            router = RouterAgent()
            
            # Генерируем персонализированный ответ
            personalized_response = router.process_routing_data(routing_data)
            
            print(f"✅ ConversationService: Персонализированный ответ сгенерирован")
            return personalized_response
            
        except Exception as e:
            print(f"❌ ConversationService: Ошибка генерации персонализированного ответа: {e}")
            # Fallback на статическое сообщение
            return self._generate_profile_completion_message(profile)
    
    def _generate_profile_completion_message(self, profile: FamilyProfileSupabase) -> str:
        """Генерирует сообщение о завершении сбора профиля"""
        family_size = profile.get_family_size()
        age_group = profile.get_age_group()
        interests = ", ".join(profile.interests) if profile.interests else "No especificados"
        
        # Получаем budget_level из текущего состояния разговора
        current_state = self.conversation_manager.get_conversation_state(profile.family_id, profile.family_id)
        budget_level = current_state.collected_data.get("budget_level", "medium") if current_state else "medium"
        
        return f"""🎉 ¡Perfecto! He creado tu perfil familiar personalizado:

👨‍👩‍👧‍👦 **Tu familia:** {family_size} miembros ({age_group})
💰 **Presupuesto:** {budget_level}
🎯 **Intereses:** {interests}
🌍 **Origen:** {profile.origin_country}
✨ **Necesidades especiales:** {', '.join(profile.special_needs) if profile.special_needs else 'Ninguna'}

🐭 **¡Ahora puedo ayudarte a planificar tu viaje perfecto a Madrid!**

¿En qué te gustaría que te ayude?
- 🏨 Recomendaciones de hoteles
- 🍽️ Sugerencias de restaurantes
- 🎯 Actividades para toda la familia
- 🚌 Consejos de transporte
- 📅 Itinerario completo"""
    
    def _update_conversation_state(self, state: ConversationState, response_data: Dict[str, Any]):
        """Обновляет состояние разговора"""
        try:
            # Обновляем собранные данные
            if "collected_info" in response_data:
                state.collected_data.update(response_data["collected_info"])
            
            # Обновляем текущий шаг
            if "next_step" in response_data and response_data["next_step"]:
                state.update_step(response_data["next_step"])
            
            # Отмечаем профиль как собранный если нужно
            if response_data.get("profile_complete", False):
                state.mark_profile_complete()
            
            # Сохраняем обновленное состояние
            self.conversation_manager.update_conversation_state(state.conversation_id, state)
            
            print(f"✅ ConversationService: Состояние разговора {state.conversation_id} обновлено")
            print(f"   Текущий шаг: {state.current_step}")
            print(f"   Собранные данные: {len(state.collected_data)} полей")
            print(f"   Профиль собран: {state.profile_complete}")
            
        except Exception as e:
            print(f"❌ ConversationService: Ошибка обновления состояния: {e}")
    
    def get_conversation_state(self, conversation_id: str, family_id: str) -> ConversationState:
        """Получает состояние разговора"""
        return self.conversation_manager.get_conversation_state(conversation_id, family_id)
    
    def start_new_conversation(self, family_id: str) -> str:
        """Начинает новый разговор"""
        import time
        conversation_id = f"conv_{int(time.time())}_{family_id}"
        
        # Создаем новое состояние
        state = ConversationState(
            conversation_id=conversation_id,
            family_id=family_id
        )
        
        self.conversation_manager.update_conversation_state(conversation_id, state)
        
        print(f"✅ ConversationService: Новый разговор {conversation_id} начат для семьи {family_id}")
        return conversation_id

# Глобальный экземпляр сервиса
conversation_service = ConversationService()
