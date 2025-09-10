# app/models/family_models_supabase.py
"""
Модели данных для системы персонализации с интеграцией Supabase
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import os
from supabase import create_client, Client

@dataclass
class FamilyProfileSupabase:
    """Профиль семьи с интеграцией Supabase"""
    
    # Основные поля
    family_id: str  # ID семьи в Supabase
    kids_ages: List[int]
    adults_count: int
    interests: List[str]
    origin_country: str
    
    # Дополнительные поля
    special_needs: Optional[List[str]] = None
    language_preference: str = "es"
    accommodation_type: Optional[str] = None
    transportation_preference: Optional[str] = None
    
    # Supabase клиент
    _supabase: Optional[Client] = None
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.special_needs is None:
            self.special_needs = []
        if self.accommodation_type is None:
            self.accommodation_type = "hotel"
        if self.transportation_preference is None:
            self.transportation_preference = "public"
        
        # Инициализируем Supabase клиент
        if not self._supabase:
            self._init_supabase()
    
    def _init_supabase(self):
        """Инициализация Supabase клиента"""
        try:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_ANON_KEY")
            
            if not url or not key:
                print("⚠️ SUPABASE_URL и SUPABASE_ANON_KEY не установлены")
                raise ValueError("Supabase credentials not found")
            
            self._supabase = create_client(url, key)
            print("✅ Supabase клиент инициализирован успешно")
        except Exception as e:
            print(f"❌ Ошибка инициализации Supabase: {e}")
            raise
    
    def get_stay_duration(self, start_date: str, end_date: str) -> int:
        """Возвращает продолжительность поездки в днях"""
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days
    
    def get_family_size(self) -> int:
        """Возвращает общий размер семьи"""
        return self.adults_count + len(self.kids_ages)
    
    def get_age_group(self) -> str:
        """Возвращает возрастную группу детей"""
        if not self.kids_ages:
            return "adults_only"
        
        max_age = max(self.kids_ages)
        if max_age <= 5:
            return "toddlers"
        elif max_age <= 12:
            return "children"
        else:
            return "teenagers"
    
    def to_supabase_family_data(self) -> Dict[str, Any]:
        """Преобразует в формат для таблицы families"""
        return {
            "family_id": self.family_id,
            "origin_country": self.origin_country,
            "languages": [self.language_preference],
            "interests": self.interests,
            "dietary_restrictions": self.special_needs or [],
            "accommodation_preferences": [self.accommodation_type] if self.accommodation_type else [],
            "transport_preferences": [self.transportation_preference] if self.transportation_preference else [],
            "accessibility_needs": self.special_needs or [],
            "medical_restrictions": [],
            "metadata": {
                "family_size": self.get_family_size(),
                "age_group": self.get_age_group()
            }
        }
    
    def to_supabase_members_data(self) -> List[Dict[str, Any]]:
        """Преобразует в формат для таблицы family_members"""
        members_data = []
        
        # Добавляем детей
        for i, age in enumerate(self.kids_ages):
            members_data.append({
                "member_type": "child",
                "age": float(age),  # Конвертируем в float для Supabase
                "role": "child",
                "interests": self.interests,
                "special_needs": self.special_needs or [],
                "mobility_restrictions": []
            })
        
        # Добавляем взрослых
        for i in range(self.adults_count):
            members_data.append({
                "member_type": "adult",
                "age": 30 + i * 5,  # Примерный возраст
                "role": "parent",
                "interests": self.interests,
                "special_needs": self.special_needs or [],
                "mobility_restrictions": []
            })
        
        return members_data
    
    def save_to_supabase(self) -> Optional[str]:
        """Сохраняет профиль в Supabase"""
        if not self._supabase:
            print("❌ Supabase клиент не инициализирован")
            return None
        
        try:
            # Проверяем, существует ли уже семья с таким family_id
            existing_family = self._supabase.table("families").select("id").eq("family_id", self.family_id).execute()
            
            if existing_family.data:
                print(f"⚠️ Семья с ID {self.family_id} уже существует, обновляем...")
                family_uuid = existing_family.data[0]["id"]
                
                # Обновляем данные семьи
                family_update = self.to_supabase_family_data()
                del family_update["family_id"]  # Убираем family_id из обновления
                
                self._supabase.table("families").update(family_update).eq("id", family_uuid).execute()
                
                # Обновляем членов семьи (удаляем старых и создаем новых)
                self._supabase.table("family_members").delete().eq("family_id", family_uuid).execute()
                
                members_data = self.to_supabase_members_data()
                for member in members_data:
                    member["family_id"] = family_uuid
                
                self._supabase.table("family_members").insert(members_data).execute()
                
                print(f"✅ Профиль семьи обновлен в Supabase: {family_uuid}")
                return family_uuid
            
            # Создаем новую семью
            family_result = self._supabase.table("families").insert(
                self.to_supabase_family_data()
            ).execute()
            
            if not family_result.data:
                print("❌ Не удалось создать семью")
                return None
            
            family_uuid = family_result.data[0]["id"]
            
            # Создаем членов семьи
            members_data = self.to_supabase_members_data()
            for member in members_data:
                member["family_id"] = family_uuid
            
            members_result = self._supabase.table("family_members").insert(
                members_data
            ).execute()
            
            if members_result.data:
                print(f"✅ Профиль семьи сохранен в Supabase: {family_uuid}")
                return family_uuid
            else:
                print("❌ Не удалось создать членов семьи")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка сохранения в Supabase: {e}")
            return None
    
    def load_from_supabase(self, family_id: str) -> bool:
        """Загружает профиль из Supabase"""
        if not self._supabase:
            print("❌ Supabase клиент не инициализирован")
            return False
        
        try:
            # Получаем данные семьи
            family_result = self._supabase.table("families").select("*").eq("family_id", family_id).execute()
            
            print(f"🔍 Поиск семьи с ID: {family_id}")
            print(f"🔍 Результат поиска: {len(family_result.data) if family_result.data else 0} записей")
            
            if not family_result.data:
                print(f"❌ Семья с ID {family_id} не найдена")
                return False
            
            family_data = family_result.data[0]
            
            # Получаем членов семьи
            members_result = self._supabase.table("family_members").select("*").eq("family_id", family_data["id"]).execute()
            members_data = members_result.data or []
            
            # Извлекаем данные детей и взрослых
            kids_ages = []
            adults_count = 0
            
            for member in members_data:
                if member["member_type"] == "child":
                    kids_ages.append(member["age"])
                elif member["member_type"] == "adult":
                    adults_count += 1
            
            # Обновляем поля объекта
            self.family_id = family_data["family_id"]
            self.kids_ages = kids_ages
            self.adults_count = adults_count
            # budget_level, start_date, end_date больше не хранятся в таблице families
            self.interests = family_data["interests"]
            self.origin_country = family_data["origin_country"]
            self.special_needs = family_data["accessibility_needs"]
            self.language_preference = family_data["languages"][0] if family_data["languages"] else "es"
            self.accommodation_type = family_data["accommodation_preferences"][0] if family_data["accommodation_preferences"] else "hotel"
            self.transportation_preference = family_data["transport_preferences"][0] if family_data["transport_preferences"] else "public"
            
            print(f"✅ Профиль семьи загружен из Supabase: {family_id}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Supabase: {e}")
            return False
    
    def update_in_supabase(self) -> bool:
        """Обновляет профиль в Supabase"""
        if not self._supabase:
            print("❌ Supabase клиент не инициализирован")
            return False
        
        try:
            # Получаем UUID семьи
            family_result = self._supabase.table("families").select("id").eq("family_id", self.family_id).execute()
            
            if not family_result.data:
                print(f"❌ Семья с ID {self.family_id} не найдена")
                return False
            
            family_uuid = family_result.data[0]["id"]
            
            # Обновляем данные семьи
            family_update = self.to_supabase_family_data()
            del family_update["family_id"]  # Убираем family_id из обновления
            
            self._supabase.table("families").update(family_update).eq("id", family_uuid).execute()
            
            # Обновляем членов семьи (удаляем старых и создаем новых)
            self._supabase.table("family_members").delete().eq("family_id", family_uuid).execute()
            
            members_data = self.to_supabase_members_data()
            for member in members_data:
                member["family_id"] = family_uuid
            
            self._supabase.table("family_members").insert(members_data).execute()
            
            print(f"✅ Профиль семьи обновлен в Supabase: {self.family_id}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления в Supabase: {e}")
            return False
    
    def create_ai_profile(self, ai_analysis: Dict[str, Any]) -> Optional[str]:
        """Создает AI профиль семьи"""
        if not self._supabase:
            print("❌ Supabase клиент не инициализирован")
            return None
        
        try:
            # Получаем UUID семьи
            family_result = self._supabase.table("families").select("id").eq("family_id", self.family_id).execute()
            
            if not family_result.data:
                print(f"❌ Семья с ID {self.family_id} не найдена")
                return None
            
            family_uuid = family_result.data[0]["id"]
            
            # Создаем AI профиль
            profile_data = {
                "family_id": family_uuid,
                "family_type": ai_analysis.get("family_type", "mixed_age_family"),
                "family_type_confidence": ai_analysis.get("confidence", 0.8),
                "ai_analysis": ai_analysis,
                "confidence_score": ai_analysis.get("confidence", 0.8)
            }
            
            result = self._supabase.table("family_profiles").insert(profile_data).execute()
            
            if result.data:
                print(f"✅ AI профиль создан: {result.data[0]['id']}")
                return result.data[0]["id"]
            else:
                print("❌ Не удалось создать AI профиль")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка создания AI профиля: {e}")
            return None
    
    def save_travel_request(self, request_type: str, request_data: Dict[str, Any], trip_preferences: str = "", 
                          budget_level: str = "medium", start_date: str = "", end_date: str = "") -> Optional[str]:
        """Сохраняет запрос на планирование поездки с пожеланиями"""
        if not self._supabase:
            print("❌ Supabase клиент не инициализирован")
            return None
        
        try:
            # Получаем UUID семьи
            family_result = self._supabase.table("families").select("id").eq("family_id", self.family_id).execute()
            
            if not family_result.data:
                print(f"❌ Семья с ID {self.family_id} не найдена")
                return None
            
            family_uuid = family_result.data[0]["id"]
            
            # Создаем запрос с пожеланиями по поездке
            request_record = {
                "family_id": family_uuid,
                "request_type": request_type,
                "request_data": {
                    **request_data,
                    "trip_preferences": trip_preferences  # Добавляем пожелания в request_data
                },
                "status": "pending",
                "priority": 1,
                "preferences": {
                    **request_data.get("preferences", {}),
                    "trip_preferences": trip_preferences,
                    "family_profile": {
                        "kids_ages": self.kids_ages,
                        "adults_count": self.adults_count,
                        "interests": self.interests,
                        "special_needs": self.special_needs or []
                    }
                },
                "budget_level": budget_level,
                "arrival_date": start_date,
                "departure_date": end_date
                # duration_days убрано - база данных сама вычислит как (departure_date - arrival_date)
            }
            
            result = self._supabase.table("travel_requests").insert(request_record).execute()
            
            if result.data:
                print(f"✅ Запрос с пожеланиями сохранен: {result.data[0]['id']}")
                return result.data[0]["id"]
            else:
                print("❌ Не удалось сохранить запрос")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка сохранения запроса: {e}")
            return None

@dataclass
class PersonalizedQuery:
    """Персонализированный запрос с контекстом семьи"""
    original_query: str
    family_profile: FamilyProfileSupabase
    personalized_context: str
    target_agent: str  # "hotels", "restaurants", "activities", "transportation", "all"
