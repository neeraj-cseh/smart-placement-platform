import { useState, useEffect } from 'react';
import { api } from '../api/client';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mail, 
  GraduationCap, 
  Building, 
  Phone, 
  ExternalLink as Linkedin, 
  GitBranch as Github, 
  Globe, 
  Save, 
  User, 
  Briefcase, 
  AlertCircle, 
  CheckCircle 
} from 'lucide-react';
import './profile.css';

const fadeUp = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
};

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } }
};

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [form, setForm] = useState({});
  const [fieldErrors, setFieldErrors] = useState({});

  useEffect(() => {
    api.get('/auth/profile/').then(d => {
      setProfile(d);
      setForm(d);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    // Clear field error on change
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const errors = {};
    
    // CGPA Validation
    if (form.cgpa && (isNaN(form.cgpa) || parseFloat(form.cgpa) < 0 || parseFloat(form.cgpa) > 10)) {
      errors.cgpa = "CGPA must be between 0.0 and 10.0";
    }

    // Graduation Year Validation
    if (form.graduation_year && (!/^\d{4}$/.test(form.graduation_year) || parseInt(form.graduation_year) < 1900 || parseInt(form.graduation_year) > 2100)) {
      errors.graduation_year = "Enter a valid 4-digit graduation year";
    }

    // URL Validations
    const urlPattern = /^(https?:\/\/)?([\w\d-]+\.)+\w{2,}(\/.*)?$/i;
    if (form.linkedin_url && !urlPattern.test(form.linkedin_url)) {
      errors.linkedin_url = "Enter a valid URL";
    }
    if (form.github_url && !urlPattern.test(form.github_url)) {
      errors.github_url = "Enter a valid URL";
    }
    if (form.portfolio_url && !urlPattern.test(form.portfolio_url)) {
      errors.portfolio_url = "Enter a valid URL";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      setError("Please fix the validation errors before saving.");
      setSuccess('');
      return;
    }

    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await api.put('/auth/profile/', form);
      setSuccess('Profile updated successfully! Your credentials are now synced.');
      // Auto-hide success after 4s
      setTimeout(() => setSuccess(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="skeleton skeleton--card" />;

  const hasChanges = JSON.stringify(form) !== JSON.stringify(profile);

  const renderField = (f) => {
    const hasError = !!fieldErrors[f.name];
    return (
      <div key={f.name} className={`profile__field ${f.fullWidth ? 'profile__field--full' : ''} ${hasError ? 'profile__field--error' : ''}`}>
        <label htmlFor={f.name}>{f.label}</label>
        <div className={`profile__input-wrapper ${f.icon ? 'profile__input-wrapper--has-icon' : ''}`}>
          {f.icon && <f.icon size={16} className="profile__field-icon" />}
          {f.type === 'textarea' ? (
            <textarea
              id={f.name}
              name={f.name}
              rows={f.rows || 3}
              placeholder={f.placeholder}
              value={form[f.name] || ''}
              onChange={handleChange}
            />
          ) : (
            <input
              id={f.name}
              name={f.name}
              type={f.type || 'text'}
              placeholder={f.placeholder}
              value={form[f.name] || ''}
              onChange={handleChange}
            />
          )}
        </div>
        {hasError && <span className="profile__field-error-text">{fieldErrors[f.name]}</span>}
      </div>
    );
  };

  return (
    <motion.div variants={stagger} initial="hidden" animate="show">
      <Card>
        {/* HEADER */}
        <motion.div variants={fadeUp} className="profile__header">
          <div className="profile__avatar-large">
            {form?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'U'}
          </div>
          <div className="profile__header-text">
            <h2>{form.name || 'Your Profile'}</h2>
            <p>
              <Mail size={14} />
              {form.email}
            </p>
          </div>
        </motion.div>

        {/* NOTIFICATIONS */}
        <AnimatePresence>
          {error && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="profile__error-banner">
              <AlertCircle size={16} /> {error}
            </motion.div>
          )}
          {success && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="profile__success-banner">
              <CheckCircle size={16} /> {success}
            </motion.div>
          )}
        </AnimatePresence>

        {/* SECTION 1: PERSONAL INFO */}
        <motion.div variants={fadeUp} className="profile__section">
          <div className="profile__section-header">
            <User size={18} className="profile__section-icon" />
            <h3 className="profile__section-title">Personal Information</h3>
          </div>
          <div className="profile__section-content profile__grid">
            {renderField({ name: 'name', label: 'Full Name', placeholder: 'John Doe', type: 'text' })}
            {renderField({ name: 'preferred_role', label: 'Target Role', placeholder: 'e.g. Frontend Engineer', type: 'text' })}
            {renderField({ name: 'location', label: 'Location', placeholder: 'City, Country', type: 'text' })}
            {renderField({ name: 'phone', label: 'Phone Number', icon: Phone, placeholder: '+1 234 567 8900', type: 'tel' })}
          </div>
        </motion.div>

        {/* SECTION 2: EDUCATION */}
        <motion.div variants={fadeUp} className="profile__section">
          <div className="profile__section-header">
            <GraduationCap size={18} className="profile__section-icon" />
            <h3 className="profile__section-title">Academic Background</h3>
          </div>
          <div className="profile__section-content profile__grid">
            {renderField({ name: 'degree', label: 'Degree', placeholder: 'e.g. B.Tech', type: 'text' })}
            {renderField({ name: 'branch', label: 'Field of Study (Branch)', placeholder: 'Computer Science', type: 'text' })}
            {renderField({ name: 'college', label: 'Institution / College', icon: Building, placeholder: 'University Name', type: 'text', fullWidth: true })}
            {renderField({ name: 'graduation_year', label: 'Graduation Year', placeholder: '2026', type: 'number' })}
            {renderField({ name: 'cgpa', label: 'CGPA', placeholder: 'e.g. 8.5', type: 'number', step: '0.01' })}
          </div>
        </motion.div>

        {/* SECTION 3: PROFESSIONAL PRESENCE */}
        <motion.div variants={fadeUp} className="profile__section">
          <div className="profile__section-header">
            <Briefcase size={18} className="profile__section-icon" />
            <h3 className="profile__section-title">Professional Presence</h3>
          </div>
          <div className="profile__section-content profile__grid">
            {renderField({ name: 'resume_headline', label: 'Resume Headline', placeholder: 'Passionate software engineer building scalable systems', type: 'text', fullWidth: true })}
            {renderField({ name: 'linkedin_url', label: 'LinkedIn URL', icon: Linkedin, placeholder: 'https://linkedin.com/in/username', type: 'url' })}
            {renderField({ name: 'github_url', label: 'GitHub URL', icon: Github, placeholder: 'https://github.com/username', type: 'url' })}
            {renderField({ name: 'portfolio_url', label: 'Portfolio URL', icon: Globe, placeholder: 'https://yourwebsite.com', type: 'url' })}
            {renderField({ name: 'bio', label: 'Professional Summary', placeholder: 'Tell recruiters about your journey, skills, and goals...', type: 'textarea', rows: 4, fullWidth: true })}
          </div>
        </motion.div>

        {/* FOOTER */}
        <motion.div variants={fadeUp} className="profile__footer">
          {hasChanges && (
            <Button variant="secondary" onClick={() => { setForm(profile); setFieldErrors({}); setError(''); setSuccess(''); }}>
              Discard Changes
            </Button>
          )}
          <Button variant="primary" onClick={handleSave} loading={saving} icon={Save} disabled={!hasChanges}>
            Save Profile Changes
          </Button>
        </motion.div>

      </Card>
    </motion.div>
  );
}
