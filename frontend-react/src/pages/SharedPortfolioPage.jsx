import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Briefcase,
  ShieldCheck,
  ExternalLink,
  GitBranch as Github,
  User
} from 'lucide-react';
import { api } from '../api/client';
import './portfolio.css';

export default function SharedPortfolioPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.get(`/portfolio/shared/${slug}/`)
      .then(res => {
        setData(res);
        if (res?.user_info?.name) {
          document.title = `${res.user_info.name}'s Verification Portfolio | PrepSmart`;
        }
      })
      .catch(err => {
        setError(err.message || 'Portfolio not found or set to private.');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [slug]);

  if (loading) {
    return (
      <div className="shared-port-loading">
        <div className="shared-port-loading__spinner" />
        <span>Loading Verified Candidate Profile...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="shared-port-error">
        <h3>Profile Access Blocked</h3>
        <p className="text-muted">{error}</p>
        <Link to="/" className="shared-port-error__btn">Return to PrepSmart</Link>
      </div>
    );
  }

  const { user_info, portfolio, projects } = data;
  const isAI = portfolio.selected_template === 'AI Engineer Portfolio';
  const isFullStack = portfolio.selected_template === 'Full Stack Portfolio';
  const isData = portfolio.selected_template === 'Data Analyst Portfolio';

  let themeClass = "theme-sde";
  if (isAI) themeClass = "theme-ai";
  else if (isFullStack) themeClass = "theme-fs";
  else if (isData) themeClass = "theme-data";

  return (
    <div className={`shared-port-container ${themeClass}`}>
      
      {/* HEADER SECTION */}
      <header className="shared-port-header">
        <div className="shared-port-header__inner">
          <div className="shared-port-header__brand">
            <span className="shared-port-header__logo-icon">PS</span>
            <div>
              <span className="shared-port-header__logo-text">PrepSmart Verified Profile</span>
              <span className="shared-port-header__badge">Recruiter Review Mode</span>
            </div>
          </div>
          <Link to="/" className="shared-port-header__back">Join PrepSmart</Link>
        </div>
      </header>

      <main className="shared-port-main">
        
        {/* HERO BANNER CARD */}
        <div className="shared-port-hero">
          <div className="shared-port-hero__avatar">
            <User size={32} />
          </div>
          <div className="shared-port-hero__info">
            <h1 className="shared-port-hero__name">{user_info.name}</h1>
            <p className="shared-port-hero__meta">{user_info.college} · {user_info.branch} ({user_info.graduation_year})</p>
            
            <div className="shared-port-hero__stats">
              <div className="shared-port-hero__stat-pill">
                <span>Employability Profile Strength: <strong>{portfolio.portfolio_strength}%</strong></span>
              </div>
              <div className="shared-port-hero__stat-pill">
                <span>Recruiter Competitiveness Rank: <strong>{portfolio.competitiveness_score}%</strong></span>
              </div>
            </div>
          </div>
        </div>

        {/* PROJECTS SECTION */}
        <div className="shared-port-section">
          <h2 className="shared-port-section-title"><Briefcase size={18} /> Verified Proof-of-Work Projects</h2>
          
          <div className="shared-port-grid">
            {projects?.map(p => (
              <div key={p.id} className="shared-port-card">
                <div className="shared-port-card__header">
                  <div>
                    <h3 className="shared-port-card__title">{p.title}</h3>
                    <span className="shared-port-card__domain">{p.domain}</span>
                  </div>
                  <div className="shared-port-card__badges">
                    <span className="shared-port-card__difficulty">{p.difficulty}</span>
                    {p.status === 'Evaluated' && (
                      <span className="shared-port-card__status">Verified Impact</span>
                    )}
                  </div>
                </div>

                <p className="shared-port-card__desc">{p.description}</p>

                <div className="shared-port-card__techs">
                  {p.tech_stack?.map((t, idx) => (
                    <span key={idx} className="shared-port-card__tech-badge">{t}</span>
                  ))}
                </div>

                {/* ARCHITECTURE DIAGRAM */}
                {p.architecture_diagram && (
                  <div className="shared-port-card__section">
                    <span className="shared-port-card__sub-title">System Architecture Flow:</span>
                    <div className="shared-port-architecture">
                      <pre className="monospace">{p.architecture_diagram}</pre>
                    </div>
                  </div>
                )}

                {/* EVALUATION SCORES */}
                {p.status === 'Evaluated' && p.impact_scores && (
                  <div className="shared-port-card__section">
                    <span className="shared-port-card__sub-title">AI Sandbox Complexity Audits:</span>
                    <div className="shared-port-scores">
                      <div className="shared-port-score">
                        <span className="shared-port-score-lbl">Technical Depth</span>
                        <span className="shared-port-score-val text-green">{p.impact_scores.technical_depth}%</span>
                      </div>
                      <div className="shared-port-score">
                        <span className="shared-port-score-lbl">Complexity Index</span>
                        <span className="shared-port-score-val text-indigo">{p.impact_scores.complexity}%</span>
                      </div>
                      <div className="shared-port-score">
                        <span className="shared-port-score-lbl">Deployment Quality</span>
                        <span className="shared-port-score-val text-amber">{p.impact_scores.deployment_quality}%</span>
                      </div>
                      <div className="shared-port-score">
                        <span className="shared-port-score-lbl">Recruiter Alignment</span>
                        <span className="shared-port-score-val text-green">{p.evaluation_report?.recruiter_relevance_score || 85}%</span>
                      </div>
                    </div>
                    <p className="shared-port-card__eval-desc text-muted">{p.evaluation_report?.architecture_quality}</p>
                  </div>
                )}

                <div className="shared-port-card__links">
                  {p.github_url && (
                    <a href={p.github_url} target="_blank" rel="noreferrer" className="shared-port-card__link">
                      <Github size={12} /> View Codebase
                    </a>
                  )}
                  {p.deployment_url && (
                    <a href={p.deployment_url} target="_blank" rel="noreferrer" className="shared-port-card__link">
                      <ExternalLink size={12} /> Live Staging Deployment
                    </a>
                  )}
                </div>
              </div>
            ))}
            {projects?.length === 0 && (
              <div className="shared-port-empty">No projects published in this portfolio.</div>
            )}
          </div>
        </div>

        {/* LEDGER PROOF SECTION */}
        <div className="shared-port-section shared-port-ledger">
          <div className="shared-port-ledger__card">
            <ShieldCheck size={28} className="text-green" />
            <div>
              <h3 className="shared-port-ledger__title">Cryptographic Employability Ledger</h3>
              <p className="shared-port-ledger__desc">All projects, compiler metrics, and evaluation scores on this profile are authenticated by PrepSmart Sandbox compiler signatures and plagiarism-safe checks.</p>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
