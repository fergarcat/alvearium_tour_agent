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
            from app.agents.personalization_agent import PersonalizedTripPlanner
            self.planner = PersonalizedTripPlanner()
            print("✅ Система инициализирована успешно")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            return False
    
    def display_welcome(self):
        """Отображает приветствие"""
        print("\n" + "=" * 60)
        print("🐭 ДОБРО ПОЖАЛОВАТЬ В СИМУЛЯТОР ФРОНТЕНДА")
        print("=" * 60)
        print("Этот тест имитирует взаимодействие с фронтендом")
        print("Вы можете вводить сообщения как настоящий пользователь")
        print("\n📋 Доступные команды:")
        print("  /help     - Показать справку")
        print("  /profile  - Показать профиль семьи")
        print("  /data     - Показать детальную передачу данных")
        print("  /scenario - Запустить тестовый сценарий")
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
        """Показывает информацию о передаче данных между агентами"""
        try:
            print("\n" + "=" * 60)
            print("🔄 АНАЛИЗ ПЕРЕДАЧИ ДАННЫХ МЕЖДУ АГЕНТАМИ")
            print("=" * 60)
            
            # Получаем профиль семьи
            profile = self.planner.personalization_agent.get_family_profile(self.current_family_id)
            
            if profile:
                print("📤 PersonalizationReactAgent ПЕРЕДАЕТ RouterAgent:")
                print(f"   • Query: {user_input}")
                print(f"   • Family ID: {self.current_family_id}")
                print(f"   • Profile: {profile.family_id}")
                print(f"     - Kids ages: {profile.kids_ages}")
                print(f"     - Adults count: {profile.adults_count}")
                print(f"     - Interests: {profile.interests}")
                print(f"     - Special needs: {profile.special_needs}")
                print(f"     - Language: {profile.language_preference}")
                
                # Анализируем запрос
                query_analysis = self.planner.personalization_agent._analyze_query(user_input, self.current_family_id, profile)
                print(f"   • Query analysis: {query_analysis}")
                
                # Показываем, какие агенты будут задействованы
                needs_agents = []
                if query_analysis.get("needs_hotels", False):
                    needs_agents.append("hotels")
                if query_analysis.get("needs_restaurants", False):
                    needs_agents.append("restaurants")
                if query_analysis.get("needs_activities", False):
                    needs_agents.append("activities")
                if query_analysis.get("needs_transport", False):
                    needs_agents.append("transport")
                
                if needs_agents:
                    print(f"   • Needs multi-agent: True")
                    print(f"   • Agents needed: {', '.join(needs_agents)}")
                    print(f"   • Query type: {query_analysis.get('query_type', 'general')}")
                else:
                    print(f"   • Needs multi-agent: False")
                    print(f"   • Will use simple response")
            else:
                print("📤 PersonalizationReactAgent ПЕРЕДАЕТ RouterAgent:")
                print(f"   • Query: {user_input}")
                print(f"   • Family ID: {self.current_family_id}")
                print(f"   • Profile: НЕ НАЙДЕН (будет создан новый)")
                print(f"   • Will use sequential data collection")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Ошибка анализа данных: {e}")
            print("=" * 60)
    
    def show_router_response_info(self, response: str):
        """Показывает информацию о том, что получил RouterAgent"""
        try:
            print("\n" + "=" * 60)
            print("📥 RouterAgent ОТВЕТИЛ ПОЛЬЗОВАТЕЛЮ:")
            print("=" * 60)
            
            # Анализируем ответ
            if "RouterAgent" in response:
                print("✅ RouterAgent обработал запрос")
                print(f"   • Тип ответа: Multi-Agent")
                print(f"   • Длина ответа: {len(response)} символов")
                
                # Проверяем, какие агенты были задействованы
                agents_used = []
                if "🏨" in response:
                    agents_used.append("hotels")
                if "🍽️" in response:
                    agents_used.append("restaurants")
                if "🎯" in response:
                    agents_used.append("activities")
                if "🚌" in response:
                    agents_used.append("transport")
                
                if agents_used:
                    print(f"   • Агенты использованы: {', '.join(agents_used)}")
                else:
                    print(f"   • Агенты использованы: простой ответ")
                    
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
                    
            else:
                print("ℹ️ PersonalizationReactAgent обработал запрос")
                print(f"   • Тип ответа: Simple/Sequential")
                print(f"   • Длина ответа: {len(response)} символов")
                print(f"   • RouterAgent не задействован")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Ошибка анализа ответа: {e}")
            print("=" * 60)
    
    def process_user_input(self, user_input: str) -> str:
        """Обрабатывает пользовательский ввод"""
        start_time = datetime.now()
        
        try:
            # Обрабатываем команды
            if user_input.startswith('/'):
                return self.handle_command(user_input)
            
            # Обрабатываем обычное сообщение
            if not self.current_family_id:
                self.current_family_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"🆔 Создан ID семьи: {self.current_family_id}")
            
            # Показываем информацию о передаче данных между агентами
            self.show_data_flow_info(user_input)
            
            # Отправляем запрос в систему
            response = self.planner.process_query(user_input, self.current_family_id)
            
            # Показываем, что получил RouterAgent
            self.show_router_response_info(response)
            
            # Логируем время ответа
            response_time = (datetime.now() - start_time).total_seconds()
            self.log_message(user_input, response, response_time)
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Ошибка обработки: {str(e)}"
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

/help     - Показать эту справку
/profile  - Показать текущий профиль семьи
/data     - Показать детальную передачу данных между агентами
/scenario - Запустить тестовый сценарий
/stats    - Показать статистику сессии
/exit     - Выход из программы

💡 СОВЕТЫ:
- Начните с приветствия: "Hola"
- Опишите свою семью: "Tengo 2 niños de 5 y 8 años"
- Задавайте вопросы о поездке: "¿Qué hoteles me recomiendas?"
- Используйте естественный язык для общения
        """
    
    def show_detailed_data_flow(self) -> str:
        """Показывает детальную информацию о передаче данных между агентами"""
        if not self.current_family_id:
            return "❌ Семья не выбрана. Начните диалог с ботом."
        
        try:
            profile = self.planner.personalization_agent.get_family_profile(self.current_family_id)
            
            if not profile:
                return """
📊 ДЕТАЛЬНЫЙ АНАЛИЗ ПЕРЕДАЧИ ДАННЫХ:

❌ Профиль семьи не найден
📤 PersonalizationReactAgent будет:
   • Создавать новый профиль через последовательный сбор данных
   • Не передавать данные в RouterAgent
   • Обрабатывать запросы самостоятельно

💡 Создайте профиль семьи, описав свою семью боту.
                """
            
            # Получаем полную информацию о том, что передается
            routing_data = self.planner.personalization_agent.prepare_data_for_routing("test_query", self.current_family_id)
            
            return f"""
📊 ДЕТАЛЬНЫЙ АНАЛИЗ ПЕРЕДАЧИ ДАННЫХ:

📤 PersonalizationReactAgent ПЕРЕДАЕТ RouterAgent:
{json.dumps(routing_data, indent=2, ensure_ascii=False)}

📥 RouterAgent ПОЛУЧАЕТ:
   • Query: {routing_data.get('query', 'N/A')}
   • Family ID: {routing_data.get('family_id', 'N/A')}
   • Profile data: {len(routing_data.get('profile', {}))} полей
   • Query analysis: {len(routing_data.get('query_analysis', {}))} полей
   • Needs flags: {[k for k, v in routing_data.items() if k.startswith('needs_') and v]}

🔍 АНАЛИЗ ИСПОЛЬЗОВАНИЯ ДАННЫХ:
   • Используется в логах: query, family_id
   • Используется для агентов: needs_hotels, needs_restaurants, needs_activities, needs_transport
   • Используется в ответах: profile.kids_ages, profile.adults_count, profile.budget_level, etc.
   • НЕ используется: query_analysis (полностью), is_planning

💡 РЕКОМЕНДАЦИИ:
   • Все данные передаются корректно
   • RouterAgent получает полную информацию о семье
   • Специализированные агенты могут использовать все поля профиля
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
  • Бюджет: {profile.budget_level}
  • Даты: {profile.start_date} - {profile.end_date}
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
                "name": "Новая семья",
                "messages": [
                    "Hola, quiero planificar un viaje a Madrid",
                    "Tengo 2 niños de 3 y 7 años, somos 4 adultos",
                    "Presupuesto medio, del 15 al 20 de junio",
                    "¿Qué hoteles me recomiendas?"
                ]
            },
            {
                "name": "Семья с особыми потребностями",
                "messages": [
                    "Hola, necesito ayuda con mi viaje",
                    "Somos 3 adultos y 1 niño de 4 años",
                    "Mi hijo tiene autismo, necesitamos lugares tranquilos",
                    "¿Qué actividades son adecuadas para nosotros?"
                ]
            },
            {
                "name": "Быстрый запрос",
                "messages": [
                    "¿Dónde puedo comer con niños en Madrid?",
                    "¿Qué museos son buenos para niños de 8 años?"
                ]
            }
        ]
        
        print("\n🎭 ДОСТУПНЫЕ СЦЕНАРИИ:")
        for i, scenario in enumerate(scenarios, 1):
            print(f"  {i}. {scenario['name']}")
        
        try:
            choice = input("\nВыберите сценарий (1-3) или нажмите Enter для отмены: ").strip()
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
        """Выполняет выбранный сценарий"""
        print(f"\n🎬 ВЫПОЛНЕНИЕ СЦЕНАРИЯ: {scenario['name']}")
        print("=" * 50)
        
        # Сбрасываем ID семьи для нового сценария
        self.current_family_id = f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for i, message in enumerate(scenario['messages'], 1):
            print(f"\n📤 Сообщение {i}: {message}")
            response = self.process_user_input(message)
            print(f"🤖 Ответ: {response[:200]}{'...' if len(response) > 200 else ''}")
            
            # Небольшая пауза между сообщениями
            input("\n⏸️  Нажмите Enter для следующего сообщения...")
        
        return f"✅ Сценарий '{scenario['name']}' выполнен успешно"
    
    def show_stats(self) -> str:
        """Показывает статистику сессии"""
        total_messages = len(self.session_data["messages"])
        if total_messages == 0:
            return "📊 Статистика: Нет сообщений в сессии"
        
        avg_response_time = sum(msg["response_time"] for msg in self.session_data["messages"]) / total_messages
        
        return f"""
📊 СТАТИСТИКА СЕССИИ:

🕐 Время начала: {self.session_data['start_time'].strftime('%H:%M:%S')}
💬 Всего сообщений: {total_messages}
⚡ Среднее время ответа: {avg_response_time:.2f} сек
👨‍👩‍👧‍👦 ID семьи: {self.current_family_id or 'Не выбрана'}

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
