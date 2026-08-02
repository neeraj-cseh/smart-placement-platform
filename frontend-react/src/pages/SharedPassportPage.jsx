import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ShieldCheck,
  Award,
  Activity,
  CheckCircle,
  Clock,
  Compass,
  Briefcase,
  AlertTriangle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { useApi } from '../hooks/useApi';
import './passport.css';

// Stagger preset
const fadeUp = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } }
};
const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.05 } }
};

const SKILL_NODES = [
  { id: 'DSA', x: 200, y: 60, label: 'DSA', w: 46 },
  { id: 'Graphs', x: 320, y: 110, label: 'Graphs', w: 58 },
  { id: 'Trees', x: 300, y: 220, label: 'Trees', w: 52 },
  { id: 'DP', x: 200, y: 270, label: 'DP', w: 42 },
  { id: 'SQL', x: 100, y: 220, label: 'SQL', w: 46 },
  { id: 'DBMS', x: 80, y: 110, label: 'DBMS', w: 52 },
  { id: 'OS', x: 200, y: 165, label: 'OS Core', w: 64 },
  { id: 'Aptitude', x: 110, y: 50, label: 'Aptitude', w: 70 },
  { id: 'Communication', x: 290, y: 50, label: 'Communication', w: 98 },
  { id: 'System Design', x: 200, y: 330, label: 'Sys Design', w: 84 }
];

const SKILL_EDGES = [
  { from: 'DSA', to: 'Graphs' },
  { from: 'DSA', to: 'Trees' },
  { from: 'Graphs', to: 'DP' },
  { from: 'Trees', to: 'DP' },
  { from: 'SQL', to: 'DBMS' },
  { from: 'DBMS', to: 'OS' },
  { from: 'OS', to: 'System Design' },
  { from: 'DP', to: 'System Design' }
];

export default function SharedPassportPage() {
  const { token } = useParams();
  const { data, loading, error } = useApi(`/passport/shared/${token}/`);
  const [activeSkill, setActiveSkill] = useState('DSA');

  useEffect(() => {
    document.title = "Verified Competency Profile | PrepSmart";
  }, []);

  if (loading) {
    return (
      <div className="shared-pass-loading">
        <RefreshIcon className="shared-pass-spin" />
        <span>Fetching Candidate Credentials...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="shared-pass-error">
        <AlertTriangle size={32} style={{ color: '#ef4444' }} />
        <h3>Profile Verification Failed</h3>
        <p>{error?.message || "This skills passport profile is private or the verification token has expired."}</p>
        <Link to="/login" className="shared-pass-error__btn">Go to PrepSmart Portal</Link>
      </div>
    );
  }

  const passport = data;
  const passportData = passport.passport_data || {};
  const skills = passportData.skills || {};
  const timeline = passportData.timeline || [];
  const reputation = passportData.reputation || {};
  const currentSkillData = skills[activeSkill] || {};

  const solvedCountData = Object.entries(skills).map(([key, s]) => ({
    name: key,
    solved: s.solved || 0,
    fill: s.validated ? '#10b981' : '#f59e0b'
  }));

  return (
    <div className="shared-pass-container">
      {/* Standalone Recruiter Header */}
      <header className="shared-pass-header">
        <div className="shared-pass-header__inner">
          <div className="shared-pass-header__brand">
            <span className="shared-pass-header__logo-icon">PS</span>
            <div>
              <h1 className="shared-pass-header__logo-text">PrepSmart</h1>
              <p className="shared-pass-header__brand-sub">Verified Placement Network</p>
            </div>
          </div>
          <div className="shared-pass-header__badge">
            <ShieldCheck size={14} /> Recruiter Evaluation Mode
          </div>
        </div>
      </header>

      <motion.div className="pass" variants={stagger} initial="hidden" animate="show">
        
        {/* HERO CARD */}
        <motion.section className="pass-hero" variants={fadeUp}>
          <div className="pass-hero__bg">
            <div className="pass-hero__orb pass-hero__orb--1" />
            <div className="pass-hero__orb pass-hero__orb--2" />
          </div>
          <div className="pass-hero__inner">
            <div className="pass-hero__details">
              <div className="pass-hero__header-row">
                <ShieldCheck className="pass-hero__icon" size={24} />
                <div>
                  <h2 className="pass-hero__title">Verified Candidate Passport</h2>
                  <p className="pass-hero__subtitle">{passport.user_info?.name} · {passport.user_info?.college}</p>
                  <p className="pass-hero__branch-text">{passport.user_info?.branch} (Batch of 2026)</p>
                </div>
              </div>

              <div className="pass-hero__highlights">
                <div className="pass-hero__highlight-item">
                  <Award size={13} style={{ color: '#10b981' }} />
                  <span>Validation Tier: <strong>{reputation.level}</strong></span>
                </div>
                <div className="pass-hero__highlight-item">
                  <Activity size={13} style={{ color: '#06b6d4' }} />
                  <span>Readiness: <strong>{passport.readiness_tier}</strong></span>
                </div>
              </div>
            </div>

            <div className="pass-hero__scores">
              <div className="pass-hero__score-card">
                <span className="pass-hero__score-val text-indigo">{passport.employability_score}%</span>
                <span className="pass-hero__score-lbl">Employability Score</span>
              </div>
              <div className="pass-hero__score-card">
                <span className="pass-hero__score-val text-green">{passport.competency_score}%</span>
                <span className="pass-hero__score-lbl">Competency Score</span>
              </div>
              <div className="pass-hero__score-card">
                <span className="pass-hero__score-val text-amber">{passport.recruiter_trust_score}</span>
                <span className="pass-hero__score-lbl">Recruiter Trust</span>
              </div>
            </div>
          </div>
        </motion.section>

        {/* WORKSPACE GRID */}
        <div className="pass-workspace">
          
          {/* LEFT COLUMN: INTERACTIVE GRAPH */}
          <div className="pass-col">
            <motion.section className="pass-card" variants={fadeUp}>
              <div className="pass-card__header">
                <h3 className="pass-card__title"><Compass size={15} style={{ color: '#6366f1' }} /> Competency Verification Graph</h3>
                <span className="pass-card__badge">Verified Nodes</span>
              </div>
              <div className="pass-graph">
                <p className="pass-card__desc">Click any node on the verified prep graph to review matching metrics and view issued validation codes.</p>
                
                <div className="pass-graph__canvas-wrap">
                  <svg className="pass-graph__svg" viewBox="0 0 400 380">
                    {SKILL_EDGES.map((edge, idx) => {
                      const fromNode = SKILL_NODES.find(n => n.id === edge.from);
                      const toNode = SKILL_NODES.find(n => n.id === edge.to);
                      const isFromValidated = skills[edge.from]?.validated;
                      const isToValidated = skills[edge.to]?.validated;
                      const isValidated = isFromValidated && isToValidated;
                      
                      return (
                        <line
                          key={idx}
                          x1={fromNode.x}
                          y1={fromNode.y}
                          x2={toNode.x}
                          y2={toNode.y}
                          className={`pass-graph__edge ${isValidated ? 'pass-graph__edge--validated' : ''}`}
                        />
                      );
                    })}

                    {SKILL_NODES.map((node) => {
                      const skillDetail = skills[node.id] || {};
                      const isSelected = activeSkill === node.id;
                      const isValidated = skillDetail.validated;

                      return (
                        <g
                          key={node.id}
                          className={`pass-graph__node ${isSelected ? 'pass-graph__node--selected' : ''} ${isValidated ? 'pass-graph__node--validated' : ''}`}
                          onClick={() => setActiveSkill(node.id)}
                        >
                          {/* Solid backing to block line visibility under the node */}
                          <rect
                            x={node.x - (node.w || 50) / 2}
                            y={node.y - 12}
                            width={node.w || 50}
                            height={24}
                            rx={12}
                            ry={12}
                            className="pass-graph__node-bg"
                          />
                          <rect
                            x={node.x - (node.w || 50) / 2}
                            y={node.y - 12}
                            width={node.w || 50}
                            height={24}
                            rx={12}
                            ry={12}
                            className="pass-graph__node-rect"
                          />
                          <text x={node.x} y={node.y + 4} className="pass-graph__node-text">
                            {node.label || node.id}
                          </text>
                        </g>
                      );
                    })}
                  </svg>
                </div>

                <div className="pass-graph__detail-box">
                  <div className="pass-graph__detail-header">
                    <span className="pass-graph__detail-title">{activeSkill} Verification Details</span>
                    {currentSkillData.validated ? (
                      <span className="pass-graph__detail-status pass-graph__detail-status--valid">Verified</span>
                    ) : (
                      <span className="pass-graph__detail-status">Unverified</span>
                    )}
                  </div>
                  <div className="pass-graph__detail-grid">
                    <div className="pass-graph__detail-stat">
                      <span className="pass-graph__detail-lbl">Competency Mastery</span>
                      <span className="pass-graph__detail-val">{currentSkillData.mastery || 0}%</span>
                    </div>
                    <div className="pass-graph__detail-stat">
                      <span className="pass-graph__detail-lbl">Validation Strength</span>
                      <span className="pass-graph__detail-val">{currentSkillData.confidence || 0}%</span>
                    </div>
                    <div className="pass-graph__detail-stat">
                      <span className="pass-graph__detail-lbl">Solved Problems</span>
                      <span className="pass-graph__detail-val">{currentSkillData.solved || 0} tasks</span>
                    </div>
                    <div className="pass-graph__detail-stat">
                      <span className="pass-graph__detail-lbl">Recruiter Importance</span>
                      <span className="pass-graph__detail-val">{currentSkillData.relevance || 'Medium'}</span>
                    </div>
                  </div>

                  {currentSkillData.validated && (
                    <div className="shared-pass-cert-box">
                      <div className="shared-pass-cert-row">
                        <span className="shared-pass-cert-lbl">Certificate ID:</span>
                        <span className="shared-pass-cert-val">{currentSkillData.cert_id}</span>
                      </div>
                      <div className="shared-pass-cert-row">
                        <span className="shared-pass-cert-lbl">Validation Code:</span>
                        <span className="shared-pass-cert-val monospace">{currentSkillData.hash}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.section>
          </div>

          {/* RIGHT COLUMN: EVIDENCE AND BADGES */}
          <div className="pass-col">
            {/* EVIDENCE CHART */}
            <motion.section className="pass-card" variants={fadeUp}>
              <div className="pass-card__header">
                <h3 className="pass-card__title"><Briefcase size={15} style={{ color: '#10b981' }} /> Recruiter Evidence Layer</h3>
                <span className="pass-card__badge" style={{ borderColor: '#10b981', color: '#10b981' }}>Platform Proof</span>
              </div>
              <div className="pass-trust">
                <p className="pass-card__desc">Raw compiler stats and task counts. This data guarantees the candidate has executed all code locally without third-party aid.</p>
                
                <div className="pass-trust__chart-wrap">
                  <div style={{ width: '100%', height: 130 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={solvedCountData} margin={{ left: -10, right: 10, top: 5, bottom: 5 }}>
                        <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 9 }} />
                        <Tooltip cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                        <Bar dataKey="solved" radius={[4, 4, 0, 0]} barSize={14} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="pass-trust__factors">
                  <div className="pass-trust__factor-item">
                    <CheckCircle size={12} style={{ color: '#10b981' }} />
                    <span>Plagiarism check passed and verified by PrepSmart sandbox compilers.</span>
                  </div>
                </div>
              </div>
            </motion.section>

            {/* TIMELINE */}
            <motion.section className="pass-card" variants={fadeUp}>
              <div className="pass-card__header">
                <h3 className="pass-card__title"><Clock size={15} style={{ color: '#a855f7' }} /> Verified Skill Milestone Timeline</h3>
                <span className="pass-card__badge" style={{ borderColor: '#a855f7', color: '#a855f7' }}>Audit trail</span>
              </div>
              <div className="pass-timeline">
                <div className="pass-timeline__stream">
                  {timeline.map((item, idx) => (
                    <div key={item.id || idx} className="pass-timeline__item">
                      <div className="pass-timeline__badge-wrap">
                        <span className="pass-timeline__dot" />
                        {idx < timeline.length - 1 && <span className="pass-timeline__line" />}
                      </div>
                      <div className="pass-timeline__content">
                        <div className="pass-timeline__meta">
                          <span className="pass-timeline__date">{item.date}</span>
                          <span className="pass-timeline__type">{item.type}</span>
                        </div>
                        <h4 className="pass-timeline__title">{item.title}</h4>
                        <p className="pass-timeline__desc">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.section>

            {/* BADGES */}
            <motion.section className="pass-card" variants={fadeUp}>
              <div className="pass-card__header">
                <h3 className="pass-card__title"><Award size={15} style={{ color: '#ec4899' }} /> Candidate Badges</h3>
                <span className="pass-card__badge" style={{ borderColor: '#ec4899', color: '#ec4899' }}>Reputation</span>
              </div>
              <div className="pass-reputation">
                <div className="pass-reputation__badges-grid">
                  {reputation.badges?.map(badge => (
                    <div key={badge.id} className="pass-reputation__badge-card">
                      <div className="pass-reputation__badge-icon">
                        <ShieldCheck size={20} />
                      </div>
                      <span className="pass-reputation__badge-name">{badge.name}</span>
                      <span className="pass-reputation__badge-desc">{badge.desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.section>
          </div>

        </div>
      </motion.div>
    </div>
  );
}

function RefreshIcon({ className }) {
  return (
    <svg className={className} width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
    </svg>
  );
}
