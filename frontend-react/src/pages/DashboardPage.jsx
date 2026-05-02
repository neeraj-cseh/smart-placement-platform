import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { ArrowRight } from 'lucide-react';
import './dashboard.css';

function DashboardPage() {
  const navigate = useNavigate();
  const { data, loading } = useApi('/auth/dashboard/');

  if (loading) {
    return (
      <Layout title="Dashboard">
        <div className="dashboard__loading">
          <div className="skeleton skeleton--card" />
          <div className="skeleton skeleton--card" />
          <div className="skeleton skeleton--card" />
        </div>
      </Layout>
    );
  }

  if (!data) return null;

  const metrics = data.metrics || [];
  const plan = data.todays_plan || {};
  const tracks = data.learning_tracks || [];
  const weekly = data.weekly_momentum || [];
  const companies = data.company_readiness || [];
  const activity = data.recent_activity || [];

  return (
    <Layout title={data.header?.greeting || 'Dashboard'} subtitle={data.header?.subtitle}>
      <div className="dashboard">
        <div className="grid grid--4 dashboard__metrics">
          {metrics.map((m, i) => {
            return (
              <div key={i} className="stat-card">
                <div className="stat-card__label">{m.label}</div>
                <div className="stat-card__value">{m.value}</div>
                <div className="stat-card__change">{m.change}</div>
              </div>
            );
          })}
        </div>

        <div className="grid grid--2 dashboard__main">
          <Card>
            <Card.Header action={<Button variant="ghost" size="sm" onClick={() => navigate('/learning-path')}>View all <ArrowRight size={14} /></Button>}>
              Today&apos;s plan
            </Card.Header>
            <Card.Body>
              {plan.items && plan.items.length > 0 ? (
                <div className="plan-list">
                  {plan.items.map((item, i) => (
                    <div key={i} className={`plan-item plan-item--${item.tone}`}>
                      <div className="plan-item__content">
                        <span className="plan-item__task">{item.task}</span>
                        <span className="plan-item__detail">{item.detail}</span>
                      </div>
                      <span className={`badge badge--${item.tone}`}>{item.status}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <p>No tasks for today</p>
                </div>
              )}
            </Card.Body>
          </Card>

          <Card>
            <Card.Header action={<Button variant="ghost" size="sm" onClick={() => navigate('/companies')}>View all <ArrowRight size={14} /></Button>}>
              Company readiness
            </Card.Header>
            <Card.Body>
              {companies.length > 0 ? (
                <div className="company-list">
                  {companies.map((c, i) => (
                    <div key={i} className="company-item">
                      <div className="company-item__info">
                        <span className="company-item__name">{c.full_name || c.name}</span>
                        <span className="company-item__focus">{c.focus}</span>
                      </div>
                      <div className="company-item__progress">
                        <div className="progress-bar">
                          <div
                            className={`progress-bar__fill progress-bar__fill--${c.tone}`}
                            style={{ width: `${c.readiness}%` }}
                          />
                        </div>
                        <span className={`badge badge--${c.tone}`}>{c.readiness}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <p>No companies tracked yet</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </div>

        <div className="grid grid--2 dashboard__secondary">
          <Card>
            <Card.Header>Learning tracks</Card.Header>
            <Card.Body>
              {tracks.length > 0 ? (
                <div className="track-list">
                  {tracks.map((t, i) => (
                    <div key={i} className="track-item">
                      <span className="track-item__name">{t.name}</span>
                      <div className="track-item__bar">
                        <div className="progress-bar">
                          <div
                            className={`progress-bar__fill progress-bar__fill--${t.tone}`}
                            style={{ width: `${t.progress}%` }}
                          />
                        </div>
                        <span className="track-item__pct">{t.progress}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state"><p>No tracks available</p></div>
              )}
            </Card.Body>
          </Card>

          <Card>
            <Card.Header>Recent activity</Card.Header>
            <Card.Body>
              {activity.length > 0 ? (
                <div className="activity-list">
                  {activity.map((a, i) => (
                    <div key={i} className="activity-item">
                      <div className="activity-item__icon" />
                      <div className="activity-item__content">
                        <span className="activity-item__title">{a.title}</span>
                        <span className="activity-item__time">{a.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state"><p>No activity yet</p></div>
              )}
            </Card.Body>
          </Card>
        </div>

        {weekly.length > 0 && (
          <Card>
            <Card.Header>Weekly momentum</Card.Header>
            <Card.Body>
              <div className="weekly-chart">
                {weekly.map((d, i) => (
                  <div key={i} className="weekly-bar">
                    <div
                      className="weekly-bar__fill"
                      style={{ height: `${Math.max(4, d.accuracy)}%` }}
                    />
                    <span className="weekly-bar__label">{d.day}</span>
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        )}
      </div>
    </Layout>
  );
}

export default DashboardPage;
