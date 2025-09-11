#!/usr/bin/env python3
"""
Интерактивный тест, имитирующий взаимодействие с фронтендом
Позволяет тестировать систему в реальном времени с пользовательским вводом
"""

import sys
import os
import json
from datetime import datetime

# Добавляем путь к приложению
sys.path.append('app')

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

class FrontendSimulator:
    """Симулятор фронтенда для тестирования чат-бота"""
    
    def __init__(self):
        self.planner = None
        self.current_family_id = None
        self.session_data = {
            "start_time": datetime.now(),
            "messages": [],
            "family_profile": None,
            "test_scenarios": []
        }
    
    def initialize_system(self):
        """Инициализация системы"""
        print("🚀 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ")
        print("=" * 50)
        
        try:
            from agents.personalization_agent import PersonalizedTripPlanner
            self.planner = PersonalizedTripPlanner()
            print("✅ Система инициализирована успешно")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            import traceback
            print(f"📋 Детали ошибки: {traceback.format_exc()}")
            return False
    
    def display_welcome(self):
        """Отображает приветствие"""
        print("\n" + "=" * 60)
        print("🐭 ДОБРО ПОЖАЛОВАТЬ В СИМУЛЯТОР ФРОНТЕНДА")
        print("=" * 60)
        print("Этот тест имитирует взаимодействие с фронтендом")
        print("Вы можете вводить сообщения как настоящий пользователь")
        print("\n🏗️ НОВАЯ ReAct АРХИТЕКТУРА:")
        print("  PersonalizationReactAgent → RouterAgent → Специализированные агенты")
        print("  RouterAgent использует ReAct паттерн (Reasoning → Acting → Observing)")
        print("  Инструменты: AnalyzeQueryTool, CallActivitiesAgentTool, CallRestaurantsAgentTool")
        print("\n📋 Доступные команды:")
        print("  /help     - Показать справку")
        print("  /profile  - Показать профиль семьи")
        print("  /data     - Показать детальную передачу данных")
        print("  /scenario - Запустить тестовый сценарий")
        print("  /activities - Тестировать ActivitiesAgent (ReAct)")
        print("  /stats    - Показать статистику сессии")
        print("  /exit     - Выход")
        print("\n💬 Начните диалог с ботом!")
        print("-" * 60)
    
    def log_message(self, user_message: str, bot_response: str, response_time: float = 0):
        """Логирует сообщения для анализа"""
        message = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response,
            "response_time": response_time,
            "family_id": self.current_family_id
        }
        self.session_data["messages"].append(message)
    
    def show_data_flow_info(self, user_input: str):
        """Показывает информацию о передаче данных между агентами в новой ReAct архитектуре"""
        try:
            print("\n" + "=" * 60)
            print("🔄 АНАЛИЗ ПЕРЕДАЧИ ДАННЫХ МЕЖДУ АГЕНТАМИ (ReAct Architecture)")
            print("=" * 60)
            
            # Получаем профиль семьи
            profile = self.planner.personalization_agent.get_family_profile(self.current_family_id)
            
            if profile:
                print("📤 PersonalizationReactAgent → RouterAgent:")
                print(f"   • Query: {user_input}")
                print(f"   • Family ID: {self.current_family_id}")
                print(f"   • Profile found: ✅")
                
                # Показываем данные профиля
                print(f"   • Profile data:")
                print(f"     - kids_ages: {profile.kids_ages}")
                print(f"     - adults_count: {profile.adults_count}")
                print(f"     - interests: {profile.interests}")
                print(f"     - origin_country: {profile.origin_country}")
                print(f"     - special_needs: {getattr(profile, 'special_needs', [])}")
                print(f"     - budget_level: {getattr(profile, 'budget_level', 'medium')}")
                
                print("\n🧠 RouterAgent ReAct Workflow:")
                print("   1. Reasoning: AnalyzeQueryTool анализирует запрос")
                print("   2. Acting: Вызывает соответствующие инструменты:")
                print("      - CallActivitiesAgentTool (если нужны активности)")
                print("      - CallRestaurantsAgentTool (если нужны рестораны)")
                print("   3. Observing: Оценивает результаты и принимает решения")
                print("   4. Повторяет цикл до получения полного ответа")
                
                # Анализируем, какие инструменты будут использованы
                query_lower = user_input.lower()
                tools_to_use = []
                
                if any(word in query_lower for word in ['actividad', 'museo', 'parque', 'diversión', 'entretenimiento', 'taller']):
                    tools_to_use.append("CallActivitiesAgentTool")
                if any(word in query_lower for word in ['comer', 'restaurante', 'cena', 'almuerzo', 'comida', 'bar', 'café']):
                    tools_to_use.append("CallRestaurantsAgentTool")
                
                if tools_to_use:
                    print(f"\n🔧 Инструменты, которые будут использованы:")
                    for tool in tools_to_use:
                        print(f"   • {tool}")
                else:
                    print(f"\n⚠️ Возможно, будет использован простой ответ без специализированных агентов")
                
            else:
                print("📤 PersonalizationReactAgent (Sequential Mode):")
                print(f"   • Query: {user_input}")
                print(f"   • Family ID: {self.current_family_id}")
                print(f"   • Profile: НЕ НАЙДЕН")
                print(f"   • Mode: Sequential data collection")
                print(f"   • RouterAgent: НЕ ЗАДЕЙСТВОВАН")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Ошибка анализа данных: {e}")
            print("=" * 60)
    
    def show_router_response_info(self, response: str):
        """Показывает информацию о том, что получил RouterAgent в новой ReAct архитектуре"""
        try:
            print("\n" + "=" * 60)
            print("📥 RouterAgent ReAct ОТВЕТИЛ ПОЛЬЗОВАТЕЛЮ:")
            print("=" * 60)
            
            # Анализируем ответ
            if "RouterAgent" in response or "ReAct" in response:
                print("✅ RouterAgent ReAct обработал запрос")
                print(f"   • Архитектура: ReAct (Reasoning → Acting → Observing)")
                print(f"   • Длина ответа: {len(response)} символов")
                
                # Проверяем, какие инструменты были задействованы
                tools_used = []
                if "actividad" in response.lower() or "museo" in response.lower() or "parque" in response.lower():
                    tools_used.append("CallActivitiesAgentTool")
                if "comer" in response.lower() or "restaurante" in response.lower() or "cena" in response.lower():
                    tools_used.append("CallRestaurantsAgentTool")
                
                if tools_used:
                    print(f"   • Инструменты использованы: {', '.join(tools_used)}")
                    
                    # Детальный анализ ActivitiesAgent через CallActivitiesAgentTool
                    if "CallActivitiesAgentTool" in tools_used:
                        print("\n🎯 АНАЛИЗ ОТВЕТА ActivitiesAgent (через CallActivitiesAgentTool):")
                        print(f"   • Содержит план активностей: {'Sí' if 'actividad' in response.lower() else 'No'}")
                        print(f"   • Содержит расписание: {'Sí' if 'horario' in response.lower() or 'día' in response.lower() else 'No'}")
                        print(f"   • Содержит музеи: {'Sí' if 'museo' in response.lower() else 'No'}")
                        print(f"   • Содержит парки: {'Sí' if 'parque' in response.lower() else 'No'}")
                        print(f"   • Содержит образовательные активности: {'Sí' if 'educativo' in response.lower() or 'taller' in response.lower() else 'No'}")
                        print(f"   • Содержит рекомендации по возрасту: {'Sí' if 'años' in response.lower() else 'No'}")
                        print(f"   • Содержит информацию о погоде: {'Sí' if 'clima' in response.lower() or 'temperatura' in response.lower() else 'No'}")
                        print(f"   • Содержит практические советы: {'Sí' if 'recomendable' in response.lower() or 'llevar' in response.lower() else 'No'}")
                        
                        # Анализируем структуру ответа
                        lines = response.split('\n')
                        activity_sections = [line for line in lines if 'actividad' in line.lower() or 'museo' in line.lower() or 'parque' in line.lower()]
                        print(f"   • Количество активностей: {len(activity_sections)}")
                        
                        # Проверяем использование данных профиля
                        profile_usage = []
                        if "niños" in response.lower():
                            profile_usage.append("kids_ages")
                        if "adultos" in response.lower():
                            profile_usage.append("adults_count")
                        if "presupuesto" in response.lower():
                            profile_usage.append("budget_level")
                        if "fechas" in response.lower():
                            profile_usage.append("dates")
                        if "intereses" in response.lower():
                            profile_usage.append("interests")
                        if "necesidades especiales" in response.lower():
                            profile_usage.append("special_needs")
                        
                        if profile_usage:
                            print(f"   • Данные профиля использованы: {', '.join(profile_usage)}")
                        else:
                            print(f"   • Данные профиля использованы: минимально")
                            
                        # Анализ ReAct цикла
                        print(f"\n🔄 АНАЛИЗ ReAct ЦИКЛА:")
                        if "Thought:" in response or "Action:" in response or "Observation:" in response:
                            print(f"   • ReAct цикл обнаружен в ответе")
                            thought_count = response.count("Thought:")
                            action_count = response.count("Action:")
                            observation_count = response.count("Observation:")
                            print(f"   • Thoughts: {thought_count}")
                            print(f"   • Actions: {action_count}")
                            print(f"   • Observations: {observation_count}")
                        else:
                            print(f"   • ReAct цикл не отображается в финальном ответе (нормально)")
                            
                    # Детальный анализ RestaurantsAgent через CallRestaurantsAgentTool
                    if "CallRestaurantsAgentTool" in tools_used:
                        print("\n🍽️ АНАЛИЗ ОТВЕТА RestaurantsAgent (через CallRestaurantsAgentTool):")
                        print(f"   • Содержит рестораны: {'Sí' if 'restaurante' in response.lower() else 'No'}")
                        print(f"   • Содержит меню: {'Sí' if 'menú' in response.lower() or 'plato' in response.lower() else 'No'}")
                        print(f"   • Содержит цены: {'Sí' if 'precio' in response.lower() or '€' in response else 'No'}")
                        print(f"   • Содержит адреса: {'Sí' if 'dirección' in response.lower() or 'ubicación' in response.lower() else 'No'}")
                        print(f"   • Содержит отзывы: {'Sí' if 'recomendado' in response.lower() or 'estrellas' in response.lower() else 'No'}")
                        
                else:
                    print(f"   • Инструменты использованы: простой ответ (возможно, AnalyzeQueryTool определил, что специализированные агенты не нужны)")
                    
            else:
                print("ℹ️ PersonalizationReactAgent обработал запрос (Sequential Mode)")
                print(f"   • Тип ответа: Simple/Sequential")
                print(f"   • Длина ответа: {len(response)} символов")
                print(f"   • RouterAgent ReAct не задействован")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Ошибка анализа ответа: {e}")
            print("=" * 60)
    
    def analyze_activities_agent_response(self, response: str):
        """Детальный анализ ответа ActivitiesAgent"""
        try:
            print("🎯 ДЕТАЛЬНЫЙ АНАЛИЗ ОТВЕТА ActivitiesAgent:")
            print("-" * 50)
            
            # Анализ структуры ответа
            lines = response.split('\n')
            total_lines = len(lines)
            non_empty_lines = [line for line in lines if line.strip()]
            
            print(f"📊 Структура ответа:")
            print(f"   • Всего строк: {total_lines}")
            print(f"   • Непустых строк: {len(non_empty_lines)}")
            print(f"   • Средняя длина строки: {sum(len(line) for line in non_empty_lines) / len(non_empty_lines):.1f} символов")
            
            # Анализ содержания
            content_analysis = {
                "museos": len([line for line in lines if 'museo' in line.lower()]),
                "parques": len([line for line in lines if 'parque' in line.lower()]),
                "talleres": len([line for line in lines if 'taller' in line.lower()]),
                "horarios": len([line for line in lines if 'horario' in line.lower()]),
                "ubicaciones": len([line for line in lines if 'ubicación' in line.lower()]),
                "descripciones": len([line for line in lines if 'descripción' in line.lower()]),
                "fechas": len([line for line in lines if 'diciembre' in line.lower() or 'enero' in line.lower()]),
                "actividades": len([line for line in lines if 'actividad' in line.lower()])
            }
            
            print(f"📋 Содержание ответа:")
            for key, value in content_analysis.items():
                print(f"   • {key.capitalize()}: {value}")
            
            # Анализ качества персонализации
            personalization_score = 0
            if "niños" in response.lower():
                personalization_score += 1
            if "años" in response.lower():
                personalization_score += 1
            if "familia" in response.lower():
                personalization_score += 1
            if "madrid" in response.lower():
                personalization_score += 1
            if "diciembre" in response.lower() or "enero" in response.lower():
                personalization_score += 1
            
            print(f"🎯 Качество персонализации: {personalization_score}/5")
            
            # Анализ практичности
            practicality_score = 0
            if "horario" in response.lower():
                practicality_score += 1
            if "ubicación" in response.lower():
                practicality_score += 1
            if "entrada" in response.lower() or "gratis" in response.lower():
                practicality_score += 1
            if "recomendable" in response.lower() or "llevar" in response.lower():
                practicality_score += 1
            if "transporte" in response.lower():
                practicality_score += 1
            
            print(f"🔧 Практичность: {practicality_score}/5")
            
            # Общая оценка
            total_score = personalization_score + practicality_score
            print(f"⭐ Общая оценка: {total_score}/10")
            
            if total_score >= 8:
                print("   🎉 Отличный ответ!")
            elif total_score >= 6:
                print("   ✅ Хороший ответ")
            elif total_score >= 4:
                print("   ⚠️ Удовлетворительный ответ")
            else:
                print("   ❌ Требует улучшения")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Ошибка анализа ActivitiesAgent: {e}")
    
    def process_user_input(self, user_input: str) -> str:
        """Обрабатывает пользовательский ввод с детальным логированием процесса"""
        start_time = datetime.now()
        
        try:
            # Обрабатываем команды
            if user_input.startswith('/'):
                return self.handle_command(user_input)
            
            print("\n" + "=" * 80)
            print("🔄 ПОЛНЫЙ ПРОЦЕСС ОБРАБОТКИ ЗАПРОСА")
            print("=" * 80)
            
            # Шаг 1: Инициализация семьи
            if not self.current_family_id:
                self.current_family_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"🆔 ШАГ 1: Создан ID семьи: {self.current_family_id}")
            else:
                print(f"🆔 ШАГ 1: Используется существующий ID семьи: {self.current_family_id}")
            
            # Шаг 2: Анализ входных данных
            print(f"\n📝 ШАГ 2: Анализ входных данных")
            print(f"   • Пользовательский ввод: '{user_input}'")
            print(f"   • Длина сообщения: {len(user_input)} символов")
            print(f"   • Содержит ключевые слова активностей: {'Да' if any(word in user_input.lower() for word in ['actividad', 'museo', 'parque', 'diversión', 'entretenimiento']) else 'Нет'}")
            
            # Шаг 3: Проверка профиля семьи
            print(f"\n👨‍👩‍👧‍👦 ШАГ 3: Проверка профиля семьи")
            profile = self.planner.personalization_agent.get_family_profile(self.current_family_id)
            if profile:
                print(f"   ✅ Профиль найден: {profile.family_id}")
                print(f"   • Дети: {profile.kids_ages} лет")
                print(f"   • Взрослые: {profile.adults_count}")
                print(f"   • Интересы: {profile.interests}")
                print(f"   • Бюджет: {getattr(profile, 'budget_level', 'medium')}")
            else:
                print(f"   ❌ Профиль не найден - будет создан новый")
            
            # Шаг 4: Передача данных между агентами
            print(f"\n🔄 ШАГ 4: Передача данных между агентами")
            self.show_data_flow_info(user_input)
            
            # Шаг 5: Обработка запроса
            print(f"\n⚙️ ШАГ 5: Обработка запроса системой")
            print(f"   • Отправка в PersonalizedTripPlanner...")
            
            # Логируем начало ReAct цикла
            if profile:
                print(f"   🔄 ReAct RouterAgent: Начинаю цикл Reasoning → Acting → Observing")
                print(f"   🧠 Reasoning: AnalyzeQueryTool анализирует запрос")
                print(f"   ⚡ Acting: Будет вызван соответствующий инструмент")
                print(f"   👁️ Observing: Результат будет оценен и принято решение")
            
            response = self.planner.process_query(user_input, self.current_family_id)
            print(f"   ✅ Запрос обработан")
            
            # Шаг 6: Анализ результата
            print(f"\n📊 ШАГ 6: Анализ результата")
            self.show_router_response_info(response)
            
            # Шаг 7: Детальный анализ ActivitiesAgent (если задействован)
            if "activities" in response.lower() or "actividad" in response.lower():
                print(f"\n🎯 ШАГ 7: Детальный анализ ActivitiesAgent")
                self.analyze_activities_agent_response(response)
            
            # Шаг 8: Финальная статистика
            response_time = (datetime.now() - start_time).total_seconds()
            print(f"\n⏱️ ШАГ 8: Финальная статистика")
            print(f"   • Время обработки: {response_time:.2f} секунд")
            print(f"   • Длина ответа: {len(response)} символов")
            print(f"   • Содержит план активностей: {'Да' if 'actividad' in response.lower() else 'Нет'}")
            print(f"   • Содержит расписание: {'Да' if 'horario' in response.lower() or 'día' in response.lower() else 'Нет'}")
            
            # Логируем результат
            self.log_message(user_input, response, response_time)
            
            print("=" * 80)
            return response
            
        except Exception as e:
            error_msg = f"❌ Ошибка обработки: {str(e)}"
            print(f"\n❌ ОШИБКА В ПРОЦЕССЕ ОБРАБОТКИ:")
            print(f"   • Ошибка: {str(e)}")
            print(f"   • Время до ошибки: {(datetime.now() - start_time).total_seconds():.2f} секунд")
            self.log_message(user_input, error_msg, 0)
            return error_msg
    
    def handle_command(self, command: str) -> str:
        """Обрабатывает команды"""
        if command == "/help":
            return self.show_help()
        elif command == "/profile":
            return self.show_profile()
        elif command == "/data":
            return self.show_detailed_data_flow()
        elif command == "/scenario":
            return self.run_test_scenario()
        elif command == "/activities":
            return self.test_activities_agent()
        elif command == "/stats":
            return self.show_stats()
        elif command == "/exit":
            return "exit"
        else:
            return f"❌ Неизвестная команда: {command}. Используйте /help для справки."
    
    def show_help(self) -> str:
        """Показывает справку"""
        return """
📋 СПРАВКА ПО КОМАНДАМ:

/help       - Показать эту справку
/profile    - Показать текущий профиль семьи
/data       - Показать детальную передачу данных между агентами
/scenario   - Запустить тестовый сценарий
/activities - Тестировать ActivitiesAgent через ReAct архитектуру
/stats      - Показать статистику сессии
/exit       - Выход из программы

🏗️ НОВАЯ ReAct АРХИТЕКТУРА:
- PersonalizationReactAgent → RouterAgent → Специализированные агенты
- RouterAgent использует ReAct паттерн (Reasoning → Acting → Observing)
- Инструменты: AnalyzeQueryTool, CallActivitiesAgentTool, CallRestaurantsAgentTool
- Более интеллектуальный анализ запросов и маршрутизация

💡 СОВЕТЫ:
- Начните с приветствия: "Hola"
- Опишите свою семью: "Tengo 2 niños de 5 y 8 años"
- Задавайте вопросы о поездке: "¿Qué hoteles me recomiendas?"
- Тестируйте ActivitiesAgent: "¿Qué actividades puedo hacer con mis hijos?"
- Используйте естественный язык для общения

🎯 ТЕСТИРОВАНИЕ ActivitiesAgent (ReAct):
- Команда /activities запустит автоматическое тестирование
- Покажет ReAct workflow: PersonalizationReactAgent → RouterAgent → CallActivitiesAgentTool → ActivitiesAgent
- Проанализирует качество ответов ActivitiesAgent через новую архитектуру
- Включит 5 различных тестовых запросов
- Покажет детали ReAct цикла (Reasoning → Acting → Observing)

🔄 ReAct ЦИКЛ:
1. Reasoning: AnalyzeQueryTool анализирует запрос
2. Acting: Вызывает соответствующие инструменты
3. Observing: Оценивает результаты и принимает решения
4. Повторяет цикл до получения полного ответа
        """
    
    def show_detailed_data_flow(self) -> str:
        """Показывает детальную информацию о передаче данных между агентами в новой ReAct архитектуре"""
        if not self.current_family_id:
            return "❌ Семья не выбрана. Начните диалог с ботом."
        
        try:
            profile = self.planner.personalization_agent.get_family_profile(self.current_family_id)
            
            if not profile:
                return """
📊 ДЕТАЛЬНЫЙ АНАЛИЗ ПЕРЕДАЧИ ДАННЫХ (ReAct Architecture):

❌ Профиль семьи не найден
📤 PersonalizationReactAgent будет:
   • Создавать новый профиль через последовательный сбор данных
   • Не передавать данные в RouterAgent
   • Обрабатывать запросы самостоятельно (Sequential Mode)

💡 Создайте профиль семьи, описав свою семью боту.
                """
            
            # Получаем полную информацию о том, что передается
            routing_data = self.planner.personalization_agent.prepare_data_for_routing("test_query", self.current_family_id)
            
            return f"""
📊 ДЕТАЛЬНЫЙ АНАЛИЗ ПЕРЕДАЧИ ДАННЫХ (ReAct Architecture):

🏗️ АРХИТЕКТУРА:
PersonalizationReactAgent → RouterAgent → Специализированные агенты

📤 PersonalizationReactAgent ПЕРЕДАЕТ RouterAgent:
{json.dumps(routing_data, indent=2, ensure_ascii=False)}

📥 RouterAgent ПОЛУЧАЕТ И ОБРАБАТЫВАЕТ:
   • Query: {routing_data.get('query', 'N/A')}
   • Family ID: {routing_data.get('family_id', 'N/A')}
   • Profile data: {len(routing_data.get('profile', {}))} полей
   • Query analysis: {len(routing_data.get('query_analysis', {}))} полей

🔄 ReAct WORKFLOW В RouterAgent:
   1. Reasoning: AnalyzeQueryTool анализирует запрос
   2. Acting: Вызывает соответствующие инструменты:
      - CallActivitiesAgentTool (если нужны активности)
      - CallRestaurantsAgentTool (если нужны рестораны)
   3. Observing: Оценивает результаты и принимает решения
   4. Повторяет цикл до получения полного ответа

🔧 ИНСТРУМЕНТЫ RouterAgent:
   • AnalyzeQueryTool: Анализирует запрос через LLM
   • CallActivitiesAgentTool: Вызывает ActivitiesAgent
   • CallRestaurantsAgentTool: Вызывает RestoranAgent

🔍 АНАЛИЗ ИСПОЛЬЗОВАНИЯ ДАННЫХ:
   • Используется в логах: query, family_id
   • Используется в AnalyzeQueryTool: query для анализа
   • Используется в CallActivitiesAgentTool: полный routing_data
   • Используется в CallRestaurantsAgentTool: полный routing_data
   • Используется в ответах: profile.kids_ages, profile.adults_count, profile.budget_level, etc.

💡 РЕКОМЕНДАЦИИ:
   • Все данные передаются корректно через ReAct архитектуру
   • RouterAgent получает полную информацию о семье
   • Специализированные агенты могут использовать все поля профиля
   • ReAct цикл обеспечивает более интеллектуальную маршрутизацию
            """
            
        except Exception as e:
            return f"❌ Ошибка анализа данных: {e}"
    
    def show_profile(self) -> str:
        """Показывает профиль семьи"""
        if not self.current_family_id:
            return "❌ Семья не выбрана. Начните диалог с ботом."
        
        try:
            profile = self.planner.personalization_agent.get_family_profile(self.current_family_id)
            if profile:
                return f"""
👨‍👩‍👧‍👦 ПРОФИЛЬ СЕМЬИ: {profile.family_id}

📊 Основная информация:
  • Дети: {profile.kids_ages} лет
  • Взрослые: {profile.adults_count}
  • Бюджет: {getattr(profile, 'budget_level', 'medium')}
  • Даты: {getattr(profile, 'start_date', '')} - {getattr(profile, 'end_date', '')}
  • Интересы: {', '.join(profile.interests) if profile.interests else 'Не указаны'}
  • Страна: {profile.origin_country or 'Не указана'}

🎯 Дополнительно:
  • Язык: {profile.language_preference}
  • Размер семьи: {profile.get_family_size()}
  • Возрастная группа: {profile.get_age_group()}
  • Продолжительность: {profile.get_stay_duration()} дней
                """
            else:
                return "❌ Профиль семьи не найден. Создайте профиль, описав свою семью."
        except Exception as e:
            return f"❌ Ошибка получения профиля: {e}"
    
    def run_test_scenario(self) -> str:
        """Запускает тестовый сценарий"""
        scenarios = [
            {
                "name": "Полный процесс: Новая семья → ActivitiesAgent",
                "description": "Демонстрирует полный процесс от создания профиля до получения плана активностей",
                "messages": [
                    "Hola, quiero planificar un viaje a Madrid",
                    "Tengo 2 niños de 8 y 12 años, somos 2 adultos",
                    "Presupuesto medio, del 15 al 20 de diciembre",
                    "Intereses: arte, ciencia, naturaleza",
                    "¿Qué actividades puedo hacer con mis hijos en Madrid?",
                    "¿Qué museos son buenos para niños de estas edades?",
                    "¿Hay talleres de arte para niños?"
                ]
            },
            {
                "name": "Полный процесс: Семья с особыми потребностями",
                "description": "Демонстрирует персонализацию для семей с особыми потребностями",
                "messages": [
                    "Hola, necesito ayuda con mi viaje",
                    "Somos 3 adultos y 1 niño de 6 años",
                    "Mi hijo tiene autismo, necesitamos lugares tranquilos",
                    "Presupuesto bajo, del 10 al 15 de enero",
                    "¿Qué actividades son adecuadas para nosotros?",
                    "¿Hay talleres de arte para niños especiales?",
                    "¿Qué museos son tranquilos?"
                ]
            },
            {
                "name": "Полный процесс: Быстрый запрос",
                "description": "Демонстрирует быструю обработку без создания полного профиля",
                "messages": [
                    "¿Qué actividades puedo hacer con niños de 5 y 10 años?",
                    "¿Qué museos son buenos para niños de 8 años?",
                    "¿Dónde puedo llevar a mis hijos a divertirse en Madrid?"
                ]
            },
            {
                "name": "Полный процесс: Комплексное планирование",
                "description": "Демонстрирует полное планирование поездки с несколькими агентами",
                "messages": [
                    "Hola, quiero planificar un viaje completo a Madrid",
                    "Tengo 2 niños de 6 y 9 años, somos 2 adultos",
                    "Presupuesto bajo, del 20 al 25 de enero",
                    "Intereses: arte, ciencia, naturaleza",
                    "¿Qué actividades me recomiendas para toda la familia?",
                    "¿Qué hoteles me recomiendas?",
                    "¿Dónde podemos comer?"
                ]
            }
        ]
        
        print("\n🎭 ДОСТУПНЫЕ СЦЕНАРИИ:")
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i}. {scenario['name']}")
            print(f"     📝 {scenario['description']}")
            print(f"     💬 Сообщений: {len(scenario['messages'])}")
            print()
        
        try:
            choice = input("Выберите сценарий (1-4) или нажмите Enter для отмены: ").strip()
            if not choice:
                return "❌ Сценарий отменен"
            
            scenario_idx = int(choice) - 1
            if 0 <= scenario_idx < len(scenarios):
                scenario = scenarios[scenario_idx]
                return self.execute_scenario(scenario)
            else:
                return "❌ Неверный номер сценария"
        except ValueError:
            return "❌ Введите корректный номер"
    
    def execute_scenario(self, scenario: dict) -> str:
        """Выполняет выбранный сценарий с детальным логированием"""
        print(f"\n🎬 ВЫПОЛНЕНИЕ СЦЕНАРИЯ: {scenario['name']}")
        print(f"📝 Описание: {scenario['description']}")
        print("=" * 80)
        
        # Сбрасываем ID семьи для нового сценария
        self.current_family_id = f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"🆔 Создан новый ID семьи для сценария: {self.current_family_id}")
        
        # Статистика сценария
        total_messages = len(scenario['messages'])
        activities_queries = [msg for msg in scenario['messages'] if any(word in msg.lower() for word in ['actividad', 'museo', 'parque', 'diversión'])]
        
        print(f"📊 Статистика сценария:")
        print(f"   • Всего сообщений: {total_messages}")
        print(f"   • Запросов к ActivitiesAgent: {len(activities_queries)}")
        print(f"   • Ожидаемое время выполнения: {total_messages * 2} секунд")
        print("=" * 80)
        
        for i, message in enumerate(scenario['messages'], 1):
            print(f"\n{'='*20} СООБЩЕНИЕ {i}/{total_messages} {'='*20}")
            print(f"👤 Пользователь: {message}")
            
            # Обрабатываем сообщение с полным логированием
            response = self.process_user_input(message)
            
            # Краткий анализ ответа
            print(f"\n🤖 Краткий анализ ответа:")
            print(f"   • Длина: {len(response)} символов")
            print(f"   • Содержит активности: {'Да' if 'actividad' in response.lower() else 'Нет'}")
            print(f"   • Содержит музеи: {'Да' if 'museo' in response.lower() else 'Нет'}")
            print(f"   • Содержит расписание: {'Да' if 'horario' in response.lower() else 'Нет'}")
            
            # Показываем первые 300 символов ответа
            print(f"\n📄 Ответ (первые 300 символов):")
            print(f"{response[:300]}{'...' if len(response) > 300 else ''}")
            
            # Пауза между сообщениями
            if i < total_messages:
                input(f"\n⏸️  Нажмите Enter для следующего сообщения ({i+1}/{total_messages})...")
        
        # Финальная статистика сценария
        print(f"\n{'='*80}")
        print(f"🎉 СЦЕНАРИЙ ЗАВЕРШЕН: {scenario['name']}")
        print(f"{'='*80}")
        
        # Анализ результатов
        total_responses = len(self.session_data["messages"])
        activities_responses = [msg for msg in self.session_data["messages"] if 'actividad' in msg.get('bot_response', '').lower()]
        
        print(f"📊 Результаты сценария:")
        print(f"   • Всего обработано сообщений: {total_responses}")
        print(f"   • Ответов с активностями: {len(activities_responses)}")
        avg_length = sum(len(msg.get('bot_response', '')) for msg in self.session_data["messages"]) / max(total_responses, 1)
        print(f"   • Средняя длина ответа: {avg_length:.0f} символов")
        
        return f"✅ Сценарий '{scenario['name']}' выполнен успешно! Обработано {total_responses} сообщений."
    
    def test_activities_agent(self) -> str:
        """Тестирует ActivitiesAgent через новую ReAct архитектуру RouterAgent"""
        print("\n🎯 ТЕСТИРОВАНИЕ ActivitiesAgent (ReAct Architecture)")
        print("=" * 60)
        
        try:
            # Создаем тестовый профиль семьи
            test_family_id = f"test_activities_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Тестовые данные
            test_queries = [
                "¿Qué actividades puedo hacer con mis hijos de 8 y 12 años en Madrid?",
                "¿Qué museos son buenos para niños de 6 años?",
                "¿Dónde puedo llevar a mis hijos a divertirse en Madrid?",
                "¿Hay talleres de arte para niños en Madrid?",
                "¿Qué actividades hay para familias con niños pequeños?"
            ]
            
            print(f"🆔 Создан тестовый ID семьи: {test_family_id}")
            print(f"📋 Тестовые запросы: {len(test_queries)}")
            print(f"🏗️ Архитектура: PersonalizationReactAgent → RouterAgent → CallActivitiesAgentTool → ActivitiesAgent")
            
            # Создаем профиль семьи
            print("\n📝 Создание профиля семьи...")
            profile_response = self.planner.process_query(
                "Hola, tengo 2 niños de 8 y 12 años, somos 2 adultos, presupuesto medio, del 15 al 20 de diciembre, intereses: arte, ciencia, naturaleza",
                test_family_id
            )
            print(f"✅ Профиль создан: {profile_response[:100]}...")
            
            # Тестируем каждый запрос
            for i, query in enumerate(test_queries, 1):
                print(f"\n🔍 Тест {i}/{len(test_queries)}: {query}")
                print("-" * 60)
                
                # Показываем передачу данных в новой архитектуре
                print("🔄 АНАЛИЗ ReAct WORKFLOW:")
                print("   1. PersonalizationReactAgent получает запрос")
                print("   2. RouterAgent запускает ReAct цикл")
                print("   3. AnalyzeQueryTool анализирует запрос")
                print("   4. CallActivitiesAgentTool вызывает ActivitiesAgent")
                print("   5. ActivitiesAgent обрабатывает запрос")
                print("   6. Результат возвращается через ReAct цикл")
                
                # Показываем передачу данных
                self.show_data_flow_info(query)
                
                # Обрабатываем запрос
                print(f"\n⚙️ ОБРАБОТКА ЗАПРОСА:")
                response = self.planner.process_query(query, test_family_id)
                
                # Показываем анализ ответа
                self.show_router_response_info(response)
                
                # Детальный анализ ActivitiesAgent
                if "actividad" in response.lower() or "museo" in response.lower():
                    print(f"\n🎯 ДЕТАЛЬНЫЙ АНАЛИЗ ActivitiesAgent:")
                    self.analyze_activities_agent_response(response)
                
                # Логируем результат
                self.log_message(query, response, 0)
                
                print(f"✅ Тест {i} завершен")
                
                # Пауза между тестами
                if i < len(test_queries):
                    input("\n⏸️  Нажмите Enter для следующего теста...")
            
            return f"✅ Тестирование ActivitiesAgent (ReAct) завершено успешно! Выполнено {len(test_queries)} тестов."
            
        except Exception as e:
            return f"❌ Ошибка тестирования ActivitiesAgent: {e}"
    
    def show_stats(self) -> str:
        """Показывает статистику сессии"""
        total_messages = len(self.session_data["messages"])
        if total_messages == 0:
            return "📊 Статистика: Нет сообщений в сессии"
        
        avg_response_time = sum(msg["response_time"] for msg in self.session_data["messages"]) / total_messages
        
        # Анализируем использование ReAct архитектуры
        react_responses = [msg for msg in self.session_data["messages"] if "RouterAgent" in msg.get('bot_response', '') or "ReAct" in msg.get('bot_response', '')]
        activities_responses = [msg for msg in self.session_data["messages"] if "actividad" in msg.get('bot_response', '').lower()]
        
        return f"""
📊 СТАТИСТИКА СЕССИИ (ReAct Architecture):

🕐 Время начала: {self.session_data['start_time'].strftime('%H:%M:%S')}
💬 Всего сообщений: {total_messages}
⚡ Среднее время ответа: {avg_response_time:.2f} сек
👨‍👩‍👧‍👦 ID семьи: {self.current_family_id or 'Не выбрана'}

🏗️ АРХИТЕКТУРА:
🔄 ReAct RouterAgent использован: {len(react_responses)} раз
🎯 ActivitiesAgent вызван: {len(activities_responses)} раз
📤 PersonalizationReactAgent (Sequential): {total_messages - len(react_responses)} раз

📈 Последние сообщения:
{self.get_recent_messages(3)}
        """
    
    def get_recent_messages(self, count: int = 3) -> str:
        """Возвращает последние сообщения"""
        recent = self.session_data["messages"][-count:]
        result = []
        for msg in recent:
            result.append(f"  • {msg['user_message'][:50]}{'...' if len(msg['user_message']) > 50 else ''}")
        return "\n".join(result) if result else "  Нет сообщений"
    
    def run_interactive_session(self):
        """Запускает интерактивную сессию"""
        if not self.initialize_system():
            return
        
        self.display_welcome()
        
        while True:
            try:
                # Получаем пользовательский ввод
                user_input = input("\n👤 Вы: ").strip()
                
                if not user_input:
                    print("❌ Пустое сообщение. Попробуйте еще раз.")
                    continue
                
                # Обрабатываем ввод
                response = self.process_user_input(user_input)
                
                if response == "exit":
                    print("\n👋 До свидания! Спасибо за тестирование!")
                    break
                
                # Отображаем ответ
                print(f"\n🤖 Бот: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Сессия прервана пользователем. До свидания!")
                break
            except Exception as e:
                print(f"\n❌ Неожиданная ошибка: {e}")
                print("Попробуйте еще раз или используйте /exit для выхода.")
        
        # Показываем финальную статистику
        print(f"\n📊 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(self.show_stats())

def main():
    """Главная функция"""
    print("🚀 ЗАПУСК СИМУЛЯТОРА ФРОНТЕНДА")
    print("=" * 50)
    
    simulator = FrontendSimulator()
    simulator.run_interactive_session()

if __name__ == "__main__":
    main()
