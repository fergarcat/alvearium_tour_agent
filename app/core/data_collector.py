# app/core/data_collector.py
"""
Интерактивный сбор данных о семье для персонализации
"""

from typing import List, Dict, Any
from datetime import datetime
from models.family_models import FamilyProfile

class FamilyDataCollector:
    """Интерактивный сбор основных данных о семье"""
    
    def __init__(self):
        self.required_fields = [
            "kids_ages", "adults_count", "budget_level", 
            "start_date", "end_date", "interests", "origin_country"
        ]
        self.optional_fields = ["trip_preferences"]
        self.field_prompts = {
            "kids_ages": "¿Cuáles son las edades de tus hijos? (ej: 8, 12 o 5, 7, 10)",
            "adults_count": "¿Cuántos adultos viajan? (incluyéndote a ti)",
            "budget_level": "¿Cuál es tu presupuesto? (low/medium/high)",
            "start_date": "¿Cuándo empieza tu viaje? (formato: YYYY-MM-DD, ej: 2024-06-15)",
            "end_date": "¿Cuándo termina tu viaje? (formato: YYYY-MM-DD, ej: 2024-06-20)",
            "interests": "¿Qué te interesa más? (museums, parks, food, shows, shopping, history, art)",
            "origin_country": "¿Desde qué país viajas? (ej: Spain, France, Germany)",
            "trip_preferences": "¿Qué tipo de viaje prefieres? (hotel, restaurantes, actividades, transporte, general) - Describe tus preferencias específicas"
        }
        self.field_validators = {
            "kids_ages": self._validate_ages,
            "adults_count": self._validate_adults_count,
            "budget_level": self._validate_budget_level,
            "start_date": self._validate_date,
            "end_date": self._validate_date,
            "interests": self._validate_interests,
            "origin_country": self._validate_country,
            "trip_preferences": self._validate_trip_preferences
        }
    
    def _validate_ages(self, value: str) -> List[int]:
        """Валидация возрастов детей"""
        try:
            ages = [int(x.strip()) for x in value.split(",")]
            if not all(0 < age < 18 for age in ages):
                raise ValueError("Las edades deben estar entre 1 y 17 años")
            return ages
        except ValueError as e:
            raise ValueError(f"Formato inválido. Usa: 8, 12 o 5, 7, 10. Error: {e}")
    
    def _validate_adults_count(self, value: str) -> int:
        """Валидация количества взрослых"""
        try:
            count = int(value)
            if count < 1 or count > 10:
                raise ValueError("Debe ser entre 1 y 10 adultos")
            return count
        except ValueError as e:
            raise ValueError(f"Número inválido. Error: {e}")
    
    def _validate_budget_level(self, value: str) -> str:
        """Валидация уровня бюджета"""
        valid_levels = ["low", "medium", "high"]
        if value.lower() not in valid_levels:
            raise ValueError(f"Nivel inválido. Usa: {', '.join(valid_levels)}")
        return value.lower()
    
    def _validate_date(self, value: str) -> str:
        """Валидация даты"""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            raise ValueError("Formato inválido. Usa: YYYY-MM-DD (ej: 2024-06-15)")
    
    def _validate_interests(self, value: str) -> List[str]:
        """Валидация интересов"""
        valid_interests = ["museums", "parks", "food", "shows", "shopping", "history", "art", "sports", "nature"]
        interests = [x.strip().lower() for x in value.split(",")]
        invalid = [i for i in interests if i not in valid_interests]
        if invalid:
            raise ValueError(f"Intereses inválidos: {invalid}. Válidos: {', '.join(valid_interests)}")
        return interests
    
    def _validate_country(self, value: str) -> str:
        """Валидация страны"""
        if len(value.strip()) < 2:
            raise ValueError("Nombre de país muy corto")
        return value.strip().title()
    
    def _validate_trip_preferences(self, value: str) -> str:
        """Валидация пожеланий по поездке"""
        value = value.strip()
        if len(value) < 5:
            raise ValueError("Descripción muy corta. Describe qué tipo de viaje prefieres")
        
        # Проверяем, что упоминается хотя бы один тип поездки
        trip_types = ["hotel", "restaurante", "actividad", "transporte", "general", "alojamiento", "comida", "diversión"]
        if not any(trip_type in value.lower() for trip_type in trip_types):
            raise ValueError("Menciona al menos un tipo de viaje: hotel, restaurantes, actividades, transporte")
        
        return value
    
    def collect_family_data(self, user_id: str = "default") -> tuple[FamilyProfile, str]:
        """Интерактивный сбор данных о семье"""
        print("🐭 ¡Hola! Soy el Ratoncito Pérez, tu asistente mágico para viajes familiares en Madrid!")
        print("Para personalizar tu experiencia, necesito conocer algunos datos sobre tu familia:\n")
        
        family_data = {}
        
        for field in self.required_fields:
            while True:
                try:
                    print(f"📝 {self.field_prompts[field]}")
                    user_input = input("Respuesta: ").strip()
                    
                    if not user_input:
                        print("❌ Este campo es obligatorio. Por favor, responde.")
                        continue
                    
                    # Валидация
                    validated_value = self.field_validators[field](user_input)
                    family_data[field] = validated_value
                    print(f"✅ Perfecto: {validated_value}\n")
                    break
                    
                except ValueError as e:
                    print(f"❌ Error: {e}")
                    print("Inténtalo de nuevo.\n")
        
        # Валидация дат
        try:
            start_date = datetime.strptime(family_data["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(family_data["end_date"], "%Y-%m-%d")
            
            if start_date >= end_date:
                raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
            
            # Проверка, что дата не в прошлом
            today = datetime.now().date()
            if start_date.date() < today:
                raise ValueError("La fecha de inicio no puede ser en el pasado")
                
        except ValueError as e:
            print(f"❌ Error en las fechas: {e}")
            return self.collect_family_data(user_id)  # Повторный сбор
        
        # Собираем пожелания по поездке
        trip_preferences = ""
        while True:
            try:
                print(f"📝 {self.field_prompts['trip_preferences']}")
                user_input = input("Respuesta: ").strip()
                
                if not user_input:
                    print("❌ Este campo es importante para personalizar tu viaje. Por favor, responde.")
                    continue
                
                # Валидация
                validated_value = self.field_validators["trip_preferences"](user_input)
                trip_preferences = validated_value
                print(f"✅ Perfecto: {validated_value}\n")
                break
                
            except ValueError as e:
                print(f"❌ Error: {e}")
                print("Inténtalo de nuevo.\n")
        
        # Создание профиля семьи
        profile = FamilyProfile(
            kids_ages=family_data["kids_ages"],
            adults_count=family_data["adults_count"],
            budget_level=family_data["budget_level"],
            start_date=family_data["start_date"],
            end_date=family_data["end_date"],
            interests=family_data["interests"],
            origin_country=family_data["origin_country"],
            trip_preferences=trip_preferences
        )
        
        print("🎉 ¡Excelente! He recopilado toda la información necesaria.")
        print(f"📊 Resumen de tu familia:")
        print(f"   👶 Edades de los niños: {profile.kids_ages}")
        print(f"   👨‍👩‍👧‍👦 Adultos: {profile.adults_count}")
        print(f"   💰 Presupuesto: {profile.budget_level}")
        print(f"   📅 Fechas: {profile.start_date} a {profile.end_date}")
        print(f"   🎯 Intereses: {', '.join(profile.interests)}")
        print(f"   🌍 Origen: {profile.origin_country}")
        print(f"   ✨ Pожелания: {trip_preferences}")
        print("\n¡Ahora puedo personalizar tu experiencia en Madrid! 🐭✨\n")
        
        return profile, trip_preferences
    
    def collect_additional_data(self, profile: FamilyProfile) -> FamilyProfile:
        """Сбор дополнительных данных о семье"""
        print("🔍 ¿Te gustaría proporcionar información adicional para una mejor personalización?")
        print("(Responde 'sí' para continuar o 'no' para usar valores por defecto)")
        
        response = input("Respuesta: ").strip().lower()
        
        if response in ["sí", "si", "yes", "y"]:
            print("\n📝 Información adicional:")
            
            # Специальные потребности
            print("¿Tienes alguna necesidad especial? (ej: wheelchair, stroller, dietary)")
            special_needs_input = input("Respuesta (opcional): ").strip()
            if special_needs_input:
                profile.special_needs = [x.strip() for x in special_needs_input.split(",")]
            
            # Тип размещения
            print("¿Qué tipo de alojamiento prefieres? (hotel/apartment/hostel)")
            accommodation_input = input("Respuesta (opcional): ").strip()
            if accommodation_input in ["hotel", "apartment", "hostel"]:
                profile.accommodation_type = accommodation_input
            
            # Предпочтения транспорта
            print("¿Cómo prefieres moverte? (public/car/walking)")
            transport_input = input("Respuesta (opcional): ").strip()
            if transport_input in ["public", "car", "walking"]:
                profile.transportation_preference = transport_input
            
            print("✅ Información adicional guardada.")
        
        return profile
