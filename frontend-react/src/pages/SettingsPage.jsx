import { useState, useEffect } from 'react';
import { api } from '../api/client';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Save, Lock } from 'lucide-react';
import './profile.css';
import './settings.css';

function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [passwordForm, setPasswordForm] = useState({ old_password: '', new_password: '', confirm_password: '' });
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');

  useEffect(() => {
    api.get('/auth/settings/').then(d => {
      setSettings(d);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleChange = (e) => {
    const val = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setSettings(prev => ({ ...prev, [e.target.name]: val }));
  };

  const handlePasswordChange = (e) => {
    setPasswordForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await api.put('/auth/settings/', settings);
      setSuccess('Settings updated successfully');
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.message || 'Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange_Submit = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setPasswordError('New passwords do not match');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      return;
    }

    try {
      await api.put('/auth/change-password/', {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      });
      setPasswordSuccess('Password changed successfully');
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' });
      setTimeout(() => {
        setPasswordSuccess('');
        setShowPasswordForm(false);
      }, 3000);
    } catch (err) {
      setPasswordError(err.message || 'Failed to change password');
    }
  };

  if (loading) return <Layout title="Settings"><div className="skeleton skeleton--card" /></Layout>;

  return (
    <Layout title="Settings" subtitle="Manage your account and preferences">
      <div className="profile__grid" style={{ alignItems: 'start' }}>
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* General Settings */}
        <Card>
          {error && <div className="profile__error">{error}</div>}
          {success && <div className="profile__success">{success}</div>}

          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: 16 }}>Account Settings</h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)' }}>Account</h3>
              <div className="profile__field">
                <label>Full Name</label>
                <input name="name" value={settings.name || ''} onChange={handleChange} placeholder="Your full name" />
              </div>
              <div className="profile__field" style={{ marginTop: 12 }}>
                <label>Email</label>
                <input type="email" value={settings.email || ''} disabled style={{ background: 'var(--bg-disabled)', cursor: 'not-allowed' }} />
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>Email cannot be changed</p>
              </div>
            </div>

            <div style={{ borderTop: '1px solid var(--border-primary)', paddingTop: 16 }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)' }}>Goals & Preferences</h3>
              <div className="profile__field">
                <label>Weekly Goal Hours</label>
                <input name="weekly_goal_hours" type="number" min="1" max="80" value={settings.weekly_goal_hours || ''} onChange={handleChange} placeholder="e.g., 20" />
              </div>
              <div className="profile__field" style={{ marginTop: 12 }}>
                <label>Preferred Language</label>
                <select name="preferred_language" value={settings.preferred_language || 'en'} onChange={handleChange}>
                  <option value="en">English</option>
                  <option value="hi">Hindi</option>
                </select>
              </div>
            </div>

            </div>
          <Button variant="primary" onClick={handleSave} loading={saving} icon={Save} style={{ marginTop: 20 }}>
            Save Profile Settings
          </Button>
        </Card>
        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <Card>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: 16 }}>Preferences</h2>
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)' }}>Notifications</h3>
              <label className="profile__toggle">
                <input name="email_notifications" type="checkbox" checked={settings.email_notifications || false} onChange={handleChange} />
                <span>Email Notifications</span>
              </label>
              <label className="profile__toggle" style={{ marginTop: 10 }}>
                <input name="product_updates" type="checkbox" checked={settings.product_updates || false} onChange={handleChange} />
                <span>Product Updates & News</span>
              </label>
              <label className="profile__toggle" style={{ marginTop: 10 }}>
                <input name="interview_reminders" type="checkbox" checked={settings.interview_reminders || false} onChange={handleChange} />
                <span>Interview Reminders</span>
              </label>
              <label className="profile__toggle" style={{ marginTop: 10 }}>
                <input name="practice_suggestions" type="checkbox" checked={settings.practice_suggestions || false} onChange={handleChange} />
                <span>Practice Suggestions</span>
              </label>
            </div>

            <div style={{ borderTop: '1px solid var(--border-primary)', paddingTop: 16 }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)' }}>Privacy</h3>
              <label className="profile__toggle">
                <input name="profile_public" type="checkbox" checked={settings.profile_public || false} onChange={handleChange} />
                <span>Make Profile Public</span>
              </label>
              <label className="profile__toggle" style={{ marginTop: 10 }}>
                <input name="show_activity" type="checkbox" checked={settings.show_activity || false} onChange={handleChange} />
                <span>Show Activity to Others</span>
              </label>
            </div>

          <Button variant="primary" onClick={handleSave} loading={saving} icon={Save} style={{ marginTop: 20 }}>
            Save Preferences
          </Button>
        </Card>

        {/* Password Change */}
        <Card>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: 16 }}>Security</h2>

          {!showPasswordForm ? (
            <Button variant="secondary" onClick={() => setShowPasswordForm(true)} icon={Lock}>
              Change Password
            </Button>
          ) : (
            <form onSubmit={handlePasswordChange_Submit}>
              {passwordError && <div className="profile__error" style={{ marginBottom: 12 }}>{passwordError}</div>}
              {passwordSuccess && <div className="profile__success" style={{ marginBottom: 12 }}>{passwordSuccess}</div>}

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div className="profile__field">
                  <label>Current Password</label>
                  <input
                    type="password"
                    name="old_password"
                    value={passwordForm.old_password}
                    onChange={handlePasswordChange}
                    placeholder="Enter your current password"
                    required
                  />
                </div>
                <div className="profile__field">
                  <label>New Password</label>
                  <input
                    type="password"
                    name="new_password"
                    value={passwordForm.new_password}
                    onChange={handlePasswordChange}
                    placeholder="Enter new password (min 8 characters)"
                    required
                  />
                </div>
                <div className="profile__field">
                  <label>Confirm New Password</label>
                  <input
                    type="password"
                    name="confirm_password"
                    value={passwordForm.confirm_password}
                    onChange={handlePasswordChange}
                    placeholder="Confirm new password"
                    required
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
                <Button variant="primary" type="submit">Update Password</Button>
                <Button variant="secondary" onClick={() => setShowPasswordForm(false)} type="button">Cancel</Button>
              </div>
            </form>
          )}
        </Card>
        </div>
      </div>
    </Layout>
  );
}

export default SettingsPage;
