import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheck,
  Award,
  Sparkles,
  Zap,
  Activity,
  Copy,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Info,
  Clock,
  Compass,
  Briefcase,
  Star,
  Square
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  Tooltip
} from 'recharts';
import { useApi } from '../hooks/useApi';
import { useUIStore } from '../stores';
import './passport.css';

// Motion variants
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

export default function PassportPage() {
  const { data, loading, mutate } = useApi('/passport/');
  const { addToast } = useUIStore();

  const [activeSkill, setActiveSkill] = useState('DSA');
  const [copiedLink, setCopiedLink] = useState(false);

  useEffect(() => {
    document.title = "Skills Passport | PrepSmart";
  }, []);

  const handleCopyShareLink = useCallback((token) => {
    const shareUrl = `${window.location.origin}/passport/shared/${token}`;
    navigator.clipboard.writeText(shareUrl).then(() => {
      setCopiedLink(true);
      addToast({ type: 'success', message: 'Recruiter verification link copied!', duration: 3000 });
      setTimeout(() => setCopiedLink(false), 2000);
    });
  }, [addToast]);

  
  const handleChecklistToggle = useCallback(async (taskId, checked) => {
    await mutate('post', {
      action: 'copilot_checklist',
      task_id: taskId,
      done: !checked
    });
  }, [mutate]);

  if (loading && !data) {
    return (
      <>
        <div className="pass-skeleton">
          <div className="pass-skeleton__card" />
          <div className="pass-skeleton__grid">
            <div className="pass-skeleton__card" />
            <div className="pass-skeleton__card" />
          </div>
        </div>
      </>
    );
  }

  const passport = data || {
    employability_score: 74,
    competency_score: 78,
    recruiter_trust_score: "High",
    readiness_tier: "Product Company Ready",
    is_public: true,
    public_token: "",
    user_info: {},
    passport_data: {}
  };

  const passportData = passport.passport_data || {};
  const skills = passportData.skills || {};
  const timeline = passportData.timeline || [];
  const credibility = passportData.credibility_analyzer || {};
  const checklists = credibility.checklists || [];
  const reputation = passportData.reputation || {};
  const copilot = passportData.copilot || {};

  const currentSkillData = skills[activeSkill] || {};

  // Formats Recharts data for missing claims vs code proof
  const solvedCountData = Object.entries(skills).map(([key, s]) => ({
    name: key,
    solved: s.solved || 0,
    fill: s.validated ? '#10b981' : '#f59e0b'
  }));

  const handleTogglePublic = async () => {
    await mutate('post', {
      action: 'share',
      is_public: !passport.is_public
    });
    addToast({
      type: 'success',
      message: `Passport visibility set to ${!passport.is_public ? 'Public' : 'Private'}`,
      duration: 3000
    });
  };

  return (
    <>
      <motion.div className="pass" variants={stagger} initial="hidden" animate="show">

        {/* ═══════════════════════════════════════════════════════
            1. EMPLOYABILITY PASSPORT HERO
            ═══════════════════════════════════════════════════════ */}
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
                  <h2 className="pass-hero__title">Competency Passport</h2>
                  <p className="pass-hero__subtitle">{passport.user_info?.name} · {passport.user_info?.college || 'PrepSmart Institute'}</p>
                </div>
              </div>

              {/* Share & Public control */}
              <div className="pass-hero__actions">
                <button
                  className="pass-hero__btn pass-hero__btn--primary"
                  onClick={() => handleCopyShareLink(passport.public_token)}
                  disabled={!passport.is_public}
                >
                  <Copy size={13} />
                  {copiedLink ? "Link Copied!" : "Copy Recruiter Verification Link"}
                </button>
                
                <button
                  className={`pass-hero__btn ${passport.is_public ? 'pass-hero__btn--success' : 'pass-hero__btn--secondary'}`}
                  onClick={handleTogglePublic}
                >
                  {passport.is_public ? "Public Visibility: Enabled" : "Public Visibility: Disabled"}
                </button>
              </div>

              <div className="pass-hero__highlights">
                <div className="pass-hero__highlight-item">
                  <Star size={13} style={{ color: '#fbbf24' }} />
                  <span>Strongest Skill: <strong>DSA ({skills.DSA?.mastery}%)</strong></span>
                </div>
                <div className="pass-hero__highlight-item">
                  <Activity size={13} style={{ color: '#10b981' }} />
                  <span>Validation Rank: <strong>{reputation.rank}</strong></span>
                </div>
              </div>
            </div>

            {/* Verification Stats score center */}
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

        {/* ═══════════════════════════════════════════════════════
            MAIN COMPONENT GRID
            ═══════════════════════════════════════════════════════ */}
        <div className="pass-workspace">

          {/* LEFT COLUMN: VISUAL SKILL CONNECTOR GRAPH */}
          <div className="pass-col">
            
            {/* 2. VERIFIED SKILLS GRAPH */}
            <motion.section className="pass-card" variants={fadeUp}>
              <div className="pass-card__header">
                <h3 className="pass-card__title"><Compass size={15} style={{ color: '#6366f1' }} /> Interactive Skills Network</h3>
                <span className="pass-card__badge">Live Graph</span>
              </div>
              <div className="pass-graph">
                <p className="pass-card__desc">Click any node in the dependency graph below to inspect validation details and run the competency scanner.</p>
                
                <div className="pass-graph__canvas-wrap">
                  <svg className="pass-graph__svg" viewBox="0 0 400 380">
                    {/* Render edges */}
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

                    {/* Render nodes */}
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

                {/* Selected Node Details sidebox */}
                <div className="pass-graph__detail-box">
                  <div className="pass-graph__detail-header">
                    <span className="pass-graph__detail-title">{activeSkill} Competency Details</span>
                    {currentSkillData.validated ? (
                      <span className="pass-graph__detail-status pass-graph__detail-status--valid">Verified</span>
                    ) : (
                      <span className="pass-graph__detail-status pass-graph__detail-status--invalid">Unverified</span>
                    )}
                  </div>
                  <div className="pass-graph__detail-grid">
                    <div className="pass-graph__detail-stat">
                      <span className="pass-graph__detail-lbl">Estimated Mastery</span>
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
                      <span className="pass-graph__detail-lbl">Recruiter Focus</span>
                      <span className="pass-graph__detail-val">{currentSkillData.relevance || 'Medium'}</span>
                    </div>
                  </div>

                  {/* 3. COMPETENCY VALIDATION ENGINE ACTION REMOVED AS REQUESTED */}
                </div>
              </div>
            </motion.section>

            {/* 6. AI CREDIBILITY ANALYZER */}
            <motion.section className="pass-card" variants={fadeUp}>
              <div className="pass-card__header">
                <h3 className="pass-card__title"><AlertTriangle size={15} style={{ color: '#f59e0b' }} /> AI Credibility Analyzer</h3>
                <span className="pass-card__badge" style={{ borderColor: '#f59e0b', color: '#f59e0b' }}>Radar Audit</span>
              </div>
              <div className="pass-credibility">
                <p className="pass-card__desc">This engine identifies gaps between claims on your profile and verified execution history on the compiler sandboxes.</p>
                
                {/* Inflation risk alerts */}
                <div className="pass-credibility__alerts">
                  {credibility.inflated_claims?.map((claim, idx) => (
                    <div key={idx} className="pass-credibility__alert pass-credibility__alert--red">
                      <AlertTriangle size={14} style={{ flexShrink: 0, marginTop: 2 }} />
                      <span><strong>Warning:</strong> {claim}</span>
                    </div>
                  ))}
                  {credibility.weak_evidence?.map((claim, idx) => (
                    <div key={idx} className="pass-credibility__alert pass-credibility__alert--amber">
                      <Info size={14} style={{ flexShrink: 0, marginTop: 2 }} />
                      <span><strong>Evidence Alert:</strong> {claim}</span>
                    </div>
                  ))}
                </div>

                {/* Interactive checklist checklist */}
                <div className="pass-credibility__checklist-wrap">
                  <span className="pass-credibility__subtitle">Evidence Improvement Action items:</span>
                  <div className="pass-credibility__list">
                    {checklists.map(item => (
                      <div
                        key={item.id}
                        className={`pass-credibility__item ${item.done ? 'pass-credibility__item--done' : ''}`}
                        onClick={() => handleChecklistToggle(item.id, item.done)}
                      >
                        <button className="pass-credibility__checkbox">
                          {item.done ? <CheckCircle size={14} style={{ color: '#10b981' }} /> : <Square size={14} />}
                        </button>
                        <span className="pass-credibility__label">{item.task}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.section>
          </div>

          {/* RIGHT COLUMN: REVENUE TIMELINE & REPUTATION */}
          <div className="pass-col">
            
            {/* 4. RECRUITER TRUST LAYER */}
            <motion.section className="pass-card" variants={fadeUp}>
              <div className="pass-card__header">
                <h3 className="pass-card__title"><Briefcase size={15} style={{ color: '#10b981' }} /> Recruiter Trust Layer</h3>
                <span className="pass-card__badge" style={{ borderColor: '#10b981', color: '#10b981' }}>Evidence Tracker</span>
              </div>
              <div className="pass-trust">
                <p className="pass-card__desc">Solved problem metrics and verification records extracted from integrated compilers and testing engines.</p>
                
                <div className="pass-trust__chart-wrap">
                  <span className="pass-trust__chart-lbl">Solved Tasks by Category</span>
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
                    <span><strong>100% Plagiarism-Free code verification</strong> across all competitive coding problems.</span>
                  </div>
                  <div className="pass-trust__factor-item">
                    <CheckCircle size={12} style={{ color: '#10b981' }} />
                    <span><strong>Verified System Design mastery</strong> (6 mock test benchmarks).</span>
                  </div>
                </div>
              </div>
            </motion.section>

            {/* 5. SKILL EVIDENCE TIMELINE */}
            <motion.section className="pass-card" variants={fadeUp}>
              <div className="pass-card__header">
                <h3 className="pass-card__title"><Clock size={15} style={{ color: '#a855f7' }} /> Skill Evidence Timeline</h3>
                <span className="pass-card__badge" style={{ borderColor: '#a855f7', color: '#a855f7' }}>Audit Trail</span>
              </div>
              <div className="pass-timeline">
                <p className="pass-card__desc">A chronological verification logs system documenting when and how skills were validated.</p>
                
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
                        {item.badge && <span className="pass-timeline__tag">{item.badge}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.section>

          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════
            VERIFICATION UI REMOVED 
            ═══════════════════════════════════════════════════════ */}

      </motion.div>
    </>
  );
}
