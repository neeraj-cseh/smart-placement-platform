import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useApi } from '../hooks/useApi';
import { Code2, Layout, Database, BrainCircuit, Sparkles } from 'lucide-react';
import './prep-ecosystem.css';

const getTrackIcon = (name) => {
  const n = name.toLowerCase();
  if (n.includes('algorithm') || n.includes('data structure') || n.includes('dsa')) {
    return { icon: Code2, color: '#3b82f6', glow: 'glow--blue' };
  }
  if (n.includes('system design') || n.includes('architecture')) {
    return { icon: Layout, color: '#8b5cf6', glow: 'glow--purple' };
  }
  if (n.includes('cs') || n.includes('network') || n.includes('database') || n.includes('os')) {
    return { icon: Database, color: '#10b981', glow: 'glow--green' };
  }
  if (n.includes('aptitude') || n.includes('quant') || n.includes('reasoning')) {
    return { icon: BrainCircuit, color: '#f59e0b', glow: 'glow--amber' };
  }
  return { icon: Sparkles, color: '#6366f1', glow: 'glow--blue' };
};

export default function LearningPathPage() {
  const navigate = useNavigate();
  const { data, loading, error } = useApi('/prep/roadmaps/');

  if (loading) {
    return (
      <div className="prep-container">
        <div className="prep-hero">
          <div className="prep-hero__grid-bg" />
          <h2 className="prep-hero__title">Macro <span>Roadmaps</span></h2>
          <p className="prep-hero__subtitle">Loading your custom roadmaps...</p>
        </div>
        <div className="prep-bento-grid">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton skeleton--card" style={{ height: 250, borderRadius: 12 }} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="prep-container">
        <div className="prep-hero">
          <div className="prep-hero__grid-bg" />
          <h2 className="prep-hero__title">Error <span>Loading Paths</span></h2>
          <p className="prep-hero__subtitle">Please check your connection or try again later. {error}</p>
        </div>
      </div>
    );
  }

  const tracks = data?.tracks || [];

  if (tracks.length === 0) {
    return (
      <div className="prep-container">
        <div className="prep-hero">
          <div className="prep-hero__grid-bg" />
          <h2 className="prep-hero__title">No <span>Roadmaps Available</span></h2>
          <p className="prep-hero__subtitle">All roadmaps are currently offline or under maintenance.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="prep-container">
      <div className="prep-hero">
        <div className="prep-hero__grid-bg" />
        <h2 className="prep-hero__title">Macro <span>Roadmaps</span></h2>
        <p className="prep-hero__subtitle">
          Explore specialized learning paths tailored for engineering placements. Master topics step-by-step and unlock achievements as you progress.
        </p>
      </div>

      <div className="prep-bento-wrap">
        <div className="prep-bento-grid">
          {tracks.map((rm, idx) => {
            const { icon: Icon, color, glow } = getTrackIcon(rm.name);
            return (
              <motion.div 
                key={rm.id}
                className="prep-card prep-bento-card"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: idx * 0.08 }}
                onClick={() => navigate(`/prep/journey?track=${rm.id}`)}
              >
                {/* Glowing radial backdrop inside card */}
                <div className={`prep-card__glow ${glow}`} />
                
                <div className="prep-bento-header">
                  <div className="prep-bento-icon-shell" style={{ color: color }}>
                    <Icon size={20} />
                  </div>
                  <span className="prep-milestone-duration">{rm.total_topics} Topics</span>
                </div>
                
                <div className="prep-bento-body">
                  <h3 className="prep-bento-title">{rm.name}</h3>
                  <p className="prep-bento-desc">{rm.description}</p>
                </div>
                
                <div className="prep-bento-footer">
                  <div className="prep-bento-progress-lbl">
                    <span>Progress</span>
                    <span style={{ color: color, fontWeight: 900 }}>{rm.progress_percentage}%</span>
                  </div>
                  <div className="prep-bento-progress-track">
                    <div 
                      className="prep-bento-progress-fill" 
                      style={{ width: `${rm.progress_percentage}%`, backgroundColor: color }}
                    />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
