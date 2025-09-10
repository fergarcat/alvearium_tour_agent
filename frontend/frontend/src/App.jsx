import { useState } from 'react';
import { FiSend, FiSmile, FiPaperclip, FiMessageCircle } from 'react-icons/fi';

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'user',
      content: 'Hello, how are you doing?',
      timestamp: '08:15 AM'
    },
    {
      role: 'assistant',
      content: "I'm doing well, thank you! How can I help you today?",
      timestamp: '08:16 AM'
    },
    {
      role: 'user',
      content: 'I have a question about the return policy for a product I purchased.',
      timestamp: 'Just Now'
    },
    {
      role: 'assistant',
      content: '',
      loading: true
    }
  ]);
  
  const [newMessage, setNewMessage] = useState('');
  
  const submitMessage = () => {
    if (!newMessage.trim()) return;
    
    const userMessage = {
      role: 'user',
      content: newMessage,
      timestamp: 'Just Now'
    };
    
    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    
    // Simular respuesta
    setTimeout(() => {
      setMessages(prev => [
        ...prev.slice(0, -1), // Remove loading message
        {
          role: 'assistant',
          content: 'Thank you for your question. I\'d be happy to help you with the return policy.',
          timestamp: 'Just Now'
        }
      ]);
    }, 2000);
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitMessage();
    }
  };
  
  return (
    <div style={{
      width: '375px',
      height: '667px',
      margin: '20px auto',
      background: 'white',
      borderRadius: '25px',
      overflow: 'hidden',
      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative'
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%)',
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
        
        {/* Logo */}
        <div style={{
          width: '40px',
          height: '40px',
          background: 'white',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '16px'
        }}>
          <span style={{
            color: '#4F46E5',
            fontWeight: 'bold',
            fontSize: '18px'
          }}>C</span>
        </div>
        
        {/* Title */}
        <h1 style={{
          fontSize: '24px',
          fontWeight: '600',
          marginBottom: '8px',
          margin: 0
        }}>ChatFlow</h1>
        
        {/* Description */}
        <p style={{
          fontSize: '12px',
          opacity: 0.9,
          lineHeight: '1.4',
          margin: 0,
          maxWidth: '280px'
        }}>
          A live chat interface that allows for seamless, natural communication and connection.
        </p>
      </div>
      
      {/* Messages */}
      <div style={{
        flex: 1,
        padding: '20px',
        background: '#F9FAFB',
        overflowY: 'auto'
      }}>
        {messages.map((message, idx) => (
          <div key={idx} style={{ marginBottom: '20px' }}>
            {message.role === 'user' ? (
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <div style={{ maxWidth: '250px' }}>
                  <div style={{
                    background: '#4F46E5',
                    color: 'white',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    borderTopRightRadius: '6px',
                    fontSize: '14px',
                    lineHeight: '1.4'
                  }}>
                    {message.content}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: '#9CA3AF',
                    textAlign: 'right',
                    marginTop: '4px'
                  }}>
                    {message.timestamp}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  background: '#E5E7EB',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    background: '#9CA3AF',
                    borderRadius: '50%'
                  }}></div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: '500',
                    color: '#374151',
                    marginBottom: '4px'
                  }}>
                    Assistant
                  </div>
                  <div style={{
                    background: 'white',
                    padding: '12px 16px',
                    borderRadius: '18px',
                    borderTopLeftRadius: '6px',
                    fontSize: '14px',
                    color: '#374151',
                    border: '1px solid #E5E7EB',
                    lineHeight: '1.4'
                  }}>
                    {message.loading ? (
                      <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                        <div style={{
                          width: '6px',
                          height: '6px',
                          background: '#6366F1',
                          borderRadius: '50%',
                          animation: 'bounce 1.5s infinite'
                        }}></div>
                        <div style={{
                          width: '6px',
                          height: '6px',
                          background: '#6366F1',
                          borderRadius: '50%',
                          animation: 'bounce 1.5s infinite 0.15s'
                        }}></div>
                        <div style={{
                          width: '6px',
                          height: '6px',
                          background: '#6366F1',
                          borderRadius: '50%',
                          animation: 'bounce 1.5s infinite 0.3s'
                        }}></div>
                      </div>
                    ) : message.content}
                  </div>
                  {!message.loading && (
                    <div style={{
                      fontSize: '11px',
                      color: '#9CA3AF',
                      marginTop: '4px'
                    }}>
                      {message.timestamp}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Input */}
      <div style={{
        padding: '16px',
        background: 'white',
        borderTop: '1px solid #E5E7EB'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button style={{
            background: 'none',
            border: 'none',
            color: '#9CA3AF',
            padding: '8px',
            cursor: 'pointer'
          }}>
            <FiSmile size={20} />
          </button>
          
          <div style={{ flex: 1, position: 'relative' }}>
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Reply ..."
              style={{
                width: '100%',
                minHeight: '40px',
                padding: '12px 40px 12px 16px',
                border: '1px solid #E5E7EB',
                borderRadius: '20px',
                resize: 'none',
                outline: 'none',
                fontSize: '14px',
                background: '#F9FAFB'
              }}
              rows={1}
            />
            <button style={{
              position: 'absolute',
              right: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              color: '#9CA3AF',
              cursor: 'pointer'
            }}>
              <FiPaperclip size={16} />
            </button>
          </div>
          
          <button
            onClick={submitMessage}
            disabled={!newMessage.trim()}
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              border: 'none',
              background: newMessage.trim() ? '#4F46E5' : '#E5E7EB',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: newMessage.trim() ? 'pointer' : 'not-allowed'
            }}
          >
            <FiSend size={16} />
          </button>
        </div>
      </div>
      
      {/* Floating button */}
      <button style={{
        position: 'absolute',
        bottom: '20px',
        right: '20px',
        width: '48px',
        height: '48px',
        borderRadius: '50%',
        background: '#4F46E5',
        border: 'none',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        boxShadow: '0 4px 12px rgba(79, 70, 229, 0.4)'
      }}>
        <FiMessageCircle size={20} />
      </button>
    </div>
  );
}

export default App;
