import { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/ActivityPage.css';

const ActivityPage = () => {
  const { theme } = useTheme();
  const [logs, setLogs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const logsPerPage = 50;

  // Fetch logs from backend
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        if (data.success) {
          const logsWithId = data.data.map((log, index) => ({
            ...log,
            id: log.id || index + 1
          }));
          setLogs(logsWithId);
        }
      } catch (error) {
        console.error('Error fetching logs:', error);
      }
    };

    fetchLogs();
    // Refresh every 30 seconds
    const interval = setInterval(fetchLogs, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
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

  // Filter logs based on search term and status
  const filteredLogs = logs.filter(log => {
    const matchesSearch = 
      log.job_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.company?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.to_email?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = !filterStatus || log.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  // Pagination
  const totalPages = Math.ceil(filteredLogs.length / logsPerPage);
  const startIndex = (currentPage - 1) * logsPerPage;
  const paginatedLogs = filteredLogs.slice(startIndex, startIndex + logsPerPage);

  const handleGoBack = () => {
    window.history.pushState({}, '', '/');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <div className="activity-page" style={{ backgroundColor: theme.colors.background, minHeight: '100vh', padding: '20px' }}>
      <div className="activity-header" style={{ marginBottom: '20px' }}>
        <button 
          onClick={handleGoBack}
          style={{
            backgroundColor: theme.colors.secondary,
            color: theme.colors.headerText,
            padding: '8px 16px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginBottom: '15px'
          }}
        >
          ← Back to Dashboard
        </button>
        <h1 style={{ color: theme.colors.text, marginBottom: '20px' }}>Email Activity Logs</h1>
        
        <div className="activity-controls" style={{ display: 'flex', gap: '15px', marginBottom: '20px', flexWrap: 'wrap' }}>
          <input
            type="text"
            placeholder="Search by job title, company, or email..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            style={{
              padding: '10px',
              borderRadius: '4px',
              border: `1px solid ${theme.colors.border}`,
              backgroundColor: theme.colors.inputBg,
              color: theme.colors.text,
              flex: 1,
              minWidth: '250px'
            }}
          />
          
          <select
            value={filterStatus}
            onChange={(e) => {
              setFilterStatus(e.target.value);
              setCurrentPage(1);
            }}
            style={{
              padding: '10px',
              borderRadius: '4px',
              border: `1px solid ${theme.colors.border}`,
              backgroundColor: theme.colors.inputBg,
              color: theme.colors.text,
              minWidth: '150px'
            }}
          >
            <option value="">All Status</option>
            <option value="SUCCESS">Success</option>
            <option value="FAILED">Failed</option>
            <option value="SKIPPED">Skipped</option>
            <option value="DRY_RUN">Dry Run</option>
          </select>

          <div style={{ color: theme.colors.textSecondary }}>
            Total: {filteredLogs.length} | Page {currentPage} of {totalPages || 1}
          </div>
        </div>
      </div>

      <div className="activity-table-container" style={{ overflowX: 'auto', backgroundColor: theme.colors.surface, borderRadius: '8px', boxShadow: theme.colors.cardShadow }}>
        <table className="activity-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: theme.colors.headerBg, borderBottom: `2px solid ${theme.colors.border}` }}>
              <th style={{ color: theme.colors.headerText, padding: '15px', textAlign: 'left', whiteSpace: 'nowrap' }}>Timestamp</th>
              <th style={{ color: theme.colors.headerText, padding: '15px', textAlign: 'left', whiteSpace: 'nowrap' }}>Job Title</th>
              <th style={{ color: theme.colors.headerText, padding: '15px', textAlign: 'left', whiteSpace: 'nowrap' }}>Company</th>
              <th style={{ color: theme.colors.headerText, padding: '15px', textAlign: 'left', whiteSpace: 'nowrap' }}>Recipient Email</th>
              <th style={{ color: theme.colors.headerText, padding: '15px', textAlign: 'left', whiteSpace: 'nowrap' }}>Status</th>
              <th style={{ color: theme.colors.headerText, padding: '15px', textAlign: 'left' }}>Error Message</th>
            </tr>
          </thead>
          <tbody>
            {paginatedLogs.map((log) => (
              <tr key={log.id} style={{ borderBottom: `1px solid ${theme.colors.border}`, '&:hover': { backgroundColor: theme.colors.background } }}>
                <td style={{ padding: '15px', color: theme.colors.text, whiteSpace: 'nowrap', fontSize: '0.9rem' }}>{log.timestamp}</td>
                <td style={{ padding: '15px', color: theme.colors.secondary, fontWeight: '500' }}>
                  {log.source_url ? (
                    <a href={log.source_url} target="_blank" rel="noopener noreferrer" style={{ color: theme.colors.secondary, textDecoration: 'none' }}>
                      {log.job_title}
                    </a>
                  ) : (
                    log.job_title
                  )}
                </td>
                <td style={{ padding: '15px', color: theme.colors.text }}>{log.company}</td>
                <td style={{ padding: '15px', color: theme.colors.text, fontSize: '0.9rem' }}>{log.to_email}</td>
                <td style={{ padding: '15px' }}>
                  <span style={{
                    padding: '6px 12px',
                    borderRadius: '4px',
                    backgroundColor: getStatusColor(log.status),
                    color: theme.colors.headerText,
                    fontWeight: 'bold',
                    fontSize: '0.85rem',
                    whiteSpace: 'nowrap'
                  }}>
                    {log.status}
                  </span>
                </td>
                <td style={{ padding: '15px', color: theme.colors.danger, fontSize: '0.9rem' }}>
                  {log.error_message || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredLogs.length === 0 && (
        <div style={{ padding: '40px', textAlign: 'center', color: theme.colors.textSecondary }}>
          <p>No activity logs available</p>
        </div>
      )}

      {totalPages > 1 && (
        <div className="pagination" style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '20px', alignItems: 'center' }}>
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            style={{
              padding: '8px 12px',
              backgroundColor: currentPage === 1 ? theme.colors.border : theme.colors.secondary,
              color: theme.colors.headerText,
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
            }}
          >
            Previous
          </button>
          
          {[...Array(totalPages)].map((_, i) => (
            <button
              key={i + 1}
              onClick={() => setCurrentPage(i + 1)}
              style={{
                padding: '8px 12px',
                backgroundColor: currentPage === i + 1 ? theme.colors.secondary : theme.colors.background,
                color: currentPage === i + 1 ? theme.colors.headerText : theme.colors.text,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {i + 1}
            </button>
          ))}
          
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            style={{
              padding: '8px 12px',
              backgroundColor: currentPage === totalPages ? theme.colors.border : theme.colors.secondary,
              color: theme.colors.headerText,
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
            }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default ActivityPage;
