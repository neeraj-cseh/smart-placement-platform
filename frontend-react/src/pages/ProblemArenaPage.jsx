import React, { useState, useEffect, useMemo } from 'react';
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
  
  const rawProblems = useMemo(() => rawProblemsData || [], [rawProblemsData]);
  const stats = useMemo(() => statsData || { solved_count: 0, total_problems: 0, acceptance_rate: 0 }, [statsData]);

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

      {/* TABS */}
      <div className="pa-tabs">
        {['All', 'Todo', 'Attempted', 'Solved', 'Bookmarked'].map(tab => (
          <button 
            key={tab}
            onClick={() => setFilterStatus(tab)}
            className={`pa-tab-btn ${filterStatus === tab ? 'active' : ''}`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="pa-main-layout" style={{ width: '100%' }}>
        
        {/* LIST AREA */}
        <div className="pa-list-container" style={{ width: '100%', maxWidth: '1000px', margin: '0 auto' }}>
          
          <div className="pa-list-toolbar" style={{ background: 'var(--pa-surface)', padding: '16px', borderRadius: '12px', border: '1px solid var(--pa-border)', marginBottom: '16px', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <div className="pa-search-wrapper" style={{ flex: 1, minWidth: '200px' }}>
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
            
            <select 
              className="pa-search-input" 
              style={{ width: 'auto', paddingRight: '16px' }}
              value={filterDifficulty}
              onChange={(e) => setFilterDifficulty(e.target.value)}
            >
              <option value="All">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
            
            <select 
              className="pa-search-input" 
              style={{ width: 'auto', paddingRight: '16px' }}
              value={filterTopic}
              onChange={(e) => setFilterTopic(e.target.value)}
            >
              {topicsList.map(t => <option key={t} value={t}>{t === 'All' ? 'All Topics' : t}</option>)}
            </select>
            
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

          <div className="pa-list-stats" style={{ marginBottom: '16px', paddingLeft: '8px' }}>
            <span className="pa-list-stats-badge">{filteredProblems.length} Problems</span>
          </div>

          {problemsLoading ? (
            <div className="pa-empty-state">Loading Problem Ecosystem...</div>
          ) : paginatedProblems.length === 0 ? (
            <div className="pa-empty-state">No matching problems found. Try adjusting your filters.</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
              {paginatedProblems.map((problem) => (
                <div 
                  key={problem.slug} 
                  className="pa-card"
                  onClick={(e) => handleSolveClick(e, problem.slug)}
                  style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '16px', padding: '24px' }}
                >
                  <div className="pa-card-status" style={{ alignSelf: 'flex-start' }}>
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
                  
                  <div className="pa-card-info" style={{ flex: 1 }}>
                    <div className="pa-card-title" style={{ fontSize: '1.2rem', marginBottom: '8px' }}>
                      {problem.title}
                    </div>
                    <div className="pa-card-meta" style={{ flexWrap: 'wrap', gap: '8px' }}>
                      <span className={`pa-diff-pill pa-diff-${problem.difficulty}`}>{problem.difficulty}</span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--pa-text-secondary)', background: 'var(--pa-surface-hover)', padding: '2px 8px', borderRadius: '12px' }}><Target size={12} style={{marginRight: '4px'}}/> {problem.acceptance_rate || 0}% Acc</span>
                    </div>
                    {problem.topics && problem.topics.length > 0 && (
                      <div style={{ marginTop: '12px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {problem.topics.slice(0, 3).map((t, idx) => (
                          <span key={idx} className="pa-tag" style={{ fontSize: '0.75rem', padding: '2px 8px' }}>{typeof t === 'string' ? t : t.name}</span>
                        ))}
                        {(problem.topics.length > 3) && (
                          <span className="pa-tag" style={{ fontSize: '0.75rem', padding: '2px 8px' }}>+{problem.topics.length - 3}</span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="pa-card-action" style={{ marginTop: 'auto', borderTop: '1px solid var(--pa-border)', paddingTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                    <button className="pa-btn pa-btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={(e) => handleSolveClick(e, problem.slug)}>
                      Solve Challenge <ChevronRight size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* PAGINATION CONTROLS */}
          {filteredProblems.length > 0 && (
            <div className="pa-pagination" style={{ marginTop: '32px' }}>
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
