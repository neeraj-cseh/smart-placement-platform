import { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Building2, Briefcase, Zap, CheckCircle2,
  XCircle, ArrowRight, ShieldCheck,
  Radar, Activity, Users, Star, 
  MapPin, Clock, Search, Filter, Cpu, Database, Layout, FileText, GitBranch
} from 'lucide-react';

import { useApi } from '../hooks/useApi';
import './companies.css';

// Motion variants
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } }
};
const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } }
};

export default function CompaniesPage() {
  const { data, loading, error, mutate } = useApi('/companies/');
  const navigate = useNavigate();
  const [cgpa, setCgpa] = useState('8.5');
  const [backlogs, setBacklogs] = useState('0');
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  const [selectedCompany, setSelectedCompany] = useState(null);

  // Set title
  useEffect(() => {
    document.title = "Companies Hub | Career";
  }, []);

  const handleDiagnose = useCallback(() => {
    // In a real app, this would trigger a refetch with the new params
    mutate('post', { action: 'diagnose', cgpa, backlogs });
  }, [cgpa, backlogs, mutate]);

  const companies = data?.companies || [];
  
  const dashboard = {
    total_tracked: data?.summary?.target_count || companies.length,
    ready_companies: companies.filter(c => c.is_eligible).length,
    active_pipelines: data?.summary?.source_count || 0
  };

  const filteredCompanies = useMemo(() => {
    return companies.filter(c => {
      const matchSearch = c.name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchFilter = activeFilter === 'All' || c.type === activeFilter;
      return matchSearch && matchFilter;
    });
  }, [companies, searchTerm, activeFilter]);

  if (loading && !data) {
    return (
      <div className="co-skeleton">
        <div className="co-skeleton__hero"></div>
        <div className="co-skeleton__grid">
          <div className="co-skeleton__card"></div>
          <div className="co-skeleton__card"></div>
          <div className="co-skeleton__card"></div>
        </div>
      </div>
    );
  }

  return (
    <motion.div className="co-page" variants={stagger} initial="hidden" animate="visible">
        
        {/* HERO SECTION */}
        <motion.section className="co-hero glass-panel" variants={fadeUp}>
          <div className="co-hero__content">
            <h1 className="co-hero__title">Target Your Dream Role</h1>
            <p className="co-hero__subtitle">Your profile currently maps to {dashboard.ready_companies} premium companies. Optimize your skills to unlock more opportunities.</p>
            
            <div className="co-hero__stats">
              <div className="co-hero__stat">
                <span className="co-hero__stat-val">{dashboard.total_tracked}</span>
                <span className="co-hero__stat-label">Tracked</span>
              </div>
              <div className="co-hero__stat">
                <span className="co-hero__stat-val text-gradient">{dashboard.ready_companies}</span>
                <span className="co-hero__stat-label">Ready</span>
              </div>
              <div className="co-hero__stat">
                <span className="co-hero__stat-val text-blue">{dashboard.active_pipelines}</span>
                <span className="co-hero__stat-label">Pipelines</span>
              </div>
            </div>
          </div>
          
          <div className="co-hero__visual">
            <div className="co-hero__orb co-hero__orb--1"></div>
            <div className="co-hero__orb co-hero__orb--2"></div>
            <div className="co-hero__glass-card">
              <Activity className="co-hero__icon" />
              <span>AI Engine Active</span>
            </div>
          </div>
        </motion.section>

        {/* DIAGNOSTICS & FILTER BAR */}
        <motion.section className="co-toolbar" variants={fadeUp}>
          <div className="co-diagnostics glass-panel">
            <h3 className="co-toolbar__title"><ShieldCheck size={18}/> Eligibility Engine</h3>
            <div className="co-diagnostics__inputs">
              <div className="co-input-group">
                <label>Current CGPA</label>
                <input type="number" step="0.1" value={cgpa} onChange={e => setCgpa(e.target.value)} />
              </div>
              <div className="co-input-group">
                <label>Active Backlogs</label>
                <input type="number" value={backlogs} onChange={e => setBacklogs(e.target.value)} />
              </div>
              <button className="co-btn co-btn--primary" onClick={handleDiagnose}>
                <Zap size={14}/> Diagnose
              </button>
            </div>
          </div>

          <div className="co-filters glass-panel">
            <div className="co-search">
              <Search size={16} />
              <input 
                type="text" 
                placeholder="Search companies..." 
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="co-filter-chips">
              {['All', 'Product', 'Service'].map(f => (
                <button 
                  key={f} 
                  className={`co-chip ${activeFilter === f ? 'active' : ''}`}
                  onClick={() => setActiveFilter(f)}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </motion.section>

        {/* COMPANIES GRID */}
        <motion.section className="co-grid" variants={fadeUp}>
          <AnimatePresence>
            {filteredCompanies.map(company => (
              <motion.div 
                key={company.id} 
                className="co-card glass-panel"
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2 }}
              >
                <div className="co-card__header">
                  <div className="co-card__brand">
                    <div className="co-card__logo"><Building2 size={20} /></div>
                    <div>
                      <h3 className="co-card__name">{company.name}</h3>
                      <span className="co-card__type">{company.type}</span>
                    </div>
                  </div>
                  <div className={`co-badge ${company.is_eligible ? 'co-badge--success' : 'co-badge--danger'}`}>
                    {company.is_eligible ? <CheckCircle2 size={12}/> : <XCircle size={12}/>}
                    {company.is_eligible ? 'Eligible' : 'Locked'}
                  </div>
                </div>

                <div className="co-card__meta">
                  <div className="co-meta-item"><Briefcase size={14}/> {company.package}</div>
                  <div className="co-meta-item"><Users size={14}/> {company.roles.length} Roles</div>
                </div>

                <div className="co-card__readiness">
                  <div className="co-readiness-label">
                    <span>Readiness Score</span>
                    <span className="text-gradient font-bold">{company.readiness}%</span>
                  </div>
                  <div className="co-progress-track">
                    <div className="co-progress-fill" style={{ width: `${company.readiness}%` }}></div>
                  </div>
                </div>

                <div className="mt-4">
                  <button className="co-btn co-btn--outline w-full" onClick={() => navigate(`/career/companies/${company.name}`)}>
                    View Full Details <ArrowRight size={14}/>
                  </button>
                </div>

              </motion.div>
            ))}
          </AnimatePresence>
        </motion.section>

    </motion.div>
  );
}
