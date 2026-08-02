import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { Calendar, Clock, Trophy, Users, Bell, BellRing, X } from 'lucide-react';
import './contest-hub.css';

const ContestCard = ({ contest, status, onAction }) => (
  <div className="ch-card">
    <div className="ch-card-info">
      <div className="ch-card-title">
        {contest.title}
        {contest.platform && contest.platform !== 'PrepSmart' && (
          <span className="ch-platform-badge">{contest.platform}</span>
        )}
      </div>
      <div className="ch-card-meta">
        <span><Calendar size={14} /> {new Date(contest.start_time).toLocaleDateString()}</span>
        <span><Clock size={14} /> {contest.duration_minutes} mins</span>
        <span><Users size={14} /> {contest.participants_count || '1k+'} Registered</span>
      </div>
    </div>
    <div className="ch-card-action" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
      {status === 'upcoming' && (
        <button 
          className="ch-icon-btn" 
          onClick={(e) => { e.stopPropagation(); contest.onToggleReminder(contest.id); }}
          title="Set Reminder"
          style={{ 
            background: 'transparent', border: 'none', cursor: 'pointer', padding: '8px',
            color: contest.isReminded ? '#fbbf24' : 'var(--ch-text-secondary)',
            transition: 'color 0.2s'
          }}
        >
          {contest.isReminded ? <BellRing size={20} fill="#fbbf24" /> : <Bell size={20} />}
        </button>
      )}
      {status === 'upcoming' && (
        <button className="ch-btn ch-btn-primary" onClick={() => onAction(contest)}>Register Now</button>
      )}
      {status === 'ongoing' && (
        <button className="ch-btn ch-btn-primary" style={{ background: '#10b981' }} onClick={() => onAction(contest)}>Enter Contest</button>
      )}
      {status === 'past' && (
        <button className="ch-btn ch-btn-secondary" onClick={() => onAction(contest)}>View Leaderboard</button>
      )}
    </div>
  </div>
);

const LeaderboardModal = ({ contest, onClose }) => {
  const { data, loading } = useApi(`/code/contests/${contest.id}/leaderboard/`);
  
  return (
    <div className="ch-modal-overlay" onClick={onClose}>
      <div className="ch-modal-content" onClick={e => e.stopPropagation()}>
        <div className="ch-modal-header">
          <h3>Leaderboard: {contest.title}</h3>
          <button className="ch-modal-close" onClick={onClose}><X size={20} /></button>
        </div>
        <div className="ch-modal-body">
          {loading ? (
            <div style={{ color: 'var(--ch-text-secondary)', padding: '20px' }}>Loading rankings...</div>
          ) : data?.leaderboard?.length > 0 ? (
            <table className="pa-dense-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Hacker</th>
                  <th>Score</th>
                  <th>Penalty (mins)</th>
                  <th>Solved</th>
                </tr>
              </thead>
              <tbody>
                {data.leaderboard.map(entry => (
                  <tr key={entry.user_id}>
                    <td>#{entry.rank}</td>
                    <td style={{ fontWeight: 600 }}>{entry.name}</td>
                    <td style={{ color: '#10b981' }}>{entry.score}</td>
                    <td>{entry.penalty}</td>
                    <td>{entry.solved} / {contest.problems?.length || '?'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ color: 'var(--ch-text-secondary)', padding: '20px', textAlign: 'center' }}>
              No participants solved any problems during this contest window.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default function ContestHubPage() {
  const navigate = useNavigate();
  const { data: contestData, loading } = useApi('/code/contests/');
  
  const [activeTab, setActiveTab] = useState('upcoming');
  const [leaderboardModal, setLeaderboardModal] = useState(null);

  const rawContests = contestData?.contests || [];
  
  const [reminders, setReminders] = useState(new Set());
  const toggleReminder = (id) => {
    setReminders(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };
  
  // Create a ticking 'now' state so the page feels alive and automatically shifts contests
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
  
  const upcomingContests = rawContests.filter(c => new Date(c.start_time) > now);
  const ongoingContests = rawContests.filter(c => new Date(c.start_time) <= now && new Date(c.end_time) > now);
  const pastContests = rawContests.filter(c => new Date(c.end_time) <= now);
  
  // Sort them
  upcomingContests.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
  ongoingContests.sort((a, b) => new Date(a.end_time) - new Date(b.end_time));
  pastContests.sort((a, b) => new Date(b.end_time) - new Date(a.end_time));
  
  const nextContest = upcomingContests[0] || null;

  const timeLeft = nextContest ? Math.max(0, Math.floor((new Date(nextContest.start_time) - now) / 1000)) : 0;

  const pad = (num) => String(num).padStart(2, '0');
  const h = Math.floor(timeLeft / 3600);
  const m = Math.floor((timeLeft % 3600) / 60);
  const s = timeLeft % 60;

  return (
    <div className="ch-container">
      
      {/* HERO SECTION */}
      <div className="ch-hero">
        <div className="ch-hero__grid-bg" />
        
        <div className="ch-hero__left">
          <div className="ch-hero__eyebrow">
            <div className="ch-hero__eyebrow-dot" />
            Arena Hub
          </div>
          
          <h1 className="ch-hero__greeting">
            Global <span>Contests</span>.
          </h1>
          
          <p className="ch-hero__subtitle">
            Compete in our internal qualifiers, or discover the top coding competitions happening globally across platforms like LeetCode and Codeforces.
          </p>
        </div>
        
        {nextContest && (
          <div className="ch-hero__right">
            <div className="ch-countdown-label">Next Contest Starts In</div>
            <div className="ch-countdown-time">
              {pad(h)}:{pad(m)}:{pad(s)}
            </div>
          </div>
        )}
      </div>

      {/* TABS */}
      <div className="ch-tabs">
        {['upcoming', 'ongoing', 'past'].map(tab => (
          <button 
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`ch-tab-btn ${activeTab === tab ? 'active' : ''}`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* CONTEST LIST */}
      <div className="ch-list">
        {loading ? (
          <div className="ch-empty-state">Loading contests...</div>
        ) : (
          (() => {
            const list = activeTab === 'upcoming' ? upcomingContests : activeTab === 'ongoing' ? ongoingContests : pastContests;
            
            if (list.length === 0) {
              return <div className="ch-empty-state">No {activeTab} contests at the moment. Please check back later!</div>;
            }

            return list.map(c => (
              <ContestCard 
                key={c.id} 
                contest={{ ...c, isReminded: reminders.has(c.id), onToggleReminder: toggleReminder }} 
                status={activeTab} 
                onAction={(contest) => {
                  if (activeTab === 'past') {
                    setLeaderboardModal(contest);
                  } else if (contest.external_url) {
                    window.open(contest.external_url, '_blank', 'noopener,noreferrer');
                  } else {
                    navigate('/code-lab/arena');
                  }
                }} 
              />
            ));
          })()
        )}
      </div>

      {leaderboardModal && (
        <LeaderboardModal 
          contest={leaderboardModal} 
          onClose={() => setLeaderboardModal(null)} 
        />
      )}
    </div>
  );
}
