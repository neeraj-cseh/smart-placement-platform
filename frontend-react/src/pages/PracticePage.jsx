import { useState, useEffect, useRef } from 'react';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Lock, AlertTriangle, Zap, Target, Trophy,
  ArrowRight, Sparkles, X,
  BarChart3, Clock, Lightbulb, Bot,
  ChevronDown, Search, TrendingDown,
  Check, Eye, Gauge, Layers,
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip,
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  BarChart, Bar, CartesianGrid,
} from 'recharts';
import './practice.css';

/* ── Animation variants ─────────────────────────────────────────── */
const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.4, 0, 0.2, 1] } },
};
const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07, delayChildren: 0.04 } },
};
const cardHover = {
  rest:  { y: 0, scale: 1 },
  hover: { y: -4, scale: 1.014, transition: { type: 'spring', stiffness: 380, damping: 22 } },
};
const shake = {
  initial: { x: 0 },
  animate: { x: [0, -8, 8, -6, 6, -3, 3, 0], transition: { duration: 0.5 } },
};


/* ══════════════════════════════════════════════════════════════════
   SUBCOMPONENTS
   ══════════════════════════════════════════════════════════════════ */

/* ── Streak Flame ─────────────────────────────────────────────── */
function StreakFlame({ count }) {
  return (
    <motion.div
      className="pd-flame"
      animate={{ scale: [1, 1.06, 1], filter: ['brightness(1)', 'brightness(1.3)', 'brightness(1)'] }}
      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
    >
      <span className="pd-flame__icon">🔥</span>
      <span className="pd-flame__count">{count}</span>
      <span className="pd-flame__label">day streak</span>
    </motion.div>
  );
}

/* ── XP Flyout ────────────────────────────────────────────────── */
function XPFlyout({ xp, visible }) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="pd-xp-flyout"
          initial={{ opacity: 0, y: 0, scale: 0.8 }}
          animate={{ opacity: 1, y: -48, scale: 1 }}
          exit={{ opacity: 0, y: -70, scale: 0.9 }}
          transition={{ duration: 0.6 }}
        >
          +{xp} XP
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/* ── Drill Card ───────────────────────────────────────────────── */
function DrillCard({ drill, onStart }) {
  const priorityColor = { critical: '#ef4444', high: '#f59e0b', medium: '#6366f1' }[drill.priority] || '#6366f1';
  const difficultyColor = { Easy: '#10b981', Medium: '#f59e0b', Hard: '#ef4444' }[drill.difficulty] || '#6366f1';
  const typeLabel = { timed: '⏱ Timed', adaptive: '🤖 Adaptive', revision: '🔄 Revision', drill: '⚔️ Drill', concept: '💡 Concept' }[drill.type] || drill.type;

  return (
    <motion.div
      className={`pd-drill-card pd-drill-card--${drill.priority}`}
      variants={cardHover}
      initial="rest"
      whileHover="hover"
      onClick={() => onStart(drill)}
      style={{ '--card-color': drill.color, '--priority-color': priorityColor }}
    >
      <div className="pd-drill-card__top">
        <span className="pd-drill-card__icon">{drill.icon}</span>
        <span className="pd-drill-card__type">{typeLabel}</span>
        {drill.priority === 'critical' && (
          <motion.span
            className="pd-drill-card__urgent"
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.2, repeat: Infinity }}
          >
            🚨 Critical
          </motion.span>
        )}
      </div>

      <h3 className="pd-drill-card__title">{drill.title}</h3>
      <p className="pd-drill-card__ai-reason">{drill.aiReason}</p>

      <div className="pd-drill-card__meta">
        <span className="pd-drill-card__diff" style={{ color: difficultyColor }}>● {drill.difficulty}</span>
        <span className="pd-drill-card__time"><Clock size={11} />{drill.time}</span>
        <span className="pd-drill-card__impact" style={{ color: '#10b981' }}>{drill.impact} readiness</span>
      </div>

      <div className="pd-drill-card__footer">
        <div className="pd-drill-card__companies">
          {drill.companies.map(c => (
            <span key={c} className="pd-drill-card__company">{c}</span>
          ))}
        </div>
        <div className="pd-drill-card__xp">+{drill.xp} XP</div>
      </div>

      <div className="pd-drill-card__glow" style={{ background: `radial-gradient(ellipse at 50% 0%, ${drill.color}22, transparent 70%)` }} />
    </motion.div>
  );
}

/* ── Sub Topic Chip ───────────────────────────────────────────── */
function SubTopicChip({ sub, active, onClick }) {
  return (
    <motion.button
      className={`pd-subtopic ${active ? 'pd-subtopic--active' : ''} ${sub.weak ? 'pd-subtopic--weak' : ''}`}
      onClick={() => onClick(sub)}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.97 }}
    >
      {sub.weak && <span className="pd-subtopic__alert">⚠</span>}
      <span className="pd-subtopic__label">{sub.label}</span>
      <span className="pd-subtopic__mastery">{sub.mastery}%</span>
    </motion.button>
  );
}

/* ── Difficulty Level Bar ─────────────────────────────────────── */
function DifficultyBar({ label, value, color, active }) {
  return (
    <div className={`pd-diff-bar ${active ? 'pd-diff-bar--active' : ''}`}>
      <div className="pd-diff-bar__top">
        <span className="pd-diff-bar__label">{label}</span>
        {active && <motion.span
          className="pd-diff-bar__current"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
        >CURRENT</motion.span>}
      </div>
      <div className="pd-diff-bar__track">
        <motion.div
          className="pd-diff-bar__fill"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
        />
      </div>
      <span className="pd-diff-bar__val">{value}%</span>
    </div>
  );
}

/* ── Weakness Card ────────────────────────────────────────────── */
function WeaknessCard({ weakness }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <motion.div
      className="pd-weakness"
      style={{ '--w-color': weakness.color }}
      whileHover={{ y: -3 }}
    >
      <div className="pd-weakness__header">
        <div className="pd-weakness__left">
          <TrendingDown size={16} color={weakness.color} />
          <span className="pd-weakness__topic">{weakness.topic}</span>
          <span className="pd-weakness__badge" style={{ color: weakness.color, borderColor: weakness.color }}>
            -{weakness.drop}%
          </span>
        </div>
        <button className="pd-weakness__expand" onClick={() => setExpanded(!expanded)}>
          <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown size={14} />
          </motion.div>
        </button>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            className="pd-weakness__plan"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <div className="pd-weakness__steps">
              {weakness.plan.map((step, i) => (
                <div key={i} className="pd-weakness__step">
                  <span className="pd-weakness__step-num">{i + 1}</span>
                  <span className="pd-weakness__step-text">{step}</span>
                </div>
              ))}
            </div>
            <motion.button
              className="pd-weakness__cta"
              style={{ background: weakness.color }}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              Start Recovery <ArrowRight size={13} />
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ── Achievement Badge ────────────────────────────────────────── */
function AchievementBadge({ ach }) {
  return (
    <motion.div
      className={`pd-achievement ${ach.earned ? 'pd-achievement--earned' : 'pd-achievement--locked'}`}
      whileHover={{ scale: 1.06, y: -2 }}
    >
      <span className="pd-achievement__icon" style={{ filter: ach.earned ? 'none' : 'grayscale(1) opacity(0.35)' }}>
        {ach.icon}
      </span>
      <span className="pd-achievement__name">{ach.name}</span>
      <span className="pd-achievement__xp">+{ach.xp} XP</span>
      {!ach.earned && <Lock size={10} className="pd-achievement__lock" />}
    </motion.div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   QUESTION WORKSPACE MODAL
   ══════════════════════════════════════════════════════════════════ */
function QuestionWorkspace({ drill, onClose, sampleQuestions }) {
  const questions = sampleQuestions.filter(q =>
    q.topic === drill.topic || sampleQuestions.indexOf(q) < 2
  ).slice(0, 3);
  const [qIndex, setQIndex] = useState(0);
  const [selected, setSelected] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [timeLeft, setTimeLeft] = useState(90);
  const [xpVisible, setXpVisible] = useState(false);
  const [score, setScore] = useState({ correct: 0, wrong: 0, xpTotal: 0 });
  const timerRef = useRef(null);
  const isCorrect = submitted && selected === questions[qIndex]?.correct;

  useEffect(() => {
    setTimeLeft(90); setSelected(null); setSubmitted(false);
    setShowHint(false); setShowExplanation(false);
  }, [qIndex]);

  useEffect(() => {
    if (submitted) return;
    timerRef.current = setInterval(() => {
      setTimeLeft(t => { if (t <= 1) { clearInterval(timerRef.current); setSubmitted(true); return 0; } return t - 1; });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [qIndex, submitted]);

  const handleSubmit = () => {
    if (selected === null) return;
    clearInterval(timerRef.current);
    setSubmitted(true);
    if (selected === questions[qIndex].correct) {
      setXpVisible(true);
      setScore(s => ({ ...s, correct: s.correct + 1, xpTotal: s.xpTotal + questions[qIndex].xp }));
      setTimeout(() => setXpVisible(false), 2000);
    } else {
      setScore(s => ({ ...s, wrong: s.wrong + 1 }));
    }
  };

  const handleNext = () => {
    if (qIndex < questions.length - 1) { setQIndex(i => i + 1); }
    else { onClose(); }
  };

  const q = questions[qIndex];
  const timerPct = (timeLeft / 90) * 100;
  const timerColor = timeLeft > 30 ? '#10b981' : timeLeft > 10 ? '#f59e0b' : '#ef4444';

  return (
    <motion.div
      className="pd-ws-backdrop"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="pd-ws-modal"
        initial={{ opacity: 0, y: 40, scale: 0.94 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 30, scale: 0.96 }}
        transition={{ type: 'spring', stiffness: 340, damping: 28 }}
        onClick={e => e.stopPropagation()}
        style={{ '--drill-color': drill.color }}
      >
        {/* Top accent bar */}
        <div className="pd-ws__topbar" style={{ background: `linear-gradient(90deg, ${drill.color}, ${drill.color}88)` }} />

        {/* Header */}
        <div className="pd-ws__header">
          <div className="pd-ws__header-left">
            <span className="pd-ws__topic-icon">{drill.icon}</span>
            <div>
              <div className="pd-ws__topic">{drill.topic}</div>
              <div className="pd-ws__qcount">Question {qIndex + 1} of {questions.length}</div>
            </div>
          </div>
          <div className="pd-ws__header-right">
            {/* Timer */}
            <div className="pd-ws__timer" style={{ '--t-color': timerColor }}>
              <svg width="36" height="36" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15" fill="none" stroke="var(--border-glass)" strokeWidth="3" />
                <motion.circle
                  cx="18" cy="18" r="15" fill="none" stroke={timerColor} strokeWidth="3"
                  strokeLinecap="round" strokeDasharray="94.2"
                  strokeDashoffset={94.2 - (94.2 * timerPct / 100)}
                  transform="rotate(-90 18 18)"
                  transition={{ duration: 1, ease: 'linear' }}
                />
              </svg>
              <span className="pd-ws__timer-text" style={{ color: timerColor }}>{timeLeft}s</span>
            </div>
            {/* Score */}
            <div className="pd-ws__score">
              <span style={{ color: '#10b981' }}>✓ {score.correct}</span>
              <span style={{ color: '#ef4444' }}>✗ {score.wrong}</span>
            </div>
            <button className="pd-ws__close" onClick={onClose}><X size={16} /></button>
          </div>
        </div>

        {/* Company tags */}
        <div className="pd-ws__tags">
          <span className="pd-ws__diff" style={{ color: { Easy: '#10b981', Medium: '#f59e0b', Hard: '#ef4444' }[q?.difficulty] }}>
            ● {q?.difficulty}
          </span>
          {q?.companies?.map(c => <span key={c} className="pd-ws__company">{c}</span>)}
          <span className="pd-ws__xp-badge">+{q?.xp} XP</span>
        </div>

        {/* Question body */}
        <div className="pd-ws__body">
          <AnimatePresence mode="wait">
            <motion.div
              key={qIndex}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              <p className="pd-ws__question">{q?.text}</p>

              {/* Hint */}
              {showHint && (
                <motion.div
                  className="pd-ws__hint"
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <Lightbulb size={14} color="#f59e0b" />
                  <span>{q?.hint}</span>
                </motion.div>
              )}

              {/* Options */}
              <div className="pd-ws__options">
                {q?.options?.map((opt, i) => {
                  let cls = 'pd-ws__option';
                  if (submitted) {
                    if (i === q.correct) cls += ' pd-ws__option--correct';
                    else if (i === selected) cls += ' pd-ws__option--wrong';
                  } else if (i === selected) {
                    cls += ' pd-ws__option--selected';
                  }
                  return (
                    <motion.button
                      key={i}
                      className={cls}
                      onClick={() => !submitted && setSelected(i)}
                      whileHover={!submitted ? { x: 4 } : {}}
                      animate={submitted && i === selected && i !== q.correct ? shake.animate : {}}
                    >
                      <span className="pd-ws__opt-letter">{String.fromCharCode(65 + i)}</span>
                      <span className="pd-ws__opt-text">{opt}</span>
                      {submitted && i === q.correct && <Check size={14} style={{ marginLeft: 'auto', color: '#10b981' }} />}
                      {submitted && i === selected && i !== q.correct && <X size={14} style={{ marginLeft: 'auto', color: '#ef4444' }} />}
                    </motion.button>
                  );
                })}
              </div>

              {/* Explanation */}
              <AnimatePresence>
                {showExplanation && submitted && (
                  <motion.div
                    className="pd-ws__explanation"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                  >
                    <div className="pd-ws__explanation-header">
                      <Bot size={14} color="#a5b4fc" />
                      <span>AI Explanation</span>
                    </div>
                    <p>{q?.explanation}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Result banner */}
        <AnimatePresence>
          {submitted && (
            <motion.div
              className={`pd-ws__result ${isCorrect ? 'pd-ws__result--correct' : 'pd-ws__result--wrong'}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              {isCorrect ? (
                <>
                  <span>🎉 Correct! +{q?.xp} XP earned</span>
                  <span className="pd-ws__result-impact" style={{ color: '#10b981' }}>+0.3% Amazon readiness</span>
                </>
              ) : (
                <>
                  <span>❌ Incorrect — Review the explanation</span>
                  <span className="pd-ws__result-impact" style={{ color: '#f59e0b' }}>Revision added to your plan</span>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer actions */}
        <div className="pd-ws__footer">
          <button className="pd-ws__btn pd-ws__btn--ghost" onClick={() => setShowHint(!showHint)}>
            <Lightbulb size={14} /> {showHint ? 'Hide Hint' : 'Show Hint'}
          </button>
          {submitted && (
            <button className="pd-ws__btn pd-ws__btn--ghost" onClick={() => setShowExplanation(!showExplanation)}>
              <Eye size={14} /> {showExplanation ? 'Hide Explanation' : 'View Explanation'}
            </button>
          )}
          <div style={{ flex: 1 }} />
          {!submitted ? (
            <motion.button
              className="pd-ws__btn pd-ws__btn--primary"
              style={{ background: drill.color, borderColor: drill.color }}
              onClick={handleSubmit}
              disabled={selected === null}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              Submit Answer
            </motion.button>
          ) : (
            <motion.button
              className="pd-ws__btn pd-ws__btn--primary"
              style={{ background: drill.color, borderColor: drill.color }}
              onClick={handleNext}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              {qIndex < questions.length - 1 ? 'Next Question' : 'Finish Drill'} <ArrowRight size={14} />
            </motion.button>
          )}
        </div>

        <XPFlyout xp={q?.xp || 25} visible={xpVisible} />
      </motion.div>
    </motion.div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MAIN PAGE
   ══════════════════════════════════════════════════════════════════ */
export default function PracticePage() {
  const { data, loading, error } = useApi('/practice/');
  const drillFeed = data?.DRILL_FEED || [];
  const topics = data?.TOPICS || [];
  const subTopics = data?.SUB_TOPICS || {};
  const sampleQuestions = data?.SAMPLE_QUESTIONS || [];
  const { user } = useAuth();
  const [activeTrack, setActiveTrack] = useState('dsa');
  const [activeDrill, setActiveDrill] = useState(null);
  const [activeSubTopic, setActiveSubTopic] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDiff, setFilterDiff] = useState('All');

  const userName = user?.name?.split(' ')[0] || 'Arjun';
  const streak = 12;
  const xpToday = 340;
  const xpTotal = 4540;
  const xpNext = 5000;
  const xpPct = Math.round((xpTotal / xpNext) * 100);
  const readiness = 74;

  const filteredFeed = drillFeed.filter(d => {
    const matchDiff = filterDiff === 'All' || d.difficulty === filterDiff;
    const matchSearch = !searchQuery || d.title.toLowerCase().includes(searchQuery.toLowerCase()) || d.topic.toLowerCase().includes(searchQuery.toLowerCase());
    return matchDiff && matchSearch;
  });

  const subs = subTopics[activeTrack] || [];

  return (
    <Layout title="Practice Arena" subtitle="AI-powered skill mastery engine">
      <motion.div className="pd" variants={stagger} initial="hidden" animate="show">

        {/* ══════════════════════════════════════════════════════════
            SECTION 1: DRILL ARENA HERO
            ══════════════════════════════════════════════════════════ */}
        <motion.section className="pd-hero" variants={fadeUp}>
          <div className="pd-hero__bg">
            <div className="pd-hero__orb pd-hero__orb--1" />
            <div className="pd-hero__orb pd-hero__orb--2" />
            <div className="pd-hero__orb pd-hero__orb--3" />
          </div>

          <div className="pd-hero__inner">
            {/* Left: greeting + goals */}
            <div className="pd-hero__left">
              <div className="pd-hero__greeting">
                <span className="pd-hero__day">Day {streak} · Today's Focus</span>
                <h2 className="pd-hero__title">
                  <span className="pd-hero__name">{userName},</span> conquer{' '}
                  <span className="pd-hero__focus">Graph Traversal</span>
                </h2>
                <p className="pd-hero__sub">Your DFS accuracy improved <strong>+12%</strong> this week. Keep the momentum!</p>
              </div>

              <div className="pd-hero__goals">
                {[
                  { icon: '🎯', text: "Today's goal: 15 questions", sub: '8 completed · 7 remaining' },
                  { icon: '📈', text: 'Amazon OA readiness: +6%', sub: 'after completing this drill set' },
                  { icon: '⚡', text: 'Weak topic alert: DP accuracy 34%', sub: 'Start recovery drill →' },
                ].map((g, i) => (
                  <motion.div
                    key={i}
                    className="pd-hero__goal"
                    initial={{ opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 + i * 0.1 }}
                  >
                    <span>{g.icon}</span>
                    <div>
                      <div className="pd-hero__goal-text">{g.text}</div>
                      <div className="pd-hero__goal-sub">{g.sub}</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>


          </div>
        </motion.section>

        {/* ══════════════════════════════════════════════════════════
            SECTION 2: SMART TOPIC SELECTOR
            ══════════════════════════════════════════════════════════ */}
        <motion.section className="pd-section" variants={fadeUp}>
          <div className="pd-section__header">
            <h2 className="pd-section__title"><Layers size={18} /> Topic Navigator</h2>
            <p className="pd-section__sub">Select a track to adapt your drill feed</p>
          </div>

          {/* Track tabs */}
          <div className="pd-tracks">
            {topics.map(t => (
              <motion.button
                key={t.id}
                className={`pd-track ${activeTrack === t.id ? 'pd-track--active' : ''} ${t.weak ? 'pd-track--weak' : ''}`}
                style={{ '--t-color': t.color }}
                onClick={() => { setActiveTrack(t.id); setActiveSubTopic(null); }}
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.97 }}
              >
                <span className="pd-track__icon">{t.icon}</span>
                <div className="pd-track__info">
                  <span className="pd-track__label">{t.label}</span>
                  <span className="pd-track__mastery" style={{ color: t.color }}>{t.mastery}%</span>
                </div>
                {t.weak && <span className="pd-track__weak-dot" />}
                {activeTrack === t.id && (
                  <motion.div className="pd-track__indicator" style={{ background: t.color }} layoutId="trackIndicator" />
                )}
              </motion.button>
            ))}
          </div>

          {/* Sub-topic chips */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTrack}
              className="pd-subtopics"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              {subs.map(s => (
                <SubTopicChip
                  key={s.id}
                  sub={s}
                  active={activeSubTopic?.id === s.id}
                  onClick={setActiveSubTopic}
                />
              ))}
            </motion.div>
          </AnimatePresence>
        </motion.section>

        {/* ══════════════════════════════════════════════════════════
            SECTION 3 + 4: ADAPTIVE FEED + AI DIFFICULTY ENGINE
            ══════════════════════════════════════════════════════════ */}
        <motion.section className="pd-section" variants={fadeUp}>
          <div className="pd-feed-layout">

            {/* Feed column */}
            <div className="pd-feed">
              <div className="pd-feed__header">
                <div className="pd-feed__title-row">
                  <h2 className="pd-section__title"><Sparkles size={18} /> Adaptive Practice Feed</h2>
                  <motion.span className="pd-feed__ai-badge"
                    animate={{ opacity: [1, 0.6, 1] }} transition={{ duration: 2, repeat: Infinity }}>
                    🤖 AI Curated
                  </motion.span>
                </div>

                {/* Search + filter */}
                <div className="pd-feed__controls">
                  <div className="pd-feed__search">
                    <Search size={14} />
                    <input
                      placeholder="Search drills..."
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <div className="pd-feed__filters">
                    {['All', 'Easy', 'Medium', 'Hard'].map(d => (
                      <button
                        key={d}
                        className={`pd-feed__filter ${filterDiff === d ? 'pd-feed__filter--active' : ''}`}
                        onClick={() => setFilterDiff(d)}
                      >
                        {d}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <motion.div className="pd-feed__grid" variants={stagger}>
                <AnimatePresence>
                  {filteredFeed.map(drill => (
                    <motion.div key={drill.id} variants={fadeUp} layout>
                      <DrillCard drill={drill} onStart={setActiveDrill} />
                    </motion.div>
                  ))}
                </AnimatePresence>
              </motion.div>
            </div>

            {/* AI Difficulty Engine sidebar */}
            <div className="pd-diff-engine">
              <div className="pd-diff-engine__header">
                <Gauge size={16} color="#a5b4fc" />
                <span>AI Difficulty Engine</span>
              </div>
              <div className="pd-diff-engine__status">
                <motion.span
                  className="pd-diff-engine__pulse"
                  animate={{ scale: [1, 1.4, 1], opacity: [1, 0.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                Adapting to your patterns…
              </div>

              <div className="pd-diff-engine__levels">
                <DifficultyBar label="Beginner"  value={100} color="#10b981" active={false} />
                <DifficultyBar label="Easy"      value={88}  color="#22d3ee" active={false} />
                <DifficultyBar label="Medium"    value={61}  color="#6366f1" active={true} />
                <DifficultyBar label="Hard"      value={34}  color="#f59e0b" active={false} />
                <DifficultyBar label="Expert"    value={12}  color="#ef4444" active={false} />
              </div>

              <div className="pd-diff-engine__insights">
                {[
                  { text: 'Graph mastery improving — Medium questions unlocked', color: '#10b981' },
                  { text: 'DP difficulty reduced temporarily — need more practice', color: '#f59e0b' },
                  { text: 'Aptitude speed challenge unlocked at 80% accuracy', color: '#6366f1' },
                ].map((ins, i) => (
                  <div key={i} className="pd-diff-engine__insight" style={{ borderLeftColor: ins.color }}>
                    {ins.text}
                  </div>
                ))}
              </div>

              <div className="pd-diff-engine__confidence">
                <div className="pd-diff-engine__conf-label">
                  <span>Confidence Meter</span>
                  <span style={{ color: '#a5b4fc' }}>74%</span>
                </div>
                <div className="pd-diff-engine__conf-track">
                  <motion.div
                    className="pd-diff-engine__conf-fill"
                    initial={{ width: 0 }}
                    animate={{ width: '74%' }}
                    transition={{ duration: 1, delay: 0.5 }}
                  />
                </div>
              </div>
            </div>
          </div>
        </motion.section>



      </motion.div>

      {/* ── Question Workspace Modal ─────────────────────────────── */}
      <AnimatePresence>
        {activeDrill && (
          <QuestionWorkspace
            drill={activeDrill}
            onClose={() => setActiveDrill(null)}
          />
        )}
      </AnimatePresence>
    </Layout>
  );
}
