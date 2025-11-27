import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useTheme } from '../context/ThemeContext';
import '../styles/JobStats.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const JobStats = ({ stats }) => {
  const { theme } = useTheme();
  const chartData = {
    labels: ['Success', 'Failed', 'Skipped', 'Dry Run'],
    datasets: [
      {
        label: 'Applications',
        data: [stats.success, stats.failed, stats.skipped, stats.dryRun],
        backgroundColor: [
          'rgba(76, 175, 80, 0.6)',   // Green for success
          'rgba(244, 67, 54, 0.6)',   // Red for failed
          'rgba(255, 152, 0, 0.6)',   // Orange for skipped
          'rgba(33, 150, 243, 0.6)',  // Blue for dry run
        ],
        borderColor: [
          'rgba(76, 175, 80, 1)',
          'rgba(244, 67, 54, 1)',
          'rgba(255, 152, 0, 1)',
          'rgba(33, 150, 243, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Application Status Distribution',
      },
    },
  };

  return (
    <div className="job-stats">
      <h3>Statistics Overview</h3>
      <div className="stats-summary">
        <div className="stat-card" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.border, color: theme.colors.text }}>
          <h4 style={{ color: theme.colors.text }}>Total Jobs</h4>
          <p className="stat-value" style={{ color: theme.colors.primary }}>{stats.totalJobs}</p>
        </div>
        <div className="stat-card success" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.success, color: theme.colors.text }}>
          <h4 style={{ color: theme.colors.success }}>Success</h4>
          <p className="stat-value" style={{ color: theme.colors.success }}>{stats.success}</p>
        </div>
        <div className="stat-card failed" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.danger, color: theme.colors.text }}>
          <h4 style={{ color: theme.colors.danger }}>Failed</h4>
          <p className="stat-value" style={{ color: theme.colors.danger }}>{stats.failed}</p>
        </div>
        <div className="stat-card skipped" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.warning, color: theme.colors.text }}>
          <h4 style={{ color: theme.colors.warning }}>Skipped</h4>
          <p className="stat-value" style={{ color: theme.colors.warning }}>{stats.skipped}</p>
        </div>
        <div className="stat-card dry-run" style={{ backgroundColor: theme.colors.surface, borderColor: theme.colors.info, color: theme.colors.text }}>
          <h4 style={{ color: theme.colors.info }}>Dry Run</h4>
          <p className="stat-value" style={{ color: theme.colors.info }}>{stats.dryRun}</p>
        </div>
      </div>
      <div className="chart-container" style={{ backgroundColor: theme.colors.surface, padding: '20px', borderRadius: '8px', boxShadow: theme.colors.cardShadow }}>
        <Bar data={chartData} options={{...chartOptions, plugins: {...chartOptions.plugins, legend: {...chartOptions.plugins.legend, labels: {color: theme.colors.text}}}}} />
      </div>
    </div>
  );
};

export default JobStats;