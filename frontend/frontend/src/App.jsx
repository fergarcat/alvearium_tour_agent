import Chatbot from './components/Chatbot';

function App() {
  return (
    <div className='max-w-sm mx-auto h-screen flex flex-col bg-white shadow-2xl relative'>
      {/* Header con gradiente exacto */}
      <div className='relative bg-gradient-to-br from-blue-500 via-purple-500 to-pink-400 text-white p-6 rounded-t-2xl'>
        {/* Botón X */}
        <button className='absolute top-4 right-4 text-white/80 hover:text-white text-lg font-light'>
          ×
        </button>
        
        {/* Logo C */}
        <div className='w-10 h-10 bg-white rounded-full flex items-center justify-center mb-4'>
          <span className='text-blue-600 font-bold text-lg'>C</span>
        </div>
        
        {/* Título */}
        <h1 className='text-xl font-semibold mb-2'>ChatFlow</h1>
        
        {/* Descripción */}
        <p className='text-white/90 text-xs leading-relaxed pr-8'>
          A live chat interface that allows for seamless, natural<br />
          communication and connection.
        </p>
      </div>
      
      <Chatbot />
    </div>
  );
}

export default App;
