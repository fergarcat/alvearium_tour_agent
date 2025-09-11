import { useRef } from 'react';
import { FiSend, FiSmile, FiPaperclip } from 'react-icons/fi';
import useAutosize from '../hooks/useAutosize';

function ChatInput({ newMessage, isLoading, setNewMessage, submitNewMessage, disabled = false }) {
  const textAreaRef = useRef(null);
  useAutosize(textAreaRef, newMessage);

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitNewMessage();
    }
  }

  return (
    <div style={{
      borderTop: '1px solid #e5e7eb',
      backgroundColor: 'white',
      padding: '16px'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: '12px'
      }}>
        {/* Botón emoji */}
        <button style={{
          padding: '8px',
          color: '#9ca3af',
          backgroundColor: 'transparent',
          border: 'none',
          cursor: 'pointer'
        }}>
          <FiSmile size={20} />
        </button>
        
        {/* Input de texto */}
        <div style={{ flex: 1, position: 'relative' }}>
          <textarea
            ref={textAreaRef}
            style={{
              width: '100%',
              minHeight: '40px',
              maxHeight: '96px',
              padding: '8px 16px 8px 16px',
              paddingRight: '48px',
              fontSize: '14px',
              backgroundColor: '#f3f4f6',
              color: '#111827',
              border: '1px solid #e5e7eb',
              borderRadius: '20px',
              resize: 'none',
              outline: 'none',
              fontFamily: 'inherit'
            }}
            placeholder='Reply ...'
            value={newMessage}
            disabled={isLoading || disabled}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
          />
          
          {/* Botón attach */}
          <button style={{
            position: 'absolute',
            right: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            padding: '4px',
            color: '#9ca3af',
            backgroundColor: 'transparent',
            border: 'none',
            cursor: 'pointer'
          }}>
            <FiPaperclip size={16} />
          </button>
        </div>
        
        {/* Botón enviar */}
        <button
          style={{
            padding: '8px',
            borderRadius: '50%',
            border: 'none',
            cursor: newMessage.trim() && !isLoading && !disabled ? 'pointer' : 'not-allowed',
            backgroundColor: newMessage.trim() && !isLoading && !disabled ? '#3b82f6' : '#e5e7eb',
            color: newMessage.trim() && !isLoading && !disabled ? 'white' : '#9ca3af',
            boxShadow: newMessage.trim() && !isLoading && !disabled ? '0 4px 6px -1px rgba(0, 0, 0, 0.1)' : 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          onClick={() => {
            submitNewMessage();
          }}
          disabled={!newMessage.trim() || isLoading || disabled}
          type='button'
        >
          <FiSend size={20} />
        </button>
      </div>
    </div>
  );
}

export default ChatInput;
