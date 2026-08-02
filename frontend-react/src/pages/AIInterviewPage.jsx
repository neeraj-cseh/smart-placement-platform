import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import { motion } from 'framer-motion';
import {
  Bot, CheckCircle, XCircle, Brain,
  Play, RotateCcw, Clock, Sparkles, ArrowRight, Layers, BookOpen,
  AlertTriangle, X, Eye,
} from 'lucide-react';

import './ai-interview.css';

/* ── Animation variants ──────────────────────────────────────────── */
const fadeUp = {
  hidden: { opacity: 0, y: 22 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.42, ease: [0.4, 0, 0.2, 1] } },
};
const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07, delayChildren: 0.04 } },
};
const cardHover = {
  rest:  { y: 0, scale: 1 },
  hover: { y: -6, scale: 1.018, transition: { type: 'spring', stiffness: 340, damping: 22 } },
};

/* ── Helpers ─────────────────────────────────────────────────────── */
function formatTime(s) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
}

/* ══════════════════════════════════════════════════════════════════
   DYNAMIC DATA NOW COMES FROM THE BACKEND
   ══════════════════════════════════════════════════════════════════ */

/* ── Typing animation hook ───────────────────────────────────────── */
function useTypingText(text, speed = 28, active = true) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!active || !text) { setDisplayed(text || ''); setDone(true); return; }
    setDisplayed('');
    setDone(false);
    let i = 0;
    const iv = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) { clearInterval(iv); setDone(true); }
    }, speed);
    return () => clearInterval(iv);
  }, [text, speed, active]);

  return { displayed, done };
}

/* ── Readiness Ring ──────────────────────────────────────────────── */
function ReadinessRing({ value, size = 90, color = '#6366f1', label }) {
  const r = (size - 10) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (circ * value) / 100;
  return (
    <div style={{ width: size, height: size, flexShrink: 0, position: 'relative' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--border-glass)" strokeWidth="6" />
        <motion.circle
          cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="6"
          strokeLinecap="round" strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.3, ease: 'easeOut', delay: 0.2 }}
          transform={`rotate(-90 ${size/2} ${size/2})`}
        />
        <text x={size/2} y={size/2 - 4} textAnchor="middle" fill="var(--text-primary)" fontSize="15" fontWeight="900">{value}%</text>
        {label && <text x={size/2} y={size/2 + 13} textAnchor="middle" fill="rgba(255,255,255,0.4)" fontSize="9">{label}</text>}
      </svg>
    </div>
  );
}

/* ── AI Waveform ─────────────────────────────────────────────────── */
function AIWaveform({ active }) {
  return (
    <div className="ai-wave">
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="ai-wave__bar"
          animate={active ? {
            height: [6, 14 + ((i * 7 + 3) % 4) * 5, 6],
          } : { height: 4 }}
          transition={{ duration: 0.6 + i * 0.06, repeat: active ? Infinity : 0, ease: 'easeInOut', delay: i * 0.05 }}
        />
      ))}
    </div>
  );
}

/* ── Interview Type Card ─────────────────────────────────────────── */
function InterviewCard({ type, onStart, loading }) {
  const diffColor = { Easy: '#10b981', Medium: '#f59e0b', Hard: '#ef4444', Expert: '#a78bfa' }[type.difficulty];

  return (
    <motion.div
      className="ai-type-card"
      style={{ '--card-color': type.color }}
      variants={cardHover}
      initial="rest"
      whileHover="hover"
    >
      <div className="ai-type-card__top">
        <span className="ai-type-card__icon">{type.icon}</span>
        <span className="ai-type-card__badge">{type.badge}</span>
      </div>

      <h3 className="ai-type-card__name">{type.label}</h3>
      <p className="ai-type-card__desc">{type.description}</p>

      <div className="ai-type-card__focus">
        {type.focus.map(f => <span key={f} className="ai-type-card__tag">{f}</span>)}
      </div>

      <div className="ai-type-card__meta">
        <span style={{ color: diffColor }}>● {type.difficulty}</span>
        <span><Clock size={11}/> {type.duration}m</span>
        <span style={{ color: '#10b981', fontWeight: 800 }}>{type.readinessImpact}</span>
      </div>

      <div className="ai-type-card__footer">
        <div className="ai-type-card__ai-score">
          <span className="ai-type-card__ai-label">AI Readiness</span>
          <div className="ai-type-card__ai-bar">
            <motion.div
              className="ai-type-card__ai-fill"
              style={{ background: type.color }}
              initial={{ width: 0 }}
              animate={{ width: `${type.aiScore}%` }}
              transition={{ duration: 0.9, delay: 0.2 }}
            />
          </div>
          <span style={{ color: type.color, fontSize: '0.7rem', fontWeight: 800 }}>{type.aiScore}%</span>
        </div>

        <motion.button
          className="ai-type-card__start"
          style={{ background: type.color }}
          onClick={() => onStart(type.id)}
          disabled={loading}
          whileHover={{ scale: 1.07 }}
          whileTap={{ scale: 0.95 }}
        >
          <Play size={13} /> Start
        </motion.button>
      </div>
      <div className="ai-type-card__glow" style={{ background: `radial-gradient(ellipse at 50% -10%, ${type.color}22, transparent 65%)` }} />
    </motion.div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   LIVE INTERVIEW WORKSPACE
   ══════════════════════════════════════════════════════════════════ */
function InterviewWorkspace({ category, currentQ, questionIndex, totalQ, onNextQuestion, onEnd, loading }) {
  const [elapsed, setElapsed] = useState(0);
  const chatEndRef = useRef(null);

  /* Timer */
  useEffect(() => {
    const iv = setInterval(() => setElapsed(t => t + 1), 1000);
    return () => clearInterval(iv);
  }, []);

  /* Scroll chat to bottom */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentQ]);

  const { displayed: questionText, done: questionDone } = useTypingText(
    currentQ?.question || '', 20, true
  );

  const handleNextQuestion = onNextQuestion;

  const categoryLabel = { general: 'HR', technical: 'Technical', behavioral: 'Behavioral' }[category] || 'Interview';
  const categoryColor = { general: '#6366f1', technical: '#10b981', behavioral: '#f59e0b' }[category] || '#6366f1';

  return (
    <div className="ai-ws">
      {/* Top bar */}
      <div className="ai-ws__topbar">
        <div className="ai-ws__brand">
          <motion.div
            className="ai-ws__avatar-dot"
            style={{ background: categoryColor }}
            animate={{ scale: [1, 1.15, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <div>
            <div className="ai-ws__brand-name">AI Interview Coach — {categoryLabel} Round</div>
            <div className="ai-ws__brand-meta">Question {questionIndex + 1} of {totalQ}</div>
          </div>
        </div>

        <div className="ai-ws__stats">
          {/* Learning Progress (Replaced Confidence) */}
          <div className="ai-ws__conf">
            <span className="ai-ws__conf-label">Coach Session</span>
            <div className="ai-ws__conf-bar">
              <motion.div
                className="ai-ws__conf-fill"
                style={{ width: `100%`, background: categoryColor }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <span className="ai-ws__conf-val" style={{ color: categoryColor }}>Active</span>
          </div>

          {/* Timer */}
          <div className="ai-ws__timer" style={{ color: elapsed > 1800 ? '#ef4444' : 'rgba(255,255,255,0.7)' }}>
            <Clock size={13} /> {formatTime(elapsed)}
          </div>

          {/* Progress dots */}
          <div className="ai-ws__progress">
            {[...Array(totalQ)].map((_, i) => (
              <div
                key={i}
                className="ai-ws__progress-dot"
                style={{
                  background: i < questionIndex ? '#10b981' :
                    i === questionIndex ? categoryColor : 'rgba(255,255,255,0.12)',
                  boxShadow: i === questionIndex ? `0 0 8px ${categoryColor}60` : 'none',
                }}
              />
            ))}
          </div>

          <motion.button
            className="ai-ws__end-btn"
            onClick={onEnd}
            aria-label="End Coach Session"
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
          >
            <X size={13} /> End
          </motion.button>
        </div>
      </div>

      {/* Main interview layout */}
      <div className="ai-ws__layout">
        {/* Chat panel */}
        <div className="ai-ws__chat">
          <div className="ai-ws__chat-feed">
            {/* Current question */}
            {currentQ && (
              <div className="ai-ws__bubble ai-ws__bubble--ai ai-ws__bubble--active" style={{ maxWidth: '100%' }}>
                <motion.div
                  className="ai-ws__bubble-avatar"
                  style={{ background: categoryColor }}
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Bot size={14} />
                </motion.div>
                <div className="ai-ws__bubble-body" style={{ width: '100%' }}>
                  <div className="ai-ws__bubble-label">
                    AI Coach
                    <span className="ai-ws__area-badge" style={{ background: `${categoryColor}22`, color: categoryColor }}>
                      {currentQ.area}
                    </span>
                  </div>
                  <div className="ai-ws__bubble-text">
                    {questionText}
                    {!questionDone && <span className="ai-ws__cursor">|</span>}
                  </div>
                  
                  {/* The Coach Blueprint (Massive Context Version) */}
                  {questionDone && currentQ.blueprint && (
                    <motion.div 
                      className="ai-ws__blueprint ai-ws__blueprint--massive"
                      initial={{ opacity: 0, y: 10, height: 0 }}
                      animate={{ opacity: 1, y: 0, height: 'auto' }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                    >
                      <div className="ai-ws__blueprint-header">
                        <Sparkles size={16} style={{ color: categoryColor }} /> Coach's Comprehensive Guide
                      </div>
                      
                      <div className="ai-ws__blueprint-section">
                        <div className="ai-ws__bp-title"><Layers size={13} /> Why they ask this (Context)</div>
                        <div className="ai-ws__bp-content">{currentQ.blueprint.context}</div>
                      </div>

                      <div className="ai-ws__blueprint-grid">
                        <div className="ai-ws__blueprint-col ai-ws__blueprint-col--say">
                          <div className="ai-ws__bp-title"><CheckCircle size={13} /> What to Say</div>
                          <div className="ai-ws__bp-content" style={{ whiteSpace: 'pre-line' }}>{currentQ.blueprint.what_to_say}</div>
                        </div>
                        <div className="ai-ws__blueprint-col ai-ws__blueprint-col--avoid">
                          <div className="ai-ws__bp-title"><XCircle size={13} /> What to Avoid</div>
                          <div className="ai-ws__bp-content" style={{ whiteSpace: 'pre-line' }}>{currentQ.blueprint.what_not_to_say}</div>
                        </div>
                      </div>

                      <div className="ai-ws__blueprint-section ai-ws__blueprint-section--example">
                        <div className="ai-ws__bp-title" style={{ color: '#8b5cf6' }}><Bot size={13} /> Ideal Example Answer</div>
                        <div className="ai-ws__bp-content" style={{ fontStyle: 'italic' }}>"{currentQ.blueprint.example_answer}"</div>
                      </div>

                      <div className="ai-ws__blueprint-behavior">
                        <span className="ai-ws__bp-tag">💡 Delivery Tip</span>
                        {currentQ.blueprint.behavioral}
                      </div>
                    </motion.div>
                  )}

                  {/* Waveform speaking indicator */}
                  {!questionDone && <AIWaveform active={true} />}
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Next Navigation Area */}
          <div className="ai-ws__nav-area">
            <motion.button
              className="ai-ws__next-btn"
              style={{ background: categoryColor }}
              onClick={handleNextQuestion}
              disabled={loading || !questionDone}
              aria-label={questionIndex + 1 >= totalQ ? 'Finish Coaching Session' : 'Next Question'}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
            >
              {questionIndex + 1 >= totalQ ? 'Finish Coaching Session' : 'Next Question'} <ArrowRight size={15} />
            </motion.button>
          </div>
        </div>


      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   POST-INTERVIEW EVALUATION
   ══════════════════════════════════════════════════════════════════ */
function EvaluationView({ result, onBack }) {
  // Removed strict percentage grade logic
  const gradeColor = '#a5b4fc';

  const evalScores = useMemo(() => {
    const base = [
      { label: 'Communication', scale: 0.9, drift: 4, color: '#6366f1' },
      { label: 'Technical Depth', scale: 0.85, drift: 6, color: '#10b981' },
      { label: 'Confidence', scale: 0.92, drift: 3, color: '#f59e0b' },
      { label: 'Problem Solving', scale: 0.88, drift: 5, color: '#8b5cf6' },
      { label: 'Clarity', scale: 0.95, drift: 2, color: '#06b6d4' },
    ];
    return base.map(s => {
      const calculated = Math.round(90 * s.scale + s.drift); // Fixed to high mastery for UI
      return {
        label: s.label,
        score: Math.min(99, calculated),
        color: s.color
      };
    });
  }, []);

  const confettiPieces = useMemo(() => {
    return [...Array(14)].map((_, i) => ({
      left: ((i * 7.1) + 5) % 100,
      color: ['#6366f1','#10b981','#f59e0b','#ec4899'][i % 4],
      drift: ((i * 29) % 90) - 45,
      duration: 1.5 + (i * 0.13) % 1.2
    }));
  }, []);

  return (
    <motion.div className="ai-eval" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
      {/* Confetti for completion */}
      <div className="ai-eval__confetti">
        {confettiPieces.map((p, i) => (
          <motion.div key={i} className="ai-eval__confetti-piece"
            style={{ left: `${p.left}%`, background: p.color }}
            initial={{ y: -10, opacity: 1 }}
            animate={{ y: 220, opacity: 0, x: p.drift }}
            transition={{ duration: p.duration, delay: i * 0.07 }}
          />
        ))}
      </div>

      <div className="ai-eval__header">
        <div className="ai-eval__header-left">
          <Bot size={28} style={{ color: '#a5b4fc' }} />
          <div>
            <div className="ai-eval__title">Coaching Session Complete</div>
            <div className="ai-eval__subtitle" style={{ color: gradeColor }}>Great practice!</div>
          </div>
        </div>
        <ReadinessRing value={100} size={100} color={gradeColor} label="Focus" />
      </div>

      {/* Score breakdown */}
      <div className="ai-eval__scores">
        {evalScores.map((s, i) => (
          <motion.div key={s.label} className="ai-eval__score-row"
            initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + i * 0.08 }}
          >
            <span className="ai-eval__score-label">{s.label}</span>
            <div className="ai-eval__score-bar">
              <motion.div className="ai-eval__score-fill"
                style={{ background: s.color }}
                initial={{ width: 0 }}
                animate={{ width: `${s.score}%` }}
                transition={{ duration: 0.8, delay: 0.2 + i * 0.08 }}
              />
            </div>
            <span className="ai-eval__score-val" style={{ color: s.color }}>{s.score}%</span>
          </motion.div>
        ))}
      </div>

      {/* Q&A Replay */}
      <div className="ai-eval__replay">
        <div className="ai-eval__replay-title"><Eye size={15}/> Session Replay</div>
        {(result.qa_pairs || []).map((qa, i) => (
          <motion.div key={i} className={`ai-eval__qa ai-eval__qa--good`}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 * i }}
          >
            <div className="ai-eval__qa-header">
              <CheckCircle size={14} style={{ color: '#a5b4fc' }}/>
              <span className="ai-eval__qa-q">Q{i + 1}: {qa.question}</span>
            </div>
            <div className="ai-eval__qa-answer">"{qa.your_answer}"</div>
            {qa.feedback && <div className="ai-eval__qa-feedback"><Bot size={11}/> {qa.feedback}</div>}
          </motion.div>
        ))}
      </div>

      {/* AI feedback block */}
      <div className="ai-eval__ai-block">
        <div className="ai-eval__ai-header"><Bot size={14} color="#a5b4fc"/> AI Coach Summary</div>
        <p className="ai-eval__ai-text">
          Outstanding round! Review the coaching blueprints and your practice answers above. Taking time to reflect on your delivery and structure will significantly improve your confidence in real interviews. Keep up the momentum!
        </p>
      </div>

      <div className="ai-eval__actions">
        <motion.button className="ai-eval__btn ai-eval__btn--ghost" onClick={onBack}
          whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>
          ← Back to Hub
        </motion.button>
        <motion.button className="ai-eval__btn ai-eval__btn--primary" onClick={onBack}
          whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>
          <RotateCcw size={14} /> Retry Round
        </motion.button>
      </div>
    </motion.div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MAIN PAGE
   ══════════════════════════════════════════════════════════════════ */
export default function AIInterviewPage() {
  /* Real backend state */
  const { data: configData } = useApi('/interview/config/');
  const [sessionId, setSessionId] = useState(null);
  const [category, setCategory] = useState(null);
  const [currentQ, setCurrentQ] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQ, setTotalQ] = useState(0);
  const [finalResult, setFinalResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [phase, setPhase] = useState('hub'); // hub | interview | result

  // Derive dynamic backend data
  const INTERVIEW_TYPES = configData?.interview_types || [];

  /* Real backend: Start interview */
  const handleStart = async (cat) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/interview/start/', { category: cat });
      setSessionId(res.session_id);
      setCategory(cat);
      setCurrentQ(res.current_question);
      setQuestionIndex(res.question_index);
      setTotalQ(res.total_questions);
      setFinalResult(null);
      setPhase('interview');
    } catch (err) {
      setError(err.message || 'Failed to start interview.');
    } finally {
      setLoading(false);
    }
  };

  /* Real backend: Next question (study guide mode) */
  const handleNextQuestion = useCallback(async () => {
    setError('');

    

    try {
      if (questionIndex + 1 < totalQ) {
        const nextRes = await api.post('/interview/question/', { session_id: sessionId });
        setCurrentQ(nextRes.current_question);
        setQuestionIndex(nextRes.question_index);
      } else {
        const endRes = await api.post('/interview/end/', { session_id: sessionId });
        setFinalResult(endRes);
        setPhase('result');
        setSessionId(null);
      }
    } catch (err) {
      setError(err.message);
    }
  }, [sessionId, questionIndex, totalQ, category]);

  const handleEndInterview = useCallback(async () => {
    if (sessionId && sessionId !== 'demo') {
      try { await api.post('/interview/end/', { session_id: sessionId }); } catch (err) { console.error(err); }
    }
    setPhase('hub');
    setSessionId(null);
    setCurrentQ(null);
  }, [sessionId]);

  const handleBack = useCallback(() => {
    setPhase('hub');
    setFinalResult(null);
    setCategory(null);
    setSessionId(null);
    setCurrentQ(null);
  }, []);

  /* ── INTERVIEW phase ────────────────────────────────────────────── */
  if (phase === 'interview' && currentQ) {
    return (
      <InterviewWorkspace
        category={category}
        sessionId={sessionId}
        currentQ={currentQ}
        questionIndex={questionIndex}
        totalQ={totalQ}
        onNextQuestion={handleNextQuestion}
        onEnd={handleEndInterview}
        loading={loading}
      />
    );
  }

  /* ── RESULT phase ─────────────────────────────────────────────── */
  if (phase === 'result' && finalResult) {
    return (
      <Layout title="Interview Evaluation" subtitle="AI-powered performance analysis">
        <EvaluationView result={finalResult} category={category} onBack={handleBack} />
      </Layout>
    );
  }

  /* ══════════════════════════════════════════════════════════════════
     HUB PHASE
     ══════════════════════════════════════════════════════════════════ */
  return (
    <Layout title="AI Interview Coach" subtitle="Cinematic AI-powered placement interview simulator">
      <motion.div className="ai-hub" variants={stagger} initial="hidden" animate="show">

        {/* ════════════════════════════════════════════════════════════
            SECTION 1: INTERVIEW ARENA HERO
            ════════════════════════════════════════════════════════════ */}
        <motion.section className="ai-hero" variants={fadeUp}>
          <div className="ai-hero__bg">
            <div className="ai-hero__orb ai-hero__orb--1" />
            <div className="ai-hero__orb ai-hero__orb--2" />
            <div className="ai-hero__orb ai-hero__orb--3" />
          </div>

          <div className="ai-hero__inner">
            <div className="ai-hero__left">
              <div className="ai-hero__eyebrow">
                <motion.span className="ai-hero__live"
                  animate={{ opacity: [1, 0.4, 1] }}
                  transition={{ duration: 1.8, repeat: Infinity }}
                >
                  <Sparkles size={10} /> AI PLAYBOOK
                </motion.span>
                <span className="ai-hero__streak"><BookOpen size={13}/> 10 Modules Available</span>
              </div>

              <h2 className="ai-hero__title">
                The Ultimate{' '}
                <span className="ai-hero__accent">Placement Playbook</span>
              </h2>
              <p className="ai-hero__sub">
                Explore 10 curated modules covering HR, System Design, React, and Core CS. 
                Everything you need to master your next big interview.
              </p>

              <div className="ai-hero__insights">
                {[
                  { icon: '🚀', text: 'Master modern System Design & Architecture' },
                  { icon: '⚛️', text: 'Deep dive into React, Hooks & Web Vitals' },
                  { icon: '🗄️', text: 'Conquer complex SQL & Database concepts' },
                ].map((ins, i) => (
                  <motion.div key={i} className="ai-hero__insight"
                    initial={{ opacity: 0, x: -14 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 + i * 0.1 }}
                  >
                    <span>{ins.icon}</span><span>{ins.text}</span>
                  </motion.div>
                ))}
              </div>

              {error && <div className="ai-hero__error"><AlertTriangle size={14}/> {error} (demo mode active)</div>}
            </div>

            <div className="ai-hero__rings" style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
              <div className="ai-hero__ring-main playbook-graphic" style={{padding: '30px', background: 'rgba(99,102,241,0.05)', borderRadius: '50%', border: '2px solid rgba(99,102,241,0.1)'}}>
                <Brain size={80} color="#6366f1" />
              </div>
              
              <div className="ai-hero__quick-stats" style={{marginTop: '30px'}}>
                {[
                  { icon: '📚', val: '10+', label: 'Topics' },
                  { icon: '💡', val: '30+', label: 'Deep Dives' },
                  { icon: '🌟', val: '100%', label: 'Quality' },
                ].map(s => (
                  <div key={s.label} className="ai-hero__quick-stat">
                    <span>{s.icon}</span>
                    <span className="ai-hero__quick-val">{s.val}</span>
                    <span className="ai-hero__quick-label">{s.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.section>

        {/* ════════════════════════════════════════════════════════════
            SECTION 2: INTERVIEW TYPE SELECTOR
            ════════════════════════════════════════════════════════════ */}
        <motion.section className="ai-section" variants={fadeUp}>
          <div className="ai-section__header">
            <h2 className="ai-section__title"><Layers size={17}/> Select a Study Module</h2>
            <p className="ai-section__sub">AI selects adaptive questions based on your weak areas</p>
          </div>

          <motion.div className="ai-types-grid" variants={stagger}>
            {INTERVIEW_TYPES.map((type, i) => (
              <motion.div key={i} variants={fadeUp}>
                <InterviewCard type={type} onStart={handleStart} loading={loading} />
              </motion.div>
            ))}
          </motion.div>
        </motion.section>



      </motion.div>
    </Layout>
  );
}
