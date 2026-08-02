import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight, BarChart3, Brain, Building2,
  CheckCircle2, Code2, Flame, Target, Trophy,
  Zap, Sparkles, TrendingUp, AlertTriangle,
  Calendar, Activity, Bot, X,
  ChevronRight, Lightbulb, Cpu, Ghost, FolderSearch,
} from 'lucide-react';
import {
  Bar, BarChart, ResponsiveContainer,
  Tooltip, CartesianGrid, XAxis, YAxis, Area, AreaChart,
} from 'recharts';
import './dashboard.css';

/* ── Animation variants ─────────────────────────────────────────── */
const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.4, 0, 0.2, 1] } },
};

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
};

/* ── Mock data removed ────────────── */







const COMPANY_COLORS = [
  '#f97316', '#3b82f6', '#10b981', '#8b5cf6', '#06b6d4', '#ef4444',
];

/* ── Animated Counter ───────────────────────────────────────────── */
function AnimatedCounter({ value, duration = 1200 }) {
  const [display, setDisplay] = useState(0);
  const start = useRef(null);
  const target = parseFloat(value) || 0;

  useEffect(() => {
    start.current = null;
    let raf;
    const step = (ts) => {
      if (!start.current) start.current = ts;
      const progress = Math.min((ts - start.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(eased * target));
      if (progress < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);

  return <>{display}</>;
}

/* ── Readiness Ring ─────────────────────────────────────────────── */
function ReadinessRing({ value = 0, color = 'url(#ringGrad)', size = 160 }) {
  const r = 68;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, value));
  const offset = circ - (pct / 100) * circ;

  return (
    <div className="db-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3b82f6" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} className="db-ring-track" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r}
          className="db-ring-fill"
          stroke={color}
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: [0.4, 0, 0.2, 1] }}
        />
      </svg>
      <div className="db-ring-inner">
        <span className="db-ring-value">
          <AnimatedCounter value={pct} />%
        </span>
        <span className="db-ring-label">Placement Ready</span>
      </div>
    </div>
  );
}

/* ── Skill bar color ────────────────────────────────────────────── */
function skillColor(score) {
  if (score >= 80) return '#10b981';
  if (score >= 60) return '#3b82f6';
  if (score >= 40) return '#f59e0b';
  return '#ef4444';
}


/* ── Empty State Component ──────────────────────────────────────── */
function EmptyState({ icon: Icon, title, desc, actionText, onAction }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '32px 20px', textAlign: 'center', background: 'rgba(255,255,255,0.01)', borderRadius: 12, border: '1px dashed var(--border-primary)', height: '100%' }}>
      <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'rgba(59, 130, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16 }}>
        <Icon size={24} style={{ color: '#3b82f6' }} />
      </div>
      <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>{title}</span>
      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: 240, lineHeight: 1.5, marginBottom: actionText ? 16 : 0 }}>{desc}</span>
      {actionText && (
        <button className="btn btn--secondary btn--sm" onClick={onAction}>
          {actionText}
        </button>
      )}
    </div>
  );
}

/* ── Main Dashboard ─────────────────────────────────────────────── */

function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data, loading } = useApi('/auth/dashboard/');
  const [tasks, setTasks] = useState({});
  const [aiOpen, setAiOpen] = useState(false);

  useEffect(() => {
    if (data?.todays_plan?.items) {
      const init = {};
      data.todays_plan.items.forEach((_, i) => { init[i] = false; });
      setTasks(init);
    }
  }, [data]);

  if (loading) {
    return (
      <Layout title="Dashboard">
        <div className="db-loading">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton skeleton--card" style={{ height: 120 }} />
          ))}
        </div>
      </Layout>
    );
  }

  if (!data) return null;

  /* ── Derived data ─────────────────────────────────────────────── */
  const metrics      = data.metrics || [];
  const plan         = data.todays_plan || {};
  const weekly       = data.weekly_momentum || [];
  const companies    = data.company_readiness || [];
  const activity     = data.recent_activity || [];
  const skills       = data.subject_mastery || [];
  const weakTopics   = data.weakness_priorities || [];
  const interviewPrep = data.interview_prep || [];
  const target       = data.sidebar?.current_target || {};
  const readiness    = plan.readiness || {};
  const planItems    = plan.items || [];
  const planDone     = Object.values(tasks).filter(Boolean).length;
  const planTotal    = planItems.length || plan.total_count || 0;
  const planPct      = planTotal ? Math.round((planDone / planTotal) * 100) : 0;
  const streak       = data.streak || 14;
  const xpTotal      = data.xp || 2480;
  const studyHours   = data.study_hours || 3.5;
  const firstName    = user?.name?.split(' ')[0] || data.header?.greeting?.split(' ')[1] || 'Champion';

  /* ── Stat card tones ──────────────────────────────────────────── */
  const statTones = ['blue', 'green', 'violet', 'amber'];
  const metricIcons = { target: Target, check: CheckCircle2, flame: Flame, line: TrendingUp };



  return (
    <Layout title={data.header?.greeting || `Welcome back, ${firstName}`} subtitle={data.header?.subtitle}>
      <motion.div className="db" variants={stagger} initial="hidden" animate="show">

        {/* ══════════════════════════════════════════════════════
            1. AI WELCOME HERO
        ══════════════════════════════════════════════════════ */}
        <motion.section className="db-hero" variants={fadeUp}>
          <div className="db-hero__grid-bg" />

          <div className="db-hero__left">
            <div className="db-hero__eyebrow">
              <div className="db-hero__eyebrow-dot" />
              <Cpu size={12} /> AI Placement Command Center
            </div>

            <h2 className="db-hero__greeting">
              Hey, <span>{firstName}</span>.<br />
              Let's crush today.
            </h2>

            <p className="db-hero__subtitle">
              {data.header?.subtitle || 'Your AI co-pilot is tracking every metric, adapting every plan, and pushing you toward your dream company.'}
            </p>

            <div className="db-hero__insights">
              <motion.span
                className="db-hero__insight-pill db-hero__insight-pill--blue"
                whileHover={{ scale: 1.04 }}
              >
                <TrendingUp size={12} />
                You are {readiness.value || 72}% {target.name || 'Amazon'}-ready
              </motion.span>
              <motion.span
                className="db-hero__insight-pill db-hero__insight-pill--green"
                whileHover={{ scale: 1.04 }}
              >
                <Flame size={12} />
                {streak}-day consistency streak
              </motion.span>
              <motion.span
                className="db-hero__insight-pill db-hero__insight-pill--violet"
                whileHover={{ scale: 1.04 }}
              >
                <Zap size={12} />
                {xpTotal} XP earned this week
              </motion.span>
              <motion.span
                className="db-hero__insight-pill db-hero__insight-pill--amber"
                whileHover={{ scale: 1.04 }}
              >
                <Activity size={12} />
                Graph speed ↑18% this week
              </motion.span>
            </div>

            <div className="db-hero__actions">
              <motion.button
                className="btn btn--primary btn--md"
                onClick={() => navigate('/practice')}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
              >
                Practice Now <ArrowRight size={16} />
              </motion.button>
              <motion.button
                className="btn btn--secondary btn--md"
                onClick={() => navigate('/mock-tests')}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
              >
                Take Mock Test
              </motion.button>
              <motion.button
                className="btn btn--secondary btn--md"
                onClick={() => navigate('/ai-interview')}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
              >
                <Bot size={15} /> AI Interview
              </motion.button>
            </div>
          </div>

          <div className="db-hero__right">
            <div className="db-ring-wrap">
              <ReadinessRing value={readiness.value || 72} />
            </div>

            <div className="db-target-card">
              <div className="db-target-label">🎯 Current Target</div>
              <div className="db-target-name">
                {target.full_name || target.name || 'Amazon'}
              </div>
              <span
                className="db-target-badge"
                style={{
                  background: 'rgba(16,185,129,0.12)',
                  color: '#10b981',
                  border: '1px solid rgba(16,185,129,0.25)',
                  fontSize: '0.65rem',
                  fontWeight: 800,
                  padding: '3px 10px',
                  borderRadius: 999,
                }}
              >
                {target.readiness_label || `${readiness.value || 72}% Ready`}
              </span>
            </div>
          </div>
        </motion.section>

        {/* ══════════════════════════════════════════════════════
            STAT CARDS
        ══════════════════════════════════════════════════════ */}
        <motion.div className="db-stats" variants={stagger}>
          {metrics.map((m, i) => {
            const Icon = metricIcons[m.icon] || BarChart3;
            const tone = statTones[i % statTones.length];
            const isUp = (m.change || '').includes('+') || (m.change || '').includes('↑');
            return (
              <motion.div
                key={i}
                className={`db-stat db-stat--${tone}`}
                variants={fadeUp}
                whileHover="hover"
                initial="rest"
              >
                <div className="db-stat__glow" />
                <div className="db-stat__top">
                  <div className="db-stat__icon"><Icon size={18} /></div>
                  {m.change && (
                    <span className={`db-stat__change db-stat__change--${isUp ? 'up' : 'down'}`}>
                      {m.change}
                    </span>
                  )}
                </div>
                <div className="db-stat__value">
                  <AnimatedCounter value={parseFloat(m.value) || 0} />
                  {String(m.value).includes('%') ? '%' : ''}
                </div>
                <div className="db-stat__label">{m.label}</div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* ══════════════════════════════════════════════════════
            2 + 3. DAILY MISSION  ‖  WEEKLY MOMENTUM
        ══════════════════════════════════════════════════════ */}
        <motion.div className="db-grid-2" variants={stagger}>

          {/* Daily Mission */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title">
                <Target size={15} />Daily Mission Center
              </span>
              <span className="db-mission-xp">
                <Zap size={13} />{xpTotal} XP
              </span>
            </div>
            <div className="db-card-body">
              <div className="db-mission-header">
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Today's Focus · Est. 2h 30m
                </span>
                <button
                  className="db-card-action"
                  onClick={() => navigate('/learning-path')}
                >
                  View all <ChevronRight size={12} />
                </button>
              </div>

              <div className="db-mission-progress">
                <div className="db-mission-progress-text">
                  <strong>{planDone}/{planTotal || 5}</strong>
                  <span>tasks done</span>
                </div>
                <div className="db-mission-bar">
                  <motion.div
                    className="db-mission-bar-fill"
                    initial={{ width: 0 }}
                    animate={{ width: `${planPct}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                  />
                </div>
                <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#10b981', minWidth: 36 }}>
                  {planPct}%
                </span>
              </div>

              <motion.div className="db-task-list" variants={stagger}>
                {(!planItems || planItems.length === 0) ? (
                  <EmptyState icon={Target} title="No Active Missions" desc="You have cleared your queue. Start a practice session to unlock new AI missions." actionText="Go to Arena" onAction={() => navigate('/code-lab/arena')} />
                ) : (
                  (planItems || []).map((item, i) => (

                  <motion.div
                    key={i}
                    className={`db-task ${tasks[i] ? 'db-task--done' : ''}`}
                    variants={fadeUp}
                    whileHover={{ x: 3 }}
                    onClick={() => setTasks(prev => ({ ...prev, [i]: !prev[i] }))}
                  >
                    <div className="db-task-check">
                      {tasks[i] && <CheckCircle2 size={12} />}
                    </div>
                    <div className="db-task-info">
                      <span className="db-task-name">{item.task}</span>
                      <span className="db-task-detail">{item.detail}</span>
                    </div>
                    <div className="db-task-right">
                      <span className="db-task-xp">+{item.xp || 30} XP</span>
                      <div className={`db-priority-dot db-priority-dot--${item.priority || 'med'}`} />
                    </div>
                  </motion.div>
                ))
                )}
              </motion.div>
            </div>
          </motion.div>

          {/* Weekly Momentum Chart */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title">
                <BarChart3 size={15} />Weekly Momentum
              </span>
              <button className="db-card-action" onClick={() => navigate('/analytics')}>
                Deep dive <ChevronRight size={12} />
              </button>
            </div>
            <div className="db-card-body">
              
              <div className="db-chart-wrap">
                {(!weekly || weekly.length === 0) ? (
                  <EmptyState icon={TrendingUp} title="No Momentum Data" desc="Complete a mock test or solve problems to generate your weekly chart." actionText="Take Mock Test" onAction={() => navigate('/mock-tests')} />
                ) : (
                <ResponsiveContainer width="100%" height="100%">

                  <AreaChart
                    data={weekly.length > 0 ? weekly : [
                      { day: 'Mon', accuracy: 68, solved: 8 },
                      { day: 'Tue', accuracy: 75, solved: 12 },
                      { day: 'Wed', accuracy: 71, solved: 9 },
                      { day: 'Thu', accuracy: 82, solved: 15 },
                      { day: 'Fri', accuracy: 79, solved: 11 },
                      { day: 'Sat', accuracy: 88, solved: 18 },
                      { day: 'Sun', accuracy: 85, solved: 14 },
                    ]}
                    margin={{ top: 8, right: 8, left: -20, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="gradAcc" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
                        <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="gradSol" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="var(--border-primary)" strokeDasharray="4 4" vertical={false} />
                    <XAxis dataKey="day" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 10, fontSize: 12 }}
                      cursor={{ stroke: 'rgba(255,255,255,0.08)' }}
                    />
                    <Area type="monotone" dataKey="accuracy" stroke="#3b82f6" strokeWidth={2.5} fill="url(#gradAcc)" dot={false} />
                    <Area type="monotone" dataKey="solved"   stroke="#10b981" strokeWidth={2.5} fill="url(#gradSol)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
                )}
              </div>
              <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  <span style={{ width: 12, height: 3, borderRadius: 999, background: '#3b82f6', display: 'inline-block' }} />
                  Accuracy %
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  <span style={{ width: 12, height: 3, borderRadius: 999, background: '#10b981', display: 'inline-block' }} />
                  Problems Solved
                </span>
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* ══════════════════════════════════════════════════════
            4 + 5. COMPANY READINESS ‖ SKILL HEATMAP
        ══════════════════════════════════════════════════════ */}
        <motion.div className="db-grid-2" variants={stagger}>

          {/* Company Readiness */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title"><Building2 size={15} />Company Readiness</span>
              <button className="db-card-action" onClick={() => navigate('/companies')}>
                View all <ChevronRight size={12} />
              </button>
            </div>
            <div className="db-card-body">
              <div className="db-company-list">
                {(!companies || companies.length === 0) ? (
                  <EmptyState icon={Building2} title="No Target Companies" desc="Add target companies in your career settings to track readiness." actionText="View Companies" onAction={() => navigate('/career')} />
                ) : (
                  companies.slice(0, 6).map((c, i) => {

                  const col = COMPANY_COLORS[i % COMPANY_COLORS.length];
                  const initials = (c.full_name || c.name || '??').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
                  return (
                    <motion.div key={i} className="db-company" whileHover={{ x: 4 }}>
                      <div className="db-company-avatar" style={{ background: col }}>{initials}</div>
                      <div className="db-company-info">
                        <span className="db-company-name">{c.full_name || c.name}</span>
                        <div className="db-company-bar">
                          <motion.div
                            className="db-company-bar-fill"
                            style={{ background: col }}
                            initial={{ width: 0 }}
                            animate={{ width: `${c.readiness}%` }}
                            transition={{ duration: 1.2, delay: i * 0.1, ease: 'easeOut' }}
                          />
                        </div>
                      </div>
                      <span className="db-company-pct" style={{ color: col }}>{c.readiness}%</span>
                    </motion.div>
                  );
                }))}
              </div>
            </div>
          </motion.div>

          {/* Skill Heatmap & Weakness Engine */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title"><Brain size={15} />Skill Mastery & Weakness</span>
              <button className="db-card-action" onClick={() => navigate('/analytics')}>
                Analytics <ChevronRight size={12} />
              </button>
            </div>
            <div className="db-card-body">
              <div className="db-skills">
                {(!skills || skills.length === 0) ? (
                  <EmptyState icon={Brain} title="Skill Radar Empty" desc="Solve problems to calibrate your skill mastery heatmap." />
                ) : (
                  skills.slice(0, 7).map((s, i) => {

                  const name = s.topic || s.name;
                  const score = s.value !== undefined ? s.value : s.score;
                  const col = skillColor(score);
                  return (
                    <div key={i} className="db-skill">
                      <span className="db-skill-name">{name}</span>
                      <div className="db-skill-track">
                        <motion.div
                          className="db-skill-fill"
                          style={{ background: col }}
                          initial={{ width: 0 }}
                          animate={{ width: `${score}%` }}
                          transition={{ duration: 1, delay: i * 0.08, ease: 'easeOut' }}
                        />
                      </div>
                      <span className="db-skill-pct" style={{ color: col }}>{score}%</span>
                    </div>
                  );
                }))}
              </div>

              {/* Weakness alerts */}
              <div className="db-skill-weakness">
                <div className="db-skill-weakness-title">
                  <AlertTriangle size={12} /> AI Weakness Alerts
                </div>
                {(!weakTopics || weakTopics.length === 0) ? (
                  <div style={{ textAlign: 'center', padding: '16px 0', color: 'var(--text-muted)' }}>
                    <CheckCircle2 size={18} style={{ color: '#10b981', margin: '0 auto 8px', display: 'block' }} />
                    <span style={{ fontSize: '0.75rem' }}>No critical weaknesses detected!</span>
                  </div>
                ) : (
                  weakTopics.slice(0, 3).map((w, i) => (

                  <div key={i} className="db-weakness-item">
                    <strong style={{ color: 'var(--text-primary)', fontSize: '0.78rem' }}>
                      {w.topic || w.track}
                    </strong>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      — {w.reason || w.track}
                    </span>
                  </div>
                ))
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* ══════════════════════════════════════════════════════
            6 + 8. ACTIVITY TIMELINE ‖ AI RECOMMENDATIONS
        ══════════════════════════════════════════════════════ */}
        <motion.div className="db-grid-2" variants={stagger}>

          {/* Activity Timeline */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title"><Activity size={15} />Daily Activity Timeline</span>
            </div>
            <div className="db-card-body">
              <div className="db-timeline">
                {(!activity || activity.length === 0) ? (
                  <EmptyState icon={Activity} title="No Recent Activity" desc="Your timeline will update as you interact with the platform." />
                ) : (
                  (activity || []).map((a, i) => (

                  <motion.div key={i} className="db-tl-item" whileHover={{ x: 4 }}>
                    <div
                      className={`db-tl-dot ${a.live ? 'db-tl-dot--live' : ''}`}
                      style={{ borderColor: a.color || 'var(--accent-primary)', color: a.color }}
                    />
                    <div className="db-tl-content">
                      <span className="db-tl-title">{a.title}</span>
                      <span className="db-tl-time">{a.time}</span>
                    </div>
                  </motion.div>
                ))
                )}
              </div>
            </div>
          </motion.div>

          {/* AI Recommendations */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title"><Sparkles size={15} />AI Recommendations</span>
            </div>
            <div className="db-card-body">
              <motion.div className="db-reco-list" variants={stagger}>
                {(!data.recommendations || data.recommendations.length === 0) ? (
                  <EmptyState icon={Sparkles} title="No Recommendations" desc="The AI needs more data. Continue practicing to generate personalized recommendations." />
                ) : (
                  (data.recommendations || []).map((r, i) => (

                  <motion.div
                    key={i}
                    className={`db-reco db-reco--${r.level}`}
                    variants={fadeUp}
                    whileHover={{ x: 4 }}
                  >
                    <div className="db-reco-icon"><r.icon size={14} /></div>
                    <span className="db-reco-text">{r.text}</span>
                    <span className="db-reco-priority">{r.priority}</span>
                  </motion.div>
                ))
                )}
              </motion.div>
            </div>
          </motion.div>
        </motion.div>

        {/* ══════════════════════════════════════════════════════
            9 + 10 + 11. STREAK ‖ PRODUCTIVITY ‖ EVENTS
        ══════════════════════════════════════════════════════ */}
        <motion.div className="db-grid-3" variants={stagger}>

          {/* Streak & Achievements */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title"><Flame size={15} />Streak & Achievements</span>
            </div>
            <div className="db-card-body">
              <div className="db-streak-hero">
                <div className="db-streak-flame">🔥</div>
                <div>
                  <div className="db-streak-count"><AnimatedCounter value={streak} /></div>
                  <div className="db-streak-label">Day Streak</div>
                </div>
                <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Next milestone</div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#f59e0b' }}>21 days 🎯</div>
                </div>
              </div>
              <div className="db-badges">
                {(data.badges || []).map((b, i) => (
                  <motion.div key={i} className="db-badge" whileHover={{ scale: 1.03 }}>
                    <span className="db-badge-icon">{b.icon}</span>
                    <div>
                      <span className="db-badge-name">{b.name}</span>
                      <span className="db-badge-desc">{b.desc}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Productivity Insights */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title"><TrendingUp size={15} />Productivity Insights</span>
            </div>
            <div className="db-card-body">
              <div className="db-prod-grid">
                <div className="db-prod-stat">
                  <span className="db-prod-val">{studyHours}h</span>
                  <span className="db-prod-lbl">Today</span>
                </div>
                <div className="db-prod-stat">
                  <span className="db-prod-val">22h</span>
                  <span className="db-prod-lbl">This week</span>
                </div>
                <div className="db-prod-stat">
                  <span className="db-prod-val">94%</span>
                  <span className="db-prod-lbl">Active days</span>
                </div>
              </div>

              <div className="db-chart-wrap" style={{ height: 120, marginBottom: 12 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map((d, i) => ({
                      day: d,
                      hours: [2.5, 3, 2, 4, 3.5, 5, 2][i],
                    }))}
                    margin={{ top: 4, right: 4, left: -30, bottom: 0 }}
                  >
                    <XAxis dataKey="day" tick={{ fontSize: 10, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 8, fontSize: 11 }}
                      cursor={{ fill: 'var(--text-muted)' }}
                    />
                    <Bar dataKey="hours" fill="#3b82f6" radius={[4, 4, 0, 0]} opacity={0.8} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="db-prod-insight">
                <Lightbulb size={13} style={{ color: '#f59e0b', flexShrink: 0 }} />
                <span>
                  Your productivity peaks at <strong style={{ color: 'var(--text-primary)', margin: '0 4px' }}>8–10 PM</strong> — schedule hard topics then.
                </span>
              </div>
            </div>
          </motion.div>

          {/* Events & Deadlines */}
          <motion.div className="db-card" variants={fadeUp}>
            <div className="db-card-header">
              <span className="db-card-title"><Calendar size={15} />Events & Deadlines</span>
            </div>
            <div className="db-card-body">
              <div className="db-events">
                {(!data.events || data.events.length === 0) ? (
                  <EmptyState icon={Calendar} title="No Upcoming Events" desc="You have no scheduled interviews or mock tests." />
                ) : (
                  (data.events || []).map((e, i) => (

                  <motion.div key={i} className="db-event" whileHover={{ x: 4 }}>
                    <div className="db-event-date">
                      <span className="db-event-day">{e.day}</span>
                      <span className="db-event-month">{e.month}</span>
                    </div>
                    <div className="db-event-info">
                      <span className="db-event-title">{e.title}</span>
                      <span className="db-event-sub">{e.sub}</span>
                    </div>
                    <span className={`db-event-urgency db-event-urgency--${e.urgency}`}>
                      {e.urgency === 'hot' ? 'Urgent' : e.urgency === 'soon' ? 'Soon' : 'Upcoming'}
                    </span>
                  </motion.div>
                ))
                )}
              </div>

              <div style={{ marginTop: 14, padding: '10px 12px', borderRadius: 'var(--radius)', background: 'var(--bg-secondary)', border: '1px solid var(--border-primary)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>
                  Interview Prep Status
                </div>
                {interviewPrep.slice(0, 2).map((ip, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{ip.category}</span>
                    <span style={{
                      fontSize: '0.72rem', fontWeight: 800,
                      color: skillColor(ip.score || ip.readiness || 70),
                    }}>{ip.score || ip.readiness || 70}%</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* ══════════════════════════════════════════════════════
            Subject Mastery Bar Chart (Full Width)
        ══════════════════════════════════════════════════════ */}
        <motion.div className="db-card" variants={fadeUp}>
          <div className="db-card-header">
            <span className="db-card-title"><BarChart3 size={15} />Subject Mastery Analytics</span>
            <button className="db-card-action" onClick={() => navigate('/analytics')}>
              Full report <ChevronRight size={12} />
            </button>
          </div>
          <div className="db-card-body">
            <div className="db-chart-wrap" style={{ height: 220 }}>
              {(!skills || skills.length === 0) ? (
                <EmptyState icon={BarChart3} title="Not Enough Data" desc="We need more performance data across different topics to generate a reliable mastery report." />
              ) : (
              <ResponsiveContainer width="100%" height="100%">

                <BarChart
                  data={skills.slice(0, 8)}
                  margin={{ top: 8, right: 8, left: -20, bottom: 0 }}
                >
                  <defs>
                    {['#3b82f6','#10b981','#8b5cf6','#f59e0b','#06b6d4','#ef4444','#f97316','#ec4899'].map((c, i) => (
                      <linearGradient key={i} id={`bg${i}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor={c} stopOpacity={0.9} />
                        <stop offset="100%" stopColor={c} stopOpacity={0.4} />
                      </linearGradient>
                    ))}
                  </defs>
                  <CartesianGrid stroke="var(--border-primary)" strokeDasharray="4 4" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 10, fontSize: 12 }} cursor={{ fill: 'var(--text-muted)' }} />
                  <Bar dataKey="score" radius={[6, 6, 0, 0]} fill="url(#bg0)" />
                </BarChart>
              </ResponsiveContainer>
              )}
            </div>
          </div>
        </motion.div>

      </motion.div>

      {/* ══════════════════════════════════════════════════════
          12. FLOATING AI ASSISTANT
      ══════════════════════════════════════════════════════ */}
      <div className="db-ai-orb">
        <AnimatePresence>
          {aiOpen && (
            <motion.div
              className="db-ai-panel"
              initial={{ opacity: 0, scale: 0.85, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.85, y: 20 }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            >
              <div className="db-ai-panel-head">
                <div className="db-ai-panel-title">
                  <span style={{ fontSize: '1rem' }}>🤖</span>
                  PrepSmart AI
                </div>
                <button className="db-ai-panel-close" onClick={() => setAiOpen(false)}>
                  <X size={14} />
                </button>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.35)', marginBottom: 12 }}>
                What can I help you with today?
              </div>
              <div className="db-ai-suggestions">
                {(data?.aiSuggestions || []).map((s, i) => (
                  <motion.div
                    key={i}
                    className="db-ai-suggestion"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06 }}
                    onClick={() => navigate('/ai-interview')}
                  >
                    {s}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.button
          className="db-ai-btn"
          onClick={() => setAiOpen(v => !v)}
          whileHover={{ scale: 1.12 }}
          whileTap={{ scale: 0.92 }}
          title="Open AI Assistant"
        >
          {aiOpen ? <X size={22} /> : <Bot size={22} />}
        </motion.button>
      </div>
    </Layout>
  );
}

export default DashboardPage;
