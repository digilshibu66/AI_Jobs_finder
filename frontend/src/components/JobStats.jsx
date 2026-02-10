import { Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
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
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const JobStats = ({ stats }) => {
  const { theme } = useTheme();
  
  // Calculate success rate
  const totalApplications = stats.success + stats.failed;
  const successRate = totalApplications > 0 
    ? ((stats.success / totalApplications) * 100).toFixed(1)
    : 0;

  // Doughnut chart for overview
  const doughnutData = {
    labels: ['Success', 'Failed', 'Skipped', 'Dry Run'],
    datasets: [
      {
        data: [stats.success, stats.failed, stats.skipped, stats.dryRun],
        backgroundColor: [
          'rgba(72, 187, 120, 0.8)',   // Green
          'rgba(245, 101, 101, 0.8)',  // Red
          'rgba(236, 201, 75, 0.8)',   // Yellow
          'rgba(102, 126, 234, 0.8)',  // Blue
        ],
        borderColor: [
          'rgba(72, 187, 120, 1)',
          'rgba(245, 101, 101, 1)',
          'rgba(236, 201, 75, 1)',
          'rgba(102, 126, 234, 1)',
        ],
        borderWidth: 3,
        hoverOffset: 8,
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: theme.colors.text,
          font: {
            size: 12,
            weight: '500',
          },
          padding: 15,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: { size: 14, weight: 'bold' },
        bodyFont: { size: 13 },
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
      },
    },
  };

  const statCards = [
    {
      id: 'total',
      icon: '📊',
      label: 'Total Jobs',
      value: stats.totalJobs,
      color: '#667eea',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    },
    {
      id: 'success',
      icon: '✅',
      label: 'Sent',
      value: stats.success,
      color: '#48bb78',
      gradient: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
    },
    {
      id: 'failed',
      icon: '❌',
      label: 'Failed',
      value: stats.failed,
      color: '#f56565',
      gradient: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
    },
    {
      id: 'skipped',
      icon: '⏭️',
      label: 'Skipped',
      value: stats.skipped,
      color: '#ecc94b',
      gradient: 'linear-gradient(135deg, #ecc94b 0%, #d69e2e 100%)',
    },
    {
      id: 'rate',
      icon: '📈',
      label: 'Success Rate',
      value: `${successRate}%`,
      color: '#667eea',
      gradient: 'linear-gradient(135deg, #38b2ac 0%, #319795 100%)',
    },
  ];

  return (
    <div className="job-stats">
      {/* Stats Cards Grid */}
      <div className="stats-grid">
        {statCards.map((card) => (
          <div 
            key={card.id} 
            className="stat-card-modern"
            style={{
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
            }}
          >
            <div className="stat-card-icon" style={{ background: card.gradient }}>
              {card.icon}
            </div>
            <div className="stat-card-content">
              <p className="stat-card-label">{card.label}</p>
              <p className="stat-card-value" style={{ color: card.color }}>
                {card.value}
              </p>
            </div>
            <div 
              className="stat-card-accent" 
              style={{ background: card.gradient }}
            />
          </div>
        ))}
      </div>

      {/* Chart Section */}
      {stats.totalJobs > 0 && (
        <div className="chart-section">
          <div className="chart-card">
            <h4>Distribution Overview</h4>
            <div className="chart-wrapper">
              <Doughnut data={doughnutData} options={doughnutOptions} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobStats;
