const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

// API клиент для работы с чатботом Ratoncito Pérez
class ChatAPI {
  constructor() {
    this.baseURL = BASE_URL;
  }

  // Отправляет сообщение в чат
  async sendChatMessage(message, familyId = 'default', conversationId = null) {
    try {
      const response = await fetch(`${this.baseURL}/agents/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify({
          message,
          family_id: familyId,
          conversation_id: conversationId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending chat message:', error);
      throw error;
    }
  }

  // Начинает новый разговор
  async startNewConversation(familyId = 'default') {
    try {
      const response = await fetch(`${this.baseURL}/agents/conversations/start`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify({
          family_id: familyId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error starting conversation:', error);
      throw error;
    }
  }

  // Получает статус разговора
  async getConversationStatus(conversationId, familyId = 'default') {
    try {
      const response = await fetch(`${this.baseURL}/agents/conversations/${conversationId}/status?family_id=${familyId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation status:', error);
      throw error;
    }
  }

  // Удаляет разговор
  async deleteConversation(conversationId, familyId = 'default') {
    try {
      const response = await fetch(`${this.baseURL}/agents/conversations/${conversationId}?family_id=${familyId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }

  // Получает список всех разговоров
  async listConversations() {
    try {
      const response = await fetch(`${this.baseURL}/agents/conversations`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error listing conversations:', error);
      throw error;
    }
  }

  // Проверяет здоровье API
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}/health/`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

// Создаем экземпляр API клиента
const chatAPI = new ChatAPI();

// Экспортируем для использования в компонентах
export default chatAPI;

// Также экспортируем отдельные функции для обратной совместимости
export const {
  sendChatMessage,
  startNewConversation,
  getConversationStatus,
  deleteConversation,
  listConversations,
  checkHealth
} = chatAPI;