import { useState, useEffect } from 'react';

function useTheme() {
  const [theme, setTheme] = useState(() => {
    // Intentar obtener el tema guardado en localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      return savedTheme;
    }
    
    // Si no hay tema guardado, usar la preferencia del sistema
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  });

  useEffect(() => {
    // Guardar el tema en localStorage
    localStorage.setItem('theme', theme);
    
    // Aplicar o remover la clase 'dark' del elemento html
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  return { theme, toggleTheme };
}

export default useTheme;
