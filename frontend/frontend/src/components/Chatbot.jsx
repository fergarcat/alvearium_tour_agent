import { useState, useEffect } from 'react';
import { useImmer } from 'use-immer';
import { FiMessageCircle } from 'react-icons/fi';
import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';
import chatAPI from '../api.js';

function Chatbot() {
  const [conversationId, setConversationId] = useState(null);
  const [familyId] = useState('default'); // Можно сделать динамическим
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState(null);

  const isLoading = messages.length && messages[messages.length - 1].loading;

  // Инициализация чата при первом запуске
  useEffect(() => {
    initializeChat();
  }, []);

  async function initializeChat() {
    try {
      setError(null);
      
      // Проверяем здоровье API
      const healthResponse = await chatAPI.checkHealth();
      
      // Начинаем новый разговор
      const response = await chatAPI.startNewConversation(familyId);
      setConversationId(response.conversation_id);
      
      // Отправляем пустое сообщение для инициализации
      const initResponse = await chatAPI.sendChatMessage('', familyId, response.conversation_id);
      
      // Добавляем приветственное сообщение
      setMessages(draft => [{
        role: 'assistant',
        content: initResponse.response,
        timestamp: new Date(initResponse.timestamp),
        isCollectingData: initResponse.is_collecting_data,
        dataCollectionStep: initResponse.data_collection_step,
        profileComplete: initResponse.profile_complete
      }]);
      
      setIsInitialized(true);
    } catch (error) {
      console.error('Error initializing chat:', error);
      setError('Ошибка подключения к серверу. Проверьте, что бэкенд запущен.');
    }
  }

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    
    if (!trimmedMessage || isLoading || !isInitialized) {
      return;
    }

    setError(null);

    // Добавляем сообщение пользователя
    setMessages(draft => [...draft, {
      role: 'user',
      content: trimmedMessage,
      timestamp: new Date()
    }]);

    // Добавляем сообщение загрузки
    setMessages(draft => [...draft, {
      role: 'assistant',
      content: '',
      loading: true,
      timestamp: new Date()
    }]);

    setNewMessage('');

    try {
      // Отправляем сообщение в API
      const response = await chatAPI.sendChatMessage(
        trimmedMessage, 
        familyId, 
        conversationId
      );

      // Обновляем последнее сообщение с ответом
      setMessages(draft => {
        const lastMessage = draft[draft.length - 1];
        lastMessage.loading = false;
        lastMessage.content = response.response;
        lastMessage.timestamp = new Date(response.timestamp);
        lastMessage.isCollectingData = response.is_collecting_data;
        lastMessage.dataCollectionStep = response.data_collection_step;
        lastMessage.profileComplete = response.profile_complete;
      });

      console.log('✅ Message updated successfully');

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Обновляем сообщение с ошибкой
      setMessages(draft => {
        const lastMessage = draft[draft.length - 1];
        lastMessage.loading = false;
        lastMessage.content = 'Извините, произошла ошибка при отправке сообщения. Попробуйте еще раз.';
        lastMessage.error = true;
      });
      
      setError('Ошибка отправки сообщения');
    }
  }

  // Если есть ошибка инициализации, показываем сообщение об ошибке
  if (error && !isInitialized) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'white',
        padding: '32px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px', color: '#1f2937' }}>Ошибка подключения</h2>
          <p style={{ color: '#6b7280', marginBottom: '16px' }}>{error}</p>
          <button 
            onClick={initializeChat}
            style={{
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  // Если чат еще не инициализирован, показываем загрузку
  if (!isInitialized) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'white'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '2px solid #e5e7eb',
            borderTop: '2px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#6b7280' }}>Подключение к Ratoncito Pérez...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      position: 'relative',
      backgroundColor: 'white'
    }}>
      {/* Header con Ratoncito Pérez */}
      <div style={{
        background: 'linear-gradient(135deg, #282524 0%, #dea142 50%, #f8d9a4 100%)',
        color: 'white',
        padding: '24px',
        position: 'relative'
      }}>
        {/* Close button */}
        <button style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          background: 'none',
          border: 'none',
          color: 'rgba(255,255,255,0.8)',
          fontSize: '20px',
          cursor: 'pointer'
        }}>×</button>
        
        {/* Logo del Ratoncito */}
        <img 
          src="/logo-raton.png" 
          alt="Ratoncito Pérez" 
          width={100} 
          height={100}
          style={{ marginBottom: '16px' }}
        />
        
        {/* Title */}
        <h1 style={{
          fontSize: '24px',
          fontWeight: '600',
          marginBottom: '8px',
          margin: 0
        }}>Ratoncito Pérez</h1>
        
        {/* Description */}
        <p style={{
          fontSize: '12px',
          opacity: 0.9,
          lineHeight: '1.4',
          margin: 0,
          maxWidth: '280px'
        }}>
          Hola! Soy el Ratoncito Pérez, tu guía personal de Madrid. ¿En qué puedo ayudarte hoy?
        </p>
      </div>

      {/* Сообщение об ошибке */}
      {error && (
        <div style={{
          backgroundColor: '#fef2f2',
          borderLeft: '4px solid #f87171',
          padding: '16px',
          margin: '16px'
        }}>
          <p style={{ fontSize: '14px', color: '#b91c1c' }}>{error}</p>
        </div>
      )}

      {/* Área de mensajes */}
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
      />
      
      {/* Input de mensaje */}
      <ChatInput
        newMessage={newMessage}
        isLoading={isLoading}
        setNewMessage={setNewMessage}
        submitNewMessage={submitNewMessage}
        disabled={!isInitialized}
      />
      
      {/* Botón flotante */}
      <div style={{ position: 'absolute', bottom: '20px', right: '20px' }}>
        <button style={{
          width: '48px',
          height: '48px',
          backgroundColor: '#dea142',
          color: 'white',
          borderRadius: '50%',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(222, 161, 66, 0.4)'
        }}>
          <FiMessageCircle size={20} />
        </button>
      </div>
    </div>
  );
}

export default Chatbot;
