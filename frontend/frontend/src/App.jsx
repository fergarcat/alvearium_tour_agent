import Chatbot from './components/Chatbot.jsx';

function App() {
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
      <Chatbot />
    </div>
  );
}

export default App;