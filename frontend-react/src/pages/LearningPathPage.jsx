import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import { Check, Lock, ChevronDown, ChevronRight } from 'lucide-react';
import './learning-path.css';

function LearningPathPage() {
  const { data, loading } = useApi('/learning-path/');
  const [expandedTrack, setExpandedTrack] = useState(null);

  if (loading) return <Layout title="Learning Path"><div className="skeleton skeleton--card" /></Layout>;
  if (!data) return null;

  const { tracks, summary, focus_queue } = data;

  return (
    <Layout title="Learning Path" subtitle={`${summary.progress_percentage}% complete - ${summary.completed_topics}/${summary.total_topics} topics`}>
      <div className="learning-path">
        <div className="grid grid--3 learning-path__stats">
          <div className="stat-card">
            <div className="stat-card__label">Tracks completed</div>
            <div className="stat-card__value">{summary.completed_tracks}/{summary.total_tracks}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Questions available</div>
            <div className="stat-card__value">{summary.total_questions}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card__label">Est. remaining</div>
            <div className="stat-card__value">{Math.floor(summary.remaining_minutes / 60)}h {summary.remaining_minutes % 60}m</div>
          </div>
        </div>

        {focus_queue && focus_queue.length > 0 && (
          <Card className="learning-path__focus-card">
            <Card.Header>Focus queue</Card.Header>
            <Card.Body>
              <div className="focus-queue">
                {focus_queue.map((item) => (
                  <div key={item.id} className={`focus-item focus-item--${item.status}`}>
                    <span className="focus-item__track">{item.track_name}</span>
                    <span className="focus-item__name">{item.name}</span>
                    <span className="focus-item__reason">{item.reason}</span>
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        )}

        <div className="learning-path__tracks">
          {tracks.map((track) => {
            const isExpanded = expandedTrack === track.id;
            return (
              <Card key={track.id} hover className="learning-path__track-card">
                <div
                  className="learning-path__track-header"
                  onClick={() => setExpandedTrack(isExpanded ? null : track.id)}
                >
                  <div className="learning-path__track-info">
                    <button type="button" className="learning-path__toggle" aria-label={isExpanded ? 'Collapse track' : 'Expand track'}>
                      {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                    </button>
                    <div>
                      <h3 className="learning-path__track-name">{track.name}</h3>
                      <span className="learning-path__track-meta">
                        {track.completed_topics}/{track.total_topics} topics - {track.progress_percentage}%
                      </span>
                    </div>
                  </div>
                  <span className={`badge badge--${track.tone}`}>{track.status}</span>
                </div>

                {isExpanded && track.topics && (
                  <div className="learning-path__topics">
                    {track.topics.map((topic) => (
                      <div key={topic.id} className={`topic-row topic-row--${topic.status}`}>
                        <div className="topic-row__status">
                          {topic.is_completed ? (
                            <Check size={16} className="topic-row__check" />
                          ) : topic.is_locked ? (
                            <Lock size={16} className="topic-row__lock" />
                          ) : (
                            <div className="topic-row__dot" />
                          )}
                        </div>
                        <div className="topic-row__info">
                          <span className="topic-row__name">{topic.name}</span>
                          <span className="topic-row__meta">
                            {topic.question_count} questions - {topic.status_label}
                          </span>
                        </div>
                        <span className={`badge badge--${topic.tone}`}>{topic.checkpoint}</span>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </div>
    </Layout>
  );
}

export default LearningPathPage;
