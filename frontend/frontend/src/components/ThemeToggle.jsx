import { FiSun, FiMoon } from 'react-icons/fi';
import useTheme from '../hooks/useTheme';

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-white/20 text-white hover:bg-white/30 transition-colors duration-200"
      aria-label={`Cambiar a tema ${theme === 'light' ? 'oscuro' : 'claro'}`}
    >
      {theme === 'light' ? (
        <FiMoon className="w-4 h-4" />
      ) : (
        <FiSun className="w-4 h-4" />
      )}
    </button>
  );
}

export default ThemeToggle;
