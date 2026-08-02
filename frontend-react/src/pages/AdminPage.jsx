import { useMemo, useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, BookOpen, ClipboardList, Building2, Shield,
  Plus, RefreshCw, Pencil, Trash2, X, AlertTriangle, CheckCircle, Search, Layers, Award, Eye
} from 'lucide-react';
import Button from '../components/ui/Button';
import './admin.css';

/* ── Empty State Component ──────────────────────────────────────── */
function EmptyState({ icon: Icon, title, desc }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 20px', textAlign: 'center' }}>
      <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'rgba(255, 255, 255, 0.03)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16 }}>
        <Icon size={24} style={{ color: 'var(--text-secondary)' }} />
      </div>
      <span style={{ fontSize: '1rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 6 }}>{title}</span>
      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: 280, lineHeight: 1.4 }}>{desc}</span>
    </div>
  );
}

/* ── Drawer Component ──────────────────────────────────────── */
function SlideOverDrawer({ isOpen, onClose, title, children, footer }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="adm-drawer-overlay">
          <motion.div
            className="adm-drawer"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          >
            <div className="adm-drawer__header">
              <h3 className="adm-drawer__title">{title}</h3>
              <button className="adm-drawer__close" onClick={onClose}><X size={18}/></button>
            </div>
            <div className="adm-drawer__body">
              {children}
            </div>
            {footer && (
              <div className="adm-drawer__footer">
                {footer}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

const detailEndpoints = {
  track:    id => `/admin/tracks/${id}/`,
  topic:    id => `/admin/topics/${id}/`,
  question: id => `/admin/questions/${id}/`,
  test:     id => `/admin/tests/${id}/`,
  company:  id => `/admin/company-targets/${id}/`,
};

function initialForms() {
  return {
    track: { name: '', description: '' },
    topic: { track_id: '', name: '', description: '', order: '' },
    question: { topic_id: '', question_text: '', option_a: '', option_b: '', option_c: '', option_d: '', correct_answer: 'A', difficulty: 'medium' },
    test: { name: '', description: '', duration_minutes: 30, topic_ids: [] },
    company: { user_id: '', name: '', readiness: 50, focus: '' },
  };
}

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

/* ══════════════════════════════════════════════════════════════════
   MAIN PAGE
   ══════════════════════════════════════════════════════════════════ */
export default function AdminPage() {
  const { data, loading, refetch } = useApi('/admin/overview/');
  const location = useLocation();

  const queryParams = new URLSearchParams(location.search);
  const activeTab = queryParams.get('tab') || 'users';

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState({ type: '', id: null });
  const [viewing, setViewing] = useState({ type: '', item: null });
  const [forms, setForms] = useState(initialForms());
  
  const [saving, setSaving] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  // Auto-clear global notices & errors after 5 seconds
  useEffect(() => {
    if (notice) { const t = setTimeout(() => setNotice(''), 5000); return () => clearTimeout(t); }
  }, [notice]);
  useEffect(() => {
    if (error) { const t = setTimeout(() => setError(''), 5000); return () => clearTimeout(t); }
  }, [error]);

  // Reset search when tab changes
  useEffect(() => setSearch(''), [activeTab]);

  const allTopics = useMemo(() =>
    (data?.tracks || []).flatMap(track =>
      track.topics.map(topic => ({ ...topic, track_id: track.id, track_name: track.name }))
    ), [data]);

  const updateForm = (section, patch) => {
    setForms(prev => ({ ...prev, [section]: { ...prev[section], ...patch } }));
    setError(''); setNotice('');
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setTimeout(() => { setForms(initialForms()); setEditing({ type: '', id: null }); setViewing({ type: '', item: null }); setError(''); setNotice(''); }, 200);
  };

  const openViewer = (section, item) => {
    setViewing({ type: section, item });
    setDrawerOpen(true);
  };

  const openDrawer = (section, item = null) => {
    setError(''); setNotice('');
    if (item) {
      setEditing({ type: section, id: item.id });
      const map = {
        track:    { name: item.name || '', description: item.description || '' },
        topic:    { track_id: item.track_id || '', name: item.name || '', description: item.description || '', order: item.order || '' },
        question: { topic_id: item.topic_id || '', question_text: item.question_text || '', option_a: item.option_a || '', option_b: item.option_b || '', option_c: item.option_c || '', option_d: item.option_d || '', correct_answer: item.correct_answer || 'A', difficulty: item.difficulty || 'medium' },
        test:     { name: item.name || '', description: item.description || '', duration_minutes: item.duration_minutes || 30, topic_ids: item.topic_ids || [] },
        company:  { user_id: item.user_id || '', name: item.name || '', readiness: item.readiness ?? 0, focus: item.focus || '' },
      };
      setForms(prev => ({ ...prev, [section]: map[section] }));
    } else {
      setEditing({ type: section, id: null });
      setForms(prev => ({ ...prev, [section]: initialForms()[section] }));
    }
    setDrawerOpen(true);
  };

  const saveContent = async (section) => {
    const payload = forms[section];
    setSaving(section); setError(''); setNotice('');
    try {
      const isEditing = editing.type === section && editing.id;
      const response = isEditing
        ? await api.patch(detailEndpoints[section](editing.id), payload)
        : await api.post(section === 'company' ? '/admin/company-targets/' : '/admin/content/', { type: section, ...payload });
      setNotice(response.message || 'Saved successfully');
      await refetch();
      closeDrawer();
    } catch (err) { setError(err.message); } finally { setSaving(''); }
  };

  const deleteItem = async (section, id, label) => {
    if (!window.confirm(`Delete ${label}? This action cannot be undone.`)) return;
    setSaving(`${section}-${id}-delete`); setError(''); setNotice('');
    try {
      const response = await api.delete(detailEndpoints[section](id));
      if (response && response.message) {
        setNotice(response.message);
      }
      await refetch();
    } catch (err) { setError(err.message || 'Failed to delete item.'); } finally { setSaving(''); }
  };

  const updateUser = async (userId, patch) => {
    setSaving(`user-${userId}`); setError(''); setNotice('');
    try { await api.patch(`/admin/users/${userId}/`, patch); await refetch(); }
    catch (err) { setError(err.message || 'Failed to update user.'); } finally { setSaving(''); }
  };

  // Extract avatar initials
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  };

  if (loading) {
    return (
      <Layout title="Admin Console" subtitle="Data Management">
        <div className="adm-skeleton">
          {[...Array(6)].map((_, i) => <div key={i} className="adm-skeleton__card" style={{ animationDelay: `${i*0.08}s` }}/>)}
        </div>
      </Layout>
    );
  }
  if (!data) return null;

  const { users, tracks, questions, tests, company_targets } = data;

  const filteredUsers = users.filter(u =>
    !search || u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Layout title="Admin Console" subtitle="Enterprise Control Panel">
      <div className="adm">
        
        {/* Global Notices & Errors */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: (notice || error) ? '12px' : 0 }}>
          <AnimatePresence>
            {notice && (
              <motion.div key="notice" className="adm-notice" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }} style={{ marginBottom: 0 }}>
                <CheckCircle size={16}/> {notice}
              </motion.div>
            )}
            {error && (
              <motion.div key="error" className="adm-error" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }} style={{ marginBottom: 0 }}>
                <AlertTriangle size={16}/> {error}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        <AnimatePresence mode="wait">
          
          {/* ════════════════════════════════════════════════════════════════════
              USERS TAB
              ════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'users' && (
            <motion.div key="users" initial="hidden" animate="show" exit={{ opacity: 0 }} variants={fadeUp}>
              <div className="adm-section-header">
                <div className="adm-section-header-left">
                  <h2 className="adm-section-title"><Users size={24}/> User Directory</h2>
                  <div className="adm-search">
                    <Search size={16}/>
                    <input className="adm-search__input" placeholder="Search users by name or email..." value={search} onChange={e => setSearch(e.target.value)} />
                  </div>
                </div>
                <button className="adm-action-btn" onClick={refetch} title="Refresh Data"><RefreshCw size={18} /></button>
              </div>
              <div className="adm-table-card">
                <div className="adm-table-wrap">
                  <table className="adm-table">
                    <thead>
                      <tr><th>User</th><th>Access Role</th><th>Status</th><th>Joined</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {filteredUsers.length === 0 && <tr><td colSpan="5"><EmptyState icon={Users} title="No users found" desc="Adjust your search filters."/></td></tr>}
                      {filteredUsers.map(u => (
                        <tr key={u.id}>
                          <td>
                            <div className="adm-user-cell">
                              <div className="adm-avatar">{getInitials(u.name)}</div>
                              <div>
                                <span className="adm-table__primary">{u.name}</span>
                                <span className="adm-table__secondary">{u.email}</span>
                              </div>
                            </div>
                          </td>
                          <td>
                            {u.is_superuser ? <span className="adm-table__badge adm-badge--pink">Superuser</span> : 
                             u.is_staff ? <span className="adm-table__badge adm-badge--indigo">Staff Admin</span> : 
                             <span className="adm-table__secondary">Student</span>}
                          </td>
                          <td>
                            {u.is_active ? <span className="adm-table__badge adm-badge--green">Active</span> : 
                             <span className="adm-table__badge adm-badge--red">Suspended</span>}
                          </td>
                          <td><span className="adm-table__secondary">{new Date(u.created_at).toLocaleDateString()}</span></td>
                          <td>
                            <div className="adm-row-actions">
                              <button className="adm-action-btn" onClick={() => openViewer('user', u)} title="View Complete Data"><Eye size={16}/></button>
                              <button className="adm-action-btn" onClick={() => updateUser(u.id, { is_staff: !u.is_staff })} title="Toggle Staff Role">
                                <Shield size={16} color={u.is_staff ? "#6366f1" : "currentColor"} />
                              </button>
                              <button className={`adm-action-btn ${u.is_active ? 'adm-action-btn--danger' : ''}`} onClick={() => updateUser(u.id, { is_active: !u.is_active })} title={u.is_active ? "Suspend User" : "Activate User"}>
                                {u.is_active ? <Trash2 size={16}/> : <CheckCircle size={16}/>}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}

          {/* ════════════════════════════════════════════════════════════════════
              TRACKS TAB
              ════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'tracks' && (
            <motion.div key="tracks" initial="hidden" animate="show" exit={{ opacity: 0 }} variants={fadeUp}>
              <div className="adm-section-header">
                <div className="adm-section-header-left">
                  <h2 className="adm-section-title"><Award size={24}/> Curriculum Tracks</h2>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button className="adm-action-btn" onClick={refetch} title="Refresh Data"><RefreshCw size={18} /></button>
                  <button className="adm-fab" onClick={() => openDrawer('track')}><Plus size={16}/> New Track</button>
                </div>
              </div>
              <div className="adm-table-card">
                <div className="adm-table-wrap">
                  <table className="adm-table">
                    <thead>
                      <tr><th>Track Name</th><th>Topics</th><th>Questions</th><th>Progress</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {tracks.length === 0 && <tr><td colSpan="5"><EmptyState icon={Award} title="No Tracks" desc="Create a curriculum track to get started."/></td></tr>}
                      {tracks.map(t => (
                        <tr key={t.id}>
                          <td>
                            <span className="adm-table__primary">{t.name}</span>
                            <span className="adm-table__secondary" style={{ maxWidth: 280, display: 'inline-block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.description}</span>
                          </td>
                          <td><span className="adm-table__badge">{t.topic_count}</span></td>
                          <td><span className="adm-table__badge">{t.question_count}</span></td>
                          <td><span className="adm-table__secondary">{t.completion_rate.toFixed(1)}% Completed</span></td>
                          <td>
                            <div className="adm-row-actions">
                              <button className="adm-action-btn" onClick={() => openViewer('track', t)}><Eye size={16}/></button>
                              <button className="adm-action-btn" onClick={() => openDrawer('track', t)}><Pencil size={16}/></button>
                              <button className="adm-action-btn adm-action-btn--danger" onClick={() => deleteItem('track', t.id, t.name)}><Trash2 size={16}/></button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}

          {/* ════════════════════════════════════════════════════════════════════
              TOPICS TAB
              ════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'topics' && (
            <motion.div key="topics" initial="hidden" animate="show" exit={{ opacity: 0 }} variants={fadeUp}>
              <div className="adm-section-header">
                <div className="adm-section-header-left">
                  <h2 className="adm-section-title"><BookOpen size={24}/> Topics</h2>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button className="adm-action-btn" onClick={refetch} title="Refresh Data"><RefreshCw size={18} /></button>
                  <button className="adm-fab" onClick={() => openDrawer('topic')}><Plus size={16}/> New Topic</button>
                </div>
              </div>
              <div className="adm-table-card">
                <div className="adm-table-wrap">
                  <table className="adm-table">
                    <thead>
                      <tr><th>Topic</th><th>Track</th><th>Order</th><th>Questions</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {allTopics.length === 0 && <tr><td colSpan="5"><EmptyState icon={BookOpen} title="No Topics" desc="Topics belong to Tracks."/></td></tr>}
                      {allTopics.map(t => (
                        <tr key={t.id}>
                          <td>
                            <span className="adm-table__primary">{t.name}</span>
                          </td>
                          <td><span className="adm-table__badge adm-badge--indigo">{t.track_name}</span></td>
                          <td><span className="adm-table__secondary">#{t.order}</span></td>
                          <td><span className="adm-table__badge">{t.question_count}</span></td>
                          <td>
                            <div className="adm-row-actions">
                              <button className="adm-action-btn" onClick={() => openViewer('topic', t)}><Eye size={16}/></button>
                              <button className="adm-action-btn" onClick={() => openDrawer('topic', t)}><Pencil size={16}/></button>
                              <button className="adm-action-btn adm-action-btn--danger" onClick={() => deleteItem('topic', t.id, t.name)}><Trash2 size={16}/></button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}

          {/* ════════════════════════════════════════════════════════════════════
              QUESTIONS TAB
              ════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'questions' && (
            <motion.div key="questions" initial="hidden" animate="show" exit={{ opacity: 0 }} variants={fadeUp}>
              <div className="adm-section-header">
                <div className="adm-section-header-left">
                  <h2 className="adm-section-title"><Layers size={24}/> Questions Bank</h2>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button className="adm-action-btn" onClick={refetch} title="Refresh Data"><RefreshCw size={18} /></button>
                  <button className="adm-fab" onClick={() => openDrawer('question')}><Plus size={16}/> New Question</button>
                </div>
              </div>
              <div className="adm-table-card">
                <div className="adm-table-wrap">
                  <table className="adm-table">
                    <thead>
                      <tr><th>Question</th><th>Path (Track &gt; Topic)</th><th>Difficulty</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {questions.length === 0 && <tr><td colSpan="4"><EmptyState icon={Layers} title="Question Bank Empty" desc="Add questions to populate mock tests."/></td></tr>}
                      {questions.map(q => (
                        <tr key={q.id}>
                          <td>
                            <span className="adm-table__primary" style={{ maxWidth: 400, display: 'inline-block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{q.question_text}</span>
                          </td>
                          <td><span className="adm-table__secondary">{q.track} &gt; {q.topic}</span></td>
                          <td>
                            <span className={`adm-table__badge ${
                              q.difficulty === 'hard' ? 'adm-badge--red' :
                              q.difficulty === 'medium' ? 'adm-badge--amber' :
                              'adm-badge--green'
                            }`}>{q.difficulty}</span>
                          </td>
                          <td>
                            <div className="adm-row-actions">
                              <button className="adm-action-btn" onClick={() => openViewer('question', q)}><Eye size={16}/></button>
                              <button className="adm-action-btn" onClick={() => openDrawer('question', q)}><Pencil size={16}/></button>
                              <button className="adm-action-btn adm-action-btn--danger" onClick={() => deleteItem('question', q.id, "Question")}><Trash2 size={16}/></button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}

          {/* ════════════════════════════════════════════════════════════════════
              TESTS TAB
              ════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'tests' && (
            <motion.div key="tests" initial="hidden" animate="show" exit={{ opacity: 0 }} variants={fadeUp}>
              <div className="adm-section-header">
                <div className="adm-section-header-left">
                  <h2 className="adm-section-title"><ClipboardList size={24}/> Mock Tests</h2>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button className="adm-action-btn" onClick={refetch} title="Refresh Data"><RefreshCw size={18} /></button>
                  <button className="adm-fab" onClick={() => openDrawer('test')}><Plus size={16}/> New Test</button>
                </div>
              </div>
              <div className="adm-table-card">
                <div className="adm-table-wrap">
                  <table className="adm-table">
                    <thead>
                      <tr><th>Test Name</th><th>Duration</th><th>Topics Covered</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {tests.length === 0 && <tr><td colSpan="4"><EmptyState icon={ClipboardList} title="No Tests" desc="Assemble topics into a mock test."/></td></tr>}
                      {tests.map(t => (
                        <tr key={t.id}>
                          <td>
                            <span className="adm-table__primary">{t.name}</span>
                            <span className="adm-table__secondary">{t.description}</span>
                          </td>
                          <td><span className="adm-table__secondary">{t.duration_minutes} mins</span></td>
                          <td><span className="adm-table__badge adm-badge--indigo">{t.topics_count} Topics</span></td>
                          <td>
                            <div className="adm-row-actions">
                              <button className="adm-action-btn" onClick={() => openViewer('test', t)}><Eye size={16}/></button>
                              <button className="adm-action-btn" onClick={() => openDrawer('test', t)}><Pencil size={16}/></button>
                              <button className="adm-action-btn adm-action-btn--danger" onClick={() => deleteItem('test', t.id, t.name)}><Trash2 size={16}/></button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}

          {/* ════════════════════════════════════════════════════════════════════
              COMPANIES TAB
              ════════════════════════════════════════════════════════════════════ */}
          {activeTab === 'companies' && (
            <motion.div key="companies" initial="hidden" animate="show" exit={{ opacity: 0 }} variants={fadeUp}>
              <div className="adm-section-header">
                <div className="adm-section-header-left">
                  <h2 className="adm-section-title"><Building2 size={24}/> Company Targets</h2>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button className="adm-action-btn" onClick={refetch} title="Refresh Data"><RefreshCw size={18} /></button>
                  <button className="adm-fab" onClick={() => openDrawer('company')}><Plus size={16}/> Add Target</button>
                </div>
              </div>
              <div className="adm-table-card">
                <div className="adm-table-wrap">
                  <table className="adm-table">
                    <thead>
                      <tr><th>Company</th><th>Assigned User</th><th>Readiness Score</th><th>Focus Area</th><th>Actions</th></tr>
                    </thead>
                    <tbody>
                      {company_targets.length === 0 && <tr><td colSpan="5"><EmptyState icon={Building2} title="No Company Targets" desc="Assign company goals to users."/></td></tr>}
                      {company_targets.map(c => (
                        <tr key={c.id} style={{ opacity: c.is_active ? 1 : 0.6 }}>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                              <span className="adm-table__primary" style={{ marginBottom: 0 }}>{c.name}</span>
                              {!c.is_active && <span className="adm-table__badge adm-badge--red" style={{ padding: '2px 8px', fontSize: '0.65rem' }}>Archived</span>}
                            </div>
                          </td>
                          <td>
                            <div className="adm-user-cell">
                              <div className="adm-avatar">{getInitials(c.user)}</div>
                              <div>
                                <span className="adm-table__primary">{c.user}</span>
                                <span className="adm-table__secondary">{c.email}</span>
                              </div>
                            </div>
                          </td>
                          <td>
                            <div style={{ width: 100, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 4, overflow: 'hidden' }}>
                              <div style={{ width: `${c.readiness}%`, height: '100%', background: c.readiness > 70 ? '#10b981' : c.readiness > 40 ? '#f59e0b' : '#ef4444' }}/>
                            </div>
                            <span className="adm-table__secondary" style={{ display: 'block', marginTop: 6, fontWeight: 700 }}>{c.readiness}%</span>
                          </td>
                          <td><span className="adm-table__secondary">{c.focus}</span></td>
                          <td>
                            <div className="adm-row-actions">
                              <button className="adm-action-btn" onClick={() => openViewer('company', c)}><Eye size={16}/></button>
                              <button className="adm-action-btn" onClick={() => openDrawer('company', c)}><Pencil size={16}/></button>
                              <button className="adm-action-btn adm-action-btn--danger" onClick={() => deleteItem('company', c.id, c.name)}><Trash2 size={16}/></button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </motion.div>
          )}

        </AnimatePresence>

        {/* ════════════════════════════════════════════════════════════════════
            GLOBAL SLIDE-OVER DRAWER (FORMS)
            ════════════════════════════════════════════════════════════════════ */}
        <SlideOverDrawer 
          isOpen={drawerOpen} 
          onClose={closeDrawer} 
          title={viewing.item ? `${viewing.type.charAt(0).toUpperCase() + viewing.type.slice(1)} Details` : (editing.id ? `Edit ${editing.type}` : `New ${editing.type}`)}
          footer={
            !viewing.item && (
              <>
                <Button variant="ghost" onClick={closeDrawer}>Cancel</Button>
                <Button variant="primary" onClick={() => saveContent(editing.type || Object.keys(forms).find(k => forms[k].name !== undefined && forms[k].name !== '' || k === 'question'))} loading={!!saving}>Save Changes</Button>
              </>
            )
          }
        >
          {viewing.item ? (
            <div className="adm-data-viewer" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Object.entries(viewing.item).map(([key, value]) => (
                <div key={key} style={{ background: 'var(--bg-secondary)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-primary)' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{key.replace(/_/g, ' ')}</div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', wordBreak: 'break-word', whiteSpace: 'pre-wrap', fontFamily: typeof value === 'object' ? 'monospace' : 'inherit' }}>
                    {typeof value === 'object' && value !== null ? JSON.stringify(value, null, 2) : String(value)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <>
          
          {editing.type === 'track' && (
            <div className="adm-form">
              <div className="adm-field">
                <label>Track Name</label>
                <input className="adm-input" value={forms.track.name} onChange={e => updateForm('track', { name: e.target.value })} placeholder="e.g. Frontend Engineering" />
              </div>
              <div className="adm-field">
                <label>Description</label>
                <textarea className="adm-input adm-input--multiselect" value={forms.track.description} onChange={e => updateForm('track', { description: e.target.value })} placeholder="Detailed curriculum path description..." />
              </div>
            </div>
          )}

          {editing.type === 'topic' && (
            <div className="adm-form">
              <div className="adm-field">
                <label>Parent Track</label>
                <select className="adm-input" value={forms.topic.track_id} onChange={e => updateForm('topic', { track_id: e.target.value })}>
                  <option value="">Select Track</option>
                  {tracks.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
              </div>
              <div className="adm-field">
                <label>Topic Name</label>
                <input className="adm-input" value={forms.topic.name} onChange={e => updateForm('topic', { name: e.target.value })} placeholder="e.g. React Hooks" />
              </div>
              <div className="adm-field">
                <label>Description</label>
                <textarea className="adm-input adm-input--multiselect" value={forms.topic.description} onChange={e => updateForm('topic', { description: e.target.value })} />
              </div>
              <div className="adm-field">
                <label>Order / Sequence</label>
                <input type="number" className="adm-input" value={forms.topic.order} onChange={e => updateForm('topic', { order: e.target.value })} placeholder="1" />
              </div>
            </div>
          )}

          {editing.type === 'question' && (
            <div className="adm-form" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="adm-field">
                <label>Parent Topic</label>
                <select className="adm-input" value={forms.question.topic_id} onChange={e => updateForm('question', { topic_id: e.target.value })}>
                  <option value="">Select Topic</option>
                  {allTopics.map(t => <option key={t.id} value={t.id}>{t.track_name} &gt; {t.name}</option>)}
                </select>
              </div>
              <div className="adm-field">
                <label>Question Text</label>
                <textarea className="adm-input adm-input--multiselect" value={forms.question.question_text} onChange={e => updateForm('question', { question_text: e.target.value })} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div className="adm-field"><label>Option A</label><input className="adm-input" value={forms.question.option_a} onChange={e => updateForm('question', { option_a: e.target.value })} /></div>
                <div className="adm-field"><label>Option B</label><input className="adm-input" value={forms.question.option_b} onChange={e => updateForm('question', { option_b: e.target.value })} /></div>
                <div className="adm-field"><label>Option C</label><input className="adm-input" value={forms.question.option_c} onChange={e => updateForm('question', { option_c: e.target.value })} /></div>
                <div className="adm-field"><label>Option D</label><input className="adm-input" value={forms.question.option_d} onChange={e => updateForm('question', { option_d: e.target.value })} /></div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div className="adm-field">
                  <label>Correct Answer</label>
                  <select className="adm-input" value={forms.question.correct_answer} onChange={e => updateForm('question', { correct_answer: e.target.value })}>
                    <option value="A">A</option><option value="B">B</option><option value="C">C</option><option value="D">D</option>
                  </select>
                </div>
                <div className="adm-field">
                  <label>Difficulty</label>
                  <select className="adm-input" value={forms.question.difficulty} onChange={e => updateForm('question', { difficulty: e.target.value })}>
                    <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {editing.type === 'test' && (
            <div className="adm-form">
              <div className="adm-field">
                <label>Test Name</label>
                <input className="adm-input" value={forms.test.name} onChange={e => updateForm('test', { name: e.target.value })} placeholder="e.g. SDE-1 Assessment" />
              </div>
              <div className="adm-field">
                <label>Description</label>
                <textarea className="adm-input" value={forms.test.description} onChange={e => updateForm('test', { description: e.target.value })} />
              </div>
              <div className="adm-field">
                <label>Duration (Minutes)</label>
                <input type="number" className="adm-input" value={forms.test.duration_minutes} onChange={e => updateForm('test', { duration_minutes: e.target.value })} />
              </div>
              <div className="adm-field">
                <label>Topics Included (Select Multiple)</label>
                <select multiple className="adm-input adm-input--multiselect" value={forms.test.topic_ids} onChange={e => updateForm('test', { topic_ids: Array.from(e.target.selectedOptions, o => o.value) })}>
                  {allTopics.map(t => <option key={t.id} value={t.id}>{t.track_name} &gt; {t.name}</option>)}
                </select>
              </div>
            </div>
          )}

          {editing.type === 'company' && (
            <div className="adm-form">
              {!editing.id && (
                <div className="adm-field">
                  <label>Assign to User</label>
                  <select className="adm-input" value={forms.company.user_id} onChange={e => updateForm('company', { user_id: e.target.value })}>
                    <option value="">Select User</option>
                    {users.map(u => <option key={u.id} value={u.id}>{u.name} ({u.email})</option>)}
                  </select>
                </div>
              )}
              <div className="adm-field">
                <label>Company Name</label>
                <input className="adm-input" value={forms.company.name} onChange={e => updateForm('company', { name: e.target.value })} placeholder="e.g. Google" disabled={!!editing.id} />
              </div>
              <div className="adm-field">
                <label>Preparation Focus Area</label>
                <input className="adm-input" value={forms.company.focus} onChange={e => updateForm('company', { focus: e.target.value })} placeholder="e.g. System Design, Graphs" />
              </div>
              <div className="adm-field">
                <label>Readiness Override (0-100)</label>
                <input type="number" className="adm-input" value={forms.company.readiness} onChange={e => updateForm('company', { readiness: e.target.value })} />
              </div>
            </div>
          )}
          </>
          )}
        </SlideOverDrawer>
      </div>
    </Layout>
  );
}
