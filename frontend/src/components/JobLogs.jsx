import { useTheme } from '../context/ThemeContext';
import '../styles/JobLogs.css';

const JobLogs = ({ logs }) => {
  const { theme } = useTheme();
  const getStatusColor = (status, theme) => {
    switch (status) {
      case 'SUCCESS':
        return theme.colors.success;
      case 'FAILED':
        return theme.colors.danger;
      case 'SKIPPED':
        return theme.colors.warning;
      case 'DRY_RUN':
        return theme.colors.info;
      default:
        return theme.colors.primary;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'SUCCESS':
        return 'status-success';
      case 'FAILED':
        return 'status-failed';
      case 'SKIPPED':
        return 'status-skipped';
      case 'DRY_RUN':
        return 'status-dry-run';
      default:
        return '';
    }
  };

  return (
    <div className="job-logs" style={{ backgroundColor: theme.colors.surface, padding: '20px', borderRadius: '8px' }}>
      <h3 style={{ color: theme.colors.text }}>Recent Activity</h3>
      <div className="logs-table-container" style={{ overflowX: 'auto' }}>
        <table className="logs-table" style={{ backgroundColor: theme.colors.surface, color: theme.colors.text }}>
          <thead>
            <tr style={{ borderBottom: `2px solid ${theme.colors.border}`, backgroundColor: theme.colors.headerBg }}>
              <th style={{ color: theme.colors.headerText, padding: '12px', textAlign: 'left' }}>Timestamp</th>
              <th style={{ color: theme.colors.headerText, padding: '12px', textAlign: 'left' }}>Job Title</th>
              <th style={{ color: theme.colors.headerText, padding: '12px', textAlign: 'left' }}>Company</th>
              <th style={{ color: theme.colors.headerText, padding: '12px', textAlign: 'left' }}>Recipient</th>
              <th style={{ color: theme.colors.headerText, padding: '12px', textAlign: 'left' }}>Status</th>
              <th style={{ color: theme.colors.headerText, padding: '12px', textAlign: 'left' }}>Error</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                <td style={{ padding: '12px', color: theme.colors.text }}>{log.timestamp}</td>
                <td style={{ padding: '12px', color: theme.colors.primary }}>
                  <a href={log.sourceUrl} target="_blank" rel="noopener noreferrer" style={{ color: theme.colors.secondary, textDecoration: 'none' }}>
                    {log.jobTitle}
                  </a>
                </td>
                <td style={{ padding: '12px', color: theme.colors.text }}>{log.company}</td>
                <td style={{ padding: '12px', color: theme.colors.text }}>{log.recipientEmail}</td>
                <td style={{ padding: '12px' }}>
                  <span className={`status-badge ${getStatusClass(log.status)}`} style={{ padding: '4px 8px', borderRadius: '4px', backgroundColor: getStatusColor(log.status, theme) }}>
                    {log.status}
                  </span>
                </td>
                <td className="error-message" style={{ padding: '12px', color: theme.colors.danger, fontSize: '0.85rem' }}>
                  {log.errorMessage}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {logs.length === 0 && (
        <div className="no-logs" style={{ color: theme.colors.textSecondary }}>
          <p>No activity logs available</p>
        </div>
      )}
    </div>
  );
};

export default JobLogs;