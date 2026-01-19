import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import JobsPage from './components/JobsPage';
import ActivityPage from './components/ActivityPage';
import SettingsPage from './components/SettingsPage';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import './App.css';

function AppContent() {
  const { theme } = useTheme();
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    // Handle browser back/forward
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/jobs') setCurrentPage('jobs');
      else if (path === '/activity') setCurrentPage('activity');
      else if (path === '/settings') setCurrentPage('settings');
      else setCurrentPage('dashboard');
    };

    window.addEventListener('popstate', handlePopState);
    handlePopState(); // Set initial state

    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleNavigate = (page) => {
    setCurrentPage(page);
    const path = page === 'dashboard' ? '/' : `/${page}`;
    window.history.pushState({}, '', path);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'jobs':
        return <JobsPage />;
      case 'activity':
        return <ActivityPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Dashboard onNavigate={handleNavigate} />;
    }
  };

  const appStyle = {
    backgroundColor: theme.colors.background,
    color: theme.colors.text,
    minHeight: '100vh',
    transition: 'background-color 0.3s ease, color 0.3s ease',
  };

  return (
    <div className="App" style={appStyle}>
      <Navbar currentPage={currentPage} onNavigate={handleNavigate} />
      <main className="main-content">
        {renderPage()}
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