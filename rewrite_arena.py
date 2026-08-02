import os

css_content = """/* PREMIUM PROBLEM ARENA - EDGE-TO-EDGE DENSE IDE TIER */
:root {
  /* Deep Space Theme */
  --pa-bg: var(--bg-primary, #050505);
  --pa-surface: var(--bg-card, #0e0e11);
  --pa-surface-hover: var(--bg-hover, #18181c);
  --pa-surface-glass: rgba(14, 14, 17, 0.6);
  --pa-border: var(--border-primary, #222226);
  --pa-border-light: #333338;
  --pa-border-focus: #3b82f6;
  
  --pa-text-primary: var(--text-primary, #f8fafc);
  --pa-text-secondary: var(--text-secondary, #94a3b8);
  --pa-text-muted: #475569;
  
  /* Vibrant Accents */
  --pa-accent: #3b82f6;
  --pa-accent-glow: rgba(59, 130, 246, 0.4);
  --pa-accent-hover: #2563eb;
  
  --pa-easy: #10b981; 
  --pa-easy-bg: rgba(16, 185, 129, 0.1);
  --pa-medium: #f59e0b; 
  --pa-medium-bg: rgba(245, 158, 11, 0.1);
  --pa-hard: #f43f5e; 
  --pa-hard-bg: rgba(244, 63, 94, 0.1);
  
  --pa-font-sans: 'Inter', 'Outfit', system-ui, sans-serif;
  --pa-font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  --pa-radius-sm: 4px;
  --pa-radius-md: 6px;
  --pa-radius-lg: 16px;
}

[data-theme="light"] {
  --pa-bg: #f8fafc;
  --pa-surface: #ffffff;
  --pa-surface-hover: #f1f5f9;
  --pa-surface-glass: rgba(255, 255, 255, 0.7);
  --pa-border: #e2e8f0;
  --pa-border-light: #cbd5e1;
  --pa-text-primary: #0f172a;
  --pa-text-secondary: #475569;
  --pa-text-muted: #94a3b8;
}

@keyframes ch-blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }

.pa-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 80px 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  font-family: var(--pa-font-sans);
  background: var(--pa-bg);
  min-height: 100vh;
  color: var(--pa-text-primary);
  box-sizing: border-box;
}

/* HERO SECTION (Matches Contest Hub ch-hero) */
.pa-hero {
  position: relative;
  border-radius: var(--pa-radius-lg);
  border: 1px solid var(--pa-border);
  overflow: hidden;
  background:
    radial-gradient(ellipse at 0% 0%, rgba(59,130,246,0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 100% 100%, rgba(16,185,129,0.1) 0%, transparent 50%),
    var(--pa-surface);
  padding: 40px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 32px;
  align-items: center;
}
.pa-hero::before {
  content: '';
  position: absolute;
  top: -1px; left: -1px; right: -1px;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #10b981, #ec4899);
  border-radius: var(--pa-radius-lg) var(--pa-radius-lg) 0 0;
}
.pa-hero__grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px);
  background-size: 30px 30px;
  pointer-events: none;
}
.pa-hero__left {
  position: relative;
  z-index: 1;
}
.pa-hero__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.2);
  color: #3b82f6;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 18px;
}
.pa-hero__eyebrow-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #3b82f6;
  animation: ch-blink 2s ease infinite;
}
.pa-hero__greeting {
  font-size: 2.5rem;
  font-weight: 900;
  line-height: 1.1;
  color: var(--pa-text-primary);
  margin-bottom: 12px;
}
.pa-hero__greeting span {
  background: linear-gradient(135deg, #3b82f6, #10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.pa-hero__subtitle {
  font-size: 1rem;
  color: var(--pa-text-secondary);
  max-width: 500px;
  line-height: 1.6;
}
.pa-hero__right {
  position: relative;
  z-index: 1;
  background: rgba(0,0,0,0.3);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(59,130,246,0.3);
  text-align: center;
  min-width: 250px;
}
[data-theme="light"] .pa-hero__right {
  background: rgba(255,255,255,0.7);
}
.pa-stats-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--pa-text-secondary);
  text-transform: uppercase;
  margin-bottom: 8px;
}
.pa-stats-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2.5rem;
  font-weight: 800;
  color: #3b82f6;
  margin-bottom: 8px;
}
.pa-stats-sub {
  font-size: 0.9rem;
  color: var(--pa-text-muted);
}

/* MAIN LAYOUT */
.pa-main-layout {
  display: flex;
  gap: 20px;
  align-items: start;
}

/* COMPACT SIDEBAR */
.pa-sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 20px;
  background: var(--pa-surface);
  border: 1px solid var(--pa-border);
  border-radius: var(--pa-radius-lg);
  padding: 20px;
}

.pa-search-wrapper {
  position: relative;
  margin-bottom: 4px;
}
.pa-search-input {
  width: 100%;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--pa-border);
  color: var(--pa-text-primary);
  padding: 8px 48px 8px 32px;
  border-radius: var(--pa-radius-sm);
  font-size: 0.85rem;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}
[data-theme="light"] .pa-search-input {
  background: rgba(255, 255, 255, 0.5);
}
.pa-search-input:focus {
  border-color: var(--pa-accent);
}
.pa-search-wrapper .search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--pa-text-secondary);
}
.pa-search-wrapper .search-hint {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--pa-border);
  color: var(--pa-text-secondary);
  font-size: 0.65rem;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: var(--pa-font-mono);
}

.pa-filter-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pa-filter-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--pa-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding-left: 2px;
}

/* COMPACT PILLS */
.pa-filter-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pa-pill {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--pa-border);
  border-radius: 12px;
  font-size: 0.75rem;
  color: var(--pa-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
}
[data-theme="light"] .pa-pill {
  background: rgba(0,0,0,0.03);
}
.pa-pill:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--pa-text-primary);
}
[data-theme="light"] .pa-pill:hover {
  background: rgba(0,0,0,0.08);
}
.pa-pill.active {
  background: var(--pa-accent);
  border-color: var(--pa-accent);
  color: #fff;
  font-weight: 500;
}

/* LIST FILTERS */
.pa-filter-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 140px;
  overflow-y: auto;
  padding-right: 4px;
}
.pa-filter-list::-webkit-scrollbar { width: 4px; }
.pa-filter-list::-webkit-scrollbar-thumb { background: var(--pa-border); border-radius: 4px; }

.pa-filter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-radius: var(--pa-radius-sm);
  cursor: pointer;
  color: var(--pa-text-secondary);
  font-size: 0.75rem;
  transition: all 0.1s;
}
.pa-filter-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--pa-text-primary);
}
[data-theme="light"] .pa-filter-item:hover {
  background: rgba(0, 0, 0, 0.05);
}
.pa-filter-item.active {
  background: rgba(59, 130, 246, 0.1);
  color: var(--pa-accent);
  font-weight: 600;
  border-left: 2px solid var(--pa-accent);
}

/* PROBLEM LIST OVERHAUL (Matches Contest Card Style) */
.pa-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.pa-list-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pa-list-stats {
  font-size: 0.9rem;
  color: var(--pa-text-secondary);
  display: flex;
  align-items: center;
  gap: 8px;
}
.pa-list-stats-badge {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 4px 10px;
  border-radius: 12px;
  color: var(--pa-accent);
  font-weight: 700;
}

.pa-btn {
  padding: 10px 24px;
  border-radius: 99px;
  font-weight: 700;
  font-size: 0.95rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.pa-btn-primary {
  background: linear-gradient(135deg, #3b82f6, #10b981);
  color: #fff;
}
.pa-btn-primary:hover {
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}
.pa-btn-secondary {
  background: rgba(255,255,255,0.05);
  color: var(--pa-text-primary);
  border: 1px solid var(--pa-border);
}
[data-theme="light"] .pa-btn-secondary {
  background: rgba(0,0,0,0.05);
}
.pa-btn-secondary:hover {
  background: rgba(255,255,255,0.1);
}
[data-theme="light"] .pa-btn-secondary:hover {
  background: rgba(0,0,0,0.1);
}

.pa-empty-state {
  text-align: center;
  padding: 60px 20px;
  background: var(--pa-surface);
  border-radius: 16px;
  border: 1px dashed var(--pa-border);
  color: var(--pa-text-secondary);
  font-size: 1.1rem;
}

/* PROBLEM CARD */
.pa-card {
  background: var(--pa-surface);
  border: 1px solid var(--pa-border);
  border-radius: 16px;
  padding: 24px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 24px;
  align-items: center;
  transition: all 0.2s ease;
  cursor: pointer;
}
.pa-card:hover {
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
[data-theme="light"] .pa-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.pa-card-status {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
}
.status-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.status-solved { color: var(--pa-easy); }
.status-attempted { color: var(--pa-medium); }

.pa-card-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pa-card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--pa-text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
}
.pa-card:hover .pa-card-title {
  color: var(--pa-accent);
}
.pa-platform-badge {
  font-size: 0.75rem;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(255,255,255,0.1);
  color: var(--pa-text-secondary);
  border: 1px solid var(--pa-border);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
[data-theme="light"] .pa-platform-badge {
  background: rgba(0,0,0,0.05);
}

.pa-card-meta {
  display: flex;
  gap: 16px;
  font-size: 0.9rem;
  color: var(--pa-text-secondary);
  align-items: center;
  flex-wrap: wrap;
}
.pa-card-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pa-diff-pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}
.pa-diff-Easy { color: var(--pa-easy); background: var(--pa-easy-bg); border: 1px solid rgba(16, 185, 129, 0.2); }
.pa-diff-Medium { color: var(--pa-medium); background: var(--pa-medium-bg); border: 1px solid rgba(245, 158, 11, 0.2); }
.pa-diff-Hard { color: var(--pa-hard); background: var(--pa-hard-bg); border: 1px solid rgba(244, 63, 94, 0.2); }

.pa-card-action {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pa-tag {
  font-size: 0.75rem;
  padding: 2px 8px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--pa-border-light);
  border-radius: 12px;
  color: var(--pa-text-secondary);
  white-space: nowrap;
}
[data-theme="light"] .pa-tag {
  background: rgba(0,0,0,0.04);
}
.pa-card:hover .pa-tag {
  border-color: var(--pa-text-muted);
  color: var(--pa-text-primary);
}

/* PAGINATION */
.pa-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  margin-top: 10px;
}
.pa-page-controls {
  display: flex;
  gap: 8px;
}
.pa-page-btn {
  padding: 8px 16px;
  background: var(--pa-surface);
  border: 1px solid var(--pa-border);
  border-radius: 8px;
  color: var(--pa-text-primary);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.pa-page-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: #3b82f6;
}
.pa-page-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}
.pa-page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
"""

with open('c:/Users/neera/OneDrive/Desktop/smart-placement-platform/frontend-react/src/pages/problem-arena.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

jsx_content = """import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { 
  Search, ChevronRight, CheckCircle2, CircleDashed, Circle, Shuffle,
  Target, Zap
} from 'lucide-react';
import './problem-arena.css';

export default function ProblemArenaPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  
  const initialTopic = queryParams.get('topic') || 'All';
  const initialDifficulty = queryParams.get('difficulty') || 'All';
  const initialStatus = queryParams.get('status') || 'All';

  const { data: rawProblemsData, loading: problemsLoading } = useApi('/code/problems/');
  const { data: statsData } = useApi('/user/progress/');
  
  const rawProblems = rawProblemsData || [];
  const stats = statsData || { solved_count: 0, total_problems: 0, acceptance_rate: 0 };

  // Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState(initialDifficulty);
  const [filterStatus, setFilterStatus] = useState(initialStatus);
  const [filterTopic, setFilterTopic] = useState(initialTopic);
  const [filterCompany, setFilterCompany] = useState('All');

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

  // Sync URL Params
  useEffect(() => {
    const params = new URLSearchParams();
    if (filterTopic !== 'All') params.set('topic', filterTopic);
    if (filterDifficulty !== 'All') params.set('difficulty', filterDifficulty);
    if (filterStatus !== 'All') params.set('status', filterStatus);
    
    navigate({ search: params.toString() }, { replace: true });
  }, [filterTopic, filterDifficulty, filterStatus, navigate]);

  // Derived Data
  const companiesList = useMemo(() => {
    const set = new Set();
    rawProblems.forEach(p => p.companies?.forEach(c => set.add(c)));
    return ['All', ...Array.from(set).sort()];
  }, [rawProblems]);

  const topicsList = useMemo(() => {
    const set = new Set();
    rawProblems.forEach(p => p.topics?.forEach(t => {
      set.add(typeof t === 'string' ? t : t.name);
    }));
    return ['All', ...Array.from(set).sort()];
  }, [rawProblems]);

  // Filtering Logic
  const filteredProblems = useMemo(() => {
    return rawProblems.filter(problem => {
      if (searchQuery) {
        const sq = searchQuery.toLowerCase();
        const titleMatch = problem.title?.toLowerCase().includes(sq);
        if (!titleMatch) return false;
      }
      if (filterDifficulty !== 'All' && problem.difficulty?.toLowerCase() !== filterDifficulty.toLowerCase()) return false;
      if (filterStatus !== 'All') {
        if (filterStatus === 'Solved' && !problem.is_solved) return false;
        if (filterStatus === 'Todo' && problem.is_solved) return false;
        if (filterStatus === 'Attempted' && !problem.is_attempted) return false;
      }
      if (filterTopic !== 'All') {
        const match = (problem.topics || []).some(t => {
          const topicName = typeof t === 'string' ? t : t.name;
          return topicName?.toLowerCase() === filterTopic.toLowerCase();
        });
        if (!match) return false;
      }
      if (filterCompany !== 'All') {
        const match = (problem.companies || []).some(c => c.toLowerCase() === filterCompany.toLowerCase());
        if (!match) return false;
      }
      return true;
    });
  }, [rawProblems, searchQuery, filterDifficulty, filterStatus, filterTopic, filterCompany]);

  // Pagination
  const totalPages = Math.ceil(filteredProblems.length / itemsPerPage) || 1;
  const paginatedProblems = filteredProblems.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handleSolveClick = (e, slug) => {
    e.stopPropagation();
    navigate(`/code-lab/arena/${slug}`);
  };

  // Keyboard shortcut for search
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('paSearchInput')?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="pa-container">
      
      {/* HERO SECTION (Matches Contest Hub) */}
      <div className="pa-hero">
        <div className="pa-hero__grid-bg" />
        
        <div className="pa-hero__left">
          <div className="pa-hero__eyebrow">
            <div className="pa-hero__eyebrow-dot" />
            Arena Hub
          </div>
          
          <h1 className="pa-hero__greeting">
            Code Lab <span>Arena</span>.
          </h1>
          
          <p className="pa-hero__subtitle">
            Immerse yourself in our premier coding playground. Solve algorithms, master data structures, and prepare for top tech interviews.
          </p>
        </div>
        
        <div className="pa-hero__right">
          <div className="pa-stats-label">Global Progress</div>
          <div className="pa-stats-value">{stats.solved_count || 0} <span style={{fontSize: '1.2rem', color:'var(--pa-text-muted)'}}>/ {stats.total_problems || 0}</span></div>
          <div className="pa-stats-sub">{stats.acceptance_rate || 0}% Acceptance Rate</div>
          
          {rawProblems.length > 0 && (
            <button className="pa-btn pa-btn-primary" style={{marginTop: '20px', width: '100%', justifyContent: 'center'}} onClick={(e) => handleSolveClick(e, rawProblems[0].slug)}>
              <Zap size={16} /> Daily Challenge
            </button>
          )}
        </div>
      </div>

      <div className="pa-main-layout">
        
        {/* COMPACT SIDEBAR FILTERS */}
        <div className="pa-sidebar">
          <div className="pa-search-wrapper" style={{width: '100%'}}>
            <Search className="search-icon" size={14} />
            <input 
              id="paSearchInput"
              type="text" 
              className="pa-search-input" 
              placeholder="Search problems..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <span className="search-hint">Ctrl K</span>
          </div>

          <div className="pa-filter-section" style={{width: '100%'}}>
            <span className="pa-filter-label">Status</span>
            <div className="pa-filter-pills">
              {['All', 'Todo', 'Attempted', 'Solved'].map(status => (
                <div 
                  key={status}
                  className={`pa-pill ${filterStatus === status ? 'active' : ''}`}
                  onClick={() => setFilterStatus(status)}
                >
                  {status}
                </div>
              ))}
            </div>
          </div>

          <div className="pa-filter-section" style={{width: '100%'}}>
            <span className="pa-filter-label">Difficulty</span>
            <div className="pa-filter-pills">
              <div className={`pa-pill ${filterDifficulty === 'All' ? 'active' : ''}`} onClick={() => setFilterDifficulty('All')}>All</div>
              <div className={`pa-pill ${filterDifficulty === 'Easy' ? 'active' : ''}`} onClick={() => setFilterDifficulty('Easy')} style={filterDifficulty === 'Easy' ? {backgroundColor: 'var(--pa-easy)', borderColor: 'var(--pa-easy)', color:'#fff'} : {}}>Easy</div>
              <div className={`pa-pill ${filterDifficulty === 'Medium' ? 'active' : ''}`} onClick={() => setFilterDifficulty('Medium')} style={filterDifficulty === 'Medium' ? {backgroundColor: 'var(--pa-medium)', borderColor: 'var(--pa-medium)', color:'#fff'} : {}}>Medium</div>
              <div className={`pa-pill ${filterDifficulty === 'Hard' ? 'active' : ''}`} onClick={() => setFilterDifficulty('Hard')} style={filterDifficulty === 'Hard' ? {backgroundColor: 'var(--pa-hard)', borderColor: 'var(--pa-hard)', color:'#fff'} : {}}>Hard</div>
            </div>
          </div>

          <div className="pa-filter-section" style={{width: '100%'}}>
            <span className="pa-filter-label">Company</span>
            <div className="pa-filter-list">
              {companiesList.slice(0, 15).map(company => (
                <div 
                  key={company}
                  className={`pa-filter-item ${filterCompany === company ? 'active' : ''}`}
                  onClick={() => setFilterCompany(company)}
                >
                  {company}
                </div>
              ))}
            </div>
          </div>

          <div className="pa-filter-section" style={{width: '100%'}}>
            <span className="pa-filter-label">Topic</span>
            <div className="pa-filter-list">
              {topicsList.slice(0, 20).map(topic => (
                <div 
                  key={topic}
                  className={`pa-filter-item ${filterTopic === topic ? 'active' : ''}`}
                  onClick={() => setFilterTopic(topic)}
                >
                  {topic}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* LIST AREA (Replaces Table) */}
        <div className="pa-list-container">
          <div className="pa-list-toolbar">
            <div className="pa-list-stats">
              <span className="pa-list-stats-badge">{filteredProblems.length} Problems</span>
            </div>
            <div>
              <button className="pa-btn pa-btn-secondary" onClick={() => {
                if (filteredProblems.length > 0) {
                  const rnd = filteredProblems[Math.floor(Math.random() * filteredProblems.length)];
                  handleSolveClick({stopPropagation: ()=>{}}, rnd.slug);
                }
              }}>
                <Shuffle size={14}/> 
                Pick Random
              </button>
            </div>
          </div>

          {problemsLoading ? (
            <div className="pa-empty-state">Loading Problem Ecosystem...</div>
          ) : paginatedProblems.length === 0 ? (
            <div className="pa-empty-state">No matching problems found. Try adjusting your filters.</div>
          ) : (
            paginatedProblems.map((problem) => (
              <div 
                key={problem.slug} 
                className="pa-card"
                onClick={(e) => handleSolveClick(e, problem.slug)}
              >
                <div className="pa-card-status">
                  <span className="status-icon">
                    {problem.is_solved ? (
                      <CheckCircle2 size={24} className="status-solved" />
                    ) : problem.is_attempted ? (
                      <CircleDashed size={24} className="status-attempted" />
                    ) : (
                      <Circle size={24} color="var(--pa-border-light)" />
                    )}
                  </span>
                </div>
                
                <div className="pa-card-info">
                  <div className="pa-card-title">
                    {problem.id}. {problem.title}
                    {problem.companies && problem.companies.length > 0 && (
                      <span className="pa-platform-badge">{problem.companies[0]}</span>
                    )}
                  </div>
                  <div className="pa-card-meta">
                    <span className={`pa-diff-pill pa-diff-${problem.difficulty}`}>{problem.difficulty}</span>
                    <span><Target size={14} /> {problem.acceptance_rate || 0}% Acceptance</span>
                    
                    {problem.topics && problem.topics.slice(0, 3).map((t, idx) => (
                      <span key={idx} className="pa-tag">{typeof t === 'string' ? t : t.name}</span>
                    ))}
                    {(problem.topics?.length > 3) && (
                      <span className="pa-tag">+{problem.topics.length - 3}</span>
                    )}
                  </div>
                </div>
                
                <div className="pa-card-action">
                  <button className="pa-btn pa-btn-primary" onClick={(e) => handleSolveClick(e, problem.slug)}>
                    Solve <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            ))
          )}

          {/* PAGINATION CONTROLS */}
          {filteredProblems.length > 0 && (
            <div className="pa-pagination">
              <div style={{ fontSize: '0.9rem', color: 'var(--pa-text-secondary)' }}>
                Showing <strong style={{color: 'var(--pa-text-primary)'}}>{(currentPage - 1) * itemsPerPage + 1}</strong> to <strong style={{color: 'var(--pa-text-primary)'}}>{Math.min(currentPage * itemsPerPage, filteredProblems.length)}</strong> of <strong style={{color: 'var(--pa-text-primary)'}}>{filteredProblems.length}</strong>
              </div>
              <div className="pa-page-controls">
                <button 
                  className="pa-page-btn" 
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(p => p - 1)}
                >
                  Prev
                </button>
                {[...Array(Math.min(5, totalPages))].map((_, idx) => {
                  let pageNum = idx + 1;
                  if (totalPages > 5 && currentPage > 3) {
                    pageNum = currentPage - 2 + idx;
                    if (pageNum > totalPages) pageNum = totalPages - (4 - idx);
                  }
                  
                  return (
                    <button 
                      key={pageNum}
                      className={`pa-page-btn ${currentPage === pageNum ? 'active' : ''}`}
                      onClick={() => setCurrentPage(pageNum)}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                <button 
                  className="pa-page-btn"
                  disabled={currentPage === totalPages || totalPages === 0}
                  onClick={() => setCurrentPage(p => p + 1)}
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
"""

with open('c:/Users/neera/OneDrive/Desktop/smart-placement-platform/frontend-react/src/pages/ProblemArenaPage.jsx', 'w', encoding='utf-8') as f:
    f.write(jsx_content)

print("Both ProblemArenaPage and its CSS are updated.")
