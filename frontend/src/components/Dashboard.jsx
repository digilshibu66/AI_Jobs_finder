import { useState, useEffect } from 'react';
import JobStats from './JobStats';
import { useTheme } from '../context/ThemeContext';
import '../styles/Dashboard.css';

const Dashboard = ({ onNavigate }) => {
  const { theme } = useTheme();
  const [stats, setStats] = useState({
    totalJobs: 0,
    success: 0,
    failed: 0,
    skipped: 0,
    dryRun: 0
  });
  const [recentLogs, setRecentLogs] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, logsRes] = await Promise.all([
          fetch('/api/stats'),
          fetch('/api/logs')
        ]);

        const statsData = await statsRes.json();
        const logsData = await logsRes.json();

        if (statsData.success) setStats(statsData.data);
        if (logsData.success) setRecentLogs(logsData.data.slice(-5));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const cardStyle = {
    backgroundColor: theme.colors.surface,
    borderRadius: '16px',
    padding: '24px',
    boxShadow: theme.colors.cardShadow
  };

  const quickActions = [
    { id: 'jobs', icon: '🔍', title: 'Start Job Search', desc: 'Find and apply to jobs' },
    { id: 'activity', icon: '📋', title: 'View Activity', desc: 'See all email logs' },
    { id: 'settings', icon: '⚙️', title: 'Settings', desc: 'Configure AI models' }
  ];

  return (
    <div className="dashboard-page" style={{ backgroundColor: theme.colors.background }}>
      <div className="dashboard-container">
        {/* Welcome Section */}
        <div className="welcome-section">
          <h2 style={{ color: theme.colors.text }}>👋 Welcome Back!</h2>
          <p style={{ color: theme.colors.textSecondary }}>
            Your automated job application system is ready
          </p>
        </div>

        {/* Stats Row */}
        <div className="stats-section">
          <JobStats stats={stats} />
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <h3 style={{ color: theme.colors.text }}>Quick Actions</h3>
          <div className="actions-grid">
            {quickActions.map(action => (
              <div
                key={action.id}
                className="action-card"
                onClick={() => onNavigate(action.id)}
                style={cardStyle}
              >
                <span className="action-icon">{action.icon}</span>
                <h4 style={{ color: theme.colors.text }}>{action.title}</h4>
                <p style={{ color: theme.colors.textSecondary }}>{action.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="recent-section" style={cardStyle}>
          <h3 style={{ color: theme.colors.text }}>📊 Recent Activity</h3>
          {recentLogs.length > 0 ? (
            <div className="recent-list">
              {recentLogs.map((log, index) => (
                <div
                  key={index}
                  className="recent-item"
                  style={{ borderBottom: `1px solid ${theme.colors.border}` }}
                >
                  <div className="recent-info">
                    <span className="recent-title" style={{ color: theme.colors.text }}>
                      {log.job_title || log['Job Title'] || 'Unknown Job'}
                    </span>
                    <span className="recent-company" style={{ color: theme.colors.textSecondary }}>
                      {log.company || log['Company'] || 'Unknown Company'}
                    </span>
                  </div>
                  <span
                    className={`recent-status status-${(log.status || log['Status'] || '').toLowerCase()}`}
                  >
                    {log.status || log['Status'] || 'Unknown'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: theme.colors.textSecondary, textAlign: 'center', padding: '2rem' }}>
              No recent activity. Start a job search to see results here.
            </p>
          )}
          <button
            className="view-all-btn"
            onClick={() => onNavigate('activity')}
            style={{ color: theme.colors.primary }}
          >
            View All Activity →
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;