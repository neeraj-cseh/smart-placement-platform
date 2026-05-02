import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import './analytics.css';

function shortLabel(value = '') {
  return value.length > 14 ? `${value.slice(0, 13)}...` : value;
}

function AnalyticsPage() {
  const { data, loading } = useApi('/analytics/full/');

  if (loading) return <Layout title="Analytics"><div className="skeleton skeleton--card" /></Layout>;
  if (!data) return null;

  const { summary, topic_accuracy, track_progress, weekly_momentum, test_history, weak_topics } = data;

  return (
    <Layout title="Analytics" subtitle={`Overall accuracy: ${summary.overall_accuracy}%`}>
      <div className="grid grid--4 analytics__stats">
        <div className="stat-card">
          <div className="stat-card__label">Total attempts</div>
          <div className="stat-card__value">{summary.attempts}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Correct answers</div>
          <div className="stat-card__value">{summary.correct}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Tests taken</div>
          <div className="stat-card__value">{summary.tests_taken}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Topics practiced</div>
          <div className="stat-card__value">{summary.topics_practiced}</div>
        </div>
      </div>

      <div className="grid grid--2 analytics__section">
        <Card>
          <Card.Header>Topic accuracy</Card.Header>
          <Card.Body>
            <div className="analytics__chart">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topic_accuracy.slice(0, 10)} margin={{ top: 8, right: 8, left: 0, bottom: 36 }}>
                  <XAxis dataKey="topic" tick={{ fontSize: 10 }} tickFormatter={shortLabel} interval={0} angle={-28} textAnchor="end" height={70} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} width={34} />
                  <Tooltip />
                  <Bar dataKey="accuracy" fill="var(--accent-primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Header>Weekly momentum</Card.Header>
          <Card.Body>
            <div className="analytics__chart">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weekly_momentum} margin={{ top: 8, right: 12, left: 0, bottom: 8 }}>
                  <XAxis dataKey="day" tick={{ fontSize: 11 }} minTickGap={14} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip />
                  <Line type="monotone" dataKey="accuracy" stroke="var(--accent-primary)" strokeWidth={2} dot={{ fill: 'var(--accent-primary)' }} />
                  <Line type="monotone" dataKey="solved" stroke="var(--accent-success)" strokeWidth={2} dot={{ fill: 'var(--accent-success)' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card.Body>
        </Card>
      </div>

      <div className="grid grid--2 analytics__section">
        <Card>
          <Card.Header>Track progress</Card.Header>
          <Card.Body>
            <div className="analytics__track-list">
              {track_progress.map((track) => (
                <div key={track.track} className="analytics__track-item">
                  <div className="analytics__track-head">
                    <span>{track.track}</span>
                    <span>{track.completed_topics}/{track.total_topics} topics</span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className={`progress-bar__fill progress-bar__fill--${track.progress >= 75 ? 'green' : track.progress >= 40 ? 'amber' : track.progress > 0 ? 'cyan' : 'slate'}`}
                      style={{ width: `${track.progress}%` }}
                    />
                  </div>
                  <span className="analytics__track-score">{track.progress}%</span>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Header action={weak_topics.length > 0 && <span className="badge badge--red">{weak_topics.length} weak</span>}>
            Weak topics
          </Card.Header>
          <Card.Body>
            {weak_topics.length > 0 ? (
              <div className="analytics__weak-list">
                {weak_topics.map((t, i) => (
                  <div key={i} className="analytics__weak-item">
                    <span className="analytics__weak-name">{t.topic}</span>
                    <span className="analytics__weak-track">{t.track}</span>
                    <span className="badge badge--red">{t.accuracy}%</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state__title">No weak topics</div>
                <div className="empty-state__desc">Your accuracy is above 60% on all practiced topics.</div>
              </div>
            )}
          </Card.Body>
        </Card>
      </div>

      {test_history.length > 0 && (
        <Card className="analytics__section">
          <Card.Header>Test history</Card.Header>
          <Card.Body>
            <div className="analytics__test-list">
              {test_history.map((t, i) => (
                <div key={i} className="analytics__test-item">
                  <span className="analytics__test-name">{t.test}</span>
                  <span className="analytics__test-score">{t.raw}</span>
                  <span className={`badge badge--${t.score >= 70 ? 'green' : t.score >= 50 ? 'amber' : 'red'}`}>{t.score}%</span>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>
      )}
    </Layout>
  );
}

export default AnalyticsPage;
