import { useMemo, useState } from 'react';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Users, BookOpen, Activity, ClipboardList, Building2, Plus, RefreshCw } from 'lucide-react';
import './admin.css';

const tabs = [
  { id: 'overview', label: 'Overview', icon: Activity },
  { id: 'users', label: 'Users', icon: Users },
  { id: 'content', label: 'Content', icon: BookOpen },
  { id: 'tests', label: 'Tests', icon: ClipboardList },
  { id: 'companies', label: 'Companies', icon: Building2 },
];

function initialForms() {
  return {
    track: { name: '', description: '' },
    topic: { track_id: '', name: '', description: '', order: '' },
    question: {
      topic_id: '',
      question_text: '',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_answer: 'A',
      difficulty: 'medium',
    },
    test: { name: '', description: '', duration_minutes: 30, topic_ids: [] },
    company: { user_id: '', name: '', readiness: 50, focus: '' },
  };
}

function AdminPage() {
  const { data, loading, refetch } = useApi('/admin/overview/');
  const [activeTab, setActiveTab] = useState('overview');
  const [forms, setForms] = useState(initialForms);
  const [saving, setSaving] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  const allTopics = useMemo(() => (
    (data?.tracks || []).flatMap((track) => (
      track.topics.map((topic) => ({ ...topic, track_id: track.id, track_name: track.name }))
    ))
  ), [data]);

  const updateForm = (section, patch) => {
    setForms((prev) => ({ ...prev, [section]: { ...prev[section], ...patch } }));
    setError('');
    setNotice('');
  };

  const saveContent = async (section, payload) => {
    setSaving(section);
    setError('');
    setNotice('');
    try {
      const response = await api.post('/admin/content/', payload);
      setNotice(response.message || 'Saved');
      setForms(initialForms());
      await refetch();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving('');
    }
  };

  const saveCompany = async (event) => {
    event.preventDefault();
    const payload = {
      user_id: forms.company.user_id,
      name: forms.company.name,
      readiness: Number(forms.company.readiness),
      focus: forms.company.focus,
    };
    setSaving('company');
    setError('');
    setNotice('');
    try {
      const response = await api.post('/admin/company-targets/', payload);
      setNotice(response.message || 'Company target saved');
      setForms(initialForms());
      await refetch();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving('');
    }
  };

  const updateUser = async (userId, patch) => {
    setSaving(`user-${userId}`);
    setError('');
    setNotice('');
    try {
      await api.patch(`/admin/users/${userId}/`, patch);
      setNotice('User updated');
      await refetch();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving('');
    }
  };

  if (loading) return <Layout title="Admin"><div className="skeleton skeleton--card" /></Layout>;
  if (!data) return null;

  const { summary, users, tracks, questions, tests, company_targets, activity } = data;

  return (
    <Layout title="Admin Console" subtitle="Manage platform content, users, tests, and company targets">
      <div className="admin">
        <div className="admin__tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`admin__tab ${activeTab === tab.id ? 'admin__tab--active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={16} />
              <span>{tab.label}</span>
            </button>
          ))}
          <button type="button" className="admin__refresh" onClick={() => refetch()} aria-label="Refresh admin data">
            <RefreshCw size={16} />
          </button>
        </div>

        {notice && <div className="admin__notice">{notice}</div>}
        {error && <div className="admin__error">{error}</div>}

        {activeTab === 'overview' && (
          <>
            <div className="grid grid--4">
              <div className="stat-card"><div className="stat-card__label">Users</div><div className="stat-card__value">{summary.users}</div></div>
              <div className="stat-card"><div className="stat-card__label">Topics</div><div className="stat-card__value">{summary.topics}</div></div>
              <div className="stat-card"><div className="stat-card__label">Questions</div><div className="stat-card__value">{summary.questions}</div></div>
              <div className="stat-card"><div className="stat-card__label">Tests</div><div className="stat-card__value">{tests.length}</div></div>
            </div>

            {activity && activity.length > 0 && (
              <Card>
                <Card.Header>Recent activity</Card.Header>
                <Card.Body>
                  <div className="admin__activity-list">
                    {activity.map((item) => (
                      <div key={`${item.type}-${item.title}-${item.time}`} className="admin__activity-item">
                        <span className="admin__activity-type">{item.type}</span>
                        <span className="admin__activity-title">{item.title}</span>
                        <span className="admin__activity-user">{item.user}</span>
                        <span className="admin__activity-time">{item.time}</span>
                      </div>
                    ))}
                  </div>
                </Card.Body>
              </Card>
            )}
          </>
        )}

        {activeTab === 'users' && (
          <Card>
            <Card.Header>Users ({users.length})</Card.Header>
            <Card.Body>
              <div className="admin__table-wrap">
                <table className="admin__table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Profile</th>
                      <th>Staff</th>
                      <th>Active</th>
                      <th>Stats</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td>{user.name}</td>
                        <td>{user.email}</td>
                        <td>{user.profile_summary}</td>
                        <td><span className={`badge badge--${user.is_staff ? 'green' : 'slate'}`}>{user.is_staff ? 'Staff' : 'Student'}</span></td>
                        <td><span className={`badge badge--${user.is_active ? 'green' : 'red'}`}>{user.is_active ? 'Active' : 'Paused'}</span></td>
                        <td>{user.stats.completed_topics} topics / {user.stats.answers} answers</td>
                        <td>
                          <div className="admin__row-actions">
                            <Button size="sm" variant="secondary" loading={saving === `user-${user.id}`} onClick={() => updateUser(user.id, { is_active: !user.is_active })}>
                              {user.is_active ? 'Pause' : 'Activate'}
                            </Button>
                            {!user.is_superuser && (
                              <Button size="sm" variant="ghost" loading={saving === `user-${user.id}`} onClick={() => updateUser(user.id, { is_staff: !user.is_staff })}>
                                {user.is_staff ? 'Remove staff' : 'Make staff'}
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card.Body>
          </Card>
        )}

        {activeTab === 'content' && (
          <div className="admin__content-grid">
            <Card>
              <Card.Header>Create track</Card.Header>
              <Card.Body>
                <form className="admin__form" onSubmit={(event) => {
                  event.preventDefault();
                  saveContent('track', { type: 'track', ...forms.track });
                }}>
                  <input value={forms.track.name} onChange={(event) => updateForm('track', { name: event.target.value })} placeholder="Track name" required />
                  <textarea value={forms.track.description} onChange={(event) => updateForm('track', { description: event.target.value })} placeholder="Track description" rows={3} />
                  <Button type="submit" size="sm" icon={Plus} loading={saving === 'track'}>Save track</Button>
                </form>
              </Card.Body>
            </Card>

            <Card>
              <Card.Header>Create topic</Card.Header>
              <Card.Body>
                <form className="admin__form" onSubmit={(event) => {
                  event.preventDefault();
                  saveContent('topic', { type: 'topic', ...forms.topic, order: forms.topic.order ? Number(forms.topic.order) : undefined });
                }}>
                  <select value={forms.topic.track_id} onChange={(event) => updateForm('topic', { track_id: event.target.value })} required>
                    <option value="">Select track</option>
                    {tracks.map((track) => <option key={track.id} value={track.id}>{track.name}</option>)}
                  </select>
                  <input value={forms.topic.name} onChange={(event) => updateForm('topic', { name: event.target.value })} placeholder="Topic name" required />
                  <input value={forms.topic.order} onChange={(event) => updateForm('topic', { order: event.target.value })} placeholder="Order" type="number" min="1" />
                  <textarea value={forms.topic.description} onChange={(event) => updateForm('topic', { description: event.target.value })} placeholder="Topic description" rows={3} />
                  <Button type="submit" size="sm" icon={Plus} loading={saving === 'topic'}>Save topic</Button>
                </form>
              </Card.Body>
            </Card>

            <Card className="admin__wide">
              <Card.Header>Create question</Card.Header>
              <Card.Body>
                <form className="admin__form admin__form--question" onSubmit={(event) => {
                  event.preventDefault();
                  saveContent('question', { type: 'question', ...forms.question });
                }}>
                  <select value={forms.question.topic_id} onChange={(event) => updateForm('question', { topic_id: event.target.value })} required>
                    <option value="">Select topic</option>
                    {allTopics.map((topic) => <option key={topic.id} value={topic.id}>{topic.track_name} - {topic.name}</option>)}
                  </select>
                  <textarea className="admin__span-2" value={forms.question.question_text} onChange={(event) => updateForm('question', { question_text: event.target.value })} placeholder="Question text" rows={3} required />
                  {['a', 'b', 'c', 'd'].map((letter) => (
                    <input
                      key={letter}
                      value={forms.question[`option_${letter}`]}
                      onChange={(event) => updateForm('question', { [`option_${letter}`]: event.target.value })}
                      placeholder={`Option ${letter.toUpperCase()}`}
                      required
                    />
                  ))}
                  <select value={forms.question.correct_answer} onChange={(event) => updateForm('question', { correct_answer: event.target.value })}>
                    {['A', 'B', 'C', 'D'].map((option) => <option key={option} value={option}>Correct: {option}</option>)}
                  </select>
                  <select value={forms.question.difficulty} onChange={(event) => updateForm('question', { difficulty: event.target.value })}>
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                  <Button type="submit" size="sm" icon={Plus} loading={saving === 'question'}>Save question</Button>
                </form>
              </Card.Body>
            </Card>

            <Card className="admin__wide">
              <Card.Header>Content library</Card.Header>
              <Card.Body>
                <div className="admin__content-list">
                  {tracks.map((track) => (
                    <div key={track.id} className="admin__track-block">
                      <div className="admin__track-head">
                        <strong>{track.name}</strong>
                        <span>{track.topic_count} topics / {track.question_count} questions</span>
                      </div>
                      <div className="admin__topic-list">
                        {track.topics.map((topic) => (
                          <div key={topic.id} className="admin__topic-item">
                            <span>{topic.name}</span>
                            <span>{topic.question_count} Qs</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </Card.Body>
            </Card>
          </div>
        )}

        {activeTab === 'tests' && (
          <div className="admin__content-grid">
            <Card>
              <Card.Header>Create or update test</Card.Header>
              <Card.Body>
                <form className="admin__form" onSubmit={(event) => {
                  event.preventDefault();
                  saveContent('test', {
                    type: 'test',
                    name: forms.test.name,
                    description: forms.test.description,
                    duration_minutes: Number(forms.test.duration_minutes),
                    topic_ids: forms.test.topic_ids,
                  });
                }}>
                  <input value={forms.test.name} onChange={(event) => updateForm('test', { name: event.target.value })} placeholder="Test name" required />
                  <textarea value={forms.test.description} onChange={(event) => updateForm('test', { description: event.target.value })} placeholder="Test description" rows={3} />
                  <input value={forms.test.duration_minutes} onChange={(event) => updateForm('test', { duration_minutes: event.target.value })} type="number" min="1" placeholder="Duration minutes" />
                  <select
                    multiple
                    value={forms.test.topic_ids}
                    onChange={(event) => updateForm('test', { topic_ids: Array.from(event.target.selectedOptions).map((option) => Number(option.value)) })}
                  >
                    {allTopics.map((topic) => <option key={topic.id} value={topic.id}>{topic.track_name} - {topic.name}</option>)}
                  </select>
                  <Button type="submit" size="sm" icon={Plus} loading={saving === 'test'}>Save test</Button>
                </form>
              </Card.Body>
            </Card>

            <Card className="admin__wide">
              <Card.Header>Tests ({tests.length})</Card.Header>
              <Card.Body>
                <div className="admin__test-list">
                  {tests.map((test) => (
                    <div key={test.id} className="admin__test-item">
                      <div>
                        <strong>{test.name}</strong>
                        <p>{test.description}</p>
                      </div>
                      <span>{test.duration_minutes} min</span>
                      <span>{test.question_count} questions</span>
                      <span>{test.topic_count} sections</span>
                    </div>
                  ))}
                </div>
              </Card.Body>
            </Card>

            <Card className="admin__wide">
              <Card.Header>Recent questions ({questions.length})</Card.Header>
              <Card.Body>
                <div className="admin__question-list">
                  {questions.map((question) => (
                    <div key={question.id} className="admin__question-item">
                      <span>{question.track} / {question.topic}</span>
                      <strong>{question.question_text}</strong>
                      <span>{question.difficulty} - correct {question.correct_answer}</span>
                    </div>
                  ))}
                </div>
              </Card.Body>
            </Card>
          </div>
        )}

        {activeTab === 'companies' && (
          <div className="admin__content-grid">
            <Card>
              <Card.Header>Add company target</Card.Header>
              <Card.Body>
                <form className="admin__form" onSubmit={saveCompany}>
                  <select value={forms.company.user_id} onChange={(event) => updateForm('company', { user_id: event.target.value })} required>
                    <option value="">Select user</option>
                    {users.map((user) => <option key={user.id} value={user.id}>{user.email}</option>)}
                  </select>
                  <input value={forms.company.name} onChange={(event) => updateForm('company', { name: event.target.value })} placeholder="Company name" required />
                  <input value={forms.company.readiness} onChange={(event) => updateForm('company', { readiness: event.target.value })} type="number" min="0" max="100" />
                  <textarea value={forms.company.focus} onChange={(event) => updateForm('company', { focus: event.target.value })} placeholder="Preparation focus" rows={3} />
                  <Button type="submit" size="sm" icon={Plus} loading={saving === 'company'}>Save company</Button>
                </form>
              </Card.Body>
            </Card>

            <Card className="admin__wide">
              <Card.Header>Company targets ({company_targets.length})</Card.Header>
              <Card.Body>
                <div className="admin__table-wrap">
                  <table className="admin__table">
                    <thead>
                      <tr>
                        <th>User</th>
                        <th>Company</th>
                        <th>Readiness</th>
                        <th>Focus</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {company_targets.map((target) => (
                        <tr key={target.id}>
                          <td>{target.email}</td>
                          <td>{target.name}</td>
                          <td><span className={`badge badge--${target.tone}`}>{target.readiness}%</span></td>
                          <td>{target.focus}</td>
                          <td><span className={`badge badge--${target.is_active ? 'green' : 'slate'}`}>{target.is_active ? 'Active' : 'Archived'}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card.Body>
            </Card>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default AdminPage;
