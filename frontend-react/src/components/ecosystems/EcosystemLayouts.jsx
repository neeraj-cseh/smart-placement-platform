import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { 
  Route, Brain, Timer, 
  Terminal, Target, Trophy, 
  Bot, Map,
  Building2, FileText, Briefcase,
  ShieldCheck, Award, Users, User
} from 'lucide-react';
import './ecosystem-layouts.css';

import LayoutComponent from '../Layout';

// Reusable Top Navigation Component
const EcosystemNav = ({ title, description, links }) => {
  return (
    <LayoutComponent title={title} subtitle={description}>
      <div className="ecosystem-container">
        <nav className="ecosystem-nav" style={{ marginBottom: '20px' }}>
          {links.map((link) => (
            <NavLink 
              key={link.to} 
              to={link.to} 
              className={({ isActive }) => `ecosystem-nav-link ${isActive ? 'active' : ''}`}
            >
              <link.icon size={16} />
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="ecosystem-content">
        <Outlet />
      </div>
    </LayoutComponent>
  );
};

export const PrepLayout = () => {
  return (
    <EcosystemNav 
      title="Prep" 
      description="Your structured learning and practice environment."
      links={[
        { label: 'Topic Journey', to: '/prep/journey', icon: Route },
        { label: 'Roadmaps', to: '/prep/roadmaps', icon: Map },
        { label: 'Milestones', to: '/prep/milestones', icon: Trophy }
      ]}
    />
  );
};

export const CodeLabLayout = () => {
  // We want to hide the secondary nav if the user is in the fullscreen ProblemSolvingPage
  const location = useLocation();
  const isSolving = location.pathname.split('/').length > 3 && location.pathname.includes('/code-lab/arena/');
  
  if (isSolving) {
    return <Outlet />; // Fullscreen takeover
  }

  return (
    <EcosystemNav 
      title="Code Lab" 
      description="The premium developer environment for algorithmic mastery."
      links={[
        { label: 'Problem Arena', to: '/code-lab/arena', icon: Target },
        { label: 'Workspace', to: '/code-lab/workspace', icon: Terminal },
        { label: 'Contests', to: '/code-lab/contests', icon: Trophy }
      ]}
    />
  );
};

export const AICoachLayout = () => {
  return (
    <div className="ecosystem-content" style={{ padding: '20px 0' }}>
      <Outlet />
    </div>
  );
};

export const CareerLayout = () => {
  return (
    <EcosystemNav 
      title="Career" 
      description="Track placements, hone your resume, and build your portfolio."
      links={[
        { label: 'Companies', to: '/career/companies', icon: Building2 }
      ]}
    />
  );
};

export const ProfileLayout = () => {
  return (
    <EcosystemNav 
      title="Profile" 
      description="Manage your credentials, verifications, and network."
      links={[
        { label: 'Edit Profile', to: '/profile/me', icon: User },
        { label: 'Skills Passport', to: '/profile/passport', icon: ShieldCheck }
      ]}
    />
  );
};
