import { useRef } from 'react';
import { FiSend, FiSmile, FiPaperclip } from 'react-icons/fi';
import useAutosize from '../hooks/useAutosize';

function ChatInput({ newMessage, isLoading, setNewMessage, submitNewMessage }) {
  const textAreaRef = useRef(null);
  useAutosize(textAreaRef, newMessage);

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitNewMessage();
    }
  }

  return (
    <div className='border-t border-gray-200 bg-white p-4'>
      <div className='flex items-end space-x-3'>
        {/* Botón emoji */}
        <button className='p-2 text-gray-400 hover:text-gray-600 transition-colors'>
          <FiSmile className='w-5 h-5' />
        </button>
        
        {/* Input de texto */}
        <div className='flex-1 relative'>
          <textarea
            ref={textAreaRef}
            className='w-full min-h-[40px] max-h-24 px-4 py-2 pr-12 text-sm bg-gray-100 text-gray-900 border border-gray-200 rounded-full resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-500'
            placeholder='Reply ...'
            value={newMessage}
            disabled={isLoading}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
          />
          
          {/* Botón attach */}
          <button className='absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 transition-colors'>
            <FiPaperclip className='w-4 h-4' />
          </button>
        </div>
        
        {/* Botón enviar */}
        <button
          className={`p-2 rounded-full transition-all duration-200 ${
            newMessage.trim() && !isLoading
              ? 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
          onClick={submitNewMessage}
          disabled={!newMessage.trim() || isLoading}
          type='button'
        >
          <FiSend className='w-5 h-5' />
        </button>
      </div>
    </div>
  );
}

export default ChatInput;
