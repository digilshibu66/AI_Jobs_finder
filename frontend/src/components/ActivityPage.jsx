import { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../context/ThemeContext';
import '../styles/ActivityPage.css';

const ActivityPage = () => {
  const { theme } = useTheme();
  const [logs, setLogs] = useState([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPlatform, setFilterPlatform] = useState('');
  const [filterDate, setFilterDate] = useState('');

  // Filter options from API
  const [filterOptions, setFilterOptions] = useState({
    statuses: [],
    platforms: [],
    dates: []
  });

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const logsPerPage = 25;

  // Fetch filter options when page loads
  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        const response = await fetch('/api/logs/filters');
        const data = await response.json();
        if (data.success) {
          setFilterOptions({
            statuses: data.statuses || [],
            platforms: data.platforms || [],
            dates: data.dates || []
          });
        }
      } catch (error) {
        console.error('Error fetching filter options:', error);
      }
    };

    fetchFilterOptions();
  }, []);

  // Fetch logs with filters (called on filter change)
  const fetchLogs = useCallback(async () => {
    setIsLoading(true);
    try {
      // Build query string with filters
      const params = new URLSearchParams();
      if (filterStatus) params.append('status', filterStatus);
      if (filterPlatform) params.append('platform', filterPlatform);
      if (filterDate) params.append('date', filterDate);
      if (searchTerm) params.append('search', searchTerm);

      const url = `/api/logs${params.toString() ? '?' + params.toString() : ''}`;
      const response = await fetch(url);
      const data = await response.json();

      if (data.success) {
        // Normalize field names
        const normalizedLogs = data.data.map((log, index) => ({
          ...log,
          id: log.id || index + 1,
          job_title: log.job_title || log['Job Title'] || log['job title'] || '',
          company: log.company || log['Company'] || '',
          status: log.status || log['Status'] || '',
          timestamp: log.timestamp || log['Timestamp'] || log['Date'] || '',
          platform: log.platform || log['Platform'] || '',
          to_email: log.to_email || log['To Email'] || log['Email'] || '',
          source_url: log.source_url || log['Source URL'] || log['URL'] || ''
        }));
        setLogs(normalizedLogs);
        setTotalLogs(data.total || normalizedLogs.length);
      }
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
    setIsLoading(false);
  }, [filterStatus, filterPlatform, filterDate, searchTerm]);

  // Fetch logs when page loads or filters change
  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const getStatusColor = (status) => {
    const statusUpper = (status || '').toUpperCase();
    switch (statusUpper) {
      case 'SUCCESS':
        return { bg: 'rgba(72, 187, 120, 0.2)', text: '#38a169' };
      case 'FAILED':
        return { bg: 'rgba(245, 101, 101, 0.2)', text: '#e53e3e' };
      case 'SKIPPED':
        return { bg: 'rgba(236, 201, 75, 0.2)', text: '#d69e2e' };
      case 'DRY_RUN':
      case 'SCRAPED':
      case 'PROCESSING':
        return { bg: 'rgba(66, 153, 225, 0.2)', text: '#3182ce' };
      default:
        return { bg: 'rgba(160, 174, 192, 0.2)', text: '#718096' };
    }
  };

  // Pagination (client-side on already filtered data)
  const totalPages = Math.ceil(logs.length / logsPerPage);
  const startIndex = (currentPage - 1) * logsPerPage;
  const paginatedLogs = logs.slice(startIndex, startIndex + logsPerPage);

  const clearFilters = () => {
    setSearchTerm('');
    setFilterStatus('');
    setFilterPlatform('');
    setFilterDate('');
    setCurrentPage(1);
  };

  const handleFilterChange = (setter) => (e) => {
    setter(e.target.value);
    setCurrentPage(1);
  };

  const handleDeleteAll = async () => {
    if (!window.confirm('⚠️ Delete ALL records? This cannot be undone!')) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch('/api/logs/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deleteAll: true })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('✅ All records deleted successfully!');
        fetchLogs(); // Refresh logs
      } else {
        alert('❌ Failed to delete records: ' + data.message);
      }
    } catch (error) {
      console.error('Error deleting records:', error);
      alert('❌ Error deleting records: ' + error.message);
    }
    setIsDeleting(false);
  };

  const handleDeleteByStatus = async () => {
    if (!filterStatus) {
      alert('⚠️ Please select a status filter first');
      return;
    }

    if (!window.confirm(`⚠️ Delete all records with status "${filterStatus}"? This cannot be undone!`)) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch('/api/logs/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: filterStatus })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('✅ Records deleted successfully!');
        setFilterStatus(''); // Clear filter
        fetchLogs(); // Refresh logs
      } else {
        alert('❌ ' + data.message);
      }
    } catch (error) {
      console.error('Error deleting records:', error);
      alert('❌ Error deleting records: ' + error.message);
    }
    setIsDeleting(false);
  };

  const cardStyle = {
    backgroundColor: theme.colors.surface,
    borderRadius: '16px',
    padding: '24px',
    boxShadow: theme.colors.cardShadow
  };

  return (
    <div className="activity-page" style={{ backgroundColor: theme.colors.background }}>
      <div className="activity-container">
        {/* Header */}
        <div className="activity-header">
          <h2 style={{ color: theme.colors.text }}>📋 Activity Logs</h2>
          <p style={{ color: theme.colors.textSecondary }}>
            View and filter all job application activity from Excel log
          </p>
        </div>

        {/* Filters */}
        <div className="filters-card" style={cardStyle}>
          <div className="filters-row">
            <div className="filter-group">
              <label style={{ color: theme.colors.text }}>🔍 Search</label>
              <input
                type="text"
                placeholder="Search job, company, email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
              />
            </div>

            <div className="filter-group">
              <label style={{ color: theme.colors.text }}>📊 Status</label>
              <select
                value={filterStatus}
                onChange={handleFilterChange(setFilterStatus)}
                style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
              >
                <option value="">All Statuses</option>
                {filterOptions.statuses.map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label style={{ color: theme.colors.text }}>🌐 Platform</label>
              <select
                value={filterPlatform}
                onChange={handleFilterChange(setFilterPlatform)}
                style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
              >
                <option value="">All Platforms</option>
                {filterOptions.platforms.map(platform => (
                  <option key={platform} value={platform}>{platform}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label style={{ color: theme.colors.text }}>📅 Date</label>
              <select
                value={filterDate}
                onChange={handleFilterChange(setFilterDate)}
                style={{ backgroundColor: theme.colors.inputBg, color: theme.colors.text }}
              >
                <option value="">All Dates</option>
                {filterOptions.dates.map(date => (
                  <option key={date} value={date}>{date}</option>
                ))}
              </select>
            </div>

            <button
              className="clear-btn"
              onClick={clearFilters}
              style={{ color: theme.colors.primary }}
            >
              Clear Filters
            </button>

            <button
              className="delete-btn delete-filtered"
              onClick={handleDeleteByStatus}
              disabled={!filterStatus || isDeleting}
              style={{ 
                backgroundColor: filterStatus ? '#f56565' : '#cbd5e0',
                color: 'white',
                cursor: filterStatus && !isDeleting ? 'pointer' : 'not-allowed',
                opacity: filterStatus && !isDeleting ? 1 : 0.5
              }}
              title={filterStatus ? `Delete all ${filterStatus} records` : 'Select a status to delete'}
            >
              {isDeleting ? '⏳ Deleting...' : '🗑️ Delete Filtered'}
            </button>

            <button
              className="delete-btn delete-all"
              onClick={handleDeleteAll}
              disabled={isDeleting}
              style={{ 
                backgroundColor: isDeleting ? '#cbd5e0' : '#e53e3e',
                color: 'white',
                cursor: isDeleting ? 'not-allowed' : 'pointer'
              }}
            >
              {isDeleting ? '⏳ Deleting...' : '🗑️ Delete All'}
            </button>
          </div>

          <div className="filters-summary" style={{ color: theme.colors.textSecondary }}>
            {isLoading ? 'Loading...' : (
              <>Showing {paginatedLogs.length} of {logs.length} filtered records ({totalLogs} total)</>
            )}
          </div>
        </div>

        {/* Data Table */}
        <div className="table-card" style={cardStyle}>
          {isLoading ? (
            <div className="loading-state" style={{ textAlign: 'center', padding: '40px', color: theme.colors.textSecondary }}>
              ⏳ Loading data from Excel...
            </div>
          ) : (
            <div className="table-container">
              <table className="activity-table">
                <thead>
                  <tr>
                    <th style={{ color: theme.colors.text }}>Date</th>
                    <th style={{ color: theme.colors.text }}>Job Title</th>
                    <th style={{ color: theme.colors.text }}>Company</th>
                    <th style={{ color: theme.colors.text }}>Platform</th>
                    <th style={{ color: theme.colors.text }}>Email</th>
                    <th style={{ color: theme.colors.text }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedLogs.length > 0 ? (
                    paginatedLogs.map((log) => {
                      const statusStyle = getStatusColor(log.status);
                      return (
                        <tr key={log.id} style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                          <td style={{ color: theme.colors.textSecondary }}>
                            {log.timestamp ? new Date(log.timestamp).toLocaleString() : '-'}
                          </td>
                          <td style={{ color: theme.colors.text }}>
                            {log.source_url ? (
                              <a
                                href={log.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ color: theme.colors.primary }}
                              >
                                {log.job_title || '-'}
                              </a>
                            ) : (
                              log.job_title || '-'
                            )}
                          </td>
                          <td style={{ color: theme.colors.text }}>{log.company || '-'}</td>
                          <td style={{ color: theme.colors.textSecondary }}>{log.platform || '-'}</td>
                          <td style={{ color: theme.colors.textSecondary, fontSize: '0.85rem' }}>
                            {log.to_email || '-'}
                          </td>
                          <td>
                            <span
                              className="status-badge"
                              style={{
                                backgroundColor: statusStyle.bg,
                                color: statusStyle.text
                              }}
                            >
                              {log.status || 'Unknown'}
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan="6" style={{ textAlign: 'center', padding: '40px', color: theme.colors.textSecondary }}>
                        {totalLogs === 0 ? 'No activity data. Run a job search to see results here.' : 'No matching records found.'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              style={{ backgroundColor: theme.colors.surface, color: theme.colors.text }}
            >
              ««
            </button>
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              style={{ backgroundColor: theme.colors.surface, color: theme.colors.text }}
            >
              ‹
            </button>

            <span style={{ color: theme.colors.text, padding: '0 16px' }}>
              Page {currentPage} of {totalPages}
            </span>

            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              style={{ backgroundColor: theme.colors.surface, color: theme.colors.text }}
            >
              ›
            </button>
            <button
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
              style={{ backgroundColor: theme.colors.surface, color: theme.colors.text }}
            >
              »»
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ActivityPage;
