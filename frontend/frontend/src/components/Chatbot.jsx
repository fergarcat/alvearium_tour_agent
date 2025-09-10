import { useState } from 'react';
import { useImmer } from 'use-immer';
import { FiMessageCircle } from 'react-icons/fi';
import ChatMessages from './ChatMessages';
import ChatInput from './ChatInput';

function Chatbot() {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useImmer([
    // Mensajes de ejemplo para mostrar el diseño
    {
      role: 'user',
      content: 'Hello, how are you doing?',
      timestamp: new Date(Date.now() - 60000), // Hace 1 minuto
    },
    {
      role: 'assistant',
      content: "I'm doing well, thank you! How can I help you today?",
      timestamp: new Date(Date.now() - 30000), // Hace 30 segundos
    },
    {
      role: 'user',
      content: 'I have a question about the return policy for a product I purchased.',
      timestamp: new Date(Date.now() - 10000), // Hace 10 segundos
    }
  ]);
  const [newMessage, setNewMessage] = useState('');

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    // Agregar mensaje del usuario
    setMessages(draft => [...draft, {
      role: 'user',
      content: trimmedMessage,
      timestamp: new Date()
    }]);

    // Agregar mensaje de loading del asistente
    setMessages(draft => [...draft, {
      role: 'assistant',
      content: '',
      loading: true,
      timestamp: new Date()
    }]);

    setNewMessage('');

    // Simular respuesta del bot (aquí iría la integración con el backend)
    setTimeout(() => {
      setMessages(draft => {
        draft[draft.length - 1].loading = false;
        draft[draft.length - 1].content = "I understand you have a question about the return policy. I'd be happy to help you with that. Could you please provide me with more details about your purchase?";
      });
    }, 2000);
  }

  return (
    <div className='flex flex-col h-full relative bg-white'>
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
      />
      
      {/* Botón flotante */}
      <div className='absolute bottom-4 right-4'>
        <button className='w-12 h-12 bg-blue-500 hover:bg-blue-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center'>
          <FiMessageCircle className='w-6 h-6' />
        </button>
      </div>
    </div>
  );
}

export default Chatbot;
