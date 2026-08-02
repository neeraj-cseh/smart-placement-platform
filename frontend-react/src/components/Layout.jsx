import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Brain,
  Terminal,
  Bot,
  Briefcase,
  User,
  Settings,
  Shield,
  LogOut,
  Sun,
  Moon,
  ChevronLeft,
  X,
  Menu,
  PanelLeft,
  Users,
  Award,
  BookOpen,
  Layers,
  ClipboardList,
  Building2,
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import './layout.css';


const adminNavItems = [
  { label: 'Users', to: '/admin?tab=users', icon: Users },
  { label: 'Tracks', to: '/admin?tab=tracks', icon: Award },
  { label: 'Topics', to: '/admin?tab=topics', icon: BookOpen },
  { label: 'Questions', to: '/admin?tab=questions', icon: Layers },
  { label: 'Mock Tests', to: '/admin?tab=tests', icon: ClipboardList },
  { label: 'Companies', to: '/admin?tab=companies', icon: Building2 },
];

const navItems = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Prep', to: '/prep', icon: Brain },
  { label: 'Code Lab', to: '/code-lab', icon: Terminal },
  { label: 'AI Coach', to: '/ai', icon: Bot },
  { label: 'Career', to: '/career', icon: Briefcase },
  { label: 'Profile', to: '/profile', icon: User },
];

const MotionLink = motion(Link);

function SidebarLink({ item, isActive, isMinimized, sidebarHovered, onClick }) {
  const [isHovered, setIsHovered] = useState(false);
  const isExpanded = !isMinimized || sidebarHovered;

  return (
    <MotionLink
      layout
      to={item.to}
      className={`sidebar__link ${isActive ? 'sidebar__link--active' : ''}`}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ position: 'relative', display: 'flex', alignItems: 'center' }}
    >
      {/* Floating Navigation Pill */}
      {isActive && (
        <motion.div
          layoutId="active-nav-pill"
          className="sidebar__link-pill"
          transition={{ type: 'spring', stiffness: 380, damping: 30 }}
        />
      )}

      {/* Hover Background Accent */}
      {!isActive && isHovered && (
        <motion.div
          layoutId="hover-nav-pill"
          className="sidebar__link-hover-pill"
          transition={{ type: 'spring', stiffness: 400, damping: 32 }}
        />
      )}

      {/* Centered Icon Wrapper */}
      <motion.div
        className="sidebar__link-icon-wrapper"
        animate={{
          scale: isHovered ? 1.12 : 1,
          rotate: isHovered ? 6 : 0,
        }}
        transition={{ type: 'spring', stiffness: 400, damping: 15 }}
      >
        <item.icon size={20} />
      </motion.div>

      {/* Label text that expands and fades */}
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.span
            className="sidebar__link-text"
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: 'auto' }}
            exit={{ opacity: 0, width: 0 }}
            transition={{ type: 'spring', stiffness: 450, damping: 30 }}
            style={{ overflow: 'hidden', whiteSpace: 'nowrap', display: 'inline-block' }}
          >
            {item.label}
          </motion.span>
        )}
      </AnimatePresence>

      {/* Floating Animated Tooltip (only when sidebar is fully minimized and not hovered) */}
      <AnimatePresence>
        {isMinimized && !sidebarHovered && isHovered && (
          <motion.div
            initial={{ opacity: 0, x: -15, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: -15, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 550, damping: 22 }}
            className="sidebar__tooltip"
          >
            {item.label}
          </motion.div>
        )}
      </AnimatePresence>
    </MotionLink>
  );
}

function SidebarThemeToggle({ theme, toggleTheme, isMinimized, sidebarHovered }) {
  const [isHovered, setIsHovered] = useState(false);
  const isExpanded = !isMinimized || sidebarHovered;

  return (
    <motion.button
      layout
      className="sidebar__theme-btn"
      onClick={toggleTheme}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      aria-label="Toggle theme"
      style={{ position: 'relative', display: 'flex', alignItems: 'center' }}
    >
      {isHovered && (
        <motion.div
          layoutId="hover-nav-pill"
          className="sidebar__link-hover-pill"
          transition={{ type: 'spring', stiffness: 400, damping: 32 }}
        />
      )}

      <motion.div
        className="sidebar__link-icon-wrapper"
        animate={{
          scale: isHovered ? 1.12 : 1,
          rotate: isHovered ? 15 : 0,
        }}
        transition={{ type: 'spring', stiffness: 400, damping: 15 }}
      >
        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      </motion.div>

      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.span
            className="sidebar__link-text"
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: 'auto' }}
            exit={{ opacity: 0, width: 0 }}
            transition={{ type: 'spring', stiffness: 450, damping: 30 }}
            style={{ overflow: 'hidden', whiteSpace: 'nowrap', display: 'inline-block' }}
          >
            {theme === 'dark' ? 'Light mode' : 'Dark mode'}
          </motion.span>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isMinimized && !sidebarHovered && isHovered && (
          <motion.div
            initial={{ opacity: 0, x: -15, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: -15, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 550, damping: 22 }}
            className="sidebar__tooltip"
          >
            {theme === 'dark' ? 'Light mode' : 'Dark mode'}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}

function SidebarAccount({ user, handleLogout, isMinimized, sidebarHovered, onClose, hoverExpand, toggleHoverExpand }) {
  const [accountOpen, setAccountOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const isExpanded = !isMinimized || sidebarHovered;

  return (
    <motion.div layout className="sidebar__account" style={{ position: 'relative' }}>
      <motion.button
        layout
        className={`sidebar__account-btn ${accountOpen ? 'sidebar__account-btn--active' : ''}`}
        onClick={() => setAccountOpen(!accountOpen)}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="sidebar__avatar-container">
          <div className="sidebar__avatar">
            {user?.initials || 'U'}
          </div>
          {/* Glowing Readiness indicator */}
          <span className="sidebar__avatar-status" />
        </div>

        <AnimatePresence initial={false}>
          {isExpanded && (
            <motion.div
              className="sidebar__account-info"
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              transition={{ type: 'spring', stiffness: 450, damping: 30 }}
              style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}
            >
              <span className="sidebar__account-name">{user?.name || 'User'}</span>
              <span className="sidebar__account-email">{user?.email || ''}</span>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      <AnimatePresence>
        {isMinimized && !sidebarHovered && isHovered && (
          <motion.div
            initial={{ opacity: 0, x: -15, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: -15, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 550, damping: 22 }}
            className="sidebar__tooltip"
          >
            {user?.name || 'Account'}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {accountOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.92, y: 10 }}
            transition={{ type: 'spring', stiffness: 450, damping: 25 }}
            className="sidebar__account-menu"
          >
            <Link to="/settings" className="sidebar__menu-item" onClick={() => { setAccountOpen(false); onClose(); }}>
              <Settings size={16} />
              <span>Settings</span>
            </Link>
            <button 
              className="sidebar__menu-item" 
              onClick={() => { toggleHoverExpand(); }}
            >
              <PanelLeft size={16} />
              <span>Hover Expand: {hoverExpand ? 'ON' : 'OFF'}</span>
            </button>

            <button className="sidebar__menu-item sidebar__menu-item--logout" onClick={handleLogout}>
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function Sidebar({ isOpen, onClose, isMinimized, onToggleMinimize, hoverExpand, toggleHoverExpand }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarHovered, setSidebarHovered] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isExpanded = !isMinimized || sidebarHovered;

  return (
    <>
      {isOpen && <div className="sidebar__overlay" onClick={onClose} />}
      <aside
        className={`sidebar ${isOpen ? 'sidebar--open' : ''} ${isMinimized ? 'sidebar--minimized' : ''} ${sidebarHovered ? 'sidebar--hovered' : ''}`}
        onMouseEnter={() => {
          if (hoverExpand) setSidebarHovered(true);
        }}
        onMouseLeave={() => {
          setSidebarHovered(false);
        }}
      >
        <div className="sidebar__header">
          <motion.div 
            layout 
            className="sidebar__logo-wrapper"
          >
            <Link to="/" className="sidebar__logo" onClick={() => onClose()}>
              <motion.div layout className="sidebar__logo-icon">PS</motion.div>
              <AnimatePresence>
                {isExpanded && (
                  <motion.span
                    layout
                    className="sidebar__logo-text"
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    transition={{ type: 'spring', stiffness: 450, damping: 30 }}
                    style={{ overflow: 'hidden', whiteSpace: 'nowrap', display: 'inline-block' }}
                  >
                    PrepSmart
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          </motion.div>

          <AnimatePresence>
            {isExpanded && (
              <motion.button
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.15 }}
                className="sidebar__toggle-btn"
                onClick={onToggleMinimize}
                aria-label="Toggle sidebar"
              >
                <motion.div
                  animate={{ rotate: isMinimized ? 180 : 0 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                >
                  <ChevronLeft size={18} />
                </motion.div>
              </motion.button>
            )}
          </AnimatePresence>
          
          <button className="sidebar__close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar__nav">
          {(user?.is_admin ? adminNavItems : navItems).map((item) => {
            const isActive = user?.is_admin ? (location.search === '?' + item.to.split('?')[1] || (location.search === '' && item.to.includes('tab=users'))) : (item.to === '/' ? location.pathname === '/' : location.pathname.startsWith(item.to));
            return (
              <SidebarLink
                key={item.to}
                item={item}
                isActive={isActive}
                isMinimized={isMinimized}
                sidebarHovered={sidebarHovered}
                onClick={onClose}
              />
            );
          })}
        </nav>

        <div className="sidebar__footer">
          <SidebarThemeToggle
            theme={theme}
            toggleTheme={toggleTheme}
            isMinimized={isMinimized}
            sidebarHovered={sidebarHovered}
          />

          <SidebarAccount
            user={user}
            handleLogout={handleLogout}
            isMinimized={isMinimized}
            sidebarHovered={sidebarHovered}
            onClose={onClose}
            hoverExpand={hoverExpand}
            toggleHoverExpand={toggleHoverExpand}
          />
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
  const [isMinimized, setIsMinimized] = useState(() => {
    return localStorage.getItem('prepsmart_sidebar_minimized') === 'true';
  });
  const [hoverExpand, setHoverExpand] = useState(() => {
    return localStorage.getItem('prepsmart_sidebar_hover_expand') !== 'false';
  });

  const toggleMinimize = () => {
    setIsMinimized(prev => {
      const next = !prev;
      localStorage.setItem('prepsmart_sidebar_minimized', String(next));
      return next;
    });
  };

  const toggleHoverExpand = () => {
    setHoverExpand(prev => {
      const next = !prev;
      localStorage.setItem('prepsmart_sidebar_hover_expand', String(next));
      return next;
    });
  };

  return (
    <div className={`app-layout ${isMinimized ? 'app-layout--minimized' : ''}`}>
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        isMinimized={isMinimized}
        onToggleMinimize={toggleMinimize}
        hoverExpand={hoverExpand}
        toggleHoverExpand={toggleHoverExpand}
      />
      <main className="app-main">
        <Topbar onMenuClick={() => setSidebarOpen(true)} title={title} subtitle={subtitle} />
        <div className="app-content">{children}</div>
      </main>
    </div>
  );
}

export default Layout;