# Frontend del Chatbot AI

Este es un frontend de chatbot desarrollado con React, Vite, JavaScript y Tailwind CSS que incluye soporte para temas claro/oscuro.

## 🚀 Instalación y Configuración

### 1. Instalar dependencias
```bash
npm install
```

### 2. Configurar variables de entorno
Copia `.env.example` a `.env` y configura la URL de tu API:

```bash
cp .env.example .env
```

Edita el archivo `.env`:
```
VITE_API_URL=http://localhost:3001/api
```

### 3. Ejecutar en desarrollo
```bash
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 🔧 API Endpoints Esperados

El frontend espera que el backend implemente los siguientes endpoints:

### Crear un nuevo chat
```
POST /api/chats
Content-Type: application/json

Response:
{
  "id": "chat_id_único"
}
```

### Enviar mensaje al chat
```
POST /api/chats/{chatId}
Content-Type: application/json

Body:
{
  "message": "Mensaje del usuario"
}

Response: Server-Sent Events (SSE)
Content-Type: text/event-stream

Eventos:
data: "Chunk de respuesta del AI"
data: "Siguiente chunk"
data: "[DONE]"
```

## 📋 Estructura de Mensajes

El frontend maneja mensajes con la siguiente estructura:

```javascript
{
  role: 'user' | 'assistant',
  content: 'Contenido del mensaje',
  loading: boolean, // Solo para mensajes del asistente
  error: boolean,   // En caso de error
  sources: []       // Array de fuentes (opcional)
}
```

## 🎨 Características

- ✅ **Tema claro/oscuro**: Intercambiable con botón en el header
- ✅ **Responsive**: Adaptable a diferentes tamaños de pantalla
- ✅ **Streaming**: Soporte para respuestas en tiempo real via SSE
- ✅ **Markdown**: Renderizado de respuestas con formato
- ✅ **Auto-scroll**: Desplazamiento automático durante la conversación
- ✅ **Auto-resize**: Textarea que se ajusta al contenido

## 🔌 Integración con Backend

### Headers CORS
Asegúrate de que tu backend permita requests desde `http://localhost:5173`:

```javascript
// Ejemplo para Express.js
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}));
```

### Ejemplo de implementación SSE (Node.js/Express)
```javascript
app.post('/api/chats/:chatId', (req, res) => {
  const { message } = req.body;
  
  // Configurar SSE
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': 'http://localhost:5173',
    'Access-Control-Allow-Credentials': 'true'
  });

  // Simular streaming de respuesta
  const chunks = ["Hola, ", "¿cómo ", "puedo ", "ayudarte?"];
  
  chunks.forEach((chunk, index) => {
    setTimeout(() => {
      res.write(`data: ${chunk}\n\n`);
      
      if (index === chunks.length - 1) {
        res.write('data: [DONE]\n\n');
        res.end();
      }
    }, index * 100);
  });
});
```

## 🛠️ Comandos Disponibles

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Linting
npm run lint
```

## 📁 Estructura del Proyecto

```
src/
├── components/
│   ├── Chatbot.jsx          # Componente principal del chat
│   ├── ChatInput.jsx        # Input para escribir mensajes
│   ├── ChatMessages.jsx     # Lista de mensajes
│   ├── ThemeToggle.jsx      # Botón para cambiar tema
│   └── Spinner.jsx          # Indicador de carga
├── hooks/
│   ├── useTheme.js          # Hook para gestión de tema
│   ├── useAutoScroll.js     # Auto-scroll durante conversación
│   └── useAutosize.js       # Auto-resize del textarea
├── api.js                   # Funciones para llamadas a la API
├── utils.js                 # Utilidades para parsing SSE
└── App.jsx                  # Componente raíz
```

## 🎯 Testing del Frontend

Para probar el frontend sin backend, puedes usar un servidor mock:

1. Instala `json-server`: `npm install -g json-server`
2. Crea un archivo `mock-server.js` (ejemplo en la documentación)
3. Ejecuta: `node mock-server.js`

¡El frontend está listo para ser integrado con tu backend! 🚀

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
