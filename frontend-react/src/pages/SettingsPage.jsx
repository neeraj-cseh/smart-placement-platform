import { useState, useEffect } from 'react';
import { api } from '../api/client';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Save } from 'lucide-react';
import './profile.css';

function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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

  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await api.put('/auth/settings/', settings);
      setSuccess('Settings updated');
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Layout title="Settings"><div className="skeleton skeleton--card" /></Layout>;

  return (
    <Layout title="Settings" subtitle="Manage your account preferences">
      <Card style={{ maxWidth: 600 }}>
        {error && <div className="profile__error">{error}</div>}
        {success && <div className="profile__success">{success}</div>}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>Account</h3>
            <div className="profile__field">
              <label>Name</label>
              <input name="name" value={settings.name || ''} onChange={handleChange} />
            </div>
          </div>

          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>Goals</h3>
            <div className="profile__field">
              <label>Weekly goal hours</label>
              <input name="weekly_goal_hours" type="number" min="1" max="80" value={settings.weekly_goal_hours || ''} onChange={handleChange} />
            </div>
          </div>

          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>Notifications</h3>
            <label className="profile__toggle">
              <input name="email_notifications" type="checkbox" checked={settings.email_notifications || false} onChange={handleChange} />
              <span>Email notifications</span>
            </label>
            <label className="profile__toggle">
              <input name="product_updates" type="checkbox" checked={settings.product_updates || false} onChange={handleChange} />
              <span>Product updates</span>
            </label>
          </div>

          <Button variant="primary" onClick={handleSave} loading={saving} icon={Save}>
            Save settings
          </Button>
        </div>
      </Card>
    </Layout>
  );
}

export default SettingsPage;
