import Markdown from 'react-markdown';
import assistantAvatar from '../assets/assistant-avatar.svg';

function ChatMessages({ messages, isLoading }) {
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const LoadingDots = () => (
    <div className="flex space-x-1 items-center py-1">
      <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
      <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
      <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
    </div>
  );
  
  return (
    <div className='flex-1 overflow-y-auto px-6 py-6 space-y-6 bg-gray-50'>
      {messages.map(({ role, content, loading, error, timestamp }, idx) => (
        <div key={idx}>
          {role === 'user' ? (
            // Mensaje del usuario
            <div className='flex justify-end mb-1'>
              <div className='max-w-xs'>
                <div className='bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-tr-md text-sm'>
                  {content}
                </div>
                <div className='text-xs text-gray-400 mt-2 text-right'>
                  {formatTime(timestamp || new Date())}
                </div>
              </div>
            </div>
          ) : (
            // Mensaje del asistente
            <div className='flex items-start space-x-3 mb-4'>
              <img 
                src={assistantAvatar} 
                alt="Assistant" 
                className='w-8 h-8 rounded-full flex-shrink-0 mt-0.5'
              />
              <div className='flex-1'>
                <div className='text-sm font-medium text-gray-800 mb-1'>
                  Assistant
                </div>
                {loading && !content ? (
                  <div className='bg-white px-4 py-3 rounded-2xl rounded-tl-md border border-gray-100 shadow-sm'>
                    <LoadingDots />
                  </div>
                ) : (
                  <div className='bg-white px-4 py-3 rounded-2xl rounded-tl-md border border-gray-100 shadow-sm'>
                    <div className='text-gray-800 text-sm'>
                      {content}
                    </div>
                  </div>
                )}
                {!loading && (
                  <div className='text-xs text-gray-400 mt-2'>
                    {formatTime(timestamp || new Date())}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default ChatMessages;
