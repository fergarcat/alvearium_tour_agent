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
    <div style={{ display: 'flex', gap: '4px', alignItems: 'center', padding: '4px 0' }}>
      <div style={{
        width: '6px',
        height: '6px',
        backgroundColor: '#60a5fa',
        borderRadius: '50%',
        animation: 'bounce 1.4s ease-in-out infinite both'
      }}></div>
      <div style={{
        width: '6px',
        height: '6px',
        backgroundColor: '#60a5fa',
        borderRadius: '50%',
        animation: 'bounce 1.4s ease-in-out infinite both',
        animationDelay: '150ms'
      }}></div>
      <div style={{
        width: '6px',
        height: '6px',
        backgroundColor: '#60a5fa',
        borderRadius: '50%',
        animation: 'bounce 1.4s ease-in-out infinite both',
        animationDelay: '300ms'
      }}></div>
    </div>
  );
  
  return (
    <div style={{
      flex: 1,
      overflowY: 'auto',
      padding: '24px',
      backgroundColor: '#f9fafb',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px'
    }}>
      {messages.map(({ role, content, loading, error, timestamp, isCollectingData, dataCollectionStep, profileComplete }, idx) => (
        <div key={idx}>
          {role === 'user' ? (
            // Mensaje del usuario
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '4px' }}>
              <div style={{ maxWidth: '288px' }}>
                <div style={{
                  backgroundColor: '#dea142',
                  color: 'white',
                  padding: '12px 16px',
                  borderRadius: '18px',
                  borderTopRightRadius: '6px',
                  fontSize: '14px'
                }}>
                  {content}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#9ca3af',
                  marginTop: '8px',
                  textAlign: 'right'
                }}>
                  {formatTime(timestamp || new Date())}
                </div>
              </div>
            </div>
          ) : (
            // Mensaje del asistente
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '16px' }}>
              <img 
                src={assistantAvatar} 
                alt="Assistant" 
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  flexShrink: 0,
                  marginTop: '2px'
                }}
              />
              <div style={{ flex: 1 }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: '#1f2937',
                  marginBottom: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>Ratoncito Pérez</span>
                  {isCollectingData && (
                    <span style={{
                      fontSize: '12px',
                      backgroundColor: '#fef3c7',
                      color: '#92400e',
                      padding: '4px 8px',
                      borderRadius: '9999px'
                    }}>
                      Сбор данных
                    </span>
                  )}
                  {profileComplete && (
                    <span style={{
                      fontSize: '12px',
                      backgroundColor: '#d1fae5',
                      color: '#065f46',
                      padding: '4px 8px',
                      borderRadius: '9999px'
                    }}>
                      Профиль готов
                    </span>
                  )}
                </div>
                {loading && !content ? (
                  <div style={{
                    backgroundColor: 'white',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    borderTopLeftRadius: '6px',
                    border: '1px solid #f3f4f6',
                    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
                  }}>
                    <LoadingDots />
                  </div>
                ) : (
                  <div style={{
                    padding: '12px 16px',
                    borderRadius: '18px',
                    borderTopLeftRadius: '6px',
                    border: '1px solid',
                    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                    backgroundColor: error ? '#fef2f2' : 'white',
                    borderColor: error ? '#fecaca' : '#f3f4f6'
                  }}>
                    <div style={{
                      fontSize: '14px',
                      color: error ? '#991b1b' : '#1f2937'
                    }}>
                      <Markdown>{content}</Markdown>
                    </div>
                    {dataCollectionStep && (
                      <div style={{
                        marginTop: '8px',
                        fontSize: '12px',
                        color: '#2563eb'
                      }}>
                        Шаг: {dataCollectionStep}
                      </div>
                    )}
                  </div>
                )}
                {!loading && (
                  <div style={{
                    fontSize: '12px',
                    color: '#9ca3af',
                    marginTop: '8px'
                  }}>
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
