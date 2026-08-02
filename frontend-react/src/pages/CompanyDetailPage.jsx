import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Building2, ArrowLeft, ExternalLink, Activity, 
  MapPin, Clock, Briefcase, FileText, GitBranch, AlertCircle
} from 'lucide-react';
import {
  Radar as RechartsRadar, RadarChart, PolarGrid,
  PolarAngleAxis, ResponsiveContainer
} from 'recharts';
import { useApi } from '../hooks/useApi';
import './company-detail.css';

export default function CompanyDetailPage() {
  const { name } = useParams();
  const navigate = useNavigate();
  const { data: company, loading, error } = useApi(`/companies/${name}/details/`);

  useEffect(() => {
    if (company?.name) {
      document.title = `${company.name} | Careers`;
    }
  }, [company]);

  if (loading) {
    return (
      <div className="cd-page glass-panel" style={{ minHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="cd-loading">Loading company details...</div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="cd-page glass-panel" style={{ minHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px' }}>
        <AlertCircle size={48} color="var(--danger)" />
        <h2>Company Not Found</h2>
        <button className="cd-btn" onClick={() => navigate('/career/companies')}>Back to Companies</button>
      </div>
    );
  }

  return (
    <motion.div 
      className="cd-page"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <button className="cd-back-btn" onClick={() => navigate('/career/companies')}>
        <ArrowLeft size={16} /> Back to Companies
      </button>

      {/* HEADER SECTION */}
      <div className="cd-header glass-panel">
        <div className="cd-header-brand">
          <div className="cd-logo-wrap" style={{ background: company.color || 'var(--primary)' }}>
             <Building2 size={32} color="#fff" />
          </div>
          <div>
            <h1 className="cd-title">{company.full_name || company.name}</h1>
            <span className="cd-type-badge">{company.type}</span>
          </div>
        </div>

        <div className="cd-header-actions">
          {company.official_url && (
            <a href={company.official_url} target="_blank" rel="noreferrer" className="cd-btn cd-btn--primary">
              Official Portal <ExternalLink size={14} />
            </a>
          )}
        </div>
      </div>

      {/* MAIN GRID */}
      <div className="cd-grid">
        
        {/* LEFT COLUMN */}
        <div className="cd-main-col">
          
          {/* ELIGIBILITY & ROLES */}
          <section className="cd-section glass-panel">
            <h3 className="cd-section-title"><Briefcase size={16}/> Roles & Compensation</h3>
            <div className="cd-meta-flex">
              <div className="cd-meta-item">
                <span className="cd-meta-label">Package</span>
                <span className="cd-meta-value text-gradient font-bold">{company.package}</span>
              </div>
              <div className="cd-meta-item">
                <span className="cd-meta-label">Minimum CGPA</span>
                <span className="cd-meta-value">{company.min_cgpa}+</span>
              </div>
              <div className="cd-meta-item">
                <span className="cd-meta-label">Max Backlogs</span>
                <span className="cd-meta-value">{company.max_backlogs}</span>
              </div>
            </div>
            
            <div className="cd-roles-list mt-4">
              <span className="cd-meta-label mb-2 block">Typical Roles Offered:</span>
              <div className="cd-chips">
                {company.roles?.map(role => (
                  <span key={role} className="cd-chip">{role}</span>
                ))}
              </div>
            </div>
          </section>

          {/* REQUIREMENTS */}
          <section className="cd-section glass-panel">
            <h3 className="cd-section-title"><FileText size={16}/> Requirements & Eligibility Notes</h3>
            <ul className="cd-bullet-list">
              {company.eligibility_notes?.map((note, idx) => (
                <li key={idx}>{note}</li>
              ))}
            </ul>
          </section>

          {/* HIRING PROCESS */}
          <section className="cd-section glass-panel">
            <h3 className="cd-section-title"><GitBranch size={16}/> Hiring Process</h3>
            <p className="text-secondary text-sm mb-4">{company.source_note}</p>
            <ol className="cd-process-steps">
              {company.campus_focus?.map((step, idx) => (
                <li key={idx}>
                  <div className="cd-step-number">{idx + 1}</div>
                  <div className="cd-step-text">{step}</div>
                </li>
              ))}
            </ol>
          </section>

        </div>

        {/* RIGHT COLUMN */}
        <div className="cd-side-col">
          
          {/* READINESS RADAR */}
          <section className="cd-section glass-panel cd-section--center">
            <h3 className="cd-section-title"><Activity size={16}/> Readiness Profile</h3>
            <div className="cd-radar-container mt-4">
              <ResponsiveContainer width="100%" height={250}>
                <RadarChart data={[
                  { subject: 'DSA', A: company.skills?.DSA || 0, fullMark: 100 },
                  { subject: 'Sys Design', A: company.skills?.SystemDesign || 0, fullMark: 100 },
                  { subject: 'Projects', A: company.skills?.Projects || 0, fullMark: 100 },
                ]}>
                  <PolarGrid stroke="var(--border-secondary)"/>
                  <PolarAngleAxis dataKey="subject" tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} />
                  <RechartsRadar name="Score" dataKey="A" stroke={company.color || "#6366f1"} fill={company.color || "#6366f1"} fillOpacity={0.4} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="cd-readiness-score mt-4">
              <span className="cd-meta-label">Overall Match Score</span>
              <span className="cd-score-val" style={{ color: company.color || "#6366f1" }}>
                {company.readiness}%
              </span>
            </div>
          </section>
          
          {/* PREPARATION FOCUS */}
          <section className="cd-section glass-panel">
            <h3 className="cd-section-title">Preparation Focus</h3>
            <ul className="cd-bullet-list">
              {company.prep_focus?.map((focus, idx) => (
                <li key={idx}>{focus}</li>
              ))}
            </ul>
          </section>

        </div>
      </div>
    </motion.div>
  );
}
