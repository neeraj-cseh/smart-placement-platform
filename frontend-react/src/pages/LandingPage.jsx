import { Link } from 'react-router-dom';
import { Sun, Moon, ArrowRight, Shield, Brain, BarChart3, Code2, Timer, Bot, Building2 } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { useTheme } from '../contexts/ThemeContext';
import Button from '../components/ui/Button';
import heroImage from '../assets/hero.png';
import './landing.css';

const iconMap = {
  learning: Brain,
  tests: Timer,
  code: Code2,
  analytics: BarChart3,
  companies: Building2,
  admin: Shield,
};

function LandingPage() {
  const { data, loading } = useApi('/landing/');
  const { theme, toggleTheme } = useTheme();

  if (loading) {
    return (
      <div className="landing">
        <div className="landing__loading">Loading...</div>
      </div>
    );
  }

  if (!data) return null;

  const { brand, hero, metrics, features, feature_heading, workflow } = data;

  return (
    <div className="landing">
      <header className="landing__header">
        <Link to="/" className="landing__logo">
          <span className="landing__logo-icon">{brand.initials}</span>
          <span>{brand.name}</span>
        </Link>
        <div className="landing__header-actions">
          <button type="button" className="landing__theme-btn" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <Link to={hero.secondary_action.href}>
            <Button variant="secondary" size="sm">{hero.secondary_action.label}</Button>
          </Link>
          <Link to={hero.primary_action.href}>
            <Button variant="primary" size="sm">{hero.primary_action.label}</Button>
          </Link>
        </div>
      </header>

      <section className="landing__hero">
        <div className="landing__hero-content">
          <span className="landing__eyebrow">{hero.eyebrow}</span>
          <h1 className="landing__title">{hero.title}</h1>
          <p className="landing__subtitle">{hero.subtitle}</p>
          <div className="landing__hero-actions">
            <Link to={hero.primary_action.href}>
              <Button variant="primary" size="lg" icon={ArrowRight}>{hero.primary_action.label}</Button>
            </Link>
            <Link to={hero.secondary_action.href}>
              <Button variant="secondary" size="lg">{hero.secondary_action.label}</Button>
            </Link>
          </div>
        </div>

        <div className="landing__hero-media">
          <img src={heroImage} alt={`${brand.name} dashboard preview`} />
          <div className="landing__metric-panel">
            {metrics.slice(0, 4).map((metric) => (
              <div key={metric.label} className="landing__stat">
                <span className="landing__stat-value">{metric.value}</span>
                <span className="landing__stat-label">{metric.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="landing__features">
        <div className="landing__section-head">
          <h2>{feature_heading}</h2>
        </div>
        <div className="landing__features-grid">
          {features.map((feature) => {
            const Icon = iconMap[feature.id] || Bot;
            return (
              <div key={feature.id} className="landing__feature-card">
                <div className="landing__feature-icon">
                  <Icon size={22} />
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      <section className="landing__workflow">
        {workflow.map((item) => (
          <div key={item.step} className="landing__workflow-item">
            <span>{item.step}</span>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </div>
        ))}
      </section>
    </div>
  );
}

export default LandingPage;
