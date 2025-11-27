import { useTheme } from '../context/ThemeContext';
import '../styles/ThemeSwitcher.css';

const ThemeSwitcher = () => {
  const { currentTheme, toggleTheme, theme } = useTheme();

  const buttonStyle = {
    backgroundColor: theme.colors.secondary,
    color: theme.colors.headerText,
    border: 'none',
    padding: '8px 16px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    transition: 'background-color 0.3s ease',
  };

  const buttonHoverStyle = {
    ...buttonStyle,
    backgroundColor: theme.colors.buttonHover,
  };

  return (
    <button
      onClick={toggleTheme}
      className="theme-switcher"
      style={buttonStyle}
      onMouseEnter={(e) => (e.target.style.backgroundColor = theme.colors.buttonHover)}
      onMouseLeave={(e) => (e.target.style.backgroundColor = theme.colors.secondary)}
      title={`Switch to ${currentTheme === 'light' ? 'dark' : 'light'} theme`}
    >
      {currentTheme === 'light' ? '🌙 Dark' : '☀️ Light'}
    </button>
  );
};

export default ThemeSwitcher;