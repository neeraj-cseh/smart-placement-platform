import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import { Check, Lock, Play, BookOpen, Sparkles, Target, Zap, Clock, HelpCircle } from 'lucide-react';
import './prep-ecosystem.css';

const getTopicType = (name, qCount) => {
  const n = name.toLowerCase();
  if (n.includes('assessment') || n.includes('milestone') || n.includes('exam') || n.includes('test')) {
    return 'assessment';
  }
  if (n.includes('concept') || n.includes('fundamental') || qCount === 0) {
    return 'concept';
  }
  return 'drill';
};

function TrackProgressRing({ value = 0, size = 140 }) {
  const r = 58;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, value));
  const offset = circ - (pct / 100) * circ;

  return (
    <div className="prep-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <defs>
          <linearGradient id="prepRingGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3b82f6" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} className="prep-ring-track" />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r}
          className="prep-ring-fill"
          stroke="url(#prepRingGrad)"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: [0.4, 0, 0.2, 1] }}
        />
      </svg>
      <div className="prep-ring-inner">
        <span className="prep-ring-value">{pct}%</span>
        <span className="prep-ring-label">Completed</span>
      </div>
    </div>
  );
}

export default function PrepPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const trackId = queryParams.get('track');

  const { data, loading, error, refetch } = useApi(
    trackId ? `/prep/topic-journey/?track=${trackId}` : '/prep/topic-journey/'
  );

  if (loading) {
    return (
      <div className="prep-container">
        <div className="prep-hero">
          <div className="prep-hero__grid-bg" />
          <h2 className="prep-hero__title">Topic Journey</h2>
          <p className="prep-hero__subtitle">Loading your sequential curriculum...</p>
        </div>
        <div className="prep-layout-grid">
          <div className="prep-main-flow">
            <div className="skeleton skeleton--card" style={{ height: 180, borderRadius: 12, opacity: 0.15 }} />
            <div className="prep-timeline">
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
          <h2 className="prep-hero__title">Error <span>Loading Journey</span></h2>
          <p className="prep-hero__subtitle">Failed to load topic details. Please try again. {error}</p>
        </div>
      </div>
    );
  }

  const activeTrack = data?.tracks?.find(t => String(t.id) === String(trackId)) || data?.tracks?.[0];
  const topics = activeTrack?.topics || [];
  const focusQueue = data?.focus_queue || [];

  if (topics.length === 0) {
    return (
      <div className="prep-container">
        <div className="prep-hero">
          <div className="prep-hero__grid-bg" />
          <h2 className="prep-hero__title">No <span>Topics Available</span></h2>
          <p className="prep-hero__subtitle">This roadmap has no active topics yet. Select another roadmap in the tab above.</p>
        </div>
      </div>
    );
  }

  // Determine current active target topic
  const activeTopic = topics.find(t => t.status === 'current' || t.status === 'in_progress') || topics.find(t => t.status === 'ready') || topics[0];
  const activeTopicType = getTopicType(activeTopic.name, activeTopic.question_count);

  const handleCompleteTopic = async (topicId) => {
    try {
      await api.post('/prep/complete-topic/', { topic_id: topicId });
      refetch();
    } catch (err) {
      alert('Failed to mark concept as completed: ' + err.message);
    }
  };

  return (
    <div className="prep-container">
      {/* Dynamic Header */}
      <div className="prep-hero">
        <div className="prep-hero__grid-bg" />
        <h2 className="prep-hero__title">Topic Journey: <span>{activeTrack?.name || 'Curriculum'}</span></h2>
        <p className="prep-hero__subtitle">
          {activeTrack?.description || 'Master the fundamentals sequentially. Complete coding drills and conceptual lessons to unlock mock exams.'}
        </p>
      </div>

      {/* Two-Column Grid */}
      <div className="prep-layout-grid">
        
        {/* Left Column: Focus Card + Timeline Checklist */}
        <div className="prep-main-flow">
          
          {/* Active Target Focus Card */}
          {activeTopic && (
            <motion.div 
              className="prep-focus-card"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="prep-card__glow glow--blue" style={{ opacity: 0.08 }} />
              <div className="prep-focus-card__left">
                <div className="prep-focus-card__eyebrow">
                  <Target size={12} /> Active Focus Topic
                </div>
                <h3 className="prep-focus-card__title">{activeTopic.name}</h3>
                <p className="prep-focus-card__desc">
                  {activeTopic.description || 'Focus on completing this topic checklist to unlock advanced concepts in this track.'}
                </p>
                <div className="prep-timeline-meta" style={{ marginTop: '8px' }}>
                  {activeTopicType === 'concept' && <span className="prep-badge prep-badge--concept"><BookOpen size={11} style={{ marginRight: 2 }} /> Concept</span>}
                  {activeTopicType === 'drill' && <span className="prep-badge prep-badge--drill"><Play size={11} style={{ marginRight: 2 }} /> Drill</span>}
                  {activeTopicType === 'assessment' && <span className="prep-badge prep-badge--assessment"><Sparkles size={11} style={{ marginRight: 2 }} /> Assessment</span>}
                  {activeTopic.estimated_minutes && <span className="prep-milestone-duration">{activeTopic.estimated_minutes}m</span>}
                  {activeTopic.question_count > 0 && <span className="prep-milestone-duration">{activeTopic.question_count} Questions</span>}
                </div>
              </div>
                <button className="prep-btn-primary" onClick={() => navigate(`/prep/topic/${activeTopic.slug}`)}>
                  <Play size={12} style={{ fill: 'currentColor', marginRight: 4 }} /> Start Learning
                </button>
            </motion.div>
          )}

          {/* Timeline Nodes */}
          <div className="prep-timeline-wrap">
            <div className="prep-timeline">
              {topics.map((node, idx) => {
                const isCompleted = node.is_completed || node.status === 'completed';
                const isActiveNode = node.id === activeTopic.id;
                const isLocked = node.is_locked || node.status === 'locked';
                const type = getTopicType(node.name, node.question_count);

                return (
                  <motion.div 
                    key={node.id}
                    className={`prep-timeline-item ${isCompleted ? 'is-completed' : ''} ${isActiveNode ? 'is-active' : ''} ${isLocked ? 'is-locked' : ''}`}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: idx * 0.08 }}
                  >
                    {/* Stacking Correct Node */}
                    <div className="prep-node-shell">
                      <div className="prep-node">
                        {isCompleted ? (
                          <Check size={16} strokeWidth={3} />
                        ) : isLocked ? (
                          <Lock size={14} />
                        ) : (
                          <span className="animate-pulse" style={{ fontSize: '1.2rem', fontWeight: 900 }}>•</span>
                        )}
                      </div>
                    </div>
                    
                    {/* Card */}
                    <div className={`prep-card prep-timeline-card ${isActiveNode ? 'prep-card--active' : ''} ${isCompleted ? 'prep-card--completed' : ''} ${isLocked ? 'prep-card--locked' : ''}`}>
                      {isActiveNode && <div className="prep-card__glow glow--blue" style={{ opacity: 0.04 }} />}
                      
                      <div className="prep-timeline-details">
                        <h3>{node.name}</h3>
                        <p>{node.description || 'Topic description details.'}</p>
                        
                        <div className="prep-timeline-meta">
                          {type === 'concept' && <span className="prep-badge prep-badge--concept"><BookOpen size={11} style={{ marginRight: 2 }} /> Concept</span>}
                          {type === 'drill' && <span className="prep-badge prep-badge--drill"><Play size={11} style={{ marginRight: 2 }} /> Drill</span>}
                          {type === 'assessment' && <span className="prep-badge prep-badge--assessment"><Sparkles size={11} style={{ marginRight: 2 }} /> Assessment</span>}
                          {node.estimated_minutes && <span className="prep-milestone-duration">{node.estimated_minutes}m</span>}
                          {node.question_count > 0 && <span className="prep-milestone-duration">{node.question_count} Qs</span>}
                          {node.attempts > 0 && (
                            <span className="prep-milestone-duration" style={{ color: node.accuracy >= 60 ? '#10b981' : '#ef4444' }}>
                              Accuracy: {node.accuracy}%
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="prep-timeline-actions">
                        {isLocked ? (
                          <button className="prep-btn-secondary" disabled>
                            <Lock size={12} style={{ marginRight: 4 }} /> Locked
                          </button>
                        ) : isCompleted ? (
                          <button className="prep-btn-secondary" onClick={() => navigate(`/prep/topic/${node.slug}`)}>
                            Review
                          </button>
                        ) : (
                          <button className="prep-btn-primary" onClick={() => navigate(`/prep/topic/${node.slug}`)}>
                            <Play size={12} style={{ fill: 'currentColor', marginRight: 4 }} /> Start
                          </button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Sidebar Widgets */}
        <div className="prep-sidebar-flow">
          
          {/* Circular Progress Ring Widget */}
          <div className="prep-card" style={{ flexDirection: 'column', padding: '24px', alignItems: 'center', gap: '20px' }}>
            <div className="prep-card__glow glow--purple" style={{ opacity: 0.05 }} />
            <h3 style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-secondary)', letterSpacing: '0.06em' }}>
              Track Progress
            </h3>
            <TrackProgressRing value={activeTrack?.progress_percentage || 0} />
            <div style={{ textAlign: 'center', width: '100%', borderTop: '1px solid var(--border-primary)', paddingTop: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <span style={{ display: 'block', fontSize: '1.2rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                  {activeTrack?.completed_topics}/{activeTrack?.total_topics}
                </span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Topics Done</span>
              </div>
              <div>
                <span style={{ display: 'block', fontSize: '1.2rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                  {activeTrack?.estimated_remaining_minutes || 0}m
                </span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Time Left</span>
              </div>
            </div>
          </div>

          {/* Practice Focus Queue Widget */}
          <div className="prep-card" style={{ flexDirection: 'column', gap: '16px', padding: '24px' }}>
            <h3 style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-secondary)', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Zap size={14} style={{ color: '#fbbf24' }} /> Practice Queue
            </h3>
            <div className="prep-side-list">
              {focusQueue.slice(0, 3).map((item) => (
                <div key={item.id} className="prep-side-item" style={{ cursor: 'pointer' }} onClick={() => navigate(`/prep/topic/${item.slug}`)}>
                  <div className="prep-side-item-icon">
                    <Play size={12} />
                  </div>
                  <div className="prep-side-item-info">
                    <span className="prep-side-item-name">{item.name}</span>
                    <span className="prep-side-item-detail">{item.track_name} · {item.reason}</span>
                  </div>
                </div>
              ))}
              {focusQueue.length === 0 && (
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center', padding: '10px 0' }}>Focus queue is empty.</p>
              )}
            </div>
          </div>

          {/* AI Guidance Insights Widget */}
          <div className="prep-card" style={{ flexDirection: 'column', gap: '12px', padding: '24px', background: 'rgba(59,130,246,0.02)', borderColor: 'rgba(59,130,246,0.15)' }}>
            <h3 style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', color: '#3b82f6', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Sparkles size={14} /> Coach Guidance
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Completing lessons in chronological order is scientifically proven to build stronger cognitive schema. Make sure you score 70%+ on all drills before starting milestones!
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}
