import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Briefcase, PlusCircle, CheckCircle2, Circle,
  Columns, Layers, Terminal, Target, Code, CheckSquare, ChevronRight, Zap
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';
import { useApi } from '../hooks/useApi';
import Mermaid from '../components/ui/Mermaid';
import './portfolio.css';

const fadeUp = {
  hidden: { opacity: 0, y: 15 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
};
const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } }
};

export default function PortfolioPage() {
  const { data, loading } = useApi('/portfolio/');
  const [activeTab, setActiveTab] = useState('kanban');
  const [generating, setGenerating] = useState(false);
  const [showGenModal, setShowGenModal] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState(null);

  useEffect(() => {
    document.title = "Portfolio Hub | Career";
  }, []);
  
  useEffect(() => {
    if (data?.projects?.length && !selectedProjectId) {
      setSelectedProjectId(data.projects[0].id);
    }
  }, [data, selectedProjectId]);

  const handleGenerate = () => {
    setGenerating(true);
    setTimeout(() => {
      setGenerating(false);
      setShowGenModal(false);
    }, 1500);
  };

  const portfolio = data?.portfolio || {
    portfolio_strength: 0,
    analytics: { views: [], recruiter_clicks: [], timeline: [] },
    copilot_advice: null
  };
  
  const projects = data?.projects || [];
  const completedProjects = projects.filter(p => p.status === 'Evaluated' || p.status === 'Completed').length;
  const activeProjects = projects.filter(p => p.status === 'Active').length;

  const chartData = useMemo(() => {
    const timeline = portfolio.analytics?.timeline || [];
    const views = portfolio.analytics?.views || [];
    const clicks = portfolio.analytics?.recruiter_clicks || [];
    return timeline.map((date, i) => ({
      name: date.split('-').slice(1).join('/'),
      views: views[i] || 0,
      clicks: clicks[i] || 0
    }));
  }, [portfolio.analytics]);
  
  const selectedProject = projects.find(p => p.id === selectedProjectId) || projects[0];

  if (loading && !data) {
    return (
      <div className="port-skeleton">
        <div className="port-skeleton__hero"></div>
      </div>
    );
  }

  return (
    <motion.div className="port-page" variants={stagger} initial="hidden" animate="visible">
        
        {/* HERO */}
        <motion.section className="port-hero glass-panel" variants={fadeUp}>
          <div className="port-hero__content">
            <h1 className="port-hero__title">Portfolio Command Center</h1>
            <p className="port-hero__subtitle">Your portfolio is stronger than {portfolio.portfolio_strength}% of peers. Generate a new AI-guided project to reach the top 10%.</p>
            <button className="port-btn port-btn--primary" onClick={() => setShowGenModal(true)}>
              <PlusCircle size={16}/> Generate Project Blueprint
            </button>
          </div>
          
          <div className="port-hero__stats">
            <div className="port-stat-card">
              <span className="port-stat-val text-blue">{portfolio.portfolio_strength}%</span>
              <span className="port-stat-label">Strength</span>
            </div>
            <div className="port-stat-card">
              <span className="port-stat-val text-green">{completedProjects}</span>
              <span className="port-stat-label">Completed</span>
            </div>
            <div className="port-stat-card">
              <span className="port-stat-val text-amber">{activeProjects}</span>
              <span className="port-stat-label">Active</span>
            </div>
          </div>
        </motion.section>

        {/* WORKSPACE & ANALYTICS */}
        <div className="port-grid">
          
          {/* Active Project Workspace */}
          <motion.section className="port-card glass-panel port-workspace" variants={fadeUp}>
            {projects.length > 0 ? (
              <>
                <div className="port-card__header">
                  <div className="port-project-selector">
                    <h3><Terminal size={18} className="text-blue" /> Active Project</h3>
                    <select 
                      className="port-select"
                      value={selectedProjectId || ''} 
                      onChange={e => setSelectedProjectId(parseInt(e.target.value))}
                    >
                      {projects.map(p => (
                        <option key={p.id} value={p.id}>{p.title}</option>
                      ))}
                    </select>
                  </div>
                  <div className="port-tabs">
                    <button className={`port-tab ${activeTab === 'kanban' ? 'active' : ''}`} onClick={() => setActiveTab('kanban')}>
                      <Columns size={14}/> Kanban
                    </button>
                    <button className={`port-tab ${activeTab === 'architecture' ? 'active' : ''}`} onClick={() => setActiveTab('architecture')}>
                      <Layers size={14}/> Architecture
                    </button>
                  </div>
                </div>
                
                <div className="port-workspace-content">
                  {activeTab === 'kanban' ? (
                    <div className="port-kanban">
                      <div className="port-kanban-col">
                        <h4>To Do</h4>
                        {selectedProject?.kanban_board?.todo?.map(t => (
                          <div key={t.id} className="port-kanban-item"><Circle size={14} className="text-muted"/> {t.title}</div>
                        ))}
                      </div>
                      <div className="port-kanban-col">
                        <h4>In Progress</h4>
                        {selectedProject?.kanban_board?.in_progress?.map(t => (
                          <div key={t.id} className="port-kanban-item border-blue"><CheckCircle2 size={14} className="text-blue"/> {t.title}</div>
                        ))}
                      </div>
                      <div className="port-kanban-col">
                        <h4>Done</h4>
                        {selectedProject?.kanban_board?.done?.map(t => (
                          <div key={t.id} className="port-kanban-item border-green opacity-50"><CheckCircle2 size={14} className="text-green"/> {t.title}</div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="port-architecture">
                        {selectedProject?.architecture_diagram ? (
                          <Mermaid chart={selectedProject.architecture_diagram} />
                        ) : (
                          <div className="port-empty-state">No architecture diagram provided.</div>
                        )}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="port-empty-state">
                <Code size={48} className="text-muted" />
                <p>No projects found. Generate a new blueprint to get started.</p>
              </div>
            )}
          </motion.section>

          {/* Right Column: Analytics & Copilot */}
          <div className="port-right-col">
            {/* Analytics */}
            <motion.section className="port-card glass-panel" variants={fadeUp}>
              <div className="port-card__header">
                <h3><Target size={18} className="text-green" /> Recruiter Impressions</h3>
              </div>
              <div className="port-chart-wrap">
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
                    <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-2)', borderRadius: '8px' }} />
                    <Area type="monotone" dataKey="views" stroke="#10b981" fillOpacity={1} fill="url(#colorViews)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="port-analytics-summary">
                <div className="port-summary-item">
                  <span className="port-summary-val">{portfolio.analytics?.views?.reduce((a, b) => a + b, 0) || 0}</span>
                  <span className="port-summary-label">Total Views</span>
                </div>
                <div className="port-summary-item">
                  <span className="port-summary-val">{portfolio.analytics?.recruiter_clicks?.reduce((a, b) => a + b, 0) || 0}</span>
                  <span className="port-summary-label">Recruiter Clicks</span>
                </div>
              </div>
            </motion.section>

            {/* AI Copilot Advice */}
            {portfolio.copilot_advice && (
              <motion.section className="port-card glass-panel port-copilot" variants={fadeUp}>
                <div className="port-card__header">
                  <h3><Zap size={18} className="text-amber" /> AI Copilot Advice</h3>
                </div>
                <div className="port-copilot-content">
                  <p className="port-copilot-advice">{portfolio.copilot_advice.advice}</p>
                  <p className="port-copilot-strategy"><strong>Strategy:</strong> {portfolio.copilot_advice.strategy}</p>
                  
                  {portfolio.copilot_advice.checklist?.length > 0 && (
                    <div className="port-copilot-checklist">
                      <h4>Action Items</h4>
                      {portfolio.copilot_advice.checklist.map(item => (
                        <div key={item.id} className={`port-copilot-task ${item.done ? 'done' : ''}`}>
                          {item.done ? <CheckSquare size={16} className="text-green"/> : <Circle size={16} className="text-muted"/>}
                          <span>{item.task}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </motion.section>
            )}
          </div>
        </div>

        {/* Generate Project Modal */}
        <AnimatePresence>
          {showGenModal && (
            <motion.div 
              className="port-modal-overlay"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            >
              <motion.div 
                className="port-modal glass-panel"
                initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              >
                <h3>Generate AI Project Blueprint</h3>
                <div className="port-modal-form">
                  <div className="port-input-group">
                    <label>Domain</label>
                    <select>
                      <option>Full-stack Web</option>
                      <option>Machine Learning</option>
                      <option>Fintech</option>
                    </select>
                  </div>
                  <div className="port-input-group">
                    <label>Difficulty</label>
                    <select>
                      <option>Advanced (Impress FAANG)</option>
                      <option>Intermediate (Core Skills)</option>
                    </select>
                  </div>
                  <div className="port-modal-actions">
                    <button className="port-btn port-btn--outline" onClick={() => setShowGenModal(false)}>Cancel</button>
                    <button className="port-btn port-btn--primary" onClick={handleGenerate} disabled={generating}>
                      {generating ? 'Generating Blueprint...' : 'Generate'}
                    </button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
        
    </motion.div>
  );
}
