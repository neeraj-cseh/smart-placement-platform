import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen, TrendingUp, CheckCircle, ChevronLeft,
  Brain, Code2, HelpCircle, Send, RefreshCw,
  Play, Check, Lock, Target, ChevronRight,
  ArrowRight, Award, Flame, AlertCircle, Sparkles,
  Lightbulb, Zap, Clock, Star, Eye, RotateCcw,
  MessageSquare, X
} from 'lucide-react';
import { api } from '../api/client';
import './topic-study.css';

// ─── Enhanced Markdown Renderer ───────────────────────────────────────────────
const renderMarkdown = (text) => {
  if (!text) return null;
  const lines = text.split('\n');
  const elements = [];
  let codeLines = [];
  let inCode = false;
  let listItems = [];

  const flushList = (key) => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`ul-${key}`} className="topic-markdown-ul">{listItems}</ul>
      );
      listItems = [];
    }
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    if (trimmed.startsWith('```')) {
      if (!inCode) {
        flushList(idx);
        inCode = true;
        codeLines = [];
      } else {
        inCode = false;
        elements.push(
          <pre key={`code-${idx}`} className="topic-markdown-code">
            <code>{codeLines.join('\n')}</code>
          </pre>
        );
        codeLines = [];
      }
      return;
    }
    if (inCode) { codeLines.push(line); return; }

    let content = line;
    content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    content = content.replace(/`(.*?)`/g, '<code>$1</code>');

    if (trimmed.startsWith('#### ')) {
      flushList(idx);
      elements.push(<h5 key={idx} className="topic-markdown-h5" dangerouslySetInnerHTML={{ __html: content.replace(/^#+\s*/, '') }} />);
    } else if (trimmed.startsWith('### ')) {
      flushList(idx);
      elements.push(<h4 key={idx} className="topic-markdown-h4" dangerouslySetInnerHTML={{ __html: content.replace(/^#+\s*/, '') }} />);
    } else if (trimmed.startsWith('## ')) {
      flushList(idx);
      elements.push(<h3 key={idx} className="topic-markdown-h3" dangerouslySetInnerHTML={{ __html: content.replace(/^#+\s*/, '') }} />);
    } else if (trimmed.startsWith('# ')) {
      flushList(idx);
      elements.push(<h2 key={idx} className="topic-markdown-h2" dangerouslySetInnerHTML={{ __html: content.replace(/^#+\s*/, '') }} />);
    } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      listItems.push(<li key={idx} className="topic-markdown-li" dangerouslySetInnerHTML={{ __html: content.replace(/^[-*]\s+/, '') }} />);
    } else if (/^\d+\.\s/.test(trimmed)) {
      listItems.push(<li key={idx} className="topic-markdown-li topic-markdown-li-num" dangerouslySetInnerHTML={{ __html: content.replace(/^\d+\.\s+/, '') }} />);
    } else if (trimmed.startsWith('|')) {
      flushList(idx);
      if (!trimmed.replace(/\|/g, '').replace(/-/g, '').trim()) return;
      const cells = trimmed.split('|').filter((_, i, arr) => i > 0 && i < arr.length - 1);
      elements.push(
        <div key={idx} className="topic-markdown-table-row">
          {cells.map((cell, ci) => (
            <span key={ci} className="topic-markdown-table-cell" dangerouslySetInnerHTML={{ __html: cell.trim() }} />
          ))}
        </div>
      );
    } else if (trimmed === '' || trimmed === '---') {
      flushList(idx);
    } else {
      flushList(idx);
      elements.push(<p key={idx} className="topic-markdown-p" dangerouslySetInnerHTML={{ __html: content }} />);
    }
  });

  flushList('end');
  if (codeLines.length > 0) {
    elements.push(
      <pre key="code-end" className="topic-markdown-code">
        <code>{codeLines.join('\n')}</code>
      </pre>
    );
  }
  return elements;
};

// ─── Difficulty badge color ───────────────────────────────────────────────────
const diffColor = (d) => {
  const dl = (d || '').toLowerCase();
  if (dl === 'easy') return '#10b981';
  if (dl === 'medium') return '#fb923c';
  return '#ef4444';
};

// ─── Quick reply chips for AI chat ───────────────────────────────────────────
const AI_CHIPS = [
  { label: 'Explain concept', icon: <Lightbulb size={11} /> },
  { label: 'Show example', icon: <Eye size={11} /> },
  { label: 'Key tricks', icon: <Zap size={11} /> },
  { label: 'Interview tips', icon: <Star size={11} /> },
  { label: "What's next?", icon: <ArrowRight size={11} /> },
  { label: 'My progress', icon: <TrendingUp size={11} /> },
];

// ─── Visualizer data ──────────────────────────────────────────────────────────
// Data is now loaded dynamically from the backend topic.visualization.config_data

// ─── Generic concept visualizer ───────────────────────────────────────────────
function GenericConceptVisualizer({ topic }) {
  const steps = topic?.visualization?.config_data?.steps || [];
  const [activeStep, setActiveStep] = useState(0);
  
  if (!steps || steps.length === 0) {
    return (
      <div className="vis-generic-box" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Authentic simulation steps for {topic?.name || 'this topic'} are currently being curated.</p>
      </div>
    );
  }

  const displaySteps = steps;

  return (
    <div className="vis-generic-box">
      <div className="vis-generic-steps">
        {displaySteps.map((step, i) => (
          <button
            key={i}
            className={`vis-generic-step ${activeStep === i ? 'is-active' : ''} ${i < activeStep ? 'is-done' : ''}`}
            onClick={() => setActiveStep(i)}
          >
            <span className="step-num">{i < activeStep ? '✓' : i + 1}</span>
            <span className="step-text">{step}</span>
          </button>
        ))}
      </div>
      <div className="vis-generic-detail">
        <div className="vis-generic-detail-icon">
          {activeStep < displaySteps.length - 1 ? <Brain size={28} /> : <CheckCircle size={28} color="#10b981" />}
        </div>
        <p className="vis-generic-detail-text">
          <strong>Step {activeStep + 1}:</strong> {displaySteps[activeStep]}
        </p>
        <div className="vis-generic-progress">
          <div className="vis-generic-bar" style={{ width: `${((activeStep + 1) / displaySteps.length) * 100}%` }} />
        </div>
        <div className="vis-generic-controls">
          <button className="prep-btn-secondary" onClick={() => setActiveStep(Math.max(0, activeStep - 1))} disabled={activeStep === 0}>
            ← Back
          </button>
          <span className="vis-generic-counter">{activeStep + 1} / {displaySteps.length}</span>
          <button className="prep-btn-primary" onClick={() => setActiveStep(Math.min(displaySteps.length - 1, activeStep + 1))} disabled={activeStep === displaySteps.length - 1}>
            Next →
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Logical Puzzles visualizer ───────────────────────────────────────────────
function LogicalPuzzleVisualizer({ config }) {
  const [step, setStep] = useState(0);
  const positions = config?.positions || ['1st', '2nd', '3rd', '4th', '5th'];
  const people = config?.people || ['Alice', 'Bob', 'Carol', 'Dave', 'Eve'];
  const colors = config?.colors || ['#3b82f6', '#8b5cf6', '#10b981', '#fb923c', '#ef4444'];
  const finalOrder = config?.finalOrder || [2, 0, 4, 1, 3];
  const clues = config?.clues || [
    'Clue 1: Alice is not in position 1 or 5.',
    'Clue 2: Bob is immediately after Alice.',
    'Clue 3: Carol is before Dave.',
    'Clue 4: Eve sits exactly in the middle (3rd).',
    'Solution: Carol → Alice → Eve → Bob → Dave ✅',
  ];
  const currentOrder = step < 4
    ? Array(5).fill(null).map((_, i) => (i === 2 && step >= 3 ? 4 : null))
    : finalOrder;

  return (
    <div className="vis-puzzle-box">
      <div className="puzzle-seats-row">
        {positions.map((pos, i) => {
          const personIdx = step >= 4 ? finalOrder[i] : (i === 2 && step >= 3 ? 4 : null);
          return (
            <div key={i} className={`puzzle-seat ${personIdx !== null ? 'is-filled' : ''}`}>
              {personIdx !== null && (
                <div className="puzzle-person" style={{ background: `${colors[personIdx]}22`, borderColor: colors[personIdx] }}>
                  <span className="puzzle-person-name" style={{ color: colors[personIdx] }}>{people[personIdx]}</span>
                </div>
              )}
              <div className="puzzle-seat-label">{pos}</div>
            </div>
          );
        })}
      </div>
      <div className="puzzle-clue-box">
        <p className={`puzzle-clue ${step === 4 ? 'is-solved' : ''}`}>{clues[step]}</p>
      </div>
      <div className="visualizer-controls">
        <button className="prep-btn-secondary" onClick={() => setStep(0)}>Reset</button>
        <button className="prep-btn-primary" onClick={() => setStep(p => Math.min(4, p + 1))} disabled={step >= 4}>
          Next Clue <ChevronRight size={13} style={{ marginLeft: 4 }} />
        </button>
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function TopicStudyPage() {
  const { slug } = useParams();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('overview');
  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Quiz state
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [submittingQuiz, setSubmittingQuiz] = useState(false);
  const [expandedExplanations, setExpandedExplanations] = useState({});

  // AI chat state
  const [aiChatMessages, setAiChatMessages] = useState([]);
  const [aiInput, setAiInput] = useState('');
  const [aiTyping, setAiTyping] = useState(false);
  const [aiContext, setAiContext] = useState(null);
  const [aiSidebarOpen, setAiSidebarOpen] = useState(true);
  const chatEndRef = useRef(null);

  // Visualizer state
  const [visStep, setVisStep] = useState(0);

  // Drafts state
  const [drafts, setDrafts] = useState({});
  const draftSaveTimeout = useRef(null);

  // Aptitude sliders
  const [cp, setCp] = useState(500);
  const [sp, setSp] = useState(600);

  const fetchTopicData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [res, aiCtx, draftsRes] = await Promise.all([
        api.get(`/prep/topic/${slug}/`),
        api.get(`/prep/topic/${slug}/ai-context/`).catch(() => null),
        api.get(`/prep/topic/${slug}/drafts/`).catch(() => ({}))
      ]);
      setTopic(res);
      setAiContext(aiCtx);
      setDrafts(draftsRes || {});
      setSelectedAnswers({});
      setQuizResult(null);
      setVisStep(0);
      setExpandedExplanations({});
      setAiChatMessages([{
        role: 'assistant',
        content: `👋 **Welcome to ${res.name}!**\n\nI'm your AI ${
            res.domain === 'career' ? 'Career Preparation Coach' :
            res.domain === 'core_cs' ? 'Core CS Theory Tutor' :
            res.domain === 'aptitude' ? 'Aptitude Logic Coach' : 'Placement Tutor'
          } for this topic. I have full context about **${res.name}** — its concepts, interview patterns, and your progress.\n\nAsk me anything! Try: ${
            res.domain === 'career' ? '"Review my STAR story", "How do I explain my project impact?", or "Give me a behavioral mock prompt."' :
            '"Explain the concept", "Show me an example", or "What are the key tricks?"'
          }`
      }]);
    } catch (err) {
      setError(err.message || 'Failed to load topic.');
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => { fetchTopicData(); }, [fetchTopicData]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [aiChatMessages, aiTyping]);

  // Quiz handlers
  const handleSelectOption = (questionId, option) => {
    if (quizResult) return;
    setSelectedAnswers(prev => ({ ...prev, [questionId]: option }));
  };

  const handleSubmitQuiz = async () => {
    if (submittingQuiz || quizResult) return;
    setSubmittingQuiz(true);
    try {
      const res = await api.post(`/prep/topic/${slug}/quiz/submit/`, { answers: selectedAnswers });
      setQuizResult(res);
      if (res.passed) setTopic(prev => ({ ...prev, is_completed: true }));
    } catch (err) {
      alert('Failed to submit quiz: ' + err.message);
    } finally {
      setSubmittingQuiz(false);
    }
  };

  const handleManualComplete = async () => {
    try {
      await api.post(`/prep/topic/${slug}/complete/`);
      setTopic(prev => ({ ...prev, is_completed: true }));
    } catch (err) {
      alert('Failed to mark complete: ' + err.message);
    }
  };

  // AI chat handlers
  const sendAIMessage = async (msgText) => {
    const prompt = msgText.trim();
    if (!prompt) return;
    setAiInput('');
    setAiChatMessages(prev => [...prev, { role: 'user', content: prompt }]);
    setAiTyping(true);
    try {
      const res = await api.post(`/prep/topic/${slug}/ai-chat/`, { message: prompt });
      setAiChatMessages(prev => [...prev, { role: 'assistant', content: res.response }]);
    } catch (err) {
      setAiChatMessages(prev => [...prev, { role: 'assistant', content: `Sorry, I encountered an error: ${err.message}. Please try again!` }]);
    } finally {
      setAiTyping(false);
    }
  };

  const handleSendAIChat = (e) => {
    e.preventDefault();
    sendAIMessage(aiInput);
  };

  const handleDraftChange = (exerciseId, content) => {
    setDrafts(prev => ({ ...prev, [exerciseId]: content }));
    
    if (draftSaveTimeout.current) {
      clearTimeout(draftSaveTimeout.current);
    }
    
    draftSaveTimeout.current = setTimeout(async () => {
      try {
        await api.post(`/prep/topic/${slug}/drafts/`, { drafts: { [exerciseId]: content } });
      } catch (err) {
        console.error('Failed to save draft:', err);
      }
    }, 1000);
  };

  // Visualizer helpers
  const config = topic?.visualization?.config_data || {};
  const getVisStep = (steps) => steps && steps.length > 0 ? steps[Math.min(visStep, steps.length - 1)] : {};
  const maxVisSteps = {
    'sliding-window': config.steps ? config.steps.length - 1 : 0,
    'linked-list-cycle': config.steps ? config.steps.length - 1 : 0,
    'graph-dfs': config.steps ? config.steps.length - 1 : 0,
    'number-systems': config.steps ? config.steps.length - 1 : 0,
    'dbms-normalization': config.steps ? config.steps.length - 1 : 0,
  };

  // Aptitude calc
  const profitAmt = sp - cp;
  const isProfit = profitAmt >= 0;
  const pct = ((Math.abs(profitAmt) / cp) * 100).toFixed(1);
  const aptFormula = isProfit
    ? `Profit = SP - CP = ${sp} - ${cp} = ₹${Math.abs(profitAmt)}\nProfit % = (Profit / CP) × 100 = (${Math.abs(profitAmt)} / ${cp}) × 100 = ${pct}%`
    : `Loss = CP - SP = ${cp} - ${sp} = ₹${Math.abs(profitAmt)}\nLoss % = (Loss / CP) × 100 = (${Math.abs(profitAmt)} / ${cp}) × 100 = ${pct}%`;

  // ─── Loading state ──────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="study-container">
        <div className="study-loading-skeleton">
          <div className="study-skeleton-header skeleton" />
          <div className="study-skeleton-tabs skeleton" />
          <div className="study-skeleton-grid">
            <div className="study-skeleton-body skeleton" />
            <div className="study-skeleton-sidebar skeleton" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="study-container study-error-box">
        <AlertCircle size={40} className="study-error-icon" />
        <h3>Unable to Load Topic</h3>
        <p>{error || 'This topic is currently inactive or not configured.'}</p>
        <button className="prep-btn-primary" onClick={() => navigate('/prep/journey')}>
          <ChevronLeft size={14} style={{ marginRight: 6 }} /> Back to Journey
        </button>
      </div>
    );
  }

  const sectionsOverview = topic.sections?.filter(s => s.section_type === 'overview') || [];
  const sectionsLearn = topic.sections?.filter(s => s.section_type === 'learn') || [];
  const sectionsGuided = topic.sections?.filter(s => s.section_type === 'guided') || [];
  const answeredCount = Object.keys(selectedAnswers).length;
  const totalQuestions = topic.questions?.length || 0;
  const visType = topic.visualization?.visualization_type;
  const domain = topic?.domain || 'dsa';
  const isLogicalPuzzle = topic.name?.toLowerCase().includes('logical') || topic.name?.toLowerCase().includes('puzzle') || topic.name?.toLowerCase().includes('arrangement');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Target size={13} /> },
    { id: 'learn', label: 'Learn', icon: <BookOpen size={13} /> },
    ...(topic.visualization ? [{ id: 'visualizer', label: 'Visualizer', icon: <Play size={13} /> }] : []),
    { id: 'practice', label: 'Practice', icon: <Code2 size={13} /> },
    ...(totalQuestions > 0 ? [{ id: 'quiz', label: `Quiz (${totalQuestions})`, icon: <HelpCircle size={13} /> }] : []),
    ...(topic.revision ? [{ id: 'revision', label: 'Revision', icon: <Award size={13} /> }] : []),
  ];

  return (
    <div className="study-container">
      {/* ── Header ── */}
      <div className="study-header">
        <div className="study-header-left">
          <Link to="/prep/journey" className="study-back-link">
            <ChevronLeft size={14} /> Back to Journey
          </Link>
          <div className="study-title-row">
            <h1>{topic.name}</h1>
            {topic.is_completed ? (
              <span className="study-completed-badge"><CheckCircle size={12} /> Completed</span>
            ) : (
              <span className="study-active-badge"><Flame size={12} /> In Progress</span>
            )}
          </div>
          <p className="study-desc">{topic.description}</p>
        </div>
        <div className="study-header-right">
          <div className="study-metadata-card">
            <div className="study-meta-item">
              <span className="study-meta-label">Frequency</span>
              <span className={`study-meta-value freq-${(topic.interview_frequency || 'medium').toLowerCase()}`}>
                {topic.interview_frequency || 'Medium'}
              </span>
            </div>
            <div className="study-meta-item">
              <span className="study-meta-label">Companies</span>
              <div className="study-company-badges">
                {topic.target_companies?.slice(0, 4).map((c, i) => (
                  <span key={i} className="study-company-badge">{c}</span>
                ))}
              </div>
            </div>
            {!topic.is_completed && (
              <button className="prep-btn-secondary study-complete-btn" onClick={handleManualComplete}>
                <Check size={12} /> Mark Complete
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Tab Navigation ── */}
      <div className="study-tabs-strip">
        <div className="study-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`study-tab-btn ${activeTab === tab.id ? 'is-active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
        <button
          className={`ai-toggle-btn ${aiSidebarOpen ? 'is-open' : ''}`}
          onClick={() => setAiSidebarOpen(p => !p)}
          title={aiSidebarOpen ? 'Hide AI Tutor' : 'Show AI Tutor'}
        >
          <Brain size={14} />
          {aiSidebarOpen ? 'Hide Tutor' : 'AI Tutor'}
        </button>
      </div>

      {/* ── Main Workspace ── */}
      <div className={`study-workspace-grid ${aiSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>

        {/* Left: Tab Content */}
        <div className="study-main-area">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              {/* ══ 1. OVERVIEW ══════════════════════════════════════════════ */}
              {activeTab === 'overview' && (
                <div className="tab-pane-overview">
                  {/* Why it matters hero */}
                  <div className="overview-hero-card">
                    <div className="overview-hero-icon"><Target size={20} /></div>
                    <div>
                      <h3>Why It Matters in Interviews</h3>
                      <p>{topic.why_it_matters || `${topic.name} is a fundamental concept assessed in campus placement drives. Mastering it demonstrates your algorithmic thinking and problem-solving maturity — key signals recruiters look for.`}</p>
                    </div>
                  </div>

                  {/* Overview sections */}
                  {sectionsOverview.map(s => (
                    <div key={s.id} className="study-section-card markdown-section">
                      <h2 className="section-card-title">{s.title}</h2>
                      <div className="markdown-body">{renderMarkdown(s.content_markdown)}</div>
                    </div>
                  ))}

                  {/* Quick stats row */}
                  <div className="overview-stats-row">
                    <div className="overview-stat-card">
                      <span className="stat-number">{totalQuestions}</span>
                      <span className="stat-label">Quiz Questions</span>
                    </div>
                    <div className="overview-stat-card">
                      <span className="stat-number">{topic.problems?.length || 0}</span>
                      <span className="stat-label">Practice Problems</span>
                    </div>
                    <div className="overview-stat-card">
                      <span className="stat-number">{topic.sections?.length || 0}</span>
                      <span className="stat-label">Content Sections</span>
                    </div>
                    <div className="overview-stat-card">
                      <span className="stat-number">{topic.estimated_minutes || 30}m</span>
                      <span className="stat-label">Est. Study Time</span>
                    </div>
                  </div>

                  {/* Checkpoint CTA */}
                  <div className="study-completion-checkpoint">
                    <div className="checkpoint-left">
                      <Sparkles size={18} color="#3b82f6" />
                      <div>
                        <h3>Ready to Test Your Knowledge?</h3>
                        <p>Complete the Learn section and practice drills, then take the Concept Quiz to unlock the next topic.</p>
                      </div>
                    </div>
                    <div className="checkpoint-buttons">
                      <button className="prep-btn-secondary" onClick={() => setActiveTab('learn')}>
                        <BookOpen size={13} style={{ marginRight: 5 }} /> Start Learning
                      </button>
                      {totalQuestions > 0 && (
                        <button className="prep-btn-primary" onClick={() => setActiveTab('quiz')}>
                          Take Quiz <ArrowRight size={13} style={{ marginLeft: 5 }} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* ══ 2. LEARN SECTION ═════════════════════════════════════════ */}
              {activeTab === 'learn' && (
                <div className="tab-pane-learn">
                  <div className="learn-header">
                    <div className="learn-header-icon"><BookOpen size={20} /></div>
                    <div>
                      <h2>Learn: {topic.name}</h2>
                      <p className="learn-header-subtitle">Core concepts, patterns, complexity analysis, and worked examples</p>
                    </div>
                  </div>

                  {sectionsLearn.map(s => (
                    <div key={s.id} className="study-section-card markdown-section">
                      <h2 className="section-card-title">{s.title}</h2>
                      <div className="markdown-body">{renderMarkdown(s.content_markdown)}</div>
                    </div>
                  ))}

                  {sectionsGuided.length > 0 && (
                    <div className="study-guided-block">
                      <div className="guided-heading-row">
                        <Eye size={16} color="#3b82f6" />
                        <h3 className="guided-heading">Guided Examples & Walkthroughs</h3>
                      </div>
                      {sectionsGuided.map(s => (
                        <div key={s.id} className="study-section-card markdown-section guided-card">
                          <h3 className="section-card-title guided-title">{s.title}</h3>
                          <div className="markdown-body">{renderMarkdown(s.content_markdown)}</div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Navigate to quiz CTA */}
                  <div className="learn-cta-bar">
                    <span className="learn-cta-text">Finished reading? Test your understanding.</span>
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                      {topic.visualization && (
                        <button className="prep-btn-secondary" onClick={() => setActiveTab('visualizer')}>
                          <Play size={13} style={{ marginRight: 5 }} /> Interactive Demo
                        </button>
                      )}
                      {totalQuestions > 0 && (
                        <button className="prep-btn-primary" onClick={() => setActiveTab('quiz')}>
                          Start Quiz <ArrowRight size={13} style={{ marginLeft: 5 }} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* ══ 3. VISUALIZER ════════════════════════════════════════════ */}
              {activeTab === 'visualizer' && topic.visualization && (
                <div className="tab-pane-visualizer">
                  <div className="visualizer-container">
                    <div className="visualizer-header">
                      <div>
                        <h3>{topic.visualization.title}</h3>
                        <p className="visualizer-subtitle">Step through the algorithm interactively to build intuition</p>
                      </div>
                      <span className="vis-badge">{visType?.replace(/-/g, ' ')?.toUpperCase()}</span>
                    </div>

                    <div className="visualizer-sandbox">
                      {/* SLIDING WINDOW */}
                      {visType === 'sliding-window' && (() => {
                        const m = getVisStep(config.steps || []);
                        const swArray = config.array || [];
                        const swK = config.k || 3;
                        return (
                          <div className="vis-sliding-window-box">
                            <div className="sw-array-row">
                              {swArray.map((val, idx) => {
                                const inWin = idx >= (m.left || 0) && idx <= (m.right || 0);
                                return (
                                  <motion.div
                                    key={idx}
                                    className={`sw-cell ${inWin ? 'is-in-window' : ''} ${idx === m.left ? 'is-left' : ''} ${idx === m.right ? 'is-right' : ''}`}
                                    animate={{ scale: inWin ? 1.05 : 1 }}
                                    transition={{ duration: 0.2 }}
                                  >
                                    <span className="sw-cell-val">{val}</span>
                                    <span className="sw-cell-idx">[{idx}]</span>
                                    {idx === m.left && <span className="sw-ptr pointer--left">L</span>}
                                    {idx === m.right && <span className="sw-ptr pointer--right">R</span>}
                                  </motion.div>
                                );
                              })}
                            </div>
                            <div className="vis-metrics-panel">
                              <div className="metric-card"><span className="label">Window Sum</span><span className="val">{m.sum || 0}</span></div>
                              <div className="metric-card"><span className="label">Max Sum</span><span className="val highlight">{m.maxSum || 0}</span></div>
                              <div className="metric-card"><span className="label">Window K</span><span className="val">{swK}</span></div>
                            </div>
                            <div className="vis-step-desc-box">
                              <span className="vis-step-badge">Step {visStep + 1}</span>
                              <p className="vis-step-desc">{m.desc || ''}</p>
                            </div>
                          </div>
                        );
                      })()}

                      {/* LINKED LIST CYCLE */}
                      {visType === 'linked-list-cycle' && (() => {
                        const m = getVisStep(config.steps || []);
                        const llNodes = config.nodes || [];
                        return (
                          <div className="vis-linked-list-box">
                            <div className="ll-nodes-row">
                              {llNodes.map((val, idx) => {
                                const hasSlow = m.slowIdx === idx;
                                const hasFast = m.fastIdx === idx;
                                const hasBoth = hasSlow && hasFast;
                                return (
                                  <div key={idx} className="ll-node-wrapper">
                                    <motion.div
                                      className={`ll-node ${hasSlow ? 'has-slow' : ''} ${hasFast ? 'has-fast' : ''} ${hasBoth ? 'has-both' : ''}`}
                                      animate={{ scale: (hasSlow || hasFast) ? 1.15 : 1 }}
                                      transition={{ duration: 0.2 }}
                                    >
                                      <span className="node-val">{val}</span>
                                      {hasSlow && !hasBoth && <span className="ll-tag tag--slow">S</span>}
                                      {hasFast && !hasBoth && <span className="ll-tag tag--fast">F</span>}
                                      {hasBoth && <span className="ll-tag tag--meet">MEET!</span>}
                                    </motion.div>
                                    <div className="ll-arrow">
                                      {idx === llNodes.length - 1
                                        ? <span className="cycle-arrow">↩ cycle</span>
                                        : <ChevronRight size={18} />
                                      }
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                            <div className="vis-metrics-panel">
                              <div className="metric-card"><span className="label">Slow Ptr</span><span className="val">Node {m.slowIdx || 0}</span></div>
                              <div className="metric-card"><span className="label">Fast Ptr</span><span className="val">Node {m.fastIdx || 0}</span></div>
                              <div className="metric-card"><span className="label">Status</span><span className={`val ${m.slowIdx === m.fastIdx && visStep > 0 ? 'highlight' : ''}`}>{m.slowIdx === m.fastIdx && visStep > 0 ? 'CYCLE!' : 'Searching'}</span></div>
                            </div>
                            <div className="vis-step-desc-box">
                              <span className="vis-step-badge">Step {visStep + 1}</span>
                              <p className="vis-step-desc">{m.desc || ''}</p>
                            </div>
                          </div>
                        );
                      })()}

                      {/* GRAPH DFS */}
                      {visType === 'graph-dfs' && (() => {
                        const m = getVisStep(config.steps || []);
                        const graphNodes = config.nodes || [];
                        return (
                          <div className="vis-graph-box">
                            <div className="graph-diagram">
                              {graphNodes.map(node => {
                                const isActive = m.active === node;
                                const isVisited = (m.visited || []).includes(node);
                                const isQueued = (m.structure || []).includes(node);
                                return (
                                  <motion.div
                                    key={node}
                                    className={`graph-node-circle ${isActive ? 'is-active' : ''} ${isVisited ? 'is-visited' : ''} ${isQueued ? 'is-queued' : ''}`}
                                    animate={{ scale: isActive ? 1.25 : 1 }}
                                    transition={{ duration: 0.2 }}
                                  >
                                    {node}
                                    {isActive && <span className="graph-node-label">Active</span>}
                                  </motion.div>
                                );
                              })}
                            </div>
                            <div className="vis-metrics-panel">
                              <div className="metric-card"><span className="label">Current</span><span className="val">{m.active || '-'}</span></div>
                              <div className="metric-card"><span className="label">Stack</span><span className="val">[{m.structure ? m.structure.join(',') : ''}]</span></div>
                              <div className="metric-card"><span className="label">Visited</span><span className="val highlight">[{m.visited ? m.visited.join(',') : ''}]</span></div>
                            </div>
                            <div className="vis-step-desc-box">
                              <span className="vis-step-badge">Step {visStep + 1}</span>
                              <p className="vis-step-desc">{m.desc || ''}</p>
                            </div>
                          </div>
                        );
                      })()}

                      {/* APTITUDE PROFIT/LOSS */}
                      {visType === 'aptitude-profit' && (
                        <div className="vis-aptitude-box">
                          <div className="slider-row">
                            <div className="slider-container">
                              <label>Cost Price (CP): ₹{cp}</label>
                              <input type="range" min="100" max="2000" step="50" value={cp} onChange={e => setCp(Number(e.target.value))} />
                            </div>
                            <div className="slider-container">
                              <label>Selling Price (SP): ₹{sp}</label>
                              <input type="range" min="50" max="3000" step="50" value={sp} onChange={e => setSp(Number(e.target.value))} />
                            </div>
                          </div>
                          <div className="profit-result-card">
                            <div className={`profit-result-badge ${isProfit ? 'is-profit' : 'is-loss'}`}>
                              {isProfit ? '📈 PROFIT' : '📉 LOSS'}: {pct}%
                            </div>
                            <div className="profit-bar-track">
                              <div className="profit-bar-cp" style={{ width: `${Math.min(95, (cp / 3000) * 100)}%` }} />
                              <div className={`profit-bar-diff ${isProfit ? 'profit' : 'loss'}`}
                                style={{ width: `${Math.min(30, (Math.abs(sp - cp) / 3000) * 100)}%`, left: `${Math.min(95, (Math.min(cp, sp) / 3000) * 100)}%` }}
                              />
                            </div>
                            <div className="profit-bar-labels"><span>CP ₹{cp}</span><span>SP ₹{sp}</span></div>
                          </div>
                          <div className="vis-formula-block">
                            <h5>Formula Calculation:</h5>
                            <pre>{aptFormula}</pre>
                          </div>
                        </div>
                      )}

                      {/* NUMBER SYSTEMS */}
                      {visType === 'number-systems' && (() => {
                        const m = getVisStep(config.steps || []);
                        return (
                          <div className="vis-generic-box" style={{textAlign:'center', padding:'20px'}}>
                            <h3>Convert Decimal {config.decimal} to Binary</h3>
                            <div style={{fontSize:'1.5rem', margin:'20px 0'}}>
                              <span style={{opacity: 0.5}}>Target Binary: </span> 
                              <strong style={{color:'#3b82f6', letterSpacing:'4px'}}>{config.binary}</strong>
                            </div>
                            <div className="vis-step-desc-box">
                              <span className="vis-step-badge">Step {visStep + 1}</span>
                              <p className="vis-step-desc">{m.desc || ''}</p>
                              {m.bit && <div style={{marginTop:'15px', padding:'10px', background:'#F0F9FF', color:'#0369A1', borderRadius:'6px', display:'inline-block', fontWeight:'bold'}}>Extracted Bit: {m.bit}</div>}
                            </div>
                          </div>
                        );
                      })()}

                      {/* DBMS NORMALIZATION */}
                      {visType === 'dbms-normalization' && (() => {
                        const m = getVisStep(config.steps || []);
                        return (
                          <div className="vis-generic-box" style={{textAlign:'center', padding:'20px'}}>
                            <h3>Database Normalization Sequence</h3>
                            <div style={{display:'flex', justifyContent:'center', gap:'15px', margin:'20px 0'}}>
                              {(config.tables || []).map((t, i) => (
                                <div key={i} style={{padding:'12px 24px', border:'2px solid #10b981', borderRadius:'8px', background:'#ECFDF5', color:'#047857', fontWeight:'bold'}}>{t}</div>
                              ))}
                            </div>
                            <div className="vis-step-desc-box">
                              <span className="vis-step-badge">Phase {visStep + 1}</span>
                              <p className="vis-step-desc">{m.desc || ''}</p>
                            </div>
                          </div>
                        );
                      })()}

                      {/* CAREER */}
                      {visType === 'generic' && domain === 'career' && (() => {
                        return (
                          <div className="vis-generic-box" style={{textAlign:'left', padding:'20px'}}>
                            <h3 style={{marginBottom:'15px', color:'#8b5cf6'}}>STAR Framework Builder</h3>
                            <div style={{display:'flex', flexDirection:'column', gap:'10px'}}>
                              <div style={{padding:'10px', background:'var(--bg-panel)', color:'var(--text-primary)', borderLeft:'4px solid #8b5cf6', borderRadius:'4px'}}>
                                <strong>Situation:</strong> Set the scene and provide necessary details.
                              </div>
                              <div style={{padding:'10px', background:'var(--bg-panel)', color:'var(--text-primary)', borderLeft:'4px solid #f59e0b', borderRadius:'4px'}}>
                                <strong>Task:</strong> Describe your specific responsibility in that situation.
                              </div>
                              <div style={{padding:'10px', background:'var(--bg-panel)', color:'var(--text-primary)', borderLeft:'4px solid #10b981', borderRadius:'4px'}}>
                                <strong>Action:</strong> Explain exactly what steps you took.
                              </div>
                              <div style={{padding:'10px', background:'var(--bg-panel)', color:'var(--text-primary)', borderLeft:'4px solid #3b82f6', borderRadius:'4px'}}>
                                <strong>Result:</strong> Share the quantified outcomes.
                              </div>
                            </div>
                          </div>
                        );
                      })()}

                      {/* LOGICAL PUZZLES */}
                      {(visType === 'logical-puzzle' || isLogicalPuzzle) && <LogicalPuzzleVisualizer config={config} />}

                      {/* GENERIC */}
                      {visType === 'generic' && !isLogicalPuzzle && <GenericConceptVisualizer topic={topic} />}
                    </div>

                    {/* Controls */}
                    {visType !== 'aptitude-profit' && visType !== 'generic' && !isLogicalPuzzle && (
                      <div className="visualizer-controls">
                        <button className="prep-btn-secondary" onClick={() => setVisStep(0)}>
                          <RotateCcw size={13} style={{ marginRight: 4 }} /> Reset
                        </button>
                        <div className="vis-step-dots">
                          {Array(maxVisSteps[visType] + 1 || 5).fill(0).map((_, i) => (
                            <span key={i} className={`vis-dot ${i === visStep ? 'is-active' : i < visStep ? 'is-done' : ''}`} onClick={() => setVisStep(i)} />
                          ))}
                        </div>
                        <button
                          className="prep-btn-primary"
                          onClick={() => setVisStep(p => p < (maxVisSteps[visType] || 4) ? p + 1 : 0)}
                        >
                          Next Step <ChevronRight size={13} style={{ marginLeft: 4 }} />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ══ 4. PRACTICE DRILLS ═══════════════════════════════════════ */}
              {activeTab === 'practice' && (
                <div className="tab-pane-practice">
                  <div className="practice-header">
                    <div className="practice-header-icon">
                      {domain === 'career' ? <MessageSquare size={20} /> : <Code2 size={20} />}
                    </div>
                    <div>
                      <h2>
                        {domain === 'career' ? 'Drafting Exercises' :
                         domain === 'core_cs' ? 'Conceptual Drill' :
                         domain === 'aptitude' ? 'Quantitative Practice' : 'Practice Drills'}
                      </h2>
                      <p className="practice-header-subtitle">
                        {domain === 'career' ? 'Behavioral prompts and project explanation drafts' :
                         domain === 'core_cs' ? 'System design scenarios and theory exercises' :
                         domain === 'aptitude' ? 'Problem solving and numeric reasoning' : 'Coding problems matched to this topic'}
                      </p>
                    </div>
                  </div>

                  {domain === 'dsa' && topic.problems && topic.problems.length > 0 ? (
                    <div className="problems-grid">
                      {topic.problems.map(prob => (
                        <div key={prob.id} className="problem-card-item">
                          <div className="problem-meta-top">
                            <span className="difficulty-badge" style={{ color: diffColor(prob.difficulty), background: `${diffColor(prob.difficulty)}18` }}>
                              {prob.difficulty}
                            </span>
                            <div className="company-logos">
                              {prob.companies?.slice(0, 2).map((c, i) => (
                                <span key={i} className="comp-logo-tag">{c}</span>
                              ))}
                            </div>
                          </div>
                          <h3>{prob.title}</h3>
                          <p className="prob-desc">{prob.description}</p>
                          <div className="prob-tags">
                            {prob.topics?.slice(0, 3).map((t, i) => (
                              <span key={i} className="prob-tag">{t}</span>
                            ))}
                          </div>
                          <div className="problem-card-action">
                            {prob.is_solved ? (
                              <span className="solved-status"><Check size={12} /> Solved</span>
                            ) : (
                              <span className="unsolved-status">Not attempted</span>
                            )}
                            <Link to={`/code-lab/arena/${prob.slug}`} className="solve-btn">
                              Solve <ArrowRight size={12} style={{ marginLeft: 4 }} />
                            </Link>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : domain === 'dsa' ? (
                    <div className="practice-empty-note">
                      <Code2 size={32} />
                      <p>Coding problems for this topic are coming soon. In the meantime, test your conceptual mastery in the <strong>Quiz</strong> tab.</p>
                      <button className="prep-btn-primary" onClick={() => setActiveTab('quiz')}>
                        Go to Quiz <ArrowRight size={13} style={{ marginLeft: 5 }} />
                      </button>
                    </div>
                  ) : (
                    <div className="practice-domain-mock">
                      <div style={{background:'var(--bg-panel)', padding:'20px', borderRadius:'8px', border:'1px solid var(--border-color)', marginBottom:'20px'}}>
                        <h4 style={{marginBottom:'10px', color:'var(--text-primary)'}}>
                          {domain === 'career' ? 'Exercise 1: Behavioral Scenario' : domain === 'aptitude' ? 'Exercise 1: Formula Extraction' : 'Exercise 1: Concept Summary'}
                        </h4>
                        <div style={{color:'var(--text-secondary)', marginBottom:'15px', fontSize:'0.95rem', lineHeight:'1.5'}}>
                          {domain === 'career' ? (
                            <>Think of a specific past experience where you demonstrated <strong>{topic?.name}</strong>. Draft the <em>Situation</em> and <em>Task</em> components of your STAR response here.</>
                          ) : domain === 'aptitude' ? (
                            <>What are the core mathematical formulas, shortcuts, or principles underlying <strong>{topic?.name}</strong>? Write them down here for quick reference during practice.</>
                          ) : (
                            <>Summarize the core concept of <strong>{topic?.name}</strong> in your own words. How would you explain it clearly and concisely to a beginner?</>
                          )}
                        </div>
                        <textarea
                          value={drafts['exercise_1'] || ''}
                          onChange={(e) => handleDraftChange('exercise_1', e.target.value)}
                          placeholder="Type your draft here... It will autosave."
                          style={{
                            width: '100%',
                            padding: '15px',
                            background: 'var(--bg-surface)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '6px',
                            minHeight: '120px',
                            color: 'var(--text-primary)',
                            resize: 'vertical',
                            fontFamily: 'inherit',
                            outline: 'none'
                          }}
                        />
                      </div>
                      <div style={{background:'var(--bg-panel)', padding:'20px', borderRadius:'8px', border:'1px solid var(--border-color)'}}>
                        <h4 style={{marginBottom:'10px', color:'var(--text-primary)'}}>
                          {domain === 'career' ? 'Exercise 2: Action & Impact' : domain === 'aptitude' ? 'Exercise 2: Logic Breakdown' : 'Exercise 2: Real-World Application'}
                        </h4>
                        <div style={{color:'var(--text-secondary)', marginBottom:'15px', fontSize:'0.95rem', lineHeight:'1.5'}}>
                          {domain === 'career' ? (
                            <>Continuing from Exercise 1, draft the <em>Action</em> and <em>Result</em> components. Focus on the specific steps <strong>you</strong> took and the quantifiable impact of your actions.</>
                          ) : domain === 'aptitude' ? (
                            <>Create a simple real-world word problem that tests <strong>{topic?.name}</strong>. Briefly outline the logical steps required to solve it without doing the full math.</>
                          ) : (
                            <>Describe a real-world scenario, system design, or engineering problem where applying <strong>{topic?.name}</strong> is critical. What specific trade-offs does it introduce?</>
                          )}
                        </div>
                        <textarea
                          value={drafts['exercise_2'] || ''}
                          onChange={(e) => handleDraftChange('exercise_2', e.target.value)}
                          placeholder="Type your draft here... It will autosave."
                          style={{
                            width: '100%',
                            padding: '15px',
                            background: 'var(--bg-surface)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '6px',
                            minHeight: '120px',
                            color: 'var(--text-primary)',
                            resize: 'vertical',
                            fontFamily: 'inherit',
                            outline: 'none'
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* MCQ Drill mode — additional conceptual questions */}
                  {totalQuestions > 0 && (
                    <div className="practice-mcq-section">
                      <div className="practice-mcq-header">
                        <HelpCircle size={16} color="#8b5cf6" />
                        <div>
                          <h3>Conceptual Drill Questions</h3>
                          <p>MCQ-style questions from the Concept Quiz — great for quick self-testing</p>
                        </div>
                        <button className="prep-btn-primary" onClick={() => setActiveTab('quiz')}>
                          Start Full Quiz <ArrowRight size={13} style={{ marginLeft: 5 }} />
                        </button>
                      </div>
                      <div className="drill-questions-preview">
                        {topic.questions?.slice(0, 3).map((q, i) => (
                          <div key={q.id} className="drill-q-preview">
                            <span className="drill-q-num">Q{i + 1}</span>
                            <span className="drill-q-text">{q.question_text}</span>
                            <span className={`drill-q-diff diff-${(q.difficulty || 'medium').toLowerCase()}`}>{q.difficulty || 'Medium'}</span>
                          </div>
                        ))}
                        <p className="drill-q-more">+{Math.max(0, totalQuestions - 3)} more in the quiz…</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ══ 5. QUIZ ══════════════════════════════════════════════════ */}
              {activeTab === 'quiz' && (
                <div className="tab-pane-quiz">
                  {/* Quiz header with progress */}
                  <div className="quiz-header-panel">
                    <div className="quiz-header-left">
                      <h2>Concept Validation Quiz</h2>
                      <p>Answer all {totalQuestions} questions. Score ≥60% to clear this topic checkpoint.</p>
                    </div>
                    <div className="quiz-progress-pill">
                      <span className="quiz-progress-text">{answeredCount}/{totalQuestions} answered</span>
                      <div className="quiz-progress-bar">
                        <div className="quiz-progress-fill" style={{ width: `${totalQuestions > 0 ? (answeredCount / totalQuestions) * 100 : 0}%` }} />
                      </div>
                    </div>
                  </div>

                  <div className="quiz-questions-list">
                    {topic.questions?.map((q, qIdx) => {
                      const selected = selectedAnswers[q.id];
                      const qResult = quizResult?.results?.find(r => r.question_id === q.id);
                      const showExplanation = expandedExplanations[q.id];
                      return (
                        <div key={q.id} className={`quiz-question-card ${qResult ? (qResult.is_correct ? 'card-correct' : 'card-incorrect') : ''}`}>
                          <div className="quiz-q-meta">
                            <span className="q-number">Question {qIdx + 1}</span>
                            <span className={`q-difficulty diff-${(q.difficulty || 'medium').toLowerCase()}`}>{q.difficulty || 'Medium'}</span>
                          </div>
                          <p className="q-text">{q.question_text}</p>

                          <div className="quiz-options-list">
                            {[
                              { key: 'A', text: q.option_a },
                              { key: 'B', text: q.option_b },
                              { key: 'C', text: q.option_c },
                              { key: 'D', text: q.option_d }
                            ].filter(o => o.text).map(opt => {
                              let cls = '';
                              if (selected === opt.key) cls = 'is-selected';
                              if (qResult) {
                                if (qResult.correct_answer === opt.key) cls = 'is-correct';
                                else if (qResult.selected === opt.key && !qResult.is_correct) cls = 'is-incorrect';
                              }
                              return (
                                <button
                                  key={opt.key}
                                  className={`quiz-option-btn ${cls}`}
                                  onClick={() => handleSelectOption(q.id, opt.key)}
                                  disabled={!!quizResult}
                                >
                                  <span className="option-letter">{opt.key}</span>
                                  <span className="option-text">{opt.text}</span>
                                  {qResult && qResult.correct_answer === opt.key && (
                                    <Check size={14} className="option-check-icon" />
                                  )}
                                </button>
                              );
                            })}
                          </div>

                          {/* Explanation panel (shows after submission) */}
                          {qResult && q.explanation && (
                            <div className="quiz-explanation-panel">
                              <button
                                className="explanation-toggle"
                                onClick={() => setExpandedExplanations(prev => ({ ...prev, [q.id]: !prev[q.id] }))}
                              >
                                <Lightbulb size={13} />
                                {showExplanation ? 'Hide' : 'Show'} Explanation
                              </button>
                              <AnimatePresence>
                                {showExplanation && (
                                  <motion.div
                                    className="explanation-body"
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    transition={{ duration: 0.2 }}
                                  >
                                    <p>{q.explanation}</p>
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Submit / Result bar */}
                  <div className="quiz-action-bar">
                    {!quizResult ? (
                      <div className="quiz-submit-area">
                        <span className="quiz-submit-hint">
                          {answeredCount < totalQuestions
                            ? `${totalQuestions - answeredCount} question${totalQuestions - answeredCount !== 1 ? 's' : ''} remaining`
                            : 'All answered — ready to submit!'}
                        </span>
                        <button
                          className="prep-btn-primary quiz-submit-btn"
                          onClick={handleSubmitQuiz}
                          disabled={answeredCount < totalQuestions || submittingQuiz}
                        >
                          {submittingQuiz ? (
                            <><RefreshCw size={14} className="spin" style={{ marginRight: 6 }} /> Evaluating…</>
                          ) : (
                            <>Submit Answers <ArrowRight size={13} style={{ marginLeft: 6 }} /></>
                          )}
                        </button>
                      </div>
                    ) : (
                      <div className="quiz-result-banner-box">
                        <div className={`result-status-badge ${quizResult.passed ? 'passed' : 'failed'}`}>
                          {quizResult.passed
                            ? <><CheckCircle size={20} /> Passed — {quizResult.accuracy}% Accuracy</>
                            : <><AlertCircle size={20} /> {quizResult.accuracy}% — Need 60% to Pass</>
                          }
                        </div>
                        <div className="result-stats-row">
                          <span>✅ Correct: {quizResult.correct_count}/{quizResult.total_questions}</span>
                          <span>❌ Wrong: {quizResult.total_questions - quizResult.correct_count}/{quizResult.total_questions}</span>
                        </div>
                        <p className="result-detail-text">
                          {quizResult.passed
                            ? 'Excellent! You\'ve cleared this checkpoint. The next topic is now unlocked. Check the explanations above to reinforce what you learned.'
                            : 'Review the explanations above to understand the correct reasoning. Re-read the Learn section, then retry the quiz.'}
                        </p>
                        <div className="result-actions">
                          <button className="prep-btn-secondary" onClick={() => {
                            setQuizResult(null); setSelectedAnswers({}); setExpandedExplanations({});
                          }}>
                            <RotateCcw size={13} style={{ marginRight: 5 }} /> Retry Quiz
                          </button>
                          {quizResult.passed && (
                            <button className="prep-btn-primary" onClick={() => navigate('/prep/journey')}>
                              Continue Journey <ArrowRight size={13} style={{ marginLeft: 5 }} />
                            </button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ══ 6. REVISION CARD ═════════════════════════════════════════ */}
              {activeTab === 'revision' && topic.revision && (
                <div className="tab-pane-revision">
                  <div className="revision-header">
                    <div className="revision-header-icon"><Award size={20} /></div>
                    <div>
                      <h2>Revision Card</h2>
                      <p className="revision-header-subtitle">Quick reference for exam day — formulas, shortcuts, and interview notes</p>
                    </div>
                  </div>

                  <div className="study-section-card">
                    <h3 className="section-card-title">🔑 Key Takeaways</h3>
                    <div className="takeaways-grid">
                      {topic.revision.key_takeaways?.map((takeaway, idx) => (
                        <div key={idx} className="takeaway-card">
                          <span className="takeaway-number">{String(idx + 1).padStart(2, '0')}</span>
                          <p className="takeaway-text">{takeaway}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="study-section-card markdown-section">
                    <h3 className="section-card-title">📋 Cheat Sheet</h3>
                    <div className="markdown-body">{renderMarkdown(topic.revision.cheat_sheet_markdown)}</div>
                  </div>

                  {/* Interview prep tips */}
                  <div className="study-section-card revision-interview-tips">
                    <h3 className="section-card-title">🎯 Interview Tips</h3>
                    <div className="interview-tips-grid">
                      <div className="interview-tip-card">
                        <span className="tip-icon">⏱️</span>
                        <div>
                          <strong>Time Pressure</strong>
                          <p>Always clarify constraints first. Ask: "What are the input size bounds?" before coding.</p>
                        </div>
                      </div>
                      <div className="interview-tip-card">
                        <span className="tip-icon">🗣️</span>
                        <div>
                          <strong>Think Aloud</strong>
                          <p>Explain your approach before writing code. Interviewers score your thought process equally.</p>
                        </div>
                      </div>
                      <div className="interview-tip-card">
                        <span className="tip-icon">📊</span>
                        <div>
                          <strong>Complexity First</strong>
                          <p>Always mention Time and Space complexity — even if not asked. Shows strong CS fundamentals.</p>
                        </div>
                      </div>
                      <div className="interview-tip-card">
                        <span className="tip-icon">🧪</span>
                        <div>
                          <strong>Test Edge Cases</strong>
                          <p>Walk through empty inputs, single elements, and maximum boundary cases after implementation.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* ── Right: AI Tutor Sidebar ──────────────────────────────────────── */}
        {aiSidebarOpen && (
          <motion.div
            className="study-sidebar-ai"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="ai-sidebar-card">
              <div className="ai-sidebar-header">
                <div className="header-title">
                  <Brain size={16} color="#3b82f6" />
                  <span>AI Placement Tutor</span>
                </div>
                <div className="ai-header-right">
                  <span className="ai-context-pill">● Live</span>
                </div>
              </div>

              {/* Context summary */}
              {aiContext && (
                <div className="ai-context-summary">
                  <div className="ai-context-stat">
                    <span className="ctx-val">{aiContext.completed_topics?.length || 0}</span>
                    <span className="ctx-label">Topics done</span>
                  </div>
                  <div className="ai-context-stat">
                    <span className="ctx-val">{aiContext.current_topic?.interview_frequency || 'High'}</span>
                    <span className="ctx-label">Frequency</span>
                  </div>
                  {aiContext.weaknesses?.length > 0 && (
                    <div className="ai-context-weakness">
                      <AlertCircle size={11} />
                      Weak area: {aiContext.weaknesses[0].topic_name}
                    </div>
                  )}
                </div>
              )}

              {/* Messages */}
              <div className="ai-chat-messages-box">
                {aiChatMessages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    className={`chat-message ${msg.role}`}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.15 }}
                  >
                    <div className="msg-avatar">{msg.role === 'user' ? '👤' : '🤖'}</div>
                    <div className="msg-bubble">
                      <p dangerouslySetInnerHTML={{
                        __html: msg.content
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/`(.*?)`/g, '<code>$1</code>')
                          .replace(/\n/g, '<br/>')
                      }} />
                    </div>
                  </motion.div>
                ))}
                {aiTyping && (
                  <div className="chat-message assistant typing">
                    <div className="msg-avatar">🤖</div>
                    <div className="msg-bubble">
                      <span className="typing-dots"><span /><span /><span /></span>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Quick reply chips */}
              <div className="ai-chip-bar">
                {AI_CHIPS.map(chip => (
                  <button
                    key={chip.label}
                    className="ai-chip"
                    onClick={() => sendAIMessage(chip.label)}
                    disabled={aiTyping}
                  >
                    {chip.icon} {chip.label}
                  </button>
                ))}
              </div>

              {/* Input */}
              <form onSubmit={handleSendAIChat} className="ai-chat-input-bar">
                <input
                  type="text"
                  placeholder={`Ask about ${topic.name}…`}
                  value={aiInput}
                  onChange={e => setAiInput(e.target.value)}
                  disabled={aiTyping}
                />
                <button type="submit" disabled={!aiInput.trim() || aiTyping}>
                  <Send size={14} />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
