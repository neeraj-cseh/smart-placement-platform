import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sun, Moon, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import Button from '../components/ui/Button';
import './auth.css';

function AuthPage({ mode: initialMode = 'login' }) {
  const { login, register } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const [mode, setMode] = useState(initialMode);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    branch: '',
    college: '',
    degree: '',
    graduation_year: '',
    cgpa: '',
    preferred_role: '',
  });

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (mode === 'login') {
        await login(form.email, form.password);
      } else {
        const payload = {
          email: form.email,
          name: form.name,
          password: form.password,
        };
        if (form.branch) payload.branch = form.branch;
        if (form.college) payload.college = form.college;
        if (form.degree) payload.degree = form.degree;
        if (form.graduation_year) payload.graduation_year = parseInt(form.graduation_year);
        if (form.cgpa) payload.cgpa = parseFloat(form.cgpa);
        if (form.preferred_role) payload.preferred_role = form.preferred_role;
        await register(payload);
      }
      navigate('/');
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <header className="auth-page__header">
        <Link to="/" className="auth-page__logo">
          <span className="auth-page__logo-icon">PS</span>
          <span>PrepSmart</span>
        </Link>
        <button className="auth-page__theme-btn" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </header>

      <div className="auth-page__container">
        <div className="auth-page__card">
          <div className="auth-page__tabs">
            <button
              className={`auth-page__tab ${mode === 'login' ? 'auth-page__tab--active' : ''}`}
              onClick={() => setMode('login')}
            >
              Sign in
            </button>
            <button
              className={`auth-page__tab ${mode === 'signup' ? 'auth-page__tab--active' : ''}`}
              onClick={() => setMode('signup')}
            >
              Create account
            </button>
          </div>

          {error && (
            <div className="auth-page__error" role="alert">
              {error}
            </div>
          )}

          <form className="auth-page__form" onSubmit={handleSubmit}>
            {mode === 'signup' && (
              <div className="auth-page__field">
                <label htmlFor="name">Full name</label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  placeholder="John Doe"
                  value={form.name}
                  onChange={handleChange}
                />
              </div>
            )}

            <div className="auth-page__field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
              />
            </div>

            <div className="auth-page__field">
              <label htmlFor="password">Password</label>
              <div className="auth-page__password-wrap">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  minLength={8}
                  placeholder="Password"
                  value={form.password}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="auth-page__eye-btn"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {mode === 'signup' && (
              <>
                <div className="auth-page__row">
                  <div className="auth-page__field">
                    <label htmlFor="branch">Branch</label>
                    <input
                      id="branch"
                      name="branch"
                      type="text"
                      placeholder="CSE"
                      value={form.branch}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="auth-page__field">
                    <label htmlFor="college">College</label>
                    <input
                      id="college"
                      name="college"
                      type="text"
                      placeholder="MIT"
                      value={form.college}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="auth-page__row">
                  <div className="auth-page__field">
                    <label htmlFor="cgpa">CGPA</label>
                    <input
                      id="cgpa"
                      name="cgpa"
                      type="number"
                      min="0"
                      max="10"
                      step="0.01"
                      placeholder="8.5"
                      value={form.cgpa}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="auth-page__field">
                    <label htmlFor="graduation_year">Grad Year</label>
                    <input
                      id="graduation_year"
                      name="graduation_year"
                      type="number"
                      min="2020"
                      max="2035"
                      placeholder="2026"
                      value={form.graduation_year}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="auth-page__field">
                  <label htmlFor="preferred_role">Target Role</label>
                  <input
                    id="preferred_role"
                    name="preferred_role"
                    type="text"
                    placeholder="Software Engineer"
                    value={form.preferred_role}
                    onChange={handleChange}
                  />
                </div>
              </>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="auth-page__submit"
            >
              {mode === 'login' ? 'Sign in' : 'Create account'}
            </Button>
          </form>

          <p className="auth-page__switch">
            {mode === 'login' ? (
              <>Don't have an account? <button onClick={() => setMode('signup')}>Sign up</button></>
            ) : (
              <>Already have an account? <button onClick={() => setMode('login')}>Sign in</button></>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}

export default AuthPage;
