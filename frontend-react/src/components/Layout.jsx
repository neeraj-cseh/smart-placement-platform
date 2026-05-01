import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  BookOpenCheck,
  BriefcaseBusiness,
  Bot,
  Brain,
  Building2,
  CalendarCheck2,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Circle,
  Code2,
  Clock3,
  ExternalLink,
  FileText,
  Flame,
  LayoutDashboard,
  LineChart,
  ListChecks,
  LogIn,
  LogOut,
  Mail,
  MapPin,
  Pencil,
  Play,
  Plus,
  Search,
  RefreshCw,
  Route,
  Save,
  Settings,
  ShieldCheck,
  Target,
  TimerReset,
  Trash2,
  Trophy,
  UserPlus,
  UsersRound,
  X,
} from "lucide-react";
import "./layout.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";
const AUTH_STORAGE_KEYS = ["access", "refresh", "accessToken", "refreshToken", "authToken", "token"];

const navItems = [
  { label: "Dashboard", to: "/", icon: LayoutDashboard },
  { label: "Learning Path", to: "/learning-path", icon: Route },
  { label: "Practice", to: "/practice", icon: Brain },
  { label: "Mock Tests", to: "/mock-tests", icon: TimerReset },
  { label: "Code Editor", to: "/code-editor", icon: Code2 },
  { label: "AI Interview", to: "/ai-interview", icon: Bot },
  { label: "Analytics", to: "/analytics", icon: BarChart3 },
  { label: "Companies", to: "/companies", icon: Building2 },
];

const metricIcons = {
  target: Target,
  check: CheckCircle2,
  flame: Flame,
  line: LineChart,
};

function getStoredAccessToken() {
  return AUTH_STORAGE_KEYS.map((key) => localStorage.getItem(key) || sessionStorage.getItem(key)).find(Boolean);
}

function clearStoredAuth() {
  AUTH_STORAGE_KEYS.forEach((key) => {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  });
}

async function readApiPayload(response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    const compactText = text.replace(/\s+/g, " ").trim();
    const preview = compactText.slice(0, 120);
    throw new Error(
      preview.startsWith("<!DOCTYPE") || preview.startsWith("<html")
        ? `The API returned an HTML page instead of JSON. Check that Django is running at ${API_BASE_URL}.`
        : `The API returned invalid JSON: ${preview}`
    );
  }
}

async function apiFetch(path, options = {}) {
  const token = getStoredAccessToken();

  if (!token) {
    throw new Error("Please sign in again.");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  const payload = await readApiPayload(response);

  if (response.status === 401) {
    clearStoredAuth();
    throw new Error("Your session expired. Please log in again.");
  }

  if (!response.ok) {
    throw new Error(payload?.detail || payload?.error || JSON.stringify(payload));
  }

  return payload;
}

function ProgressBar({ value = 0, tone = "cyan" }) {
  return (
    <div className="progress" aria-label={`${value}%`}>
      <span className={`progress-value ${tone}`} style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
    </div>
  );
}

function EmptyState({ message }) {
  return <div className="empty-state">{message}</div>;
}

function Panel({ title, subtitle, action, onAction, children, className = "" }) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-header">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        {action ? (
          <button className="ghost-button" onClick={onAction} type="button">
            {action}
            <ChevronRight size={15} />
          </button>
        ) : null}
      </div>
      {children}
    </section>
  );
}

function MetricCard({ metric }) {
  const Icon = metricIcons[metric.icon] ?? Target;

  return (
    <article className="metric-card">
      <div className={`metric-icon ${metric.tone}`}>
        <Icon size={18} />
      </div>
      <div>
        <span>{metric.label}</span>
        <strong>{metric.value}</strong>
        <p>{metric.change}</p>
      </div>
    </article>
  );
}

function StatusPanel({ title, message, actionLabel, onAction }) {
  return (
    <section className="status-panel">
      <div>
        <h1>{title}</h1>
        <p>{message}</p>
      </div>
      {actionLabel ? (
        <button className="primary-button" onClick={onAction} type="button">
          {actionLabel}
        </button>
      ) : null}
    </section>
  );
}

function LandingPage() {
  const highlights = [
    "Adaptive learning paths",
    "Company readiness",
    "Practice analytics",
    "Admin control center",
  ];
  const featureCards = [
    {
      title: "Guided preparation",
      copy: "Daily plans, topic unlocks, revision queues, and mock signals stay connected to one preparation timeline.",
      icon: Route,
    },
    {
      title: "Company targeting",
      copy: "Track readiness for TCS, Infosys, Accenture, Zoho, and custom targets with official-source preparation notes.",
      icon: Building2,
    },
    {
      title: "Actionable analytics",
      copy: "Weak topics, accuracy movement, solved history, and interview readiness are surfaced where students act.",
      icon: BarChart3,
    },
    {
      title: "Admin governance",
      copy: "Admins can monitor students, activate accounts, seed catalog data, and manage readiness without database work.",
      icon: ShieldCheck,
    },
  ];

  return (
    <div className="landing-page">
      <header className="landing-header">
        <Link className="landing-brand" to="/">
          <span className="brand-mark">PS</span>
          <span>
            <strong>PrepSmart</strong>
            <small>Smart placement platform</small>
          </span>
        </Link>
        <nav aria-label="Landing navigation">
          <a href="#features">Features</a>
          <a href="#workflow">Workflow</a>
          <a href="#admin">Admin</a>
        </nav>
        <div className="landing-actions">
          <Link className="ghost-link-button" to="/login">
            <LogIn size={15} />
            Login
          </Link>
          <Link className="primary-link-button" to="/signup">
            <UserPlus size={15} />
            Sign up
          </Link>
        </div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-copy">
            <span className="eyebrow">Placement readiness, managed end to end</span>
            <h1>Prepare students for campus hiring with one connected workspace.</h1>
            <p>
              PrepSmart brings learning paths, practice, mock tests, analytics, company targets, profile readiness, and admin control into a single backend-backed platform.
            </p>
            <div className="landing-cta-row">
              <Link className="primary-link-button large" to="/signup">
                Start preparing
                <ArrowRight size={17} />
              </Link>
              <Link className="ghost-link-button large" to="/login">
                Login to dashboard
              </Link>
            </div>
            <div className="landing-highlight-row">
              {highlights.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </div>
          <div className="landing-product-panel" aria-label="PrepSmart product overview">
            <div className="product-panel-header">
              <span>Live readiness</span>
              <b>Corporate placement suite</b>
            </div>
            <div className="product-score-grid">
              <article>
                <strong>82%</strong>
                <span>Student readiness</span>
              </article>
              <article>
                <strong>214</strong>
                <span>Questions solved</span>
              </article>
              <article>
                <strong>18</strong>
                <span>Active company targets</span>
              </article>
            </div>
            <div className="product-flow-list">
              {["Admin verifies catalog", "Student opens drill popup", "Analytics updates weak topics"].map((item, index) => (
                <div key={item}>
                  <b>{`0${index + 1}`}</b>
                  <span>{item}</span>
                  <CheckCircle2 size={16} />
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="landing-section landing-proof" id="features">
          <div>
            <span className="eyebrow">What it contains</span>
            <h2>A complete landing-to-dashboard journey</h2>
          </div>
          <div className="landing-feature-grid">
            {featureCards.map((feature) => {
              const Icon = feature.icon;

              return (
                <article key={feature.title}>
                  <Icon size={20} />
                  <h3>{feature.title}</h3>
                  <p>{feature.copy}</p>
                </article>
              );
            })}
          </div>
        </section>

        <section className="landing-section landing-workflow" id="workflow">
          <div>
            <span className="eyebrow">Workflow</span>
            <h2>From signup to measurable readiness</h2>
          </div>
          <div className="workflow-steps">
            <article>
              <b>01</b>
              <strong>Create profile</strong>
              <span>Student details, skills, companies, links, and goals are captured during signup or profile editing.</span>
            </article>
            <article>
              <b>02</b>
              <strong>Follow the plan</strong>
              <span>Learning path, daily schedule, practice, mock tests, and revision all feed the same readiness score.</span>
            </article>
            <article>
              <b>03</b>
              <strong>Admin manages access</strong>
              <span>Staff accounts supervise users, catalog health, company readiness, and platform activity.</span>
            </article>
          </div>
        </section>

        <section className="landing-section landing-admin" id="admin">
          <div>
            <span className="eyebrow">Admin-ready</span>
            <h2>Admins get the control surface, students get the guided workspace.</h2>
            <p>
              Staff accounts can use the Django admin and the in-app admin page to review users, account state, learning content, companies, and platform activity.
            </p>
          </div>
          <Link className="primary-link-button large" to="/login">
            Open admin login
            <ShieldCheck size={17} />
          </Link>
        </section>
      </main>
    </div>
  );
}

function PublicAuthPage({ initialMode, onAuthenticated }) {
  return (
    <div className="public-auth-page">
      <header className="landing-header compact">
        <Link className="landing-brand" to="/">
          <span className="brand-mark">PS</span>
          <span>
            <strong>PrepSmart</strong>
            <small>Placement platform</small>
          </span>
        </Link>
        <div className="landing-actions">
          <Link className="ghost-link-button" to="/">
            Landing page
          </Link>
          <Link className="primary-link-button" to={initialMode === "signup" ? "/login" : "/signup"}>
            {initialMode === "signup" ? "Login" : "Sign up"}
          </Link>
        </div>
      </header>
      <AuthPanel
        key={initialMode}
        initialMode={initialMode}
        message={
          initialMode === "signup"
            ? "Create a student account. PrepSmart will seed a full placement dashboard, learning path, target company list, and practice history for testing."
            : "Login with a student or admin account to load the backend-powered dashboard and management tools."
        }
        onAuthenticated={onAuthenticated}
      />
    </div>
  );
}

function AuthPanel({ initialMode = "login", message, onAuthenticated }) {
  const [mode, setMode] = useState(initialMode);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [branch, setBranch] = useState("");
  const [cgpa, setCgpa] = useState("");
  const [targetCompanies, setTargetCompanies] = useState("");
  const [authError, setAuthError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isSignup = mode === "signup";

  function extractError(payload) {
    if (payload?.error) {
      return payload.error;
    }

    if (payload && typeof payload === "object") {
      const firstError = Object.values(payload).flat().find(Boolean);
      if (firstError) {
        return String(firstError);
      }
    }

    return isSignup ? "Unable to create account." : "Unable to sign in.";
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setAuthError("");

    const companies = targetCompanies
      .split(",")
      .map((company) => company.trim())
      .filter(Boolean);

    const body = isSignup
      ? {
          email,
          name,
          password,
          ...(branch ? { branch } : {}),
          ...(cgpa ? { cgpa: Number(cgpa) } : {}),
          ...(companies.length ? { target_companies: companies } : {}),
          has_backlog: false,
        }
      : { email, password };

    try {
      const response = await fetch(`${API_BASE_URL}/auth/${isSignup ? "register" : "login"}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const payload = await readApiPayload(response);

      if (!response.ok) {
        throw new Error(extractError(payload));
      }

      localStorage.setItem("access", payload.access);
      localStorage.setItem("refresh", payload.refresh);
      onAuthenticated?.(payload.user);
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="auth-panel">
      <div className="auth-copy">
        <span className="eyebrow">{isSignup ? "Create account" : "Backend protected"}</span>
        <h1>{isSignup ? "Start with a complete placement workspace" : "Sign in to load dashboard data"}</h1>
        <p>{message}</p>
      </div>

      <form className="auth-card" onSubmit={handleSubmit}>
        <div className="auth-mode-switch" role="tablist" aria-label="Authentication mode">
          <button
            aria-selected={!isSignup}
            className={!isSignup ? "active" : ""}
            onClick={() => {
              setMode("login");
              setAuthError("");
            }}
            role="tab"
            type="button"
          >
            <LogIn size={15} />
            Sign in
          </button>
          <button
            aria-selected={isSignup}
            className={isSignup ? "active" : ""}
            onClick={() => {
              setMode("signup");
              setAuthError("");
            }}
            role="tab"
            type="button"
          >
            <UserPlus size={15} />
            Sign up
          </button>
        </div>
        {isSignup ? (
          <label>
            Name
            <input autoComplete="name" onChange={(event) => setName(event.target.value)} required type="text" value={name} />
          </label>
        ) : null}
        <label>
          Email
          <input autoComplete="email" onChange={(event) => setEmail(event.target.value)} required type="email" value={email} />
        </label>
        <label>
          Password
          <input
            autoComplete="current-password"
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
        </label>
        {isSignup ? (
          <>
            <label>
              Branch
              <input
                autoComplete="organization-title"
                onChange={(event) => setBranch(event.target.value)}
                placeholder="Computer Science and Engineering"
                type="text"
                value={branch}
              />
            </label>
            <div className="auth-form-grid">
              <label>
                CGPA
                <input max="10" min="0" onChange={(event) => setCgpa(event.target.value)} step="0.01" type="number" value={cgpa} />
              </label>
              <label>
                Targets
                <input
                  onChange={(event) => setTargetCompanies(event.target.value)}
                  placeholder="TCS, Infosys, Accenture"
                  type="text"
                  value={targetCompanies}
                />
              </label>
            </div>
          </>
        ) : null}
        {authError ? <p className="form-error">{authError}</p> : null}
        <button className="primary-button" disabled={isSubmitting} type="submit">
          {isSubmitting ? (isSignup ? "Creating..." : "Signing in...") : isSignup ? "Create account" : "Sign in"}
        </button>
      </form>
    </section>
  );
}

function ProfileModal({ profile, onClose, onSaved }) {
  const [branch, setBranch] = useState(profile?.branch ?? "");
  const [college, setCollege] = useState(profile?.college ?? "");
  const [degree, setDegree] = useState(profile?.degree ?? "");
  const [graduationYear, setGraduationYear] = useState(profile?.graduation_year ?? "");
  const [cgpa, setCgpa] = useState(profile?.cgpa ?? "");
  const [hasBacklog, setHasBacklog] = useState(Boolean(profile?.has_backlog));
  const [location, setLocation] = useState(profile?.location ?? "");
  const [preferredRole, setPreferredRole] = useState(profile?.preferred_role ?? "");
  const [phone, setPhone] = useState(profile?.phone ?? "");
  const [linkedinUrl, setLinkedinUrl] = useState(profile?.linkedin_url ?? "");
  const [githubUrl, setGithubUrl] = useState(profile?.github_url ?? "");
  const [portfolioUrl, setPortfolioUrl] = useState(profile?.portfolio_url ?? "");
  const [resumeHeadline, setResumeHeadline] = useState(profile?.resume_headline ?? "");
  const [bio, setBio] = useState(profile?.bio ?? "");
  const [skills, setSkills] = useState((profile?.skills ?? []).join(", "));
  const [targetCompanies, setTargetCompanies] = useState((profile?.target_companies ?? []).join(", "));
  const [formError, setFormError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSaving(true);
    setFormError("");

    try {
      await apiFetch("/auth/profile/", {
        method: "PUT",
        body: JSON.stringify({
          branch,
          college,
          degree,
          graduation_year: graduationYear === "" ? null : Number(graduationYear),
          cgpa: cgpa === "" ? null : Number(cgpa),
          has_backlog: hasBacklog,
          location,
          preferred_role: preferredRole,
          phone,
          linkedin_url: linkedinUrl,
          github_url: githubUrl,
          portfolio_url: portfolioUrl,
          resume_headline: resumeHeadline,
          bio,
          skills: skills
            .split(",")
            .map((skill) => skill.trim())
            .filter(Boolean),
          target_companies: targetCompanies
            .split(",")
            .map((company) => company.trim())
            .filter(Boolean),
        }),
      });

      onSaved();
    } catch (error) {
      setFormError(error.message);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section aria-labelledby="profile-modal-title" className="profile-modal" role="dialog">
        <div className="modal-header">
          <div>
            <span className="eyebrow">Profile</span>
            <h2 id="profile-modal-title">Edit profile</h2>
          </div>
          <button className="ghost-button" onClick={onClose} type="button">
            Close
          </button>
        </div>

        <form className="profile-form" onSubmit={handleSubmit}>
          <div className="form-grid two">
            <label>
              Branch
              <input onChange={(event) => setBranch(event.target.value)} required value={branch} />
            </label>
            <label>
              Preferred role
              <input onChange={(event) => setPreferredRole(event.target.value)} value={preferredRole} />
            </label>
          </div>
          <label>
            College
            <input onChange={(event) => setCollege(event.target.value)} value={college} />
          </label>
          <div className="form-grid three">
            <label>
              Degree
              <input onChange={(event) => setDegree(event.target.value)} value={degree} />
            </label>
            <label>
              Grad year
              <input min="2020" max="2035" onChange={(event) => setGraduationYear(event.target.value)} type="number" value={graduationYear} />
            </label>
            <label>
              CGPA
              <input max="10" min="0" onChange={(event) => setCgpa(event.target.value)} step="0.01" type="number" value={cgpa} />
            </label>
          </div>
          <div className="form-grid two">
            <label>
              Location
              <input onChange={(event) => setLocation(event.target.value)} value={location} />
            </label>
            <label>
              Phone
              <input onChange={(event) => setPhone(event.target.value)} value={phone} />
            </label>
          </div>
          <label>
            Resume headline
            <input onChange={(event) => setResumeHeadline(event.target.value)} value={resumeHeadline} />
          </label>
          <label>
            Bio
            <textarea onChange={(event) => setBio(event.target.value)} rows="3" value={bio} />
          </label>
          <div className="form-grid three">
            <label>
              LinkedIn
              <input onChange={(event) => setLinkedinUrl(event.target.value)} value={linkedinUrl} />
            </label>
            <label>
              GitHub
              <input onChange={(event) => setGithubUrl(event.target.value)} value={githubUrl} />
            </label>
            <label>
              Portfolio
              <input onChange={(event) => setPortfolioUrl(event.target.value)} value={portfolioUrl} />
            </label>
          </div>
          <label>
            Skills
            <input onChange={(event) => setSkills(event.target.value)} placeholder="Python, Django, React, SQL" value={skills} />
          </label>
          <label className="checkbox-field">
            <input checked={hasBacklog} onChange={(event) => setHasBacklog(event.target.checked)} type="checkbox" />
            Has active backlog
          </label>
          <label>
            Target companies
            <input onChange={(event) => setTargetCompanies(event.target.value)} placeholder="TCS, Infosys, Wipro" value={targetCompanies} />
          </label>
          {formError ? <p className="form-error">{formError}</p> : null}
          <div className="modal-actions">
            <button className="ghost-button" onClick={onClose} type="button">
              Cancel
            </button>
            <button className="primary-button" disabled={isSaving} type="submit">
              {isSaving ? "Saving..." : "Save profile"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

function AccountSettingsModal({ settings, onClose, onSaved }) {
  const [name, setName] = useState(settings?.name ?? "");
  const [weeklyGoalHours, setWeeklyGoalHours] = useState(settings?.weekly_goal_hours ?? 12);
  const [timezone, setTimezone] = useState(settings?.timezone ?? "Asia/Kolkata");
  const [emailNotifications, setEmailNotifications] = useState(Boolean(settings?.email_notifications));
  const [productUpdates, setProductUpdates] = useState(Boolean(settings?.product_updates));
  const [publicProfile, setPublicProfile] = useState(Boolean(settings?.public_profile));
  const [formError, setFormError] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSaving(true);
    setFormError("");

    try {
      await apiFetch("/auth/settings/", {
        method: "PUT",
        body: JSON.stringify({
          name,
          weekly_goal_hours: Number(weeklyGoalHours),
          timezone,
          email_notifications: emailNotifications,
          product_updates: productUpdates,
          public_profile: publicProfile,
        }),
      });
      onSaved();
    } catch (error) {
      setFormError(error.message);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section aria-labelledby="settings-modal-title" className="profile-modal" role="dialog">
        <div className="modal-header">
          <div>
            <span className="eyebrow">Account</span>
            <h2 id="settings-modal-title">Account settings</h2>
          </div>
          <button className="ghost-button" onClick={onClose} type="button">
            Close
          </button>
        </div>

        <form className="profile-form" onSubmit={handleSubmit}>
          <label>
            Display name
            <input onChange={(event) => setName(event.target.value)} required value={name} />
          </label>
          <div className="form-grid two">
            <label>
              Weekly goal hours
              <input min="1" max="80" onChange={(event) => setWeeklyGoalHours(event.target.value)} type="number" value={weeklyGoalHours} />
            </label>
            <label>
              Timezone
              <input onChange={(event) => setTimezone(event.target.value)} value={timezone} />
            </label>
          </div>
          <label className="checkbox-field">
            <input checked={emailNotifications} onChange={(event) => setEmailNotifications(event.target.checked)} type="checkbox" />
            Email reminders for daily plan and mock tests
          </label>
          <label className="checkbox-field">
            <input checked={productUpdates} onChange={(event) => setProductUpdates(event.target.checked)} type="checkbox" />
            Product and opportunity updates
          </label>
          <label className="checkbox-field">
            <input checked={publicProfile} onChange={(event) => setPublicProfile(event.target.checked)} type="checkbox" />
            Public placement profile
          </label>
          {formError ? <p className="form-error">{formError}</p> : null}
          <div className="modal-actions">
            <button className="ghost-button" onClick={onClose} type="button">
              Cancel
            </button>
            <button className="primary-button" disabled={isSaving} type="submit">
              <Save size={15} />
              {isSaving ? "Saving..." : "Save settings"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

function ScheduleModal({ plan, onClose, onResume }) {
  const items = plan?.items ?? [];

  return (
    <div className="modal-backdrop" role="presentation">
      <section aria-labelledby="schedule-modal-title" className="profile-modal schedule-modal" role="dialog">
        <div className="modal-header">
          <div>
            <span className="eyebrow">Today</span>
            <h2 id="schedule-modal-title">{plan?.title ?? "Today's schedule"}</h2>
          </div>
          <button className="ghost-button" onClick={onClose} type="button">
            Close
          </button>
        </div>

        <div className="schedule-summary">
          <div>
            <strong>{plan?.completed_count ?? 0}/{plan?.total_count ?? 0}</strong>
            <span>completed</span>
          </div>
          <div>
            <strong>{plan?.readiness?.value ?? 0}%</strong>
            <span>{plan?.readiness?.label ?? "readiness"}</span>
          </div>
        </div>

        <div className="schedule-list">
          {items.length ? (
            items.map((item) => (
              <article className="schedule-row" key={`${item.task}-${item.status}`}>
                <div className={`task-status ${item.tone}`} />
                <div>
                  <strong>{item.task}</strong>
                  <span>{item.detail}</span>
                </div>
                <b>{item.status}</b>
                <ProgressBar value={item.progress} tone={item.tone} />
              </article>
            ))
          ) : (
            <EmptyState message="No schedule items are available for today." />
          )}
        </div>

        <div className="modal-actions">
          <button className="ghost-button" onClick={onClose} type="button">
            Done
          </button>
          <button className="primary-button" onClick={onResume} type="button">
            Resume learning
          </button>
        </div>
      </section>
    </div>
  );
}

function PracticeDrillModal({ answers, feedback, isLoading, onAnswerSelect, onClose, onSubmit, questions, topic }) {
  return (
    <div className="modal-backdrop" role="presentation">
      <section aria-labelledby="practice-modal-title" className="profile-modal drill-modal" role="dialog">
        <div className="modal-header">
          <div>
            <span className="eyebrow">{topic?.track ?? "Practice"}</span>
            <h2 id="practice-modal-title">{topic?.name ?? "Practice drill"}</h2>
          </div>
          <button className="icon-button" onClick={onClose} type="button" aria-label="Close drill">
            <X size={17} />
          </button>
        </div>

        <div className="drill-summary-grid">
          <span>Accuracy <b>{topic?.accuracy ?? 0}%</b></span>
          <span>Questions <b>{topic?.question_count ?? questions.length}</b></span>
          <span>Time <b>{topic?.recommended_minutes ?? 20}m</b></span>
          <span>Priority <b>{topic?.priority ?? "steady"}</b></span>
        </div>

        {isLoading ? (
          <EmptyState message="Loading questions for this drill." />
        ) : (
          <div className="question-list modal-question-list">
            {questions.length ? (
              questions.map((question) => (
                <article className="question-card" key={question.id}>
                  <div className="question-head">
                    <span>{question.difficulty}</span>
                    <strong>{question.question_text}</strong>
                  </div>
                  <div className="option-grid">
                    {Object.entries(question.options).map(([key, value]) => (
                      <button
                        className={answers[question.id] === key ? "active" : ""}
                        key={key}
                        onClick={() => onAnswerSelect(question.id, key)}
                        type="button"
                      >
                        <b>{key}</b>
                        {value}
                      </button>
                    ))}
                  </div>
                  <div className="question-actions">
                    <button className="primary-button" onClick={() => onSubmit(question.id)} type="button">
                      Submit answer
                    </button>
                    {feedback[question.id] ? <span>{feedback[question.id]}</span> : null}
                  </div>
                </article>
              ))
            ) : (
              <EmptyState message="No questions are available for this topic yet." />
            )}
          </div>
        )}
      </section>
    </div>
  );
}

function TopicLibraryModal({ onClose, onTopicSelect, query, setQuery, topics }) {
  const filteredTopics = topics.filter((topic) => `${topic.name} ${topic.track}`.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="modal-backdrop" role="presentation">
      <section aria-labelledby="topic-library-title" className="profile-modal topic-library-modal" role="dialog">
        <div className="modal-header">
          <div>
            <span className="eyebrow">Topic library</span>
            <h2 id="topic-library-title">Choose a practice topic</h2>
          </div>
          <button className="icon-button" onClick={onClose} type="button" aria-label="Close topic library">
            <X size={17} />
          </button>
        </div>
        <div className="search-field modal-search-field">
          <Search size={16} />
          <input autoFocus onChange={(event) => setQuery(event.target.value)} placeholder="Search topics" value={query} />
        </div>
        <div className="compact-topic-list modal-topic-list">
          {filteredTopics.length ? (
            filteredTopics.map((topic) => (
              <button key={topic.id} onClick={() => onTopicSelect(topic)} type="button">
                <strong>{topic.name}</strong>
                <span>{topic.track} - {topic.question_count} questions</span>
                <ProgressBar value={topic.accuracy} tone={topic.tone} />
              </button>
            ))
          ) : (
            <EmptyState message="No topics match this search." />
          )}
        </div>
      </section>
    </div>
  );
}

function TestDetailModal({ onClose, test }) {
  if (!test) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section aria-labelledby="test-modal-title" className="profile-modal compact-detail-modal" role="dialog">
        <div className="modal-header">
          <div>
            <span className="eyebrow">Mock test</span>
            <h2 id="test-modal-title">{test.name}</h2>
          </div>
          <button className="icon-button" onClick={onClose} type="button" aria-label="Close test details">
            <X size={17} />
          </button>
        </div>
        <p className="modal-lede">{test.description}</p>
        <div className="drill-summary-grid">
          <span>Duration <b>{test.duration_minutes}m</b></span>
          <span>Questions <b>{test.question_count}</b></span>
          <span>Topics <b>{test.topic_count}</b></span>
          <span>Last score <b>{test.last_score ?? "New"}</b></span>
        </div>
      </section>
    </div>
  );
}

const topicFilters = [
  { label: "All", value: "all" },
  { label: "Current", value: "current" },
  { label: "Open", value: "open" },
  { label: "Done", value: "completed" },
];

function formatDuration(minutes = 0) {
  const safeMinutes = Math.max(0, Number(minutes) || 0);
  if (safeMinutes < 60) {
    return `${safeMinutes}m`;
  }

  const hours = Math.floor(safeMinutes / 60);
  const remainingMinutes = safeMinutes % 60;
  return remainingMinutes ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

function LearningTopicModal({ isUpdating, onClose, onToggle, topic }) {
  if (!topic) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section aria-labelledby="learning-topic-title" className="profile-modal compact-detail-modal" role="dialog">
        <div className="modal-header">
          <div>
            <span className="eyebrow">{topic.track_name ?? "Learning path"}</span>
            <h2 id="learning-topic-title">{topic.name}</h2>
          </div>
          <button className="icon-button" onClick={onClose} type="button" aria-label="Close topic details">
            <X size={17} />
          </button>
        </div>
        <p className="modal-lede">{topic.description || "Practice checkpoint"}</p>
        <div className="drill-summary-grid">
          <span>Status <b>{topic.status_label}</b></span>
          <span>Checkpoint <b>{topic.checkpoint}</b></span>
          <span>Questions <b>{topic.question_count}</b></span>
          <span>Accuracy <b>{topic.accuracy}%</b></span>
        </div>
        <div className="detail-split-list">
          {Object.entries(topic.difficulty_mix ?? {}).map(([difficulty, count]) => (
            <span key={difficulty}>{difficulty} <b>{count}</b></span>
          ))}
        </div>
        <div className="modal-actions">
          <button className="ghost-button" onClick={onClose} type="button">
            Close
          </button>
          <button
            className={`primary-button${topic.is_completed ? " muted-primary" : ""}`}
            disabled={topic.is_locked || isUpdating}
            onClick={() => onToggle(topic)}
            type="button"
          >
            {isUpdating ? "Saving..." : topic.is_completed ? "Reopen topic" : "Mark complete"}
          </button>
        </div>
      </section>
    </div>
  );
}

function TopicRow({ topic, isUpdating, onOpen, onToggle }) {
  const StatusIcon = topic.is_completed ? CheckCircle2 : topic.is_locked ? Circle : topic.status === "current" ? Play : Circle;
  const canToggle = !topic.is_locked && !isUpdating;

  return (
    <article className={`topic-row ${topic.status}`}>
      <div className={`topic-status-icon ${topic.tone}`}>
        <StatusIcon size={18} />
      </div>
      <div className="topic-main">
        <div className="topic-title-row">
          <button className="title-link-button" onClick={() => onOpen(topic)} type="button">
            {topic.name}
          </button>
          <span>{topic.status_label}</span>
        </div>
        <p>{topic.description || "Practice checkpoint"}</p>
        <div className="topic-meta">
          <span>
            <ListChecks size={13} />
            {topic.question_count} questions
          </span>
          <span>
            <Clock3 size={13} />
            {formatDuration(topic.estimated_minutes)}
          </span>
          <span>
            <Trophy size={13} />
            {topic.accuracy}% accuracy
          </span>
        </div>
      </div>
      <div className="topic-progress-block">
        <span>{topic.checkpoint}</span>
        <ProgressBar value={topic.is_completed ? 100 : topic.accuracy} tone={topic.tone} />
        <button
          aria-label={topic.is_completed ? `Reopen ${topic.name}` : `Complete ${topic.name}`}
          className={`topic-complete-button${topic.is_completed ? " done" : ""}`}
          disabled={!canToggle}
          onClick={() => onToggle(topic)}
          title={topic.is_locked ? "Complete earlier checkpoints first" : topic.is_completed ? "Reopen topic" : "Mark complete"}
          type="button"
        >
          {topic.is_completed ? <RefreshCw size={14} /> : <Check size={14} />}
          {isUpdating ? "Saving..." : topic.is_completed ? "Reopen" : "Complete"}
        </button>
      </div>
    </article>
  );
}

function LearningPathPage({ onProgressChange }) {
  const [pathData, setPathData] = useState(null);
  const [pathError, setPathError] = useState(null);
  const [isPathLoading, setIsPathLoading] = useState(true);
  const [activeTrackId, setActiveTrackId] = useState(null);
  const [activeFilter, setActiveFilter] = useState("all");
  const [updatingTopicId, setUpdatingTopicId] = useState(null);
  const [selectedTopicDetail, setSelectedTopicDetail] = useState(null);

  const loadLearningPath = useCallback(async function loadLearningPath() {
    const token = getStoredAccessToken();

    if (!token) {
      setPathData(null);
      setPathError({
        title: "Sign in required",
        message: "Log in to load your learning path, topic progress, focus queue, and completion controls.",
      });
      setIsPathLoading(false);
      return;
    }

    setIsPathLoading(true);
    setPathError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/learning-path/`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.status === 401) {
        clearStoredAuth();
        throw new Error("Your session expired. Please log in again.");
      }

      if (!response.ok) {
        throw new Error(`Learning path API failed with status ${response.status}.`);
      }

      setPathData(await readApiPayload(response));
    } catch (error) {
      setPathData(null);
      setPathError({
        title: "Learning path unavailable",
        message: error.message,
      });
    } finally {
      setIsPathLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      loadLearningPath();
    }, 0);

    return () => window.clearTimeout(timer);
  }, [loadLearningPath]);

  const activeTrack = useMemo(() => {
    const tracks = pathData?.tracks ?? [];

    if (!tracks.length) {
      return null;
    }

    const currentTrackId = pathData?.summary?.next_topic?.track_id;

    return (
      tracks.find((track) => track.id === activeTrackId) ??
      tracks.find((track) => track.id === currentTrackId) ??
      tracks[0]
    );
  }, [activeTrackId, pathData]);

  const filteredTopics = useMemo(() => {
    const topics = activeTrack?.topics ?? [];

    if (activeFilter === "current") {
      return topics.filter((topic) => topic.status === "current" || topic.status === "in_progress");
    }

    if (activeFilter === "open") {
      return topics.filter((topic) => !topic.is_completed);
    }

    if (activeFilter === "completed") {
      return topics.filter((topic) => topic.is_completed);
    }

    return topics;
  }, [activeFilter, activeTrack]);

  async function handleTopicToggle(topic) {
    const token = getStoredAccessToken();

    if (!token) {
      setPathError({
        title: "Sign in required",
        message: "Log in again before updating topic progress.",
      });
      return;
    }

    setUpdatingTopicId(topic.id);
    setPathError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/topics/${topic.id}/progress/`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ is_completed: !topic.is_completed }),
      });

      if (response.status === 401) {
        clearStoredAuth();
        throw new Error("Your session expired. Please log in again.");
      }

      if (!response.ok) {
        const payload = await readApiPayload(response);
        throw new Error(payload.error || `Progress update failed with status ${response.status}.`);
      }

      await loadLearningPath();
      onProgressChange?.();
      setSelectedTopicDetail((current) => current?.id === topic.id ? { ...current, is_completed: !topic.is_completed } : current);
    } catch (error) {
      setPathError({
        title: "Progress update failed",
        message: error.message,
      });
    } finally {
      setUpdatingTopicId(null);
    }
  }

  if (isPathLoading) {
    return <StatusPanel title="Loading learning path" message="Fetching tracks, checkpoints, focus topics, and progress from the backend API." />;
  }

  if (pathError) {
    return <StatusPanel title={pathError.title} message={pathError.message} actionLabel="Retry" onAction={loadLearningPath} />;
  }

  const summary = pathData?.summary;
  const nextTopic = summary?.next_topic;

  return (
    <div className="learning-page">
      <section className="learning-hero-panel">
        <div>
          <span className="eyebrow">Learning path</span>
          <h2>{nextTopic ? nextTopic.name : "All checkpoints complete"}</h2>
          <p>{nextTopic ? `${nextTopic.track_name} - ${nextTopic.reason}` : "Your active learning tracks are fully completed."}</p>
        </div>
        <div className="learning-hero-score">
          <strong>{summary?.progress_percentage ?? 0}%</strong>
          <span>{summary?.completed_topics ?? 0}/{summary?.total_topics ?? 0} topics</span>
        </div>
      </section>

      <section className="learning-stats" aria-label="Learning path summary">
        <article>
          <BookOpenCheck size={18} />
          <span>Tracks</span>
          <strong>{summary?.completed_tracks ?? 0}/{summary?.total_tracks ?? 0}</strong>
        </article>
        <article>
          <ListChecks size={18} />
          <span>Question bank</span>
          <strong>{summary?.total_questions ?? 0}</strong>
        </article>
        <article>
          <Play size={18} />
          <span>Started topics</span>
          <strong>{summary?.attempted_topics ?? 0}</strong>
        </article>
        <article>
          <Clock3 size={18} />
          <span>Remaining</span>
          <strong>{formatDuration(summary?.remaining_minutes)}</strong>
        </article>
      </section>

      <section className="learning-layout">
        <aside className="learning-track-panel">
          <div className="learning-section-header">
            <h2>Tracks</h2>
            <span>{pathData.tracks?.length ?? 0} active</span>
          </div>
          <div className="track-selector-list">
            {pathData.tracks?.length ? (
              pathData.tracks.map((track) => (
                <button
                  className={`track-selector${activeTrack?.id === track.id ? " active" : ""}`}
                  key={track.id}
                  onClick={() => setActiveTrackId(track.id)}
                  type="button"
                >
                  <div>
                    <strong>{track.name}</strong>
                    <span>{track.status}</span>
                  </div>
                  <b>{track.progress_percentage}%</b>
                  <ProgressBar value={track.progress_percentage} tone={track.tone} />
                </button>
              ))
            ) : (
              <EmptyState message="No learning tracks have been added yet." />
            )}
          </div>
        </aside>

        <div className="learning-topic-panel">
          <div className="learning-section-header">
            <div>
              <h2>{activeTrack?.name ?? "Learning track"}</h2>
              <p>{activeTrack?.description || "Ordered checkpoints for placement preparation"}</p>
            </div>
            <div className="segmented-control" role="tablist" aria-label="Topic filter">
              {topicFilters.map((filter) => (
                <button
                  aria-selected={activeFilter === filter.value}
                  className={activeFilter === filter.value ? "active" : ""}
                  key={filter.value}
                  onClick={() => setActiveFilter(filter.value)}
                  role="tab"
                  type="button"
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>

          <div className="topic-list">
            {filteredTopics.length ? (
              filteredTopics.map((topic) => (
                <TopicRow
                  isUpdating={updatingTopicId === topic.id}
                  key={topic.id}
                  onOpen={setSelectedTopicDetail}
                  onToggle={handleTopicToggle}
                  topic={topic}
                />
              ))
            ) : (
              <EmptyState message="No topics match this filter." />
            )}
          </div>
        </div>

        <aside className="learning-side-panel">
          <div className="learning-section-header">
            <h2>Focus queue</h2>
            <span>{pathData.focus_queue?.length ?? 0} items</span>
          </div>
          <div className="focus-list">
            {pathData.focus_queue?.length ? (
              pathData.focus_queue.map((topic) => (
                <button
                  className="focus-item"
                  key={topic.id}
                  onClick={() => {
                    setActiveTrackId(topic.track_id);
                    setActiveFilter("all");
                    setSelectedTopicDetail(topic);
                  }}
                  type="button"
                >
                  <span>{topic.track_name}</span>
                  <strong>{topic.name}</strong>
                  <p>{topic.reason}</p>
                </button>
              ))
            ) : (
              <EmptyState message="No open focus topics." />
            )}
          </div>

          <div className="recent-completions">
            <div className="learning-section-header">
              <h2>Recent wins</h2>
              <span>{pathData.recent_completions?.length ?? 0}</span>
            </div>
            <div className="completion-list">
              {pathData.recent_completions?.length ? (
                pathData.recent_completions.map((item) => (
                  <article className="completion-item" key={`${item.id}-${item.completed_at}`}>
                    <CheckCircle2 size={16} />
                    <div>
                      <strong>{item.topic}</strong>
                      <span>{item.track}</span>
                    </div>
                  </article>
                ))
              ) : (
                <EmptyState message="Completed topics will appear here." />
              )}
            </div>
          </div>
        </aside>
      </section>
      <LearningTopicModal
        isUpdating={updatingTopicId === selectedTopicDetail?.id}
        onClose={() => setSelectedTopicDetail(null)}
        onToggle={handleTopicToggle}
        topic={selectedTopicDetail}
      />
    </div>
  );
}

function PracticePage() {
  const [practiceData, setPracticeData] = useState(null);
  const [practiceError, setPracticeError] = useState(null);
  const [isPracticeLoading, setIsPracticeLoading] = useState(true);
  const [isQuestionLoading, setIsQuestionLoading] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedTest, setSelectedTest] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [feedback, setFeedback] = useState({});
  const [query, setQuery] = useState("");
  const [practiceModal, setPracticeModal] = useState(null);

  const loadPractice = useCallback(async function loadPractice() {
    setIsPracticeLoading(true);
    setPracticeError(null);

    try {
      const payload = await apiFetch("/practice/");
      setPracticeData(payload);
      setSelectedTopic(payload.sample_topic);
      setQuestions([]);
    } catch (error) {
      setPracticeError(error.message);
    } finally {
      setIsPracticeLoading(false);
    }
  }, []);

  async function loadTopicQuestions(topic) {
    setSelectedTopic(topic);
    setAnswers({});
    setFeedback({});
    setIsQuestionLoading(true);
    setPracticeModal("drill");

    try {
      const payload = await apiFetch(`/topics/${topic.id}/questions/`);
      setQuestions(payload.map((question) => ({
        id: question.id,
        question_text: question.question_text,
        difficulty: question.difficulty,
        options: {
          A: question.option_a,
          B: question.option_b,
          C: question.option_c,
          D: question.option_d,
        },
      })));
    } catch (error) {
      setPracticeError(error.message);
      setPracticeModal(null);
    } finally {
      setIsQuestionLoading(false);
    }
  }

  async function submitAnswer(questionId) {
    const answer = answers[questionId];

    if (!answer) {
      setFeedback((current) => ({ ...current, [questionId]: "Choose an option first." }));
      return;
    }

    try {
      const payload = await apiFetch(`/questions/${questionId}/submit/`, {
        method: "POST",
        body: JSON.stringify({ answer }),
      });
      setFeedback((current) => ({
        ...current,
        [questionId]: payload.correct ? "Correct answer" : "Review this concept again",
      }));
    } catch (error) {
      setFeedback((current) => ({ ...current, [questionId]: error.message }));
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(loadPractice, 0);
    return () => window.clearTimeout(timer);
  }, [loadPractice]);

  if (isPracticeLoading) {
    return <StatusPanel title="Loading practice" message="Preparing drills, questions, weak topics, and mock tests from the backend." />;
  }

  if (practiceError) {
    return <StatusPanel title="Practice unavailable" message={practiceError} actionLabel="Retry" onAction={loadPractice} />;
  }

  const filteredTopics = (practiceData?.topics ?? []).filter((topic) =>
    `${topic.name} ${topic.track}`.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="route-page">
      <section className="route-stats">
        <article><ListChecks size={18} /><span>Questions</span><strong>{practiceData.summary.total_questions}</strong></article>
        <article><Target size={18} /><span>Attempts</span><strong>{practiceData.summary.attempts}</strong></article>
        <article><LineChart size={18} /><span>Accuracy</span><strong>{practiceData.summary.accuracy}%</strong></article>
        <article><Flame size={18} /><span>Weak topics</span><strong>{practiceData.summary.weak_topics}</strong></article>
      </section>

      <section className="practice-command-grid">
        <section className="panel route-panel">
          <div className="panel-header">
            <div>
              <h2>Recommended drills</h2>
              <p>Prioritized from your answer history</p>
            </div>
          </div>
          <div className="focus-list">
            {practiceData.recommended.map((topic) => (
              <button className="focus-item" key={topic.id} onClick={() => loadTopicQuestions(topic)} type="button">
                <span>{topic.track}</span>
                <strong>{topic.name}</strong>
                <p>{topic.accuracy}% accuracy - {topic.recommended_minutes} min</p>
              </button>
            ))}
          </div>
        </section>

        <section className="panel route-panel">
          <div className="panel-header">
            <div>
              <h2>Topic library</h2>
              <p>Search opens in a focused popup</p>
            </div>
            <button className="primary-button" onClick={() => setPracticeModal("topics")} type="button">
              <Search size={15} />
              Browse
            </button>
          </div>
          <div className="practice-preview-list">
            {(practiceData?.topics ?? []).slice(0, 5).map((topic) => (
              <button key={topic.id} onClick={() => loadTopicQuestions(topic)} type="button">
                <div>
                  <strong>{topic.name}</strong>
                  <span>{topic.track} - {topic.question_count} questions</span>
                </div>
                <ChevronRight size={16} />
              </button>
            ))}
          </div>
        </section>

        <section className="panel route-panel">
          <div className="panel-header">
            <div>
              <h2>Mock tests</h2>
              <p>Open test details before starting</p>
            </div>
          </div>
          <div className="practice-preview-list">
            {(practiceData.tests ?? []).map((test) => (
              <button key={test.id} onClick={() => setSelectedTest(test)} type="button">
                <div>
                  <strong>{test.name}</strong>
                  <span>{test.duration_minutes}m - {test.question_count} questions</span>
                </div>
                <ChevronRight size={16} />
              </button>
            ))}
          </div>
        </section>
      </section>

      {practiceModal === "drill" ? (
        <PracticeDrillModal
          answers={answers}
          feedback={feedback}
          isLoading={isQuestionLoading}
          onAnswerSelect={(questionId, answer) => setAnswers((current) => ({ ...current, [questionId]: answer }))}
          onClose={() => setPracticeModal(null)}
          onSubmit={submitAnswer}
          questions={questions}
          topic={selectedTopic}
        />
      ) : null}
      {practiceModal === "topics" ? (
        <TopicLibraryModal
          onClose={() => setPracticeModal(null)}
          onTopicSelect={loadTopicQuestions}
          query={query}
          setQuery={setQuery}
          topics={filteredTopics}
        />
      ) : null}
      <TestDetailModal onClose={() => setSelectedTest(null)} test={selectedTest} />
    </div>
  );
}

function AnalyticsPage() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsError, setAnalyticsError] = useState(null);
  const [isAnalyticsLoading, setIsAnalyticsLoading] = useState(true);

  const loadAnalytics = useCallback(async function loadAnalytics() {
    setIsAnalyticsLoading(true);
    setAnalyticsError(null);

    try {
      setAnalyticsData(await apiFetch("/analytics/full/"));
    } catch (error) {
      setAnalyticsError(error.message);
    } finally {
      setIsAnalyticsLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(loadAnalytics, 0);
    return () => window.clearTimeout(timer);
  }, [loadAnalytics]);

  if (isAnalyticsLoading) {
    return <StatusPanel title="Loading analytics" message="Calculating topic accuracy, track progress, test history, and preparation momentum." />;
  }

  if (analyticsError) {
    return <StatusPanel title="Analytics unavailable" message={analyticsError} actionLabel="Retry" onAction={loadAnalytics} />;
  }

  return (
    <div className="route-page">
      <section className="route-stats">
        <article><LineChart size={18} /><span>Accuracy</span><strong>{analyticsData.summary.overall_accuracy}%</strong></article>
        <article><Target size={18} /><span>Attempts</span><strong>{analyticsData.summary.attempts}</strong></article>
        <article><TimerReset size={18} /><span>Mocks</span><strong>{analyticsData.summary.tests_taken}</strong></article>
        <article><BookOpenCheck size={18} /><span>Topics</span><strong>{analyticsData.summary.topics_practiced}</strong></article>
      </section>

      <section className="analytics-grid">
        <Panel title="14-day momentum" subtitle="Solved count and accuracy trend">
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={analyticsData.weekly_momentum} margin={{ top: 12, right: 12, left: -20, bottom: 0 }}>
              <CartesianGrid stroke="rgba(148,163,184,0.14)" vertical={false} />
              <XAxis dataKey="day" axisLine={false} tickLine={false} stroke="#94a3b8" fontSize={11} />
              <YAxis hide />
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 10, color: "#e5e7eb" }} />
              <Area type="monotone" dataKey="solved" stroke="#14b8a6" fill="rgba(20,184,166,0.18)" isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Track progress" subtitle="Completion by learning track">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={analyticsData.track_progress} margin={{ top: 12, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid stroke="rgba(148,163,184,0.14)" vertical={false} />
              <XAxis dataKey="track" axisLine={false} tickLine={false} stroke="#94a3b8" fontSize={10} />
              <YAxis hide domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid rgba(148,163,184,0.2)", borderRadius: 10, color: "#e5e7eb" }} />
              <Bar dataKey="progress" radius={[8, 8, 0, 0]} fill="#22c55e" isAnimationActive={false} />
            </BarChart>
          </ResponsiveContainer>
        </Panel>

        <Panel title="Weak topics" subtitle="Fix these before the next mock">
          <div className="priority-list">
            {analyticsData.weak_topics.map((topic) => (
              <article className="priority-row" key={`${topic.track}-${topic.topic}`}>
                <div>
                  <strong>{topic.topic}</strong>
                  <span>{topic.track} - {topic.attempts} attempts</span>
                </div>
                <b>{topic.accuracy}%</b>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Mock history" subtitle="Recent test performance">
          <div className="activity-list">
            {analyticsData.test_history.map((attempt) => (
              <article className="activity-row" key={`${attempt.test}-${attempt.completed_at}`}>
                <span>{attempt.score}%</span>
                <div>
                  <strong>{attempt.test}</strong>
                  <p>{attempt.raw}</p>
                </div>
              </article>
            ))}
          </div>
        </Panel>
      </section>
    </div>
  );
}

function CompanyDetailModal({ company, onClose, onSave }) {
  const [readiness, setReadiness] = useState(company?.readiness ?? 0);
  const [focus, setFocus] = useState(company?.focus ?? "");
  const [isSaving, setIsSaving] = useState(false);

  if (!company) {
    return null;
  }

  async function handleSave() {
    setIsSaving(true);
    try {
      await onSave(company, { readiness, focus });
      onClose();
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section aria-labelledby="company-detail-title" className="profile-modal company-detail-modal" role="dialog">
        <div className="modal-header">
          <div>
            <span className="eyebrow">{company.full_name}</span>
            <h2 id="company-detail-title">{company.name}</h2>
          </div>
          <button className="icon-button" onClick={onClose} type="button" aria-label="Close company details">
            <X size={17} />
          </button>
        </div>
        <div className="drill-summary-grid">
          <span>Readiness <b>{company.readiness}%</b></span>
          <span>Roles <b>{company.roles.length}</b></span>
          <span>Focus areas <b>{company.prep_focus.length}</b></span>
          <span>Source <b>{company.official_url ? "Official" : "Internal"}</b></span>
        </div>
        <p className="modal-lede">{company.hiring_signal}</p>
        <div className="company-edit modal-company-edit">
          <label>
            Readiness
            <input max="100" min="0" onChange={(event) => setReadiness(event.target.value)} type="range" value={readiness} />
          </label>
          <label>
            Focus
            <input onChange={(event) => setFocus(event.target.value)} value={focus} />
          </label>
        </div>
        <div className="company-detail-grid">
          <div>
            <b>Prep focus</b>
            {company.prep_focus.map((item) => <span key={item}>{item}</span>)}
          </div>
          <div>
            <b>Official notes</b>
            {company.eligibility_notes.slice(0, 4).map((item) => <span key={item}>{item}</span>)}
          </div>
        </div>
        <div className="tag-list">
          {company.roles.map((role) => <span key={role}>{role}</span>)}
        </div>
        <div className="modal-actions">
          {company.official_url ? (
            <a className="ghost-link-button" href={company.official_url} rel="noreferrer" target="_blank">
              <ExternalLink size={15} />
              {company.source_label}
            </a>
          ) : null}
          <button className="primary-button" disabled={isSaving} onClick={handleSave} type="button">
            {isSaving ? "Saving..." : "Save target"}
          </button>
        </div>
      </section>
    </div>
  );
}

function CompaniesPage() {
  const [companiesData, setCompaniesData] = useState(null);
  const [companiesError, setCompaniesError] = useState(null);
  const [isCompaniesLoading, setIsCompaniesLoading] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState(null);

  const loadCompanies = useCallback(async function loadCompanies() {
    setIsCompaniesLoading(true);
    setCompaniesError(null);

    try {
      setCompaniesData(await apiFetch("/companies/"));
    } catch (error) {
      setCompaniesError(error.message);
    } finally {
      setIsCompaniesLoading(false);
    }
  }, []);

  async function saveCompany(company, changes) {
    try {
      await apiFetch(`/companies/${encodeURIComponent(company.name)}/`, {
        method: "PATCH",
        body: JSON.stringify({
          readiness: changes.readiness,
          focus: changes.focus,
        }),
      });
      await loadCompanies();
    } catch (error) {
      setCompaniesError(error.message);
      throw error;
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(loadCompanies, 0);
    return () => window.clearTimeout(timer);
  }, [loadCompanies]);

  if (isCompaniesLoading) {
    return <StatusPanel title="Loading companies" message="Preparing target company readiness, official sources, and role-specific focus areas." />;
  }

  if (companiesError) {
    return <StatusPanel title="Companies unavailable" message={companiesError} actionLabel="Retry" onAction={loadCompanies} />;
  }

  return (
    <div className="route-page">
      <section className="learning-hero-panel compact">
        <div>
          <span className="eyebrow">Companies</span>
          <h2>{companiesData.summary.current_target?.name ?? "Target company planning"}</h2>
          <p>{companiesData.summary.current_target?.hiring_signal ?? "Prepare against official role expectations and your own readiness data."}</p>
        </div>
        <div className="learning-hero-score">
          <strong>{companiesData.summary.average_readiness}%</strong>
          <span>average readiness</span>
        </div>
      </section>

      <section className="companies-grid">
        {companiesData.companies.map((company) => (
          <button className="company-card-full company-card-button" key={company.name} onClick={() => setSelectedCompany(company)} type="button">
            <div className="company-card-head">
              <div>
                <span>{company.full_name}</span>
                <h2>{company.name}</h2>
              </div>
              <strong>{company.readiness}%</strong>
            </div>
            <ProgressBar value={company.readiness} tone={company.tone} />
            <p>{company.focus}</p>
            <div className="tag-list">
              {company.roles.slice(0, 4).map((role) => <span key={role}>{role}</span>)}
            </div>
          </button>
        ))}
      </section>
      <CompanyDetailModal
        key={selectedCompany?.name ?? "company-detail"}
        company={selectedCompany}
        onClose={() => setSelectedCompany(null)}
        onSave={saveCompany}
      />
    </div>
  );
}

function ProfilePage({ profile, onEditProfile, onEditSettings }) {
  const skills = profile?.skills ?? [];
  const targets = profile?.target_companies ?? [];

  return (
    <div className="route-page">
      <section className="profile-overview-panel">
        <div className="profile-overview-avatar">{profile?.name?.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase()}</div>
        <div>
          <span className="eyebrow">Student profile</span>
          <h2>{profile?.name}</h2>
          <p>{profile?.resume_headline}</p>
          <div className="profile-link-row">
            <span><Mail size={14} />{profile?.email}</span>
            <span><MapPin size={14} />{profile?.location}</span>
            <span><BriefcaseBusiness size={14} />{profile?.preferred_role}</span>
          </div>
        </div>
        <div className="profile-overview-actions">
          <button className="primary-button" onClick={onEditProfile} type="button"><Pencil size={15} />Edit profile</button>
          <button className="ghost-button" onClick={onEditSettings} type="button"><Settings size={15} />Account settings</button>
        </div>
      </section>

      <section className="profile-detail-grid">
        <Panel title="Academic profile" subtitle="Eligibility and background">
          <div className="profile-facts">
            <span>College <b>{profile?.college}</b></span>
            <span>Degree <b>{profile?.degree}</b></span>
            <span>Branch <b>{profile?.branch}</b></span>
            <span>Graduation <b>{profile?.graduation_year}</b></span>
            <span>CGPA <b>{profile?.cgpa}</b></span>
            <span>Backlog <b>{profile?.has_backlog ? "Active" : "None"}</b></span>
          </div>
        </Panel>
        <Panel title="Career links" subtitle="Portfolio signals">
          <div className="profile-action-links">
            <a href={profile?.linkedin_url} rel="noreferrer" target="_blank"><ExternalLink size={16} />LinkedIn</a>
            <a href={profile?.github_url} rel="noreferrer" target="_blank"><Code2 size={16} />GitHub</a>
            <a href={profile?.portfolio_url} rel="noreferrer" target="_blank"><FileText size={16} />Portfolio</a>
          </div>
        </Panel>
        <Panel title="Skills" subtitle="Backend-backed skill inventory">
          <div className="tag-list large">
            {skills.map((skill) => <span key={skill}>{skill}</span>)}
          </div>
        </Panel>
        <Panel title="Target companies" subtitle="Used for readiness scoring">
          <div className="tag-list large">
            {targets.map((company) => <span key={company}>{company}</span>)}
          </div>
        </Panel>
      </section>
    </div>
  );
}

function AdminPage() {
  const [adminData, setAdminData] = useState(null);
  const [adminError, setAdminError] = useState(null);
  const [isAdminLoading, setIsAdminLoading] = useState(true);
  const [updatingUserId, setUpdatingUserId] = useState(null);
  const [activeAdminTab, setActiveAdminTab] = useState("overview");
  const [newTrack, setNewTrack] = useState({ name: "", description: "" });
  const [newTopic, setNewTopic] = useState({ track_id: "", name: "", description: "", order: "" });
  const [newTarget, setNewTarget] = useState({ user_id: "", name: "", readiness: 0, focus: "" });

  const loadAdmin = useCallback(async function loadAdmin() {
    setIsAdminLoading(true);
    setAdminError(null);

    try {
      setAdminData(await apiFetch("/admin/overview/"));
    } catch (error) {
      setAdminError(error.message);
    } finally {
      setIsAdminLoading(false);
    }
  }, []);

  async function updateUser(user, changes) {
    setUpdatingUserId(user.id);
    setAdminError(null);

    try {
      await apiFetch(`/admin/users/${user.id}/`, {
        method: "PATCH",
        body: JSON.stringify(changes),
      });
      await loadAdmin();
    } catch (error) {
      setAdminError(error.message);
    } finally {
      setUpdatingUserId(null);
    }
  }

  async function createContent(payload) {
    setAdminError(null);
    try {
      await apiFetch("/admin/content/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setNewTrack({ name: "", description: "" });
      setNewTopic({ track_id: "", name: "", description: "", order: "" });
      await loadAdmin();
    } catch (error) {
      setAdminError(error.message);
    }
  }

  async function updateTopic(topic, changes) {
    setAdminError(null);
    try {
      await apiFetch(`/admin/topics/${topic.id}/`, {
        method: "PATCH",
        body: JSON.stringify(changes),
      });
      await loadAdmin();
    } catch (error) {
      setAdminError(error.message);
    }
  }

  async function deleteTopic(topic) {
    if (!window.confirm(`Archive or delete "${topic.name}"? Student history will be preserved by archiving when needed.`)) {
      return;
    }

    setAdminError(null);
    try {
      await apiFetch(`/admin/topics/${topic.id}/`, { method: "DELETE" });
      await loadAdmin();
    } catch (error) {
      setAdminError(error.message);
    }
  }

  async function createCompanyTarget() {
    setAdminError(null);
    try {
      await apiFetch("/admin/company-targets/", {
        method: "POST",
        body: JSON.stringify(newTarget),
      });
      setNewTarget({ user_id: "", name: "", readiness: 0, focus: "" });
      await loadAdmin();
    } catch (error) {
      setAdminError(error.message);
    }
  }

  async function updateCompanyTarget(target, changes) {
    setAdminError(null);
    try {
      await apiFetch(`/admin/company-targets/${target.id}/`, {
        method: "PATCH",
        body: JSON.stringify(changes),
      });
      await loadAdmin();
    } catch (error) {
      setAdminError(error.message);
    }
  }

  async function deleteCompanyTarget(target) {
    if (!window.confirm(`Archive "${target.name}" for ${target.user}?`)) {
      return;
    }

    setAdminError(null);
    try {
      await apiFetch(`/admin/company-targets/${target.id}/`, { method: "DELETE" });
      await loadAdmin();
    } catch (error) {
      setAdminError(error.message);
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(loadAdmin, 0);
    return () => window.clearTimeout(timer);
  }, [loadAdmin]);

  if (isAdminLoading) {
    return <StatusPanel title="Loading admin" message="Preparing users, access controls, platform catalog, and activity data." />;
  }

  if (adminError && !adminData) {
    return <StatusPanel title="Admin unavailable" message={adminError} actionLabel="Retry" onAction={loadAdmin} />;
  }

  const summary = adminData?.summary ?? {};
  const users = adminData?.users ?? [];
  const tracks = adminData?.tracks ?? [];
  const companyTargets = adminData?.company_targets ?? [];
  const tabs = [
    { label: "Overview", value: "overview", icon: LayoutDashboard },
    { label: "Users", value: "users", icon: UsersRound },
    { label: "Content", value: "content", icon: Route },
    { label: "Companies", value: "companies", icon: Building2 },
    { label: "Activity", value: "activity", icon: LineChart },
  ];

  return (
    <div className="admin-page">
      {adminError ? (
        <div className="form-error admin-inline-error">{adminError}</div>
      ) : null}
      <div className="admin-tabbar" role="tablist" aria-label="Admin sections">
        {tabs.map((tab) => {
          const Icon = tab.icon;

          return (
            <button
              aria-selected={activeAdminTab === tab.value}
              className={activeAdminTab === tab.value ? "active" : ""}
              key={tab.value}
              onClick={() => setActiveAdminTab(tab.value)}
              role="tab"
              type="button"
            >
              <Icon size={15} />
              {tab.label}
            </button>
          );
        })}
      </div>

      <section className="route-stats">
        <article>
          <UsersRound size={18} />
          <span>Users</span>
          <strong>{summary.users ?? 0}</strong>
        </article>
        <article>
          <ShieldCheck size={18} />
          <span>Admins</span>
          <strong>{summary.admins ?? 0}</strong>
        </article>
        <article>
          <Route size={18} />
          <span>Topics</span>
          <strong>{summary.topics ?? 0}</strong>
        </article>
        <article>
          <Building2 size={18} />
          <span>Company targets</span>
          <strong>{summary.company_targets ?? 0}</strong>
        </article>
      </section>

      {activeAdminTab === "overview" ? (
        <section className="admin-layout">
          <Panel title="Operations overview" subtitle="Current platform health">
            <div className="admin-overview-grid">
              <article><strong>{summary.active_users ?? 0}</strong><span>active users</span></article>
              <article><strong>{summary.tracks ?? 0}</strong><span>learning tracks</span></article>
              <article><strong>{summary.questions ?? 0}</strong><span>questions</span></article>
              <article><strong>{summary.events ?? 0}</strong><span>activity events</span></article>
            </div>
          </Panel>
          <Panel title="Catalog health" subtitle="Completion signals by track">
            <div className="admin-catalog-list">
              {tracks.map((track) => (
                <article key={track.name}>
                  <div>
                    <strong>{track.name}</strong>
                    <span>{track.topic_count} topics / {track.question_count} questions</span>
                  </div>
                  <ProgressBar value={track.completion_rate} tone={track.completion_rate > 60 ? "green" : "cyan"} />
                </article>
              ))}
            </div>
          </Panel>
        </section>
      ) : null}

      {activeAdminTab === "users" ? (
        <Panel title="User access" subtitle="Activate accounts and grant staff control">
          <div className="admin-user-list">
            {users.length ? (
              users.map((user) => (
                <article className="admin-user-row" key={user.id}>
                  <div className="profile-trigger-avatar">{user.initials}</div>
                  <div>
                    <strong>{user.name}</strong>
                    <span>{user.email}</span>
                    <em>{user.profile_summary}</em>
                  </div>
                  <div className="admin-user-badges">
                    <span>{user.is_superuser ? "Super admin" : user.is_staff ? "Admin" : "Student"}</span>
                    <span>{user.is_active ? "Active" : "Inactive"}</span>
                  </div>
                  <div className="admin-user-actions">
                    <button
                      className="ghost-button"
                      disabled={updatingUserId === user.id || user.is_superuser}
                      onClick={() => updateUser(user, { is_staff: !user.is_staff })}
                      type="button"
                    >
                      {user.is_staff ? "Remove admin" : "Make admin"}
                    </button>
                    <button
                      className={user.is_active ? "ghost-button danger" : "primary-button"}
                      disabled={updatingUserId === user.id || user.is_superuser}
                      onClick={() => updateUser(user, { is_active: !user.is_active })}
                      type="button"
                    >
                      {user.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </div>
                </article>
              ))
            ) : (
              <EmptyState message="No users have been created yet." />
            )}
          </div>
        </Panel>
      ) : null}

      {activeAdminTab === "content" ? (
        <section className="admin-layout">
          <Panel title="Add content" subtitle="Create tracks and topics for students">
            <div className="admin-form-grid">
              <div className="admin-form-box">
                <h3>New track</h3>
                <label>
                  Track name
                  <input onChange={(event) => setNewTrack((current) => ({ ...current, name: event.target.value }))} value={newTrack.name} />
                </label>
                <label>
                  Description
                  <textarea onChange={(event) => setNewTrack((current) => ({ ...current, description: event.target.value }))} rows="3" value={newTrack.description} />
                </label>
                <button className="primary-button" onClick={() => createContent({ type: "track", ...newTrack })} type="button">
                  <Plus size={15} />
                  Add track
                </button>
              </div>
              <div className="admin-form-box">
                <h3>New topic</h3>
                <label>
                  Track
                  <select onChange={(event) => setNewTopic((current) => ({ ...current, track_id: event.target.value }))} value={newTopic.track_id}>
                    <option value="">Select track</option>
                    {tracks.map((track) => <option key={track.id} value={track.id}>{track.name}</option>)}
                  </select>
                </label>
                <label>
                  Topic name
                  <input onChange={(event) => setNewTopic((current) => ({ ...current, name: event.target.value }))} value={newTopic.name} />
                </label>
                <label>
                  Description
                  <textarea onChange={(event) => setNewTopic((current) => ({ ...current, description: event.target.value }))} rows="3" value={newTopic.description} />
                </label>
                <button className="primary-button" onClick={() => createContent({ type: "topic", ...newTopic })} type="button">
                  <Plus size={15} />
                  Add topic
                </button>
              </div>
            </div>
          </Panel>

          <Panel title="Manage topics" subtitle="Edit status or archive topics">
            <div className="admin-content-list">
              {tracks.map((track) => (
                <article key={track.id}>
                  <div>
                    <strong>{track.name}</strong>
                    <span>{track.description || "No description"}</span>
                  </div>
                  {(track.topics ?? []).map((topic) => (
                    <div className="admin-topic-row" key={topic.id}>
                      <div>
                        <b>{topic.name}</b>
                        <span>{topic.question_count} questions / order {topic.order}</span>
                      </div>
                      <button className="ghost-button" onClick={() => updateTopic(topic, { is_active: !topic.is_active })} type="button">
                        {topic.is_active ? "Archive" : "Activate"}
                      </button>
                      <button className="ghost-button danger" onClick={() => deleteTopic(topic)} type="button">
                        <Trash2 size={14} />
                        Delete
                      </button>
                    </div>
                  ))}
                </article>
              ))}
            </div>
          </Panel>
        </section>
      ) : null}

      {activeAdminTab === "companies" ? (
        <section className="admin-layout">
          <Panel title="Add company target" subtitle="Assign or restore company targets for a student">
            <div className="admin-form-box">
              <label>
                User
                <select onChange={(event) => setNewTarget((current) => ({ ...current, user_id: event.target.value }))} value={newTarget.user_id}>
                  <option value="">Select user</option>
                  {users.filter((user) => !user.is_staff).map((user) => <option key={user.id} value={user.id}>{user.name} - {user.email}</option>)}
                </select>
              </label>
              <label>
                Company
                <input onChange={(event) => setNewTarget((current) => ({ ...current, name: event.target.value }))} value={newTarget.name} />
              </label>
              <label>
                Readiness
                <input max="100" min="0" onChange={(event) => setNewTarget((current) => ({ ...current, readiness: event.target.value }))} type="range" value={newTarget.readiness} />
              </label>
              <label>
                Focus
                <input onChange={(event) => setNewTarget((current) => ({ ...current, focus: event.target.value }))} value={newTarget.focus} />
              </label>
              <button className="primary-button" onClick={createCompanyTarget} type="button">
                <Plus size={15} />
                Add target
              </button>
            </div>
          </Panel>

          <Panel title="Company targets" subtitle="Monitor and update readiness">
            <div className="admin-content-list">
              {companyTargets.map((target) => (
                <article className={!target.is_active ? "muted-row" : ""} key={target.id}>
                  <div>
                    <strong>{target.name}</strong>
                    <span>{target.user} / {target.email}</span>
                    <p>{target.focus}</p>
                  </div>
                  <ProgressBar value={target.readiness} tone={target.tone} />
                  <div className="admin-row-actions">
                    <button className="ghost-button" onClick={() => updateCompanyTarget(target, { is_active: !target.is_active })} type="button">
                      {target.is_active ? "Archive" : "Activate"}
                    </button>
                    <button className="ghost-button danger" onClick={() => deleteCompanyTarget(target)} type="button">
                      <Trash2 size={14} />
                      Delete
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </Panel>
        </section>
      ) : null}

      {activeAdminTab === "activity" ? (
        <Panel title="Recent activity" subtitle="Latest platform events">
          <div className="activity-list">
            {(adminData?.activity ?? []).map((item) => (
              <article className="activity-row" key={`${item.user}-${item.title}-${item.time}`}>
                <span>{item.type}</span>
                <div>
                  <strong>{item.title}</strong>
                  <p>{item.user} / {item.time}</p>
                </div>
              </article>
            ))}
          </div>
        </Panel>
      ) : null}
    </div>
  );
}

function AdminShell({ onLogout, user }) {
  return (
    <div className="admin-shell">
      <header className="admin-shell-header">
        <Link className="landing-brand" to="/admin">
          <span className="brand-mark">PS</span>
          <span>
            <strong>PrepSmart Admin</strong>
            <small>Platform operations</small>
          </span>
        </Link>
        <div className="admin-shell-actions">
          <a className="ghost-link-button" href="http://127.0.0.1:8000/admin/" rel="noreferrer" target="_blank">
            <ExternalLink size={15} />
            Django admin
          </a>
          <button className="profile-trigger admin-profile-trigger" type="button">
            <span className="profile-trigger-avatar">{user?.initials}</span>
            <span className="profile-trigger-copy">
              <strong>{user?.name}</strong>
              <span>Administrator</span>
            </span>
          </button>
          <button className="ghost-button" onClick={onLogout} type="button">
            <LogOut size={16} />
            Log out
          </button>
        </div>
      </header>
      <main className="admin-workspace">
        <div className="admin-workspace-title">
          <span className="eyebrow">Admin console</span>
          <h1>Manage the placement platform</h1>
          <p>Add, edit, archive, and monitor users, content, company targets, and activity without entering the student workspace.</p>
        </div>
        <AdminPage />
      </main>
    </div>
  );
}

function Layout() {
  const [sessionUser, setSessionUser] = useState(null);
  const [sessionError, setSessionError] = useState(null);
  const [isSessionLoading, setIsSessionLoading] = useState(() => Boolean(getStoredAccessToken()));
  const [dashboardData, setDashboardData] = useState(null);
  const [dashboardError, setDashboardError] = useState(null);
  const [isDashboardLoading, setIsDashboardLoading] = useState(false);
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const [activeModal, setActiveModal] = useState(null);
  const accountMenuRef = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();
  const route = location.pathname;
  const isLearningPathPage = location.pathname === "/learning-path";
  const isLoginPage = location.pathname === "/login";
  const isSignupPage = location.pathname === "/signup";
  const isPracticePage = location.pathname === "/practice";
  const isAnalyticsPage = location.pathname === "/analytics";
  const isCompaniesPage = location.pathname === "/companies";
  const isProfilePage = location.pathname === "/profile";
  const isAdminPage = location.pathname === "/admin";

  const loadSession = useCallback(async function loadSession() {
    const token = getStoredAccessToken();

    if (!token) {
      setSessionUser(null);
      setIsSessionLoading(false);
      return;
    }

    setIsSessionLoading(true);
    setSessionError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/session/`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.status === 401) {
        clearStoredAuth();
        throw new Error("Your session expired. Please log in again.");
      }

      const payload = await readApiPayload(response);
      if (!response.ok) {
        throw new Error(payload?.detail || payload?.error || `Session API failed with status ${response.status}.`);
      }

      setSessionUser(payload);
    } catch (error) {
      setSessionUser(null);
      setSessionError(error.message);
    } finally {
      setIsSessionLoading(false);
    }
  }, []);

  const loadDashboard = useCallback(async function loadDashboard() {
    const token = getStoredAccessToken();

    if (!token) {
      setDashboardData(null);
      setDashboardError({
        title: "Sign in required",
        message: isSignupPage
          ? "Create your account and PrepSmart will prepare a complete dashboard, learning path, daily plan, target companies, and practice history automatically."
          : "The dashboard is now backend-driven. Log in first so PrepSmart can load your real profile, metrics, plan, and progress from the API.",
      });
      setIsDashboardLoading(false);
      return;
    }

    setIsDashboardLoading(true);
    setDashboardError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/dashboard/`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.status === 401) {
        clearStoredAuth();
        throw new Error("Your session expired. Please log in again.");
      }

      if (!response.ok) {
        throw new Error(`Dashboard API failed with status ${response.status}.`);
      }

      setDashboardData(await readApiPayload(response));
    } catch (error) {
      setDashboardData(null);
      setDashboardError({
        title: "Dashboard unavailable",
        message: error.message,
      });
    } finally {
      setIsDashboardLoading(false);
    }
  }, [isSignupPage]);

  useEffect(() => {
    if (!getStoredAccessToken()) {
      return undefined;
    }

    const timer = window.setTimeout(loadSession, 0);
    return () => window.clearTimeout(timer);
  }, [loadSession]);

  useEffect(() => {
    if (!sessionUser || sessionUser.is_admin) {
      return undefined;
    }

    const timer = window.setTimeout(loadDashboard, 0);

    return () => window.clearTimeout(timer);
  }, [loadDashboard, sessionUser]);

  useEffect(() => {
    if (sessionUser?.is_admin && route !== "/admin") {
      navigate("/admin", { replace: true });
    }
    if (sessionUser && !sessionUser.is_admin && isAdminPage) {
      navigate("/", { replace: true });
    }
  }, [isAdminPage, navigate, route, sessionUser]);

  useEffect(() => {
    function handlePointerDown(event) {
      if (!accountMenuRef.current?.contains(event.target)) {
        setAccountMenuOpen(false);
      }
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setAccountMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  function handleLogout() {
    clearStoredAuth();
    setSessionUser(null);
    setDashboardData(null);
    setDashboardError({
      title: "Signed out",
      message: "Your local session tokens were cleared. Log in again to load backend dashboard data.",
    });
    setAccountMenuOpen(false);
    navigate("/login");
  }

  function handleProfileSaved() {
    setActiveModal(null);
    loadDashboard();
  }

  function handleResumeLearning() {
    setActiveModal(null);
    navigate("/learning-path");
  }

  function handleAuthSuccess(userPayload) {
    setSessionUser(userPayload);
    navigate(userPayload?.is_admin ? "/admin" : "/");
    if (!userPayload?.is_admin) {
      loadDashboard();
    }
  }

  const user = dashboardData?.user;
  const header = dashboardData?.header;
  const todaysPlan = dashboardData?.todays_plan;
  const readinessValue = todaysPlan?.readiness?.value ?? 0;
  const sidebarFocus =
    dashboardData?.weakness_priorities?.[0]?.topic ??
    dashboardData?.learning_tracks?.find((track) => track.next && track.next !== "Completed")?.next ??
    "Open your next learning checkpoint";
  const visibleNavItems = user?.is_admin
    ? [...navItems, { label: "Admin", to: "/admin", icon: ShieldCheck }]
    : navItems;
  const pageHeaders = {
    "/learning-path": {
      eyebrow: "Learning path",
      title: "Your placement roadmap",
      subtitle: "Complete ordered checkpoints, revisit weak topics, and keep every track moving.",
    },
    "/practice": {
      eyebrow: "Practice",
      title: "Backend-powered question bank",
      subtitle: "Drill real topics, submit answers, and let weak areas flow back into analytics.",
    },
    "/analytics": {
      eyebrow: "Analytics",
      title: "Preparation intelligence",
      subtitle: "Accuracy, topic health, mock history, and readiness signals from backend activity.",
    },
    "/companies": {
      eyebrow: "Companies",
      title: "Target company readiness",
      subtitle: "Official-source career notes, role focus, and editable readiness for your targets.",
    },
    "/profile": {
      eyebrow: "Profile",
      title: "Placement profile",
      subtitle: "Academic details, links, skills, targets, and account preferences in one place.",
    },
    "/admin": {
      eyebrow: "Admin",
      title: "Platform control center",
      subtitle: "Manage users, access, learning catalog health, and activity from one staff-only workspace.",
    },
  };
  const pageHeader = pageHeaders[route] ?? {
    eyebrow: header?.date_label,
    title: header?.greeting,
    subtitle: header?.subtitle,
  };

  if (!getStoredAccessToken() && route === "/") {
    return <LandingPage />;
  }

  if (!getStoredAccessToken() && (isLoginPage || isSignupPage)) {
    return <PublicAuthPage initialMode={isSignupPage ? "signup" : "login"} onAuthenticated={handleAuthSuccess} />;
  }

  if (!getStoredAccessToken()) {
    return <PublicAuthPage initialMode="login" onAuthenticated={handleAuthSuccess} />;
  }

  if (getStoredAccessToken() && isSessionLoading) {
    return <StatusPanel title="Opening workspace" message="Checking your account role and preparing the correct workspace." />;
  }

  if (sessionError) {
    return <PublicAuthPage initialMode="login" onAuthenticated={handleAuthSuccess} />;
  }

  if (sessionUser?.is_admin) {
    return <AdminShell onLogout={handleLogout} user={sessionUser} />;
  }

  return (
    <div className="platform-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">PS</div>
          <div>
            <strong>PrepSmart</strong>
            <span>Placement platform</span>
          </div>
        </div>

        <nav className="nav" aria-label="Primary navigation">
          {visibleNavItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                end={item.to === "/"}
                key={item.label}
                to={item.to}
                className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-summary">
          <div className="sidebar-summary-head">
            <span>Readiness snapshot</span>
            <b>{readinessValue}%</b>
          </div>
          <strong>{todaysPlan?.readiness?.label ?? "Placement readiness"}</strong>
          <p>{todaysPlan?.readiness?.description ?? "Your readiness score updates from practice, learning, mocks, and profile progress."}</p>
          <em>Next focus: {sidebarFocus}</em>
          <ProgressBar value={readinessValue} tone={readinessValue >= 70 ? "green" : readinessValue >= 50 ? "amber" : "cyan"} />
          <button className="sidebar-action" onClick={handleResumeLearning} type="button">
            Resume
            <ArrowRight size={14} />
          </button>
        </div>
      </aside>

      <main className="workspace">
        {isDashboardLoading ? (
          <StatusPanel title="Loading dashboard" message="Fetching profile, progress, plans, and analytics from the backend API." />
        ) : dashboardError?.title === "Sign in required" || dashboardError?.title === "Signed out" ? (
          <AuthPanel initialMode={isSignupPage ? "signup" : "login"} message={dashboardError.message} onAuthenticated={loadDashboard} />
        ) : dashboardError ? (
          <StatusPanel title={dashboardError.title} message={dashboardError.message} actionLabel="Retry" onAction={loadDashboard} />
        ) : (
          <>
            <header className="topbar">
              <div>
                <span className="eyebrow">{pageHeader.eyebrow}</span>
                <h1>{pageHeader.title}</h1>
                <p>{pageHeader.subtitle}</p>
              </div>
              <div className="topbar-actions">
                <button className="ghost-button" onClick={() => setActiveModal("schedule")} type="button">
                  <CalendarCheck2 size={16} />
                  Today&apos;s schedule
                </button>
                <button className="primary-button" onClick={handleResumeLearning} type="button">
                  Resume learning
                </button>
                <div className="account-menu" ref={accountMenuRef}>
                  <button
                    aria-expanded={accountMenuOpen}
                    aria-haspopup="menu"
                    className="profile-trigger"
                    onClick={() => setAccountMenuOpen((open) => !open)}
                    type="button"
                  >
                    <span className="profile-trigger-avatar">{user?.initials}</span>
                    <span className="profile-trigger-copy">
                      <strong>{user?.name}</strong>
                      <span>{user?.is_admin ? "Admin account" : "Student account"}</span>
                    </span>
                    <ChevronDown size={16} />
                  </button>

                  {accountMenuOpen ? (
                    <div className="account-dropdown" role="menu">
                      <div className="account-dropdown-head">
                        <span className="profile-trigger-avatar">{user?.initials}</span>
                        <div>
                          <strong>{user?.name}</strong>
                          <span>{user?.email}</span>
                        </div>
                      </div>
                      <button
                        className="account-menu-item"
                        onClick={() => {
                          setActiveModal("profile");
                          setAccountMenuOpen(false);
                        }}
                        role="menuitem"
                        type="button"
                      >
                        <Pencil size={16} />
                        Edit profile
                      </button>
                      <button
                        className="account-menu-item"
                        onClick={() => {
                          setActiveModal("settings");
                          setAccountMenuOpen(false);
                        }}
                        role="menuitem"
                        type="button"
                      >
                        <Settings size={16} />
                        Account settings
                      </button>
                      <button className="account-menu-item logout" onClick={handleLogout} role="menuitem" type="button">
                        <LogOut size={16} />
                        Log out
                      </button>
                    </div>
                  ) : null}
                </div>
              </div>
            </header>

            {isLearningPathPage ? (
              <LearningPathPage onProgressChange={loadDashboard} />
            ) : isPracticePage ? (
              <PracticePage />
            ) : isAnalyticsPage ? (
              <AnalyticsPage />
            ) : isCompaniesPage ? (
              <CompaniesPage />
            ) : isProfilePage ? (
              <ProfilePage
                onEditProfile={() => setActiveModal("profile")}
                onEditSettings={() => setActiveModal("settings")}
                profile={user?.profile}
              />
            ) : isAdminPage ? (
              <AdminPage />
            ) : (
              <>
                <section className="metrics-grid" aria-label="Dashboard metrics">
                  {dashboardData.metrics?.length ? (
                    dashboardData.metrics.map((metric) => <MetricCard key={metric.label} metric={metric} />)
                  ) : (
                    <EmptyState message="No backend metrics available yet." />
                  )}
                </section>

                <section className="dashboard-grid">
              <div className="main-stack">
                <Panel title={todaysPlan?.title} subtitle={todaysPlan?.subtitle} action="Edit plan" onAction={() => setActiveModal("schedule")}>
                  <div className="plan-layout">
                    <div className="readiness-summary">
                      <div className="readiness-score">
                        <strong>{todaysPlan?.readiness?.value ?? 0}%</strong>
                        <span>{todaysPlan?.readiness?.label}</span>
                      </div>
                      <p>{todaysPlan?.readiness?.description}</p>
                    </div>

                    <div className="task-list">
                      {todaysPlan?.items?.length ? (
                        todaysPlan.items.map((item) => (
                          <article className="task-row" key={`${item.task}-${item.status}`}>
                            <div className={`task-status ${item.tone}`} />
                            <div>
                              <strong>{item.task}</strong>
                              <span>{item.detail}</span>
                            </div>
                            <div className="task-progress">
                              <span>{item.status}</span>
                              <ProgressBar value={item.progress} tone={item.tone} />
                            </div>
                          </article>
                        ))
                      ) : (
                        <EmptyState message="No plan items returned by the backend for today." />
                      )}
                    </div>
                  </div>
                </Panel>

                <div className="two-column-grid">
                  <Panel title="Learning tracks" subtitle="Track progress and unlocks">
                    <div className="track-grid">
                      {dashboardData.learning_tracks?.length ? (
                        dashboardData.learning_tracks.map((track) => (
                          <article className="track-card" key={track.name}>
                            <div>
                              <strong>{track.name}</strong>
                              <span>{track.status}</span>
                            </div>
                            <ProgressBar value={track.progress} tone={track.tone} />
                            <p>{track.next}</p>
                          </article>
                        ))
                      ) : (
                        <EmptyState message="No tracks found in the backend." />
                      )}
                    </div>
                  </Panel>

                  <Panel title="Weekly momentum" subtitle="Practice volume across the week">
                    {dashboardData.weekly_momentum?.length ? (
                      <ResponsiveContainer width="100%" height={248}>
                        <AreaChart data={dashboardData.weekly_momentum} margin={{ top: 12, right: 12, left: -20, bottom: 0 }}>
                          <defs>
                            <linearGradient id="solvedGradient" x1="0" x2="0" y1="0" y2="1">
                              <stop offset="0%" stopColor="#14b8a6" stopOpacity={0.28} />
                              <stop offset="100%" stopColor="#14b8a6" stopOpacity={0.03} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid stroke="rgba(148,163,184,0.14)" vertical={false} />
                          <XAxis dataKey="day" axisLine={false} tickLine={false} stroke="#94a3b8" fontSize={11} />
                          <YAxis hide domain={[0, 20]} />
                          <Tooltip
                            cursor={{ stroke: "rgba(20,184,166,0.45)" }}
                            contentStyle={{
                              background: "#111827",
                              border: "1px solid rgba(148,163,184,0.2)",
                              borderRadius: 10,
                              color: "#e5e7eb",
                            }}
                          />
                          <Area
                            type="monotone"
                            dataKey="solved"
                            stroke="#14b8a6"
                            strokeWidth={2.5}
                            fill="url(#solvedGradient)"
                            isAnimationActive={false}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    ) : (
                      <EmptyState message="No weekly activity returned by the backend." />
                    )}
                  </Panel>
                </div>

                <Panel title="Subject mastery" subtitle="Accuracy, next action, and confidence level">
                  <div className="mastery-table">
                    {dashboardData.subject_mastery?.length ? (
                      dashboardData.subject_mastery.map((item) => (
                        <article className="mastery-row" key={item.topic}>
                          <div>
                            <strong>{item.topic}</strong>
                            <span>Next: {item.next}</span>
                          </div>
                          <ProgressBar value={item.value} tone={item.tone} />
                          <b>{item.value}%</b>
                        </article>
                      ))
                    ) : (
                      <EmptyState message="No subject mastery data returned by the backend." />
                    )}
                  </div>
                </Panel>

                <div className="two-column-grid">
                  <Panel title="Accuracy profile" subtitle="Subject split">
                    {dashboardData.subject_mastery?.length ? (
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={dashboardData.subject_mastery} margin={{ top: 12, right: 8, left: -20, bottom: 0 }}>
                          <CartesianGrid stroke="rgba(148,163,184,0.14)" vertical={false} />
                          <XAxis dataKey="topic" axisLine={false} tickLine={false} stroke="#94a3b8" fontSize={10} />
                          <YAxis hide domain={[0, 100]} />
                          <Tooltip
                            cursor={{ fill: "rgba(20,184,166,0.08)" }}
                            contentStyle={{
                              background: "#111827",
                              border: "1px solid rgba(148,163,184,0.2)",
                              borderRadius: 10,
                              color: "#e5e7eb",
                            }}
                          />
                          <Bar dataKey="value" radius={[8, 8, 0, 0]} isAnimationActive={false}>
                            {dashboardData.subject_mastery.map((item) => (
                              <Cell key={item.topic} fill={item.value < 50 ? "#ef4444" : item.value < 70 ? "#f59e0b" : "#22c55e"} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    ) : (
                      <EmptyState message="No accuracy profile returned by the backend." />
                    )}
                  </Panel>

                  <Panel title="Recent activity" subtitle="Latest preparation signals">
                    <div className="activity-list">
                      {dashboardData.recent_activity?.length ? (
                        dashboardData.recent_activity.map((item) => (
                          <article className="activity-row" key={`${item.type}-${item.title}-${item.time}`}>
                            <span>{item.type}</span>
                            <div>
                              <strong>{item.title}</strong>
                              <p>{item.time}</p>
                            </div>
                          </article>
                        ))
                      ) : (
                        <EmptyState message="No recent activity returned by the backend." />
                      )}
                    </div>
                  </Panel>
                </div>
              </div>

              <aside className="side-stack">
                <section className="profile-card">
                  <div className="avatar">{user?.initials}</div>
                  <div>
                    <strong>{user?.name}</strong>
                    <span>{user?.subtitle}</span>
                  </div>
                  <div className="profile-meta">
                    <div>
                      <b>{todaysPlan?.total_count ?? 0}</b>
                      <span>Plan items</span>
                    </div>
                    <div>
                      <b>{dashboardData.company_readiness?.length ?? 0}</b>
                      <span>Targets</span>
                    </div>
                    <div>
                      <b>{dashboardData.weakness_priorities?.length ?? 0}</b>
                      <span>Alerts</span>
                    </div>
                  </div>
                </section>

                <Panel title="Company readiness" subtitle="Priority hiring targets">
                  <div className="company-list">
                    {dashboardData.company_readiness?.length ? (
                      dashboardData.company_readiness.map((company) => (
                        <article className="company-row" key={company.name}>
                          <div>
                            <strong>{company.name}</strong>
                            <span>{company.focus}</span>
                          </div>
                          <b>{company.readiness}%</b>
                          <ProgressBar value={company.readiness} tone={company.tone} />
                        </article>
                      ))
                    ) : (
                      <EmptyState message="No company targets returned by the backend." />
                    )}
                  </div>
                </Panel>

                <Panel title="Weakness priorities" subtitle="Fix these before the next mock">
                  <div className="priority-list">
                    {dashboardData.weakness_priorities?.length ? (
                      dashboardData.weakness_priorities.map((item) => (
                        <article className="priority-row" key={item.topic}>
                          <div>
                            <strong>{item.topic}</strong>
                            <span>{item.recommendation}</span>
                          </div>
                          <b>{item.score}%</b>
                        </article>
                      ))
                    ) : (
                      <EmptyState message="No weak topics returned by the backend." />
                    )}
                  </div>
                </Panel>

                <Panel title="Revision queue" subtitle="Spaced repetition due today">
                  <div className="revision-list">
                    {dashboardData.revision_queue?.length ? (
                      dashboardData.revision_queue.map((item) => (
                        <article className="revision-row" key={`${item.title}-${item.cycle}`}>
                          <div>
                            <strong>{item.title}</strong>
                            <span>{item.duration}</span>
                          </div>
                          <b>{item.cycle}</b>
                        </article>
                      ))
                    ) : (
                      <EmptyState message="No revision items returned by the backend." />
                    )}
                  </div>
                </Panel>

                <Panel title="Interview prep" subtitle="AI practice readiness">
                  <div className="interview-grid">
                    {dashboardData.interview_prep?.length ? (
                      dashboardData.interview_prep.map((item) => (
                        <article className="interview-card" key={item.area}>
                          <span>{item.area}</span>
                          <strong>{item.score}</strong>
                          <ProgressBar value={item.progress} tone={item.progress < 65 ? "amber" : "green"} />
                        </article>
                      ))
                    ) : (
                      <EmptyState message="No interview readiness data returned by the backend." />
                    )}
                  </div>
                </Panel>
              </aside>
            </section>
              </>
            )}
            {activeModal === "profile" ? (
              <ProfileModal onClose={() => setActiveModal(null)} onSaved={handleProfileSaved} profile={user?.profile} />
            ) : null}
            {activeModal === "settings" ? (
              <AccountSettingsModal onClose={() => setActiveModal(null)} onSaved={handleProfileSaved} settings={user?.profile} />
            ) : null}
            {activeModal === "schedule" ? (
              <ScheduleModal onClose={() => setActiveModal(null)} onResume={handleResumeLearning} plan={todaysPlan} />
            ) : null}
          </>
        )}
      </main>
    </div>
  );
}

export default Layout;
