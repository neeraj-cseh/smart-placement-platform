import { useState, useEffect } from 'react';
import { api } from '../api/client';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Mail, GraduationCap, Building, Phone, ExternalLink as Linkedin, GitBranch as Github, Globe, Save } from 'lucide-react';
import './profile.css';

function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({});

  useEffect(() => {
    api.get('/auth/profile/').then(d => {
      setProfile(d);
      setForm(d);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleChange = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await api.put('/auth/profile/', form);
      setSuccess('Profile updated successfully');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Layout title="Profile"><div className="skeleton skeleton--card" /></Layout>;

  const fields = [
    { name: 'branch', label: 'Branch', icon: GraduationCap, placeholder: 'Computer Science' },
    { name: 'college', label: 'College', icon: Building, placeholder: 'MIT' },
    { name: 'degree', label: 'Degree', icon: GraduationCap, placeholder: 'B.Tech' },
    { name: 'cgpa', label: 'CGPA', icon: null, placeholder: '8.5', type: 'number' },
    { name: 'graduation_year', label: 'Graduation Year', icon: null, placeholder: '2026', type: 'number' },
    { name: 'preferred_role', label: 'Target Role', icon: null, placeholder: 'Software Engineer' },
    { name: 'location', label: 'Location', icon: null, placeholder: 'Bengaluru' },
    { name: 'phone', label: 'Phone', icon: Phone, placeholder: '+91 9876543210' },
    { name: 'linkedin_url', label: 'LinkedIn', icon: Linkedin, placeholder: 'https://linkedin.com/in/...' },
    { name: 'github_url', label: 'GitHub', icon: Github, placeholder: 'https://github.com/...' },
    { name: 'portfolio_url', label: 'Portfolio', icon: Globe, placeholder: 'https://...' },
    { name: 'resume_headline', label: 'Resume Headline', icon: null, placeholder: 'Your professional headline' },
  ];

  return (
    <Layout title="Profile" subtitle="Manage your profile information">
      <Card>
        <div className="profile__header">
          <div className="profile__avatar-large">
            {profile?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'U'}
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{form.name || 'Your name'}</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              <Mail size={14} style={{ display: 'inline', marginRight: 4 }} />
              {form.email}
            </p>
          </div>
        </div>

        {error && <div className="profile__error">{error}</div>}
        {success && <div className="profile__success">{success}</div>}

        <div className="profile__grid">
          {fields.map(f => (
            <div key={f.name} className="profile__field">
              {f.icon && <f.icon size={16} className="profile__field-icon" />}
              <input
                name={f.name}
                type={f.type || 'text'}
                placeholder={f.placeholder}
                value={form[f.name] || ''}
                onChange={handleChange}
              />
            </div>
          ))}
        </div>

        <div className="profile__field" style={{ marginTop: 8 }}>
          <label htmlFor="bio">Bio</label>
          <textarea
            id="bio"
            name="bio"
            rows={3}
            placeholder="Tell us about yourself..."
            value={form.bio || ''}
            onChange={handleChange}
          />
        </div>

        <Button variant="primary" onClick={handleSave} loading={saving} icon={Save} style={{ marginTop: 16 }}>
          Save changes
        </Button>
      </Card>
    </Layout>
  );
}

export default ProfilePage;
