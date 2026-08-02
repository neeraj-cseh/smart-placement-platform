import React from 'react';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { CheckCircle2, Lock, Trophy, Sparkles, Trophy as TrophyIcon, Zap, Clock, ShieldAlert } from 'lucide-react';
import './prep-ecosystem.css';

function ScoreProgressRing({ value = 0, size = 140 }) {
  const r = 58;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, value));
  const offset = circ - (pct / 100) * circ;

  return (
    <div className="prep-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="scoreRingGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#d97706" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} className="prep-ring-track" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r}
          className="prep-ring-fill"
          stroke="url(#scoreRingGrad)"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: [0.4, 0, 0.2, 1] }}
        />
      </svg>
      <div className="prep-ring-inner">
        <span className="prep-ring-value" style={{ color: '#fbbf24' }}>{pct}%</span>
        <span className="prep-ring-label">Avg Score</span>
      </div>
    </div>
  );
}

export default function MockTestsPage() {
  const { data, loading, error, refetch } = useApi('/prep/milestones/');

  const handleStartTest = async (testId, name) => {
    try {
      const response = await api.post(`/tests/${testId}/start/`);
      alert(`Test initialized!\nAttempt ID: ${response.attempt_id}\nStarted at: ${response.started_at}\n\n(A dedicated quiz execution module can connect here. The backend database session is now successfully tracking this attempt!)`);
      refetch();
    } catch (err) {
      alert(`Failed to start test: ${err.message || err}`);
    }
  };

  if (loading) {
    return (
      <div className="prep-container">
        <div className="prep-hero">
          <div className="prep-hero__grid-bg" />
          <h2 className="prep-hero__title">Milestones</h2>
          <p className="prep-hero__subtitle">Loading timed assessments...</p>
        </div>
        <div className="prep-layout-grid">
          <div className="prep-main-flow">
            <div className="skeleton skeleton--card" style={{ height: 180, borderRadius: 12, opacity: 0.15 }} />
            <div className="prep-milestones-list">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="skeleton skeleton--card" style={{ height: 100, borderRadius: 8, opacity: 0.15 }} />
              ))}
            </div>
          </div>
          <div className="prep-sidebar-flow">
            <div className="skeleton skeleton--card" style={{ height: 220, borderRadius: 12, opacity: 0.15 }} />
            <div className="skeleton skeleton--card" style={{ height: 200, borderRadius: 12, opacity: 0.15 }} />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="prep-container">
        <div className="prep-hero">
          <div className="prep-hero__grid-bg" />
          <h2 className="prep-hero__title">Error <span>Loading Milestones</span></h2>
          <p className="prep-hero__subtitle">Failed to load milestone mock assessments. {error}</p>
        </div>
      </div>
    );
  }

  const tests = data?.tests || [];

  if (tests.length === 0) {
    return (
      <div className="prep-container">
        <div className="prep-hero">
          <div className="prep-hero__grid-bg" />
          <h2 className="prep-hero__title">No <span>Milestones Available</span></h2>
          <p className="prep-hero__subtitle">No mock tests have been registered in the database yet.</p>
        </div>
      </div>
    );
  }

  // Find next milestone and attempts metrics
  const completedTests = tests.filter(t => t.attempt_count > 0);
  const nextMilestone = tests.find(t => t.attempt_count === 0) || tests[0];
  const averageScore = completedTests.length > 0 
    ? Math.round(completedTests.reduce((acc, curr) => acc + (curr.best_score || 0), 0) / completedTests.length)
    : 0;

  return (
    <div className="prep-container">
      {/* Header */}
      <div className="prep-hero">
        <div className="prep-hero__grid-bg" />
        <h2 className="prep-hero__title">Assessments & <span>Milestones</span></h2>
        <p className="prep-hero__subtitle">
          Prove your mastery through timed milestone assessments. Clear these boss battle exams to unlock higher-tier study paths and get placement readiness certifications.
        </p>
      </div>

      {/* Two-Column Grid Layout */}
      <div className="prep-layout-grid">
        
        {/* Left Column: Focus Target + Milestones Checklist */}
        <div className="prep-main-flow">
          
          {/* Active Milestone Target Banner */}
          {nextMilestone && (
            <motion.div 
              className="prep-focus-card"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="prep-card__glow glow--amber" style={{ opacity: 0.08 }} />
              <div className="prep-focus-card__left">
                <div className="prep-focus-card__eyebrow" style={{ color: '#fbbf24' }}>
                  <TrophyIcon size={12} /> Target Assessment
                </div>
                <h3 className="prep-focus-card__title">{nextMilestone.name}</h3>
                <p className="prep-focus-card__desc">
                  {nextMilestone.description || 'Complete this core timed assessment to prove your preparation levels and unlock credentials.'}
                </p>
                <div className="prep-timeline-meta" style={{ marginTop: '8px' }}>
                  <span className="prep-milestone-duration"><Clock size={11} style={{ marginRight: 2 }} /> {nextMilestone.duration_minutes}m Duration</span>
                  {nextMilestone.question_count > 0 && <span className="prep-milestone-duration">{nextMilestone.question_count} Questions</span>}
                </div>
              </div>
              <div className="prep-focus-card__right">
                <button className="prep-btn-primary" onClick={() => handleStartTest(nextMilestone.id, nextMilestone.name)}>
                  {nextMilestone.attempt_count > 0 ? 'Retake Test Center' : 'Launch Test Center'}
                </button>
              </div>
            </motion.div>
          )}

          {/* Checklist of Milestone Tests */}
          <div className="prep-milestones-wrap">
            <div className="prep-milestones-list">
              {tests.map((milestone, idx) => {
                const isCompleted = milestone.attempt_count > 0;
                const isLocked = milestone.is_locked;
                const isUnlocked = !isLocked && !isCompleted;
                
                return (
                  <motion.div 
                    key={milestone.id}
                    className={`prep-card prep-milestone-card ${isLocked ? 'prep-card--locked' : ''} ${isCompleted ? 'prep-card--completed' : ''} ${isUnlocked ? 'prep-card--active' : ''}`}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: idx * 0.08 }}
                  >
                    {isCompleted && <div className="prep-card__glow glow--green" style={{ opacity: 0.03 }} />}
                    {isUnlocked && <div className="prep-card__glow glow--blue" style={{ opacity: 0.06 }} />}
                    
                    <div className="prep-milestone-left">
                      <div className="prep-milestone-badge-icon">
                        {isCompleted ? (
                          <CheckCircle2 size={20} strokeWidth={2.5} />
                        ) : isLocked ? (
                          <Lock size={16} />
                        ) : (
                          <Trophy size={18} />
                        )}
                      </div>
                      
                      <div className="prep-milestone-info">
                        <div className="prep-milestone-title">{milestone.name}</div>
                        <div className="prep-milestone-desc">{milestone.description || 'Milestone assessment.'}</div>
                        
                        <div className="prep-milestone-meta" style={{ marginTop: '8px' }}>
                          <span className="prep-milestone-duration">{milestone.duration_minutes}m</span>
                          {milestone.question_count > 0 && (
                            <span className="prep-milestone-duration" style={{ color: 'var(--text-muted)' }}>
                              {milestone.question_count} Qs
                            </span>
                          )}
                          {isCompleted && milestone.best_score !== null && (
                            <span className="prep-milestone-score-shell">
                              <Sparkles size={12} style={{ marginRight: 2 }} /> {milestone.best_score}% Best
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="prep-milestone-actions">
                      {isLocked ? (
                        <button className="prep-btn-secondary" disabled>
                          <Lock size={12} style={{ marginRight: 4 }} /> Locked
                        </button>
                      ) : isCompleted ? (
                        <button className="prep-btn-secondary" onClick={() => handleStartTest(milestone.id, milestone.name)}>
                          Retake Test
                        </button>
                      ) : (
                        <button className="prep-btn-primary" onClick={() => handleStartTest(milestone.id, milestone.name)}>
                          Start Test
                        </button>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Sidebar Statistics */}
        <div className="prep-sidebar-flow">
          
          {/* Average Mock Score Ring */}
          <div className="prep-card" style={{ flexDirection: 'column', padding: '24px', alignItems: 'center', gap: '20px' }}>
            <div className="prep-card__glow glow--amber" style={{ opacity: 0.05 }} />
            <h3 style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-secondary)', letterSpacing: '0.06em' }}>
              Performance Metrics
            </h3>
            <ScoreProgressRing value={averageScore} />
            <div style={{ textAlign: 'center', width: '100%', borderTop: '1px solid var(--border-primary)', paddingTop: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <span style={{ display: 'block', fontSize: '1.2rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                  {completedTests.length}
                </span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Tests Cleared</span>
              </div>
              <div>
                <span style={{ display: 'block', fontSize: '1.2rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                  {completedTests.length > 0 ? `${completedTests.length * 45}m` : '0m'}
                </span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Duration</span>
              </div>
            </div>
          </div>

          {/* Assessment History Feed Widget */}
          <div className="prep-card" style={{ flexDirection: 'column', gap: '16px', padding: '24px' }}>
            <h3 style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-secondary)', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles size={14} style={{ color: '#fbbf24' }} /> Exam Activity Log
            </h3>
            <div className="prep-side-list">
              {completedTests.map((attempt) => (
                <div key={attempt.id} className="prep-side-item">
                  <div className="prep-side-item-icon" style={{ color: '#10b981' }}>
                    <CheckCircle2 size={12} />
                  </div>
                  <div className="prep-side-item-info">
                    <span className="prep-side-item-name">{attempt.name}</span>
                    <span className="prep-side-item-detail">Cleared · Best Score: {attempt.best_score}%</span>
                  </div>
                  <span className="prep-side-item-meta">{attempt.best_score}%</span>
                </div>
              ))}
              {completedTests.length === 0 && (
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center', padding: '10px 0' }}>No exam activity logged yet.</p>
              )}
            </div>
          </div>

          {/* Dynamic AI Syllabus Advice */}
          <div className="prep-card" style={{ flexDirection: 'column', gap: '12px', padding: '24px', background: 'rgba(245,158,11,0.02)', borderColor: 'rgba(245,158,11,0.15)' }}>
            <h3 style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', color: '#d97706', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldAlert size={14} /> AI Syllabus Advice
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Milestones model actual company assessments (e.g. Amazon, Google). Complete all topic nodes in the Topic Journey before launching tests to maximize your placement readiness.
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}
