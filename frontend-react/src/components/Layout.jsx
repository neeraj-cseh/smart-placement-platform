import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Route,
  Brain,
  Timer,
  Code2,
  Bot,
  BarChart3,
  Building2,
  User,
  Settings,
  Shield,
  LogOut,
  Sun,
  Moon,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import './layout.css';

const navItems = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Learning Path', to: '/learning-path', icon: Route },
  { label: 'Practice', to: '/practice', icon: Brain },
  { label: 'Mock Tests', to: '/mock-tests', icon: Timer },
  { label: 'Code Editor', to: '/code-editor', icon: Code2 },
  { label: 'AI Interview', to: '/ai-interview', icon: Bot },
  { label: 'Analytics', to: '/analytics', icon: BarChart3 },
  { label: 'Companies', to: '/companies', icon: Building2 },
];

function Sidebar({ isOpen, onClose }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [accountOpen, setAccountOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <>
      {isOpen && <div className="sidebar__overlay" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`}>
        <div className="sidebar__header">
          <Link to="/" className="sidebar__logo">
            <span className="sidebar__logo-icon">PS</span>
            <span className="sidebar__logo-text">PrepSmart</span>
          </Link>
          <button className="sidebar__close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar__nav">
          {navItems.map((item) => {
            const isActive = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`sidebar__link ${isActive ? 'sidebar__link--active' : ''}`}
                onClick={() => onClose()}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar__footer">
          <button className="sidebar__theme-btn" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            <span>{theme === 'dark' ? 'Light mode' : 'Dark mode'}</span>
          </button>

          <div className="sidebar__account">
            <button
              className="sidebar__account-btn"
              onClick={() => setAccountOpen(!accountOpen)}
            >
              <div className="sidebar__avatar">
                {user?.initials || 'U'}
              </div>
              <div className="sidebar__account-info">
                <span className="sidebar__account-name">{user?.name || 'User'}</span>
                <span className="sidebar__account-email">{user?.email || ''}</span>
              </div>
            </button>

            {accountOpen && (
              <div className="sidebar__account-menu">
                <Link to="/profile" className="sidebar__menu-item" onClick={() => { setAccountOpen(false); onClose(); }}>
                  <User size={16} />
                  <span>Profile</span>
                </Link>
                <Link to="/settings" className="sidebar__menu-item" onClick={() => { setAccountOpen(false); onClose(); }}>
                  <Settings size={16} />
                  <span>Settings</span>
                </Link>
                {user?.is_admin && (
                  <Link to="/admin" className="sidebar__menu-item" onClick={() => { setAccountOpen(false); onClose(); }}>
                    <Shield size={16} />
                    <span>Admin</span>
                  </Link>
                )}
                <button className="sidebar__menu-item sidebar__menu-item--logout" onClick={handleLogout}>
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}

function Topbar({ onMenuClick, title, subtitle }) {
  return (
    <header className="topbar">
      <button className="topbar__menu-btn" onClick={onMenuClick}>
        <Menu size={20} />
      </button>
      <div className="topbar__content">
        <h1 className="topbar__title">{title}</h1>
        {subtitle && <p className="topbar__subtitle">{subtitle}</p>}
      </div>
    </header>
  );
}

function Layout({ children, title, subtitle }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="app-main">
        <Topbar onMenuClick={() => setSidebarOpen(true)} title={title} subtitle={subtitle} />
        <div className="app-content">{children}</div>
      </main>
    </div>
  );
}

export default Layout;