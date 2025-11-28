import { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import ActivityPage from './components/ActivityPage';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import './App.css';

function AppContent() {
  const { theme } = useTheme();
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      setCurrentPage(path === '/activity' ? 'activity' : 'dashboard');
    };

    window.addEventListener('popstate', handlePopState);
    const path = window.location.pathname;
    setCurrentPage(path === '/activity' ? 'activity' : 'dashboard');

    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const appStyle = {
    backgroundColor: theme.colors.background,
    color: theme.colors.text,
    minHeight: '100vh',
    transition: 'background-color 0.3s ease, color 0.3s ease',
  };

  const headerStyle = {
    backgroundColor: theme.colors.headerBg,
    color: theme.colors.headerText,
    padding: '1rem 0',
    boxShadow: theme.colors.cardShadow,
  };

  return (
    <div className="App" style={appStyle}>
      <header className="App-header" style={headerStyle}>
        <h1>Jobs Mail Sender Dashboard</h1>
      </header>
      <main>
        {currentPage === 'activity' ? <ActivityPage /> : <Dashboard />}
      </main>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;