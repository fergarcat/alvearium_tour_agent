#!/usr/bin/env python3
"""
Тестовый скрипт для проверки правильной логики чата
"""

import requests
import json
import time
from typing import Dict, Any

# Конфигурация
BASE_URL = "http://127.0.0.1:8001/api/v1"
FAMILY_ID = "test_family_123"

def test_conversation_flow():
    """Тестирует полный поток разговора"""
    
    print("🧪 Тестирование правильной логики чата")
    print("=" * 50)
    
    # 1. Начинаем новый разговор
    print("\n1️⃣ Начинаем новый разговор...")
    response = requests.post(f"{BASE_URL}/agents/conversations/start", 
                           json={"family_id": FAMILY_ID})
    
    if response.status_code != 200:
        print(f"❌ Ошибка начала разговора: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    conversation_id = data["conversation_id"]
    print(f"✅ Разговор начат: {conversation_id}")
    
    # 2. Первое сообщение (пустое) - должно начать сбор данных
    print("\n2️⃣ Отправляем пустое сообщение (инициализация)...")
    response = send_chat_message("", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"📝 Текущий шаг: {response['data_collection_step']}")
    
    # 3. Отвечаем на вопрос о детях
    print("\n3️⃣ Отвечаем на вопрос о детях...")
    response = send_chat_message("Tengo 2 niños de 5 y 8 años", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"📝 Текущий шаг: {response['data_collection_step']}")
    
    # 4. Отвечаем на вопрос о взрослых
    print("\n4️⃣ Отвечаем на вопрос о взрослых...")
    response = send_chat_message("Somos 2 adultos", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"📝 Текущий шаг: {response['data_collection_step']}")
    
    # 5. Отвечаем на вопрос о бюджете
    print("\n5️⃣ Отвечаем на вопрос о бюджете...")
    response = send_chat_message("Presupuesto medio", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"📝 Текущий шаг: {response['data_collection_step']}")
    
    # 6. Отвечаем на вопрос о датах
    print("\n6️⃣ Отвечаем на вопрос о датах...")
    response = send_chat_message("Del 15 al 20 de junio", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"📝 Текущий шаг: {response['data_collection_step']}")
    
    # 7. Отвечаем на вопрос об интересах
    print("\n7️⃣ Отвечаем на вопрос об интересах...")
    response = send_chat_message("Museos, parques y comida", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"📝 Текущий шаг: {response['data_collection_step']}")
    
    # 8. Отвечаем на вопрос о стране
    print("\n8️⃣ Отвечаем на вопрос о стране...")
    response = send_chat_message("España", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"📝 Текущий шаг: {response['data_collection_step']}")
    
    # 9. Отвечаем на вопрос об особых потребностях
    print("\n9️⃣ Отвечаем на вопрос об особых потребностях...")
    response = send_chat_message("No, todo normal", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"📝 Текущий шаг: {response['data_collection_step']}")
    print(f"✅ Профиль собран: {response['profile_complete']}")
    
    # 10. Проверяем статус разговора
    print("\n🔟 Проверяем статус разговора...")
    status_response = requests.get(f"{BASE_URL}/agents/conversations/{conversation_id}/status",
                                 params={"family_id": FAMILY_ID})
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"📊 Статус разговора:")
        print(f"   - Текущий шаг: {status_data['current_step']}")
        print(f"   - Сбор данных: {status_data['is_collecting']}")
        print(f"   - Профиль собран: {status_data['profile_complete']}")
        print(f"   - Собранные поля: {status_data['collected_fields']}")
    
    # 11. Тестируем обычный чат после сбора профиля
    print("\n1️⃣1️⃣ Тестируем обычный чат...")
    response = send_chat_message("¿Qué hoteles me recomiendas?", conversation_id, FAMILY_ID)
    print(f"🤖 Ответ: {response['response'][:100]}...")
    print(f"📊 Сбор данных: {response['is_collecting_data']}")
    print(f"✅ Профиль собран: {response['profile_complete']}")
    
    print("\n🎉 Тест завершен!")

def send_chat_message(message: str, conversation_id: str, family_id: str) -> Dict[str, Any]:
    """Отправляет сообщение в чат"""
    try:
        response = requests.post(f"{BASE_URL}/agents/chat", 
                               json={
                                   "message": message,
                                   "family_id": family_id,
                                   "conversation_id": conversation_id
                               })
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка отправки сообщения: {response.status_code}")
            print(response.text)
            return {}
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {}

def test_error_handling():
    """Тестирует обработку ошибок"""
    
    print("\n🧪 Тестирование обработки ошибок")
    print("=" * 50)
    
    # Тест с неверным conversation_id
    print("\n1️⃣ Тест с неверным conversation_id...")
    response = send_chat_message("Hola", "invalid_conversation", FAMILY_ID)
    print(f"🤖 Ответ: {response.get('response', 'No response')[:100]}...")
    
    # Тест с некорректным ответом
    print("\n2️⃣ Тест с некорректным ответом...")
    response = requests.post(f"{BASE_URL}/agents/conversations/start", 
                           json={"family_id": "error_test"})
    
    if response.status_code == 200:
        conversation_id = response.json()["conversation_id"]
        
        # Отправляем пустое сообщение для начала сбора
        send_chat_message("", conversation_id, "error_test")
        
        # Отправляем некорректный ответ
        response = send_chat_message("asdfghjkl", conversation_id, "error_test")
        print(f"🤖 Ответ на некорректный ввод: {response.get('response', 'No response')[:100]}...")

if __name__ == "__main__":
    print("🚀 Запуск тестов правильной логики чата")
    print("Убедитесь, что backend запущен на http://localhost:8000")
    print()
    
    try:
        # Проверяем доступность API
        health_response = requests.get(f"{BASE_URL}/health/")
        if health_response.status_code != 200:
            print("❌ Backend недоступен. Запустите: cd app && python main.py")
            print(f"Status: {health_response.status_code}")
            print(f"Response: {health_response.text}")
            exit(1)
        
        print("✅ Backend доступен")
        
        # Запускаем тесты
        test_conversation_flow()
        test_error_handling()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Тесты прерваны пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка выполнения тестов: {e}")
