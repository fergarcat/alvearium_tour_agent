import { useState } from "react";

// Componente del Travel Planner
function TravelPlanner() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://127.0.0.1:8000/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: input }),
    });
    const data = await res.json();
    setResult(data);
  };

  return (
    <div>
      <h1>Travel Planner 🧳</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribe tu idea de viaje..."
        />
        <button type="submit">Enviar</button>
      </form>
      {result && (
        <div>
          <h2>Categoría: {result.category}</h2>
          <p>{result.story}</p>
        </div>
      )}
    </div>
  );
}

// Componente principal App
function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-md p-6">
        <TravelPlanner />
      </div>
    </div>
  )
}

export default App;