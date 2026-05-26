import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  Bot,
  Brain,
  CheckCircle2,
  Code2,
  GraduationCap,
  Moon,
  Route,
  Shield,
  Sparkles,
  Sun,
  Target,
  Timer,
  Zap,
} from 'lucide-react';
import Button from '../components/ui/Button';
import { useTheme } from '../contexts/ThemeContext';
import './landing.css';

const companies = [
  { id: 'tcs', name: 'TCS', readiness: 76, focus: 'Aptitude speed + communication polish', tone: 'green' },
  { id: 'infosys', name: 'Infosys', readiness: 69, focus: 'DBMS, OOP + coding consistency', tone: 'cyan' },
  { id: 'zoho', name: 'Zoho', readiness: 54, focus: 'DSA depth + hands-on rounds', tone: 'amber' },
  { id: 'accenture', name: 'Accenture', readiness: 63, focus: 'Project explanation + verbal confidence', tone: 'violet' },
];

const tracks = [
  { label: 'DSA', value: 72 },
  { label: 'Aptitude', value: 64 },
  { label: 'CS Core', value: 81 },
  { label: 'Interview', value: 58 },
];

const modules = [
  { icon: Route, title: 'Learning path', meta: '10 tracks', copy: 'A clean curriculum map that turns broad placement prep into ordered checkpoints.' },
  { icon: Brain, title: 'Practice engine', meta: '103 drills', copy: 'Topic-wise questions, answer feedback, weak-area detection, and progress updates.' },
  { icon: Timer, title: 'Mock tests', meta: 'Timed proof', copy: 'Realistic tests with scoring, attempt history, and pressure-ready review.' },
  { icon: Code2, title: 'Code lab', meta: 'Python runner', copy: 'Run code, inspect stdout and errors, and keep submission history in one place.' },
  { icon: Bot, title: 'AI interview', meta: 'Instant feedback', copy: 'Technical and behavioral answers scored with actionable coaching.' },
  { icon: BarChart3, title: 'Analytics', meta: 'Live signal', copy: 'Accuracy, streaks, weekly momentum, weak topics, and company readiness.' },
];

const timeline = [
  ['Profile', 'Set academic details, target role, graduation year, and target companies.'],
  ['Diagnose', 'Use mocks and practice history to identify the strongest blockers.'],
  ['Train', 'Follow daily plans across learning, practice, coding, and revision.'],
  ['Prove', 'Validate readiness through tests, interviews, analytics, and company scores.'],
];

function LandingPage() {
  const { theme, toggleTheme } = useTheme();
  const [company, setCompany] = useState(companies[0]);
  const [moduleIndex, setModuleIndex] = useState(0);
  const [pointer, setPointer] = useState({ x: 50, y: 42 });
  const activeModule = modules[moduleIndex];
  const ActiveIcon = activeModule.icon;

  const plan = useMemo(() => {
    const base = Math.max(40, company.readiness - 18);
    return [
      { label: 'Topic confidence', value: base + 7 },
      { label: 'Mock accuracy', value: Math.min(94, company.readiness + 6) },
      { label: 'Interview polish', value: Math.max(38, company.readiness - 12) },
    ];
  }, [company]);

  const handlePointer = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setPointer({
      x: Math.round(((event.clientX - rect.left) / rect.width) * 100),
      y: Math.round(((event.clientY - rect.top) / rect.height) * 100),
    });
  };

  return (
    <div className="landing" onMouseMove={handlePointer} style={{ '--mx': `${pointer.x}%`, '--my': `${pointer.y}%` }}>
      <header className="landing__header">
        <Link to="/" className="landing__brand">
          <span>PS</span>
          <strong>PrepSmart</strong>
        </Link>
        <nav className="landing__nav" aria-label="Homepage sections">
          <a href="#cockpit">Cockpit</a>
          <a href="#platform">Platform</a>
          <a href="#workflow">Workflow</a>
        </nav>
        <div className="landing__actions">
          <button type="button" className="landing__theme" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <Link to="/login" className="landing__signin">Sign in</Link>
          <Link to="/signup"><Button size="sm">Start preparing</Button></Link>
        </div>
      </header>

      <main>
        <section className="landing__hero" id="cockpit">
          <div className="landing__hero-copy">
            <span className="landing__eyebrow"><Sparkles size={16} /> Placement readiness command center</span>
            <h1>Turn placement preparation into a measurable system.</h1>
            <p>
              PrepSmart brings learning paths, practice, mock tests, coding, AI interviews,
              analytics, and company readiness into one focused workspace for students.
            </p>
            <div className="landing__hero-actions">
              <Link to="/signup"><Button size="lg">Start preparing <ArrowRight size={18} /></Button></Link>
              <Link to="/login"><Button variant="secondary" size="lg">Open workspace</Button></Link>
            </div>
          </div>

          <div className="landing__cockpit">
            <div className="landing__cockpit-header">
              <div>
                <span>Target company</span>
                <strong>{company.name}</strong>
              </div>
              <span className={`landing__readiness landing__readiness--${company.tone}`}>{company.readiness}% ready</span>
            </div>

            <div className="landing__company-tabs">
              {companies.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={item.id === company.id ? 'landing__company landing__company--active' : 'landing__company'}
                  onClick={() => setCompany(item)}
                >
                  {item.name}
                </button>
              ))}
            </div>

            <div className="landing__dashboard">
              <div className="landing__dial" style={{ '--score': company.readiness }}>
                <span>{company.readiness}%</span>
                <small>placement readiness</small>
              </div>
              <div className="landing__focus">
                <span>Next best focus</span>
                <strong>{company.focus}</strong>
                <p>Generated from topic progress, attempts, test history, and company goals.</p>
              </div>
            </div>

            <div className="landing__plan">
              {plan.map((item) => (
                <div key={item.label} className="landing__plan-row">
                  <div>
                    <span>{item.label}</span>
                    <strong>{item.value}%</strong>
                  </div>
                  <i><b style={{ width: `${item.value}%` }} /></i>
                </div>
              ))}
            </div>

            <div className="landing__activity">
              <div><Zap size={15} /> Weak topic moved into revision queue</div>
              <div><CheckCircle2 size={15} /> Mock test updated readiness score</div>
              <div><Target size={15} /> Company focus recalculated</div>
            </div>
          </div>
        </section>

        <section className="landing__proof-band">
          <span>10 learning tracks</span>
          <span>48 active topics</span>
          <span>103 practice questions</span>
          <span>Mocks, coding, AI interviews</span>
        </section>

        <section className="landing__platform" id="platform">
          <div className="landing__section-head">
            <span>Platform modules</span>
            <h2>Every feature feeds the readiness model.</h2>
          </div>
          <div className="landing__platform-grid">
            <div className="landing__module-rail">
              {modules.map((module, index) => {
                const Icon = module.icon;
                return (
                  <button
                    key={module.title}
                    type="button"
                    className={index === moduleIndex ? 'landing__module landing__module--active' : 'landing__module'}
                    onClick={() => setModuleIndex(index)}
                  >
                    <Icon size={18} />
                    <span>{module.title}</span>
                    <small>{module.meta}</small>
                  </button>
                );
              })}
            </div>
            <div className="landing__module-stage">
              <div className="landing__module-icon"><ActiveIcon size={32} /></div>
              <span>{activeModule.meta}</span>
              <h3>{activeModule.title}</h3>
              <p>{activeModule.copy}</p>
              <div className="landing__track-grid">
                {tracks.map((track) => (
                  <div key={track.label} className="landing__track">
                    <strong>{track.label}</strong>
                    <span>{track.value}%</span>
                    <i><b style={{ width: `${track.value}%` }} /></i>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="landing__workflow" id="workflow">
          <div className="landing__section-head">
            <span>Daily workflow</span>
            <h2>A serious routine, not another dashboard.</h2>
          </div>
          <div className="landing__timeline">
            {timeline.map(([title, copy], index) => (
              <div key={title} className="landing__timeline-card">
                <span>{String(index + 1).padStart(2, '0')}</span>
                <h3>{title}</h3>
                <p>{copy}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="landing__admin">
          <div>
            <Shield size={26} />
            <h2>Student experience. Admin control. One system.</h2>
            <p>
              Students prepare with clarity. Administrators manage users, curriculum,
              questions, mock tests, and company targets from a dedicated operations portal.
            </p>
          </div>
          <div className="landing__admin-card">
            <GraduationCap size={24} />
            <strong>Built for placement cells</strong>
            <span>Structured preparation, measurable progress, and scalable content control.</span>
          </div>
        </section>
      </main>
    </div>
  );
}

export default LandingPage;
