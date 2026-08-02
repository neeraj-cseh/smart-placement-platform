import React from 'react';
import { Calendar, Clock, ChevronRight } from 'lucide-react';

export default function ContestCard({ contest, isUpcoming, onAction }) {
  return (
    <div className={`contest-card ${isUpcoming ? 'upcoming' : 'past'}`}>
      {isUpcoming && <div className="cc-glow" />}
      <div className="cc-content">
        <h3 className="cc-title">{contest.title}</h3>
        <div className="cc-meta">
          <span className="cc-meta-item">
            <Calendar size={14}/> 
            {isUpcoming ? new Date(contest.start_time).toLocaleString() : new Date(contest.start_time).toLocaleDateString()}
          </span>
          <span className="cc-meta-item">
            {isUpcoming ? (
              <><Clock size={14}/> {contest.duration_minutes} Minutes</>
            ) : (
              <>{contest.problems?.length || 4} Problems</>
            )}
          </span>
        </div>
      </div>
      <div className="cc-actions">
        {isUpcoming ? (
          <button className="cc-btn-primary" onClick={onAction}>
            Register Now
          </button>
        ) : (
          <button className="cc-btn-secondary" onClick={onAction}>
            Practice <ChevronRight size={14}/>
          </button>
        )}
      </div>
    </div>
  );
}
