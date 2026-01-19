import { useTheme } from '../context/ThemeContext';
import ThemeSwitcher from './ThemeSwitcher';
import '../styles/Navbar.css';

const Navbar = ({ currentPage, onNavigate }) => {
    const { theme } = useTheme();

    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'jobs', label: 'Jobs', icon: '🔍' },
        { id: 'activity', label: 'Activity', icon: '📋' },
        { id: 'settings', label: 'Settings', icon: '⚙️' }
    ];

    return (
        <nav className="navbar" style={{
            backgroundColor: theme.colors.headerBg,
            borderBottom: `1px solid ${theme.colors.border}`
        }}>
            <div className="navbar-brand">
                <span className="navbar-logo">📧</span>
                <h1 style={{ color: theme.colors.headerText }}>Freelance Mailer</h1>
            </div>

            <div className="navbar-links">
                {navItems.map(item => (
                    <button
                        key={item.id}
                        className={`nav-link ${currentPage === item.id ? 'active' : ''}`}
                        onClick={() => onNavigate(item.id)}
                        style={{
                            color: currentPage === item.id ? theme.colors.primary : theme.colors.headerText,
                            backgroundColor: currentPage === item.id ? theme.colors.surface : 'transparent'
                        }}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        <span className="nav-label">{item.label}</span>
                    </button>
                ))}
            </div>

            <div className="navbar-actions">
                <ThemeSwitcher />
            </div>
        </nav>
    );
};

export default Navbar;
