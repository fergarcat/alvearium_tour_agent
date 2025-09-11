# app/services/data_collector.py
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
        self.field_prompts = {
            "kids_ages": "¿Cuáles son las edades de tus hijos? (ej: 8, 12 o 5, 7, 10)",
            "adults_count": "¿Cuántos adultos viajan? (incluyéndote a ti)",
            "budget_level": "¿Cuál es tu presupuesto? (low/medium/high)",
            "start_date": "¿Cuándo empieza tu viaje? (formato: YYYY-MM-DD, ej: 2024-06-15)",
            "end_date": "¿Cuándo termina tu viaje? (formato: YYYY-MM-DD, ej: 2024-06-20)",
            "interests": "¿Qué te interesa más? (museums, parks, food, shows, shopping, history, art)",
            "origin_country": "¿Desde qué país viajas? (ej: Spain, France, Germany)"
        }
        self.field_validators = {
            "kids_ages": self._validate_ages,
            "adults_count": self._validate_adults_count,
            "budget_level": self._validate_budget_level,
            "start_date": self._validate_date,
            "end_date": self._validate_date,
            "interests": self._validate_interests,
            "origin_country": self._validate_country
        }
    
    def _validate_ages(self, value: str) -> List[int]:
        """Валидация возрастов детей"""
        try:
            ages = [int(x.strip()) for x in value.split(",")]
            if not all(0 <= age < 18 for age in ages):
                raise ValueError("Las edades deben estar entre 0 y 17 años")
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
    
    def collect_family_data(self, user_id: str = "default") -> FamilyProfile:
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
        
        # Создание профиля семьи
        profile = FamilyProfile(
            kids_ages=family_data["kids_ages"],
            adults_count=family_data["adults_count"],
            budget_level=family_data["budget_level"],
            start_date=family_data["start_date"],
            end_date=family_data["end_date"],
            interests=family_data["interests"],
            origin_country=family_data["origin_country"]
        )
        
        print("🎉 ¡Excelente! He recopilado toda la información necesaria.")
        print(f"📊 Resumen de tu familia:")
        print(f"   👶 Edades de los niños: {profile.kids_ages}")
        print(f"   👨‍👩‍👧‍👦 Adultos: {profile.adults_count}")
        print(f"   💰 Presupuesto: {getattr(profile, 'budget_level', 'medium')}")
        print(f"   📅 Fechas: {getattr(profile, 'start_date', 'No especificadas')} a {getattr(profile, 'end_date', 'No especificadas')}")
        print(f"   🎯 Intereses: {', '.join(profile.interests)}")
        print(f"   🌍 Origen: {profile.origin_country}")
        print("\n¡Ahora puedo personalizar tu experiencia en Madrid! 🐭✨\n")
        
        return profile
    
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
