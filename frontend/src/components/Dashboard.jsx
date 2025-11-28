import { useState, useEffect } from 'react';
import JobStats from './JobStats';
import JobRunner from './JobRunner';
import ThemeSwitcher from './ThemeSwitcher';
import { useTheme } from '../context/ThemeContext';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const { theme } = useTheme();
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({
    totalJobs: 0,
    success: 0,
    failed: 0,
    skipped: 0,
    dryRun: 0
  });

  // Fetch data from the backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch logs
        const logsResponse = await fetch('/api/logs');
        const logsData = await logsResponse.json();
        
        // Fetch stats
        const statsResponse = await fetch('/api/stats');
        const statsData = await statsResponse.json();
        
        if (logsData.success) {
          // Add id field if not present
          const logs = logsData.data.map((log, index) => ({
            ...log,
            id: log.id || index + 1
          }));
          setLogs(logs);
        }
        
        if (statsData.success) {
          setStats(statsData.data);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    
    fetchData();
    
    // Set up interval to refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Function to refresh data manually
  const refreshData = async () => {
    try {
      // Fetch logs
      const logsResponse = await fetch('/api/logs');
      const logsData = await logsResponse.json();
      
      // Fetch stats
      const statsResponse = await fetch('/api/stats');
      const statsData = await statsResponse.json();
      
      if (logsData.success) {
        // Add id field if not present
        const logs = logsData.data.map((log, index) => ({
          ...log,
          id: log.id || index + 1
        }));
        setLogs(logs);
      }
      
      if (statsData.success) {
        setStats(statsData.data);
      }
    } catch (error) {
      console.error('Error refreshing data:', error);
    }
  };

  const handleViewAllActivity = () => {
    window.history.pushState({}, '', '/activity');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <div className="dashboard" style={{ backgroundColor: theme.colors.background }}>
      <div className="dashboard-header" style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
        <h2 style={{ color: theme.colors.text }}>Job Application Dashboard</h2>
        <div className="header-controls" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button onClick={refreshData} className="refresh-button" style={{ backgroundColor: theme.colors.secondary, color: theme.colors.headerText }}>
            Refresh Data
          </button>
          <ThemeSwitcher />
        </div>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-section">
          <JobStats stats={stats} />
        </div>
        
        <div className="dashboard-section">
          <JobRunner onRunComplete={refreshData} />
        </div>
        
        <div className="dashboard-section">
          <div style={{ backgroundColor: theme.colors.surface, padding: '20px', borderRadius: '8px', boxShadow: theme.colors.cardShadow, textAlign: 'center' }}>
            <h3 style={{ color: theme.colors.text, marginBottom: '20px' }}>Activity Logs</h3>
            <button 
              onClick={handleViewAllActivity}
              style={{
                backgroundColor: theme.colors.secondary,
                color: theme.colors.headerText,
                padding: '12px 24px',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '1rem'
              }}
            >
              View Complete Activity Logs →
            </button>
            <p style={{ color: theme.colors.textSecondary, marginTop: '10px' }}>Click to view the full email activity table with search and filter options</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;