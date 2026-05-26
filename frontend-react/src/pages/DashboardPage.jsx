import { useNavigate } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  Brain,
  Building2,
  CheckCircle2,
  Code2,
  Flame,
  LineChart as LineChartIcon,
  Target,
  Timer,
  Trophy,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import './dashboard.css';

const metricIcons = {
  target: Target,
  check: CheckCircle2,
  flame: Flame,
  line: LineChartIcon,
};

function clampPercent(value = 0) {
  return Math.max(0, Math.min(100, Number(value) || 0));
}

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
  const weekly = data.weekly_momentum || [];
  const companies = data.company_readiness || [];
  const activity = data.recent_activity || [];
  const subjectMastery = data.subject_mastery || [];
  const weakPriorities = data.weakness_priorities || [];
  const revisionQueue = data.revision_queue || [];
  const interviewPrep = data.interview_prep || [];
  const targetCompany = data.sidebar?.current_target || {};
  const readiness = plan.readiness || {};
  const planTotal = plan.total_count || plan.items?.length || 0;
  const planDone = plan.completed_count || 0;
  const planProgress = planTotal ? Math.round((planDone / planTotal) * 100) : 0;

  return (
    <Layout title={data.header?.greeting || 'Dashboard'} subtitle={data.header?.subtitle}>
      <div className="dashboard">
        <section className="dashboard-hero">
          <div className="dashboard-hero__content">
            <div className="dashboard-hero__eyebrow">
              <Trophy size={16} />
              <span>{data.header?.date_label || 'Today'} readiness command center</span>
            </div>
            <h2>Turn preparation into placement momentum.</h2>
            <p>
              Focus on the highest-value topics, keep company readiness visible, and move every practice session toward interview confidence.
            </p>
            <div className="dashboard-hero__actions">
              <Button onClick={() => navigate('/practice')}>
                Practice now <ArrowRight size={16} />
              </Button>
              <Button variant="secondary" onClick={() => navigate('/mock-tests')}>
                Take mock test
              </Button>
            </div>
          </div>

          <div className="dashboard-hero__panel">
            <div className="readiness-ring" style={{ '--value': clampPercent(readiness.value) }}>
              <div className="readiness-ring__inner">
                <span>{readiness.value ?? 0}%</span>
                <small>{readiness.label || 'Placement readiness'}</small>
              </div>
            </div>
            <div className="dashboard-hero__target">
              <span className={`badge badge--${targetCompany.tone || 'slate'}`}>{targetCompany.readiness_label || 'No target set'}</span>
              <strong>{targetCompany.full_name || targetCompany.name || 'Choose a target company'}</strong>
              <p>{targetCompany.summary || readiness.description || 'Your preparation snapshot will sharpen as you practice.'}</p>
            </div>
          </div>
        </section>

        <div className="grid grid--4 dashboard__metrics">
          {metrics.map((m, i) => {
            const Icon = metricIcons[m.icon] || BarChart3;
            return (
              <div key={i} className={`stat-card stat-card--${m.tone || 'cyan'}`}>
                <div className="stat-card__top">
                  <div className="stat-card__icon"><Icon size={18} /></div>
                  <div className="stat-card__label">{m.label}</div>
                </div>
                <div className="stat-card__value">{m.value}</div>
                <div className="stat-card__change">{m.change}</div>
              </div>
            );
          })}
        </div>

        <div className="dashboard__command-grid">
          <Card className="dashboard-card dashboard-card--plan">
            <Card.Header action={<Button variant="ghost" size="sm" onClick={() => navigate('/learning-path')}>View all <ArrowRight size={14} /></Button>}>
              <span className="dashboard-card__title"><BookOpen size={18} />Today&apos;s plan</span>
            </Card.Header>
            <Card.Body>
              <div className="plan-summary">
                <div>
                  <strong>{planDone}/{planTotal}</strong>
                  <span>tasks completed</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-bar__fill progress-bar__fill--green" style={{ width: `${planProgress}%` }} />
                </div>
              </div>
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

          <Card className="dashboard-card">
            <Card.Header action={<Button variant="ghost" size="sm" onClick={() => navigate('/analytics')}>Deep dive <ArrowRight size={14} /></Button>}>
              <span className="dashboard-card__title"><BarChart3 size={18} />Weekly momentum</span>
            </Card.Header>
            <Card.Body>
              {weekly.length > 0 ? (
                <div className="dashboard-chart">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={weekly} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                      <CartesianGrid stroke="var(--border-primary)" strokeDasharray="4 4" vertical={false} />
                      <XAxis dataKey="day" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: 'var(--text-muted)' }} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 8 }} />
                      <Line type="monotone" dataKey="accuracy" stroke="var(--accent-primary)" strokeWidth={3} dot={{ r: 4, fill: 'var(--accent-primary)' }} />
                      <Line type="monotone" dataKey="solved" stroke="var(--accent-success)" strokeWidth={3} dot={{ r: 4, fill: 'var(--accent-success)' }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="empty-state"><p>No weekly data yet</p></div>
              )}
            </Card.Body>
          </Card>
        </div>

        <div className="grid grid--2 dashboard__secondary">
          <Card className="dashboard-card">
            <Card.Header action={<Button variant="ghost" size="sm" onClick={() => navigate('/companies')}>View all <ArrowRight size={14} /></Button>}>
              <span className="dashboard-card__title"><Building2 size={18} />Company readiness</span>
            </Card.Header>
            <Card.Body>
              {companies.length > 0 ? (
                <div className="company-list">
                  {companies.slice(0, 5).map((c, i) => (
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
                <div className="empty-state"><p>No companies tracked yet</p></div>
              )}
            </Card.Body>
          </Card>

          <Card className="dashboard-card">
            <Card.Header><span className="dashboard-card__title"><Target size={18} />Weakness priorities</span></Card.Header>
            <Card.Body>
              {weakPriorities.length > 0 ? (
                <div className="priority-list">
                  {weakPriorities.slice(0, 5).map((item, i) => (
                    <div key={i} className="priority-item">
                      <div>
                        <span className="priority-item__topic">{item.topic}</span>
                        <span className="priority-item__track">{item.track || item.reason}</span>
                      </div>
                      <span className="badge badge--red">{item.score ?? item.accuracy}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state"><p>No critical weak topics right now</p></div>
              )}
            </Card.Body>
          </Card>
        </div>

        <div className="dashboard__insights-grid">
          <Card className="dashboard-card">
            <Card.Header><span className="dashboard-card__title"><Brain size={18} />Subject mastery</span></Card.Header>
            <Card.Body>
              {subjectMastery.length > 0 ? (
                <div className="dashboard-chart dashboard-chart--compact">
                  <ResponsiveContainer width="100%" height={230}>
                    <BarChart data={subjectMastery.slice(0, 6)} layout="vertical" margin={{ top: 0, right: 16, left: 8, bottom: 0 }}>
                      <CartesianGrid stroke="var(--border-primary)" strokeDasharray="4 4" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} hide />
                      <YAxis dataKey="name" type="category" width={112} tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 8 }} />
                      <Bar dataKey="score" fill="var(--accent-info)" radius={[0, 6, 6, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="empty-state"><p>Mastery data appears after topic practice</p></div>
              )}
            </Card.Body>
          </Card>

          <Card className="dashboard-card">
            <Card.Header><span className="dashboard-card__title"><Timer size={18} />Revision queue</span></Card.Header>
            <Card.Body>
              {revisionQueue.length > 0 ? (
                <div className="revision-list">
                  {revisionQueue.slice(0, 5).map((item, i) => (
                    <div key={i} className="revision-item">
                      <Code2 size={16} />
                      <div>
                        <span>{item.topic || item.title}</span>
                        <small>{item.reason || item.detail || item.track}</small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state"><p>No revision tasks waiting</p></div>
              )}
            </Card.Body>
          </Card>

          <Card className="dashboard-card">
            <Card.Header><span className="dashboard-card__title"><Brain size={18} />Interview prep</span></Card.Header>
            <Card.Body>
              {interviewPrep.length > 0 ? (
                <div className="interview-list">
                  {interviewPrep.slice(0, 4).map((item, i) => (
                    <div key={i} className="interview-item">
                      <div className="interview-item__head">
                        <span>{item.category || item.name}</span>
                        <span className={`badge badge--${item.tone || 'cyan'}`}>{item.score ?? item.readiness ?? 0}%</span>
                      </div>
                      <p>{item.feedback || item.next_step || item.detail}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state"><p>Start an AI interview to build this section</p></div>
              )}
            </Card.Body>
          </Card>

          <Card className="dashboard-card">
            <Card.Header><span className="dashboard-card__title"><Flame size={18} />Recent activity</span></Card.Header>
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
      </div>
    </Layout>
  );
}

export default DashboardPage;
