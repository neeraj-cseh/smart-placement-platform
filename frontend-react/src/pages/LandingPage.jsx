import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  Bot,
  Brain,
  CheckCircle2,
  Code2,
  Moon,
  Play,
  Shield,
  Sparkles,
  Star,
  Sun,
  Target,
  Timer,
  Users,
  Zap,
  Circle,
  Check,
  Award,
  Search,
  Flame,
} from 'lucide-react';
import Button from '../components/ui/Button';
import { useTheme } from '../contexts/ThemeContext';
import './landing.css';

const testimonials = [
  {
    name: 'Priya Sharma',
    role: 'TCS Accepted',
    image: '👩‍💼',
    quote: 'PrepSmart helped me structure my preparation. Got placed in just 3 months!',
    company: 'TCS',
  },
  {
    name: 'Arjun Patel',
    role: 'Infosys Accepted',
    image: '👨‍💼',
    quote: 'The mock tests were incredibly realistic. Felt exactly like the real interview.',
    company: 'Infosys',
  },
  {
    name: 'Neha Gupta',
    role: 'Zoho Accepted',
    image: '👩‍💻',
    quote: 'AI interview feature gave me actual coaching. No other platform has this.',
    company: 'Zoho',
  },
];

const faqs = [
  {
    q: 'How long does it take to prepare?',
    a: 'Most students complete the program in 2-4 months. Our adaptive learning path adjusts to your pace.',
  },
  {
    q: 'Can I prepare for multiple companies?',
    a: 'Yes! Set multiple target companies and get company-specific readiness scores for each.',
  },
  {
    q: 'What if I already have some knowledge?',
    a: 'Take a diagnostic mock test first. We\'ll identify weak areas and create a personalized plan.',
  },
  {
    q: 'Is coding required?',
    a: 'Yes, our code lab supports Python with instant feedback on execution and edge cases.',
  },
  {
    q: 'Can I track my progress?',
    a: 'Absolutely! Real-time analytics show accuracy, streaks, momentum, weak topics, and company readiness.',
  },
  {
    q: 'What if I don\'t get placed?',
    a: 'We\'re confident in our system. Start free and see the results yourself.',
  },
];

const stats = [
  { label: 'Total Offers Tracked', value: '₹3.5Cr+', icon: Award },
  { label: 'Students Preparing', value: '12,000+', icon: Users },
  { label: 'Student Satisfaction', value: '4.9/5', icon: Star },
  { label: 'Avg. Time to Offer', value: '3 Months', icon: Timer },
];

const modules = [
  {
    icon: Brain,
    title: 'Learning Paths',
    description: 'Structured curriculum maps from basics to advanced concepts across all topics.',
    features: ['10 tracks', 'Ordered checkpoints', 'Video-backed content'],
  },
  {
    icon: Target,
    title: 'Practice Engine',
    description: 'Topic-wise questions with AI feedback, weak-area detection, and progress tracking.',
    features: ['103+ drills', 'Topic-wise', 'AI feedback'],
  },
  {
    icon: Timer,
    title: 'Mock Tests',
    description: 'Realistic timed tests with scoring, history, and pressure-ready review.',
    features: ['Timed tests', 'Score tracking', 'Review history'],
  },
  {
    icon: Code2,
    title: 'Code Lab',
    description: 'Run code instantly, inspect output, handle errors, and keep submission history.',
    features: ['Python runner', 'Instant feedback', 'Submission history'],
  },
  {
    icon: Bot,
    title: 'AI Interview',
    description: 'Technical and behavioral mock interviews with instant, actionable coaching.',
    features: ['AI coaching', 'Real-time feedback', 'Score analysis'],
  },
  {
    icon: BarChart3,
    title: 'Analytics',
    description: 'Live dashboard with accuracy, streaks, momentum, weak topics, and company scores.',
    features: ['Live metrics', 'Company readiness', 'Trend analysis'],
  },
];



const practiceQuestions = [
  {
    q: "Given an array of integers, return true if any value appears at least twice in the array.",
    opts: [
      { key: 'A', text: 'O(N^2) Time, O(1) Space', correct: false },
      { key: 'B', text: 'O(N) Time, O(N) Space (Hash Set)', correct: true },
      { key: 'C', text: 'O(N log N) Time, O(N) Space', correct: false }
    ],
    hint: "Using a nested loop takes quadratic time. A hash set tracks seen numbers in constant time, sacrificing linear space."
  },
  {
    q: "What is the worst-case lookup complexity in a balanced Binary Search Tree (BST)?",
    opts: [
      { key: 'A', text: 'O(1) Constant Time', correct: false },
      { key: 'B', text: 'O(N) Linear Time', correct: false },
      { key: 'C', text: 'O(log N) Logarithmic Time', correct: true }
    ],
    hint: "In a balanced BST, each step down the tree splits the search space in half. Hence, depth is proportional to log2(N)."
  },
  {
    q: "Which HTTP method is best suited for idempotent updates to an existing resource?",
    opts: [
      { key: 'A', text: 'POST (Non-idempotent)', correct: false },
      { key: 'B', text: 'PUT (Idempotent)', correct: true },
      { key: 'C', text: 'PATCH (Not necessarily idempotent)', correct: false }
    ],
    hint: "PUT replaces the resource entirely and is idempotent. Repeated PUT requests have the same side effect as a single request."
  }
];

const codeTemplates = {
  contains_duplicate: {
    label: "Contains Duplicate",
    code: `# Python 3
def contains_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

print(contains_duplicate([1, 2, 3, 1]))`,
    runResult: {
      stdout: "> True",
      details: "Test case 1 [1,2,3,1]: Passed (Expected: True, Got: True)\nTest case 2 [1,2,3,4]: Passed (Expected: False, Got: False)\nAll edge cases verified successfully."
    }
  },
  two_sum: {
    label: "Two Sum",
    code: `# Python 3
def two_sum(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in lookup:
            return [lookup[diff], i]
        lookup[num] = i
    return []

print(two_sum([2, 7, 11, 15], 9))`,
    runResult: {
      stdout: "> [0, 1]",
      details: "Test case 1 [2,7,11,15], target 9: Passed (Expected: [0,1], Got: [0,1])\nTest case 2 [3,2,4], target 6: Passed (Expected: [1,2], Got: [1,2])\nAll tests green."
    }
  },
  fibonacci: {
    label: "Fibonacci Number",
    code: `# Python 3
def fib(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

print(fib(10))`,
    runResult: {
      stdout: "> 55",
      details: "Test case 1 (n=2): Passed (Expected: 1, Got: 1)\nTest case 2 (n=10): Passed (Expected: 55, Got: 55)\nComplexity: O(N) Time, O(1) Space."
    }
  }
};

const interviewScenarios = {
  team_conflict: {
    q: "AI Interviewer: How do you handle disagreements in code reviews?",
    area: "Behavioral Round",
    opts: [
      {
        text: "I explain my rationale clearly with references to clean code guides and discuss it calmly.",
        score: 17,
        feedback: "Excellent behavior! Good focus on collaboration. Suggest referencing a specific instance where you compromised to show adaptability."
      },
      {
        text: "I stand my ground if I know my code is more optimal, because performance and code quality are the ultimate goals.",
        score: 11,
        feedback: "A bit rigid. While technical excellence is good, team collaboration and compromise are highly valued in production environments. Try to show openness."
      }
    ]
  },
  join_reason: {
    q: "AI Interviewer: Why do you want to join our engineering team?",
    area: "Motivation Round",
    opts: [
      {
        text: "I want to work with your tech stack at scale and contribute to your flagship product's reliability.",
        score: 18,
        feedback: "Great answer! Shows alignment with company engineering challenges. Mentioning specific scale metrics of the company could make this a 20/20 answer."
      },
      {
        text: "I am looking for a stable job where I can learn new skills and get career advancement.",
        score: 12,
        feedback: "A bit self-centered. It's good to want to learn, but companies also want to hear what value you bring to their products and customers immediately."
      }
    ]
  }
};

const companyThresholds = {
  Amazon: { dsa: 85, aptitude: 75, cs: 80, comm: 70, projects: 80 },
  Google: { dsa: 92, aptitude: 80, cs: 85, comm: 75, projects: 80 },
  Microsoft: { dsa: 88, aptitude: 78, cs: 82, comm: 72, projects: 85 },
  TCS: { dsa: 50, aptitude: 65, cs: 50, comm: 60, projects: 45 },
  Infosys: { dsa: 55, aptitude: 60, cs: 55, comm: 58, projects: 50 },
  Zoho: { dsa: 75, aptitude: 65, cs: 60, comm: 55, projects: 70 }
};

const skillGalaxyNodes = [
  { id: 'dsa', label: 'Data Structures & Algorithms', x: 300, y: 80, pct: 85, color: '#3b82f6', desc: 'Arrays, Trees, Graphs, Dynamic Programming.' },
  { id: 'os', label: 'Operating Systems', x: 120, y: 180, pct: 70, color: '#ec4899', desc: 'Process management, virtual memory, threads.' },
  { id: 'dbms', label: 'Database Systems', x: 180, y: 340, pct: 75, color: '#f59e0b', desc: 'Normalization models, transactions, ACID.' },
  { id: 'sql', label: 'SQL Queries', x: 300, y: 380, pct: 80, color: '#10b981', desc: 'Complex Joins, window functions, aggregations.' },
  { id: 'webdev', label: 'Web Development', x: 420, y: 340, pct: 60, color: '#8b5cf6', desc: 'Semantic HTML, CSS variables, React state.' },
  { id: 'aptitude', label: 'Aptitude & Logic', x: 480, y: 180, pct: 90, color: '#06b6d4', desc: 'Logical puzzles, percentages, ratios speed.' },
  { id: 'comm', label: 'Communication', x: 400, y: 80, pct: 65, color: '#a855f7', desc: 'STAR technique, structured answers, active focus.' },
  { id: 'projects', label: 'Projects & Core', x: 300, y: 220, pct: 72, color: '#f43f5e', desc: 'Architecture trade-offs, deployment, outcomes.' },
];

const skillGalaxyConnections = [
  { from: 'dsa', to: 'projects' },
  { from: 'comm', to: 'projects' },
  { from: 'os', to: 'dsa' },
  { from: 'dbms', to: 'sql' },
  { from: 'sql', to: 'webdev' },
  { from: 'webdev', to: 'projects' },
  { from: 'aptitude', to: 'dsa' },
];

const activityFeedItems = [
  { id: 1, user: 'Rahul K.', action: 'completed the Graphs milestone', time: 'Just now', avatar: '👨‍💻', track: 'DSA' },
  { id: 2, user: 'Ananya S.', action: 'cleared Amazon OA checkpoint', time: '2 mins ago', avatar: '👩‍💻', track: 'Mock Tests' },
  { id: 3, user: 'Priya D.', action: 'reached 30-day preparation streak!', time: '5 mins ago', avatar: '👩‍💼', track: 'Platform' },
  { id: 4, user: 'Karan M.', action: 'improved readiness index by 14%', time: '8 mins ago', avatar: '👨‍💼', track: 'Analytics' },
  { id: 5, user: 'Amit B.', action: 'submitted Contains Duplicate in Code Lab', time: '12 mins ago', avatar: '🧑‍💻', track: 'Code Lab' },
];



const Counter = ({ end, duration = 2000 }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let current = 0;
    // Handle potential string counts (like metrics with + or Cr)
    const numericEnd = typeof end === 'string' ? parseFloat(end.replace(/[^0-9.]/g, '')) : end;
    if (isNaN(numericEnd)) {
      setCount(end);
      return;
    }
    const increment = numericEnd / (duration / 16);
    const timer = setInterval(() => {
      current += increment;
      if (current >= numericEnd) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [end, duration]);

  return <>{count.toLocaleString()}</>;
};

const AI_STATUS_PHRASES = [
  "Analyzing placement readiness...",
  "Generating Amazon preparation roadmap...",
  "Detecting weak areas in Graphs & Trees...",
  "Simulating Online Assessment (OA) pass probability...",
  "Formulating behavioral interview response logs..."
];

export default function LandingPage() {
  const { theme, toggleTheme } = useTheme();
  const [expandedFaq, setExpandedFaq] = useState(0);
  const [visibleModule, setVisibleModule] = useState(0);

  const [coords, setCoords] = useState({ x: 50, y: 50 });
  const [mockTimer, setMockTimer] = useState(1799); // 29m 59s
  const [mockCodeRunState, setMockCodeRunState] = useState('idle');

  // Hero Simulator States
  const [heroCompany, setHeroCompany] = useState('Amazon');
  const [sliderDSA, setSliderDSA] = useState(65);
  const [sliderAptitude, setSliderAptitude] = useState(70);
  const [sliderCS, setSliderCS] = useState(60);
  const [sliderComm, setSliderComm] = useState(55);
  const [sliderProjects, setSliderProjects] = useState(50);

  // Learning Path Widget State
  const [completedCheckpoints, setCompletedCheckpoints] = useState([true, false, false]);

  // Practice Widget States
  const [practiceQIndex, setPracticeQIndex] = useState(0);
  const [practiceAnswer, setPracticeAnswer] = useState(null);
  const [practiceStreak, setPracticeStreak] = useState(2);
  const [practiceShowHint, setPracticeShowHint] = useState(false);

  // Mock Test Widget States
  const [mockTestSubmitted, setMockTestSubmitted] = useState(false);
  const [mockTestAnswers, setMockTestAnswers] = useState({});
  const [mockTestActiveQ, setMockTestActiveQ] = useState(0);

  // Code Lab Snippet State
  const [codeSnippetKey, setCodeSnippetKey] = useState('contains_duplicate');
  const [codeRunCustomDetails, setCodeRunCustomDetails] = useState('');

  // AI Interview States
  const [interviewQKey, setInterviewQKey] = useState('team_conflict');
  const [interviewAnswerIndex, setInterviewAnswerIndex] = useState(null);
  const [interviewHistory, setInterviewHistory] = useState([]);
  const [interviewTyping, setInterviewTyping] = useState(false);

  // Analytics Filter State
  const [analyticsPeriod, setAnalyticsPeriod] = useState('all');

  // FAQ Search & Category State
  const [faqSearch, setFaqSearch] = useState('');
  const [faqCategory, setFaqCategory] = useState('all');

  // Skill Galaxy Active Node State
  const [activeGalaxyNode, setActiveGalaxyNode] = useState(skillGalaxyNodes[0]);

  // AI Typing Status loop
  const [aiStatusText, setAiStatusText] = useState('');
  const [phraseIdx, setPhraseIdx] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [typingSpeed, setTypingSpeed] = useState(100);

  // Typewriter effect
  useEffect(() => {
    let timer;
    const currentPhrase = AI_STATUS_PHRASES[phraseIdx];
    
    if (isDeleting) {
      timer = setTimeout(() => {
        setAiStatusText(currentPhrase.substring(0, aiStatusText.length - 1));
        setTypingSpeed(40);
      }, typingSpeed);
    } else {
      timer = setTimeout(() => {
        setAiStatusText(currentPhrase.substring(0, aiStatusText.length + 1));
        setTypingSpeed(80);
      }, typingSpeed);
    }

    if (!isDeleting && aiStatusText === currentPhrase) {
      timer = setTimeout(() => setIsDeleting(true), 2000);
    } else if (isDeleting && aiStatusText === '') {
      setIsDeleting(false);
      setPhraseIdx((prev) => (prev + 1) % AI_STATUS_PHRASES.length);
      setTypingSpeed(300);
    }

    return () => clearTimeout(timer);
  }, [aiStatusText, isDeleting, phraseIdx, typingSpeed]);

  // Rolling feed timer removed for smooth CSS marquee ticker

  const handleMouseMove = (e) => {
    const x = (e.clientX / window.innerWidth) * 100;
    const y = (e.clientY / window.innerHeight) * 100;
    setCoords({ x, y });
  };

  const handleCardMouseMove = (e) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const xc = rect.width / 2;
    const yc = rect.height / 2;
    const dx = x - xc;
    const dy = y - yc;
    const rx = -(dy / yc) * 8;
    const ry = (dx / xc) * 8;
    card.style.setProperty('--rx', `${rx}deg`);
    card.style.setProperty('--ry', `${ry}deg`);
  };

  const handleCardMouseLeave = (e) => {
    const card = e.currentTarget;
    card.style.setProperty('--rx', '0deg');
    card.style.setProperty('--ry', '0deg');
  };

  useEffect(() => {
    const glow = document.getElementById('cursorGlow');
    if (!glow) return;
    const handleMove = (e) => {
      glow.style.left = `${e.clientX}px`;
      glow.style.top = `${e.clientY}px`;
    };
    window.addEventListener('mousemove', handleMove);
    return () => window.removeEventListener('mousemove', handleMove);
  }, []);

  useEffect(() => {
    if (visibleModule !== 2) return;
    const interval = setInterval(() => {
      setMockTimer((prev) => (prev > 0 ? prev - 1 : 1799));
    }, 1000);
    return () => clearInterval(interval);
  }, [visibleModule]);

  useEffect(() => {
    setMockCodeRunState('idle');
    setPracticeAnswer(null);
    setPracticeShowHint(false);
    setMockTestSubmitted(false);
    setMockTestAnswers({});
    setMockTestActiveQ(0);
    setInterviewAnswerIndex(null);
    setInterviewHistory([]);
    setInterviewTyping(false);
  }, [visibleModule]);

  const runMockCode = () => {
    setMockCodeRunState('running');
    setTimeout(() => {
      setMockCodeRunState('success');
      setCodeRunCustomDetails(codeTemplates[codeSnippetKey].runResult.details);
    }, 1000);
  };

  const handleSelectPracticeAnswer = (key, isCorrect) => {
    setPracticeAnswer(key);
    if (isCorrect) {
      setPracticeStreak(prev => prev + 1);
    } else {
      setPracticeStreak(0);
    }
  };

  const handleSelectMockTestAnswer = (qIdx, key) => {
    setMockTestAnswers(prev => ({ ...prev, [qIdx]: key }));
  };

  const handleSelectInterviewAnswer = (idx) => {
    if (interviewTyping) return;
    setInterviewAnswerIndex(idx);
    
    const scenario = interviewScenarios[interviewQKey];
    const selectedOpt = scenario.opts[idx];
    
    setInterviewHistory([{ sender: 'user', text: selectedOpt.text }]);
    
    setInterviewTyping(true);
    setTimeout(() => {
      setInterviewHistory(prev => [
        ...prev,
        {
          sender: 'ai-feedback',
          score: selectedOpt.score,
          feedback: selectedOpt.feedback
        }
      ]);
      setInterviewTyping(false);
    }, 1000);
  };

  const handleSelectInterviewQuestion = (key) => {
    setInterviewQKey(key);
    setInterviewAnswerIndex(null);
    setInterviewHistory([]);
    setInterviewTyping(false);
  };

  const toggleCheckpoint = (idx) => {
    setCompletedCheckpoints(prev => {
      const next = [...prev];
      next[idx] = !next[idx];
      return next;
    });
  };

  const formatMockTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const getAnalyticsData = () => {
    if (analyticsPeriod === 'week') {
      return { dsa: 72, aptitude: 80, db: 60, badge: 'Progressing Fast' };
    } else if (analyticsPeriod === 'month') {
      return { dsa: 81, aptitude: 88, db: 68, badge: 'Highly Competitive' };
    }
    return { dsa: 85, aptitude: 92, db: 70, badge: 'Placed Ready' };
  };

  // SVG Radar Path generator
  const getRadarPath = (skillsObject) => {
    const keys = ['dsa', 'aptitude', 'cs', 'comm', 'projects'];
    return keys.map((key, i) => {
      const val = skillsObject[key] || 0;
      const angle = (i * 2 * Math.PI) / 5 - Math.PI / 2;
      const x = 100 + 70 * (val / 100) * Math.cos(angle);
      const y = 100 + 70 * (val / 100) * Math.sin(angle);
      return `${x},${y}`;
    }).join(' ');
  };

  // Dynamic calculations for readiness simulator
  const activeThresholds = companyThresholds[heroCompany];
  const matchDSA = Math.min(100, Math.round((sliderDSA / activeThresholds.dsa) * 100));
  const matchAptitude = Math.min(100, Math.round((sliderAptitude / activeThresholds.aptitude) * 100));
  const matchCS = Math.min(100, Math.round((sliderCS / activeThresholds.cs) * 100));
  const matchComm = Math.min(100, Math.round((sliderComm / activeThresholds.comm) * 100));
  const matchProjects = Math.min(100, Math.round((sliderProjects / activeThresholds.projects) * 100));

  const totalReadiness = Math.round(
    (matchDSA * 0.35) + 
    (matchAptitude * 0.20) + 
    (matchCS * 0.15) + 
    (matchComm * 0.15) + 
    (matchProjects * 0.15)
  );

  const oaPassProbability = Math.round((matchDSA * 0.6) + (matchAptitude * 0.4));
  const interviewReadinessIndex = Math.round((matchProjects * 0.4) + (matchComm * 0.3) + (matchCS * 0.3));

  const simulatorWeaknesses = [];
  if (sliderDSA < activeThresholds.dsa) simulatorWeaknesses.push("DSA Core");
  if (sliderAptitude < activeThresholds.aptitude) simulatorWeaknesses.push("Aptitude Speed");
  if (sliderCS < activeThresholds.cs) simulatorWeaknesses.push("CS Core");
  if (sliderComm < activeThresholds.comm) simulatorWeaknesses.push("Communication");
  if (sliderProjects < activeThresholds.projects) simulatorWeaknesses.push("Project Outcomes");

  const weaknessText = simulatorWeaknesses.length > 0 ? simulatorWeaknesses.slice(0, 2).join(' & ') : "All criteria matched!";
  const recommendationText = simulatorWeaknesses.length > 0 
    ? `Solve 5+ drills in ${simulatorWeaknesses[0]} to close target gap.`
    : "Review complex mock tests to lock down final index.";

  const pathProgress = Math.round((completedCheckpoints.filter(Boolean).length / completedCheckpoints.length) * 100);

  return (
    <div className="landing" onMouseMove={handleMouseMove} style={{ '--mx': `${coords.x}%`, '--my': `${coords.y}%` }}>
      <div className="cursor-glow" id="cursorGlow" />
      {/* Background blobs and grid overlays */}
      <div className="landing__blob landing__blob--1" style={{ transform: `translate(${(coords.x - 50) * 0.15}px, ${(coords.y - 50) * 0.15}px)` }} />
      <div className="landing__blob landing__blob--2" style={{ transform: `translate(${(coords.x - 50) * -0.15}px, ${(coords.y - 50) * -0.15}px)` }} />
      <div className="landing__grid-texture" />

      {/* Header */}
      <header className="landing__header">
        <Link to="/" className="landing__brand">
          <span>PS</span>
          <strong>PrepSmart</strong>
        </Link>
        <nav className="landing__nav" aria-label="Navigation">
          <a href="#features">Features</a>
          <a href="#simulator">Readiness Console</a>
          <a href="#galaxy">Skill Galaxy</a>
          <a href="#workflow">Workflow</a>
          <a href="#faq">FAQ</a>
        </nav>
        <div className="landing__actions">
          <button type="button" className="landing__theme" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <Link to="/login" className="landing__signin">Sign in</Link>
          <Link to="/signup"><Button size="sm">Get Started</Button></Link>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="landing__hero">
          <div className="landing__hero-copy">
            <div className="landing__eyebrow">
              <Sparkles size={16} /> <span>Your AI Placement Command Center</span>
            </div>
            <h1>Get placement-ready, guided by AI.</h1>
            <p>
              An intelligent, adaptive operating system combining curriculum roadmaps, timed mock tests, 
              live coding sandboxes, and behavioral AI interview coaches to prepare you for top careers.
            </p>
            
            {/* AI Typing text panel */}
            <div className="hero-status-panel">
              <span className="hero-status-panel__pulse" />
              <span className="hero-status-panel__text">{aiStatusText}</span>
            </div>

            <div className="landing__hero-actions">
              <Link to="/signup"><Button size="lg">Start Free Assessment <ArrowRight size={18} /></Button></Link>
              <a href="#features"><Button variant="secondary" size="lg"><Play size={18} /> Explore Features</Button></a>
            </div>
            <div className="landing__hero-social">
              <span>⭐ Join 12,000+ students already preparing</span>
            </div>
          </div>
 
          <div className="landing__hero-visual">
            <div className="hero-preview-hud">
              {/* Glass dashboard chrome card */}
              <div className="hud-card hud-card--main" onMouseMove={handleCardMouseMove} onMouseLeave={handleCardMouseLeave} style={{ '--tx': `${(coords.x - 50) * 0.05}px`, '--ty': `${(coords.y - 50) * 0.05}px` }}>
                <div className="hud-card__header">
                  <span>MOCK ASSESSMENT ANALYSIS</span>
                  <span className="badge badge--green">Live</span>
                </div>
                <div className="hud-card__gauge-row">
                  <div className="circle-gauge">
                    <svg viewBox="0 0 36 36">
                      <path className="circle-gauge__bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                      <path className="circle-gauge__fill" strokeDasharray="85, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    </svg>
                    <div className="circle-gauge__text">85%</div>
                  </div>
                  <div className="hud-card__stats">
                    <div className="hud-card__stat-item">
                      <span>OA PROBABILITY</span>
                      <strong>92% (High)</strong>
                    </div>
                    <div className="hud-card__stat-item">
                      <span>STREAK</span>
                      <strong style={{ color: '#f97316' }}>🔥 12 Days</strong>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating detail panels */}
              <div className="hud-card hud-card--floating-1" onMouseMove={handleCardMouseMove} onMouseLeave={handleCardMouseLeave} style={{ '--tx': `${(coords.x - 50) * -0.06}px`, '--ty': `${(coords.y - 50) * 0.06}px` }}>
                <CheckCircle2 size={16} style={{ color: 'var(--accent-success)' }} />
                <div>
                  <strong>Target Unlocked</strong>
                  <span>Amazon criteria met</span>
                </div>
              </div>

              <div className="hud-card hud-card--floating-2" onMouseMove={handleCardMouseMove} onMouseLeave={handleCardMouseLeave} style={{ '--tx': `${(coords.x - 50) * 0.08}px`, '--ty': `${(coords.y - 50) * -0.08}px` }}>
                <Brain size={16} style={{ color: 'var(--accent-primary)' }} />
                <div>
                  <strong>Next Focus</strong>
                  <span>Two Pointers & Sliding Window</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Band */}
        <section className="landing__stats-band">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="landing__stat">
                <Icon size={24} />
                <div className="landing__stat-value">
                  <Counter end={stat.value} />
                </div>
                <div className="landing__stat-label">{stat.label}</div>
              </div>
            );
          })}
        </section>

        {/* AI Readiness Simulator Section */}
        <section className="landing__simulator-section" id="simulator">
          <div className="landing__section-head text-center" style={{ margin: '0 auto 48px', textAlign: 'center' }}>
            <span>Dynamic Engine</span>
            <h2>AI Readiness Simulator</h2>
            <p>Drag the sliders representing your current skills to calculate readiness indexes for major roles.</p>
          </div>

          <div className="simulator-console">
            {/* Left sliders controls */}
            <div className="simulator-console__controls">
              <div className="simulator-console__company-select">
                <span>Select Target Company:</span>
                <div className="hero-sim__tabs" style={{ marginTop: 8 }}>
                  {['Amazon', 'Google', 'Microsoft', 'TCS', 'Infosys', 'Zoho'].map((comp) => (
                    <button
                      key={comp}
                      type="button"
                      className={`hero-sim__tab ${heroCompany === comp ? 'active' : ''}`}
                      onClick={() => setHeroCompany(comp)}
                    >
                      {comp}
                    </button>
                  ))}
                </div>
              </div>

              <div className="simulator-console__sliders-list">
                <div className="hero-sim__slider-group">
                  <div className="hero-sim__slider-label"><span>Data Structures & Algorithms</span><strong>{sliderDSA}%</strong></div>
                  <input type="range" min="10" max="100" value={sliderDSA} onChange={(e) => setSliderDSA(Number(e.target.value))} className="hero-sim__slider" style={{ '--val': `${(sliderDSA - 10) / 90 * 100}%` }} />
                </div>
                <div className="hero-sim__slider-group">
                  <div className="hero-sim__slider-label"><span>Quantitative Aptitude</span><strong>{sliderAptitude}%</strong></div>
                  <input type="range" min="10" max="100" value={sliderAptitude} onChange={(e) => setSliderAptitude(Number(e.target.value))} className="hero-sim__slider" style={{ '--val': `${(sliderAptitude - 10) / 90 * 100}%` }} />
                </div>
                <div className="hero-sim__slider-group">
                  <div className="hero-sim__slider-label"><span>CS Core Fundamentals</span><strong>{sliderCS}%</strong></div>
                  <input type="range" min="10" max="100" value={sliderCS} onChange={(e) => setSliderCS(Number(e.target.value))} className="hero-sim__slider" style={{ '--val': `${(sliderCS - 10) / 90 * 100}%` }} />
                </div>
                <div className="hero-sim__slider-group">
                  <div className="hero-sim__slider-label"><span>Technical Communication</span><strong>{sliderComm}%</strong></div>
                  <input type="range" min="10" max="100" value={sliderComm} onChange={(e) => setSliderComm(Number(e.target.value))} className="hero-sim__slider" style={{ '--val': `${(sliderComm - 10) / 90 * 100}%` }} />
                </div>
                <div className="hero-sim__slider-group">
                  <div className="hero-sim__slider-label"><span>Projects & Development</span><strong>{sliderProjects}%</strong></div>
                  <input type="range" min="10" max="100" value={sliderProjects} onChange={(e) => setSliderProjects(Number(e.target.value))} className="hero-sim__slider" style={{ '--val': `${(sliderProjects - 10) / 90 * 100}%` }} />
                </div>
              </div>
            </div>

            {/* Right radar and results */}
            <div className="simulator-console__results">
              <div className="simulator-console__radar">
                <svg viewBox="0 0 200 200" className="radar-svg">
                  {/* Pentagonal grids */}
                  {[20, 40, 60, 80, 100].map((level) => {
                    const keys = ['dsa', 'aptitude', 'cs', 'comm', 'projects'];
                    const pathPoints = keys.map((_, i) => {
                      const angle = (i * 2 * Math.PI) / 5 - Math.PI / 2;
                      const x = 100 + 70 * (level / 100) * Math.cos(angle);
                      const y = 100 + 70 * (level / 100) * Math.sin(angle);
                      return `${x},${y}`;
                    }).join(' ');
                    return (
                      <polygon
                        key={level}
                        points={pathPoints}
                        className="radar-grid-line"
                      />
                    );
                  })}
                  {/* Web spokes lines */}
                  {[0, 1, 2, 3, 4].map((i) => {
                    const angle = (i * 2 * Math.PI) / 5 - Math.PI / 2;
                    const x = 100 + 70 * Math.cos(angle);
                    const y = 100 + 70 * Math.sin(angle);
                    return (
                      <line
                        key={i}
                        x1="100"
                        y1="100"
                        x2={x}
                        y2={y}
                        className="radar-web-spoke"
                      />
                    );
                  })}
                  {/* Threshold required polygon */}
                  <polygon
                    points={getRadarPath(activeThresholds)}
                    className="radar-poly-threshold"
                  />
                  {/* Student actual polygon */}
                  <polygon
                    points={getRadarPath({ dsa: sliderDSA, aptitude: sliderAptitude, cs: sliderCS, comm: sliderComm, projects: sliderProjects })}
                    className="radar-poly-student"
                  />
                </svg>
                <div className="radar-labels-legend">
                  <span className="legend-item legend-item--student">Actual Profile</span>
                  <span className="legend-item legend-item--threshold">{heroCompany} Target</span>
                </div>
              </div>

              <div className="simulator-console__scores-summary">
                <div className="scores-metrics-grid">
                  <div className="score-badge">
                    <span>READINESS INDEX</span>
                    <strong style={{ color: totalReadiness >= 80 ? 'var(--green)' : totalReadiness >= 50 ? 'var(--amber)' : 'var(--red)' }}>
                      {totalReadiness}%
                    </strong>
                  </div>
                  <div className="score-badge">
                    <span>OA PASS RATE</span>
                    <strong>{oaPassProbability}%</strong>
                  </div>
                  <div className="score-badge">
                    <span>INTERVIEW FIT</span>
                    <strong>{interviewReadinessIndex}%</strong>
                  </div>
                </div>

                <div className="sim-diagnostic-details">
                  <div className="diagnostic-row">
                    <span>Target Weakness:</span>
                    <strong>{weaknessText}</strong>
                  </div>
                  <div className="diagnostic-row">
                    <span>AI Recommendation:</span>
                    <strong style={{ color: 'var(--text-primary)' }}>{recommendationText}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Skill Galaxy Section */}
        <section className="landing__galaxy-section" id="galaxy">
          <div className="landing__section-head text-center" style={{ margin: '0 auto 48px', textAlign: 'center' }}>
            <span>Roadmap</span>
            <h2>Interactive Skill Galaxy</h2>
            <p>Click nodes on our connected constellation roadmap to reveal milestone details and completion stats.</p>
          </div>

          <div className="skill-galaxy-layout">
            <div className="skill-galaxy-canvas">
              <svg viewBox="0 0 600 450" className="skill-galaxy__svg">
                <defs>
                  <filter id="node-glow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="5" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                {/* Connections */}
                {skillGalaxyConnections.map((conn, idx) => {
                  const fromNode = skillGalaxyNodes.find(n => n.id === conn.from);
                  const toNode = skillGalaxyNodes.find(n => n.id === conn.to);
                  return (
                    <line
                      key={idx}
                      x1={fromNode.x}
                      y1={fromNode.y}
                      x2={toNode.x}
                      y2={toNode.y}
                      className="skill-galaxy__line"
                    />
                  );
                })}
                
                {/* Connected nodes */}
                {skillGalaxyNodes.map((node) => {
                  const isActive = activeGalaxyNode?.id === node.id;
                  return (
                    <g
                      key={node.id}
                      className={`skill-galaxy__node-group ${isActive ? 'active' : ''}`}
                      onClick={() => setActiveGalaxyNode(node)}
                    >
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={22}
                        className="skill-galaxy__node-glow"
                        style={{ fill: node.color }}
                        filter="url(#node-glow)"
                      />
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={12}
                        className="skill-galaxy__node-circle"
                        style={{ stroke: node.color }}
                      />
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={6}
                        className="skill-galaxy__node-dot"
                        style={{ fill: node.color }}
                      />
                      <text
                        x={node.x}
                        y={node.y + 32}
                        textAnchor="middle"
                        className="skill-galaxy__node-text"
                      >
                        {node.id.toUpperCase()} ({node.pct}%)
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Float details panel card */}
            <div className="skill-galaxy-details">
              <div className="galaxy-detail-card">
                <div className="galaxy-detail-card__header" style={{ borderBottomColor: activeGalaxyNode.color }}>
                  <h3 style={{ color: activeGalaxyNode.color }}>{activeGalaxyNode.label}</h3>
                  <span className="badge badge--green">{activeGalaxyNode.pct}% Complete</span>
                </div>
                <div className="galaxy-detail-card__body">
                  <p className="description">{activeGalaxyNode.desc}</p>
                  
                  <div className="galaxy-requirements">
                    <span>GATEWAY TARGETS</span>
                    <ul className="galaxy-check-list">
                      <li><Check size={14} style={{ color: 'var(--green)' }} /> <span>Basics & Theory</span></li>
                      <li><Check size={14} style={{ color: 'var(--green)' }} /> <span>Medium Drills solved</span></li>
                      <li><Circle size={14} style={{ color: 'var(--text-muted)' }} /> <span>Advanced mock assessment challenges</span></li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid Cockpit */}
        <section className="landing__features" id="features">
          <div className="landing__section-head">
            <span>Core Modules</span>
            <h2>Everything you need, nothing you don't.</h2>
          </div>

          <div className="landing__features-grid">
            {modules.map((module, idx) => {
              const Icon = module.icon;
              return (
                <div
                  key={module.title}
                  className={`landing__feature-card ${visibleModule === idx ? 'active' : ''}`}
                  onClick={() => setVisibleModule(idx)}
                  onMouseMove={handleCardMouseMove}
                  onMouseLeave={handleCardMouseLeave}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => e.key === 'Enter' && setVisibleModule(idx)}
                >
                  <div className="landing__feature-icon">
                    <Icon size={28} />
                  </div>
                  <h3>{module.title}</h3>
                  <p>{module.description}</p>
                  <div className="landing__feature-tags">
                    {module.features.map((f) => (
                      <span key={f} className="landing__tag">{f}</span>
                    ))}
                  </div>
                  <ArrowRight size={16} className="landing__feature-arrow" />
                </div>
              );
            })}
          </div>

          {/* Interactive Preview Cockpit */}
          <div className="landing__cockpit-container">
            <div className="landing__cockpit-window">
              <div className="landing__cockpit-chrome">
                <div className="landing__chrome-dots">
                  <span />
                  <span />
                  <span />
                </div>
                <div className="landing__chrome-address">
                  prepsmart.dev / cockpit / {modules[visibleModule].title.toLowerCase().replace(' ', '-')}
                </div>
              </div>
              <div className="landing__cockpit-body">
                {visibleModule === 0 && (
                  <div className="cockpit-widget cockpit-widget--paths">
                    <div className="cockpit-widget__head">
                      <h4>Learning Path: Data Structures & Algorithms</h4>
                      <span>{pathProgress}% completed</span>
                    </div>
                    <div className="cockpit-widget__progress">
                      <div className="cockpit-progress-bar">
                        <div className="cockpit-progress-bar__fill" style={{ width: `${pathProgress}%` }} />
                      </div>
                    </div>
                    <div className="cockpit-widget__list">
                      {[
                        { title: 'Array & String Basics', checkpoint: 'Checkpoint 1' },
                        { title: 'Two Pointers & Sliding Window', checkpoint: 'Checkpoint 2' },
                        { title: 'Binary Search Tree', checkpoint: 'Checkpoint 3' }
                      ].map((chk, cIdx) => (
                        <div
                          key={cIdx}
                          className={`cockpit-widget__item ${completedCheckpoints[cIdx] ? 'cockpit-widget__item--completed' : 'cockpit-widget__item--locked'}`}
                          onClick={() => toggleCheckpoint(cIdx)}
                          style={{ cursor: 'pointer' }}
                        >
                          <input
                            type="checkbox"
                            checked={completedCheckpoints[cIdx]}
                            onChange={() => {}}
                            style={{ pointerEvents: 'none' }}
                          />
                          <span>{chk.title}</span>
                          <span className={`cockpit-widget__badge ${completedCheckpoints[cIdx] ? 'cockpit-widget__badge--active' : ''}`}>
                            {chk.checkpoint}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {visibleModule === 1 && (
                  <div className="cockpit-widget cockpit-widget--practice">
                    <div className="cockpit-widget__head">
                      <h4>Topic: {practiceQIndex === 0 ? 'Arrays & Hashing' : practiceQIndex === 1 ? 'Trees & BST' : 'HTTP/APIs'}</h4>
                      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <span className="practice-streak">
                          <Flame size={14} style={{ fill: 'currentColor' }} /> Streak: {practiceStreak}
                        </span>
                        <span className="badge badge--amber">Medium</span>
                      </div>
                    </div>
                    <p className="cockpit-widget__question">{practiceQuestions[practiceQIndex].q}</p>
                    <div className="cockpit-widget__options">
                      {practiceQuestions[practiceQIndex].opts.map((opt) => {
                        const isSelected = practiceAnswer === opt.key;
                        const isCorrectOpt = opt.correct;
                        const optionClass = practiceAnswer
                          ? (isCorrectOpt ? 'cockpit-option--correct' : (isSelected ? 'cockpit-option--wrong' : ''))
                          : '';
                        return (
                          <button
                            key={opt.key}
                            type="button"
                            className={`cockpit-option ${optionClass}`}
                            onClick={() => !practiceAnswer && handleSelectPracticeAnswer(opt.key, opt.correct)}
                            disabled={!!practiceAnswer}
                          >
                            <span className="cockpit-option__label">{opt.key}</span>
                            <span>{opt.text}</span>
                          </button>
                        );
                      })}
                    </div>
                    {practiceAnswer && (
                      <div className={`cockpit-widget__feedback ${practiceQuestions[practiceQIndex].opts.find(o => o.key === practiceAnswer)?.correct ? 'success' : 'error'}`}>
                        {practiceQuestions[practiceQIndex].opts.find(o => o.key === practiceAnswer)?.correct
                          ? '🎉 Correct answer! Great job.'
                          : '❌ Incorrect answer. Try using the explanation details below.'}
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                      <Button size="sm" variant="secondary" onClick={() => setPracticeShowHint(!practiceShowHint)}>
                        {practiceShowHint ? 'Hide Hint' : 'View Hint'}
                      </Button>
                      {practiceAnswer && (
                        <Button
                          size="sm"
                          onClick={() => {
                            setPracticeQIndex((prev) => (prev + 1) % practiceQuestions.length);
                            setPracticeAnswer(null);
                            setPracticeShowHint(false);
                          }}
                        >
                          Next Question
                        </Button>
                      )}
                    </div>
                    {practiceShowHint && (
                      <div className="cockpit-widget__hint" style={{ marginTop: 8, padding: 12, background: 'var(--bg-secondary)', borderRadius: 'var(--radius)', fontSize: '0.8rem', borderLeft: '3px solid var(--accent-primary)', color: 'var(--text-secondary)' }}>
                        <strong>Concept:</strong> {practiceQuestions[practiceQIndex].hint}
                      </div>
                    )}
                  </div>
                )}

                {visibleModule === 2 && (
                  <div className="cockpit-widget cockpit-widget--tests">
                    <div className="cockpit-widget__head">
                      <h4>Mock Test Simulator</h4>
                      <div className="cockpit-widget__timer">
                        <Timer size={16} />
                        <span>{formatMockTime(mockTimer)}</span>
                      </div>
                    </div>
                    
                    {!mockTestSubmitted ? (
                      <div className="cockpit-widget__test-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <strong>TCS NQT Advanced Mock - Question {mockTestActiveQ + 1}/2</strong>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>1.0 Mark</span>
                        </div>
                        <p>{mockTestActiveQ === 0 ? 'Question 1: What is the postfix expression of A + B * C?' : 'Question 2: What is the result of binary 10 & 12 (Bitwise AND)?'}</p>
                        
                        <div className="cockpit-widget__options">
                          {(mockTestActiveQ === 0
                            ? [
                                { key: 'A', text: 'ABC*+' },
                                { key: 'B', text: 'AB+C*' },
                                { key: 'C', text: 'ABC+*' },
                                { key: 'D', text: 'AB*C+' }
                              ]
                            : [
                                { key: 'A', text: '8' },
                                { key: 'B', text: '10' },
                                { key: 'C', text: '12' },
                                { key: 'D', text: '14' }
                              ]
                          ).map((opt) => (
                            <button
                              key={opt.key}
                              type="button"
                              className={`cockpit-option ${mockTestAnswers[mockTestActiveQ] === opt.key ? 'cockpit-option--selected' : ''}`}
                              onClick={() => handleSelectMockTestAnswer(mockTestActiveQ, opt.key)}
                            >
                              <span className="cockpit-option__label">{opt.key}</span>
                              <span>{opt.text}</span>
                            </button>
                          ))}
                        </div>

                        <div style={{ display: 'flex', gap: 12, marginTop: 16, justifyContent: 'space-between' }}>
                          <div style={{ display: 'flex', gap: 8 }}>
                            <Button
                              size="sm"
                              variant="secondary"
                              disabled={mockTestActiveQ === 0}
                              onClick={() => setMockTestActiveQ(0)}
                            >
                              Prev
                            </Button>
                            <Button
                              size="sm"
                              variant="secondary"
                              disabled={mockTestActiveQ === 1}
                              onClick={() => setMockTestActiveQ(1)}
                            >
                              Next
                            </Button>
                          </div>
                          <Button size="sm" onClick={() => setMockTestSubmitted(true)}>
                            Submit Test
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="cockpit-widget__test-card text-center" style={{ textAlign: 'center', padding: '24px 16px' }}>
                        <Award size={48} style={{ color: 'var(--accent-success)', margin: '0 auto 12px' }} />
                        <h4 style={{ fontWeight: 800 }}>Mock Assessment Submitted</h4>
                        <p style={{ margin: '8px 0', fontSize: '0.9rem' }}>
                          Your Score: <strong>{((mockTestAnswers[0] === 'A' ? 1 : 0) + (mockTestAnswers[1] === 'A' ? 1 : 0)) * 50}%</strong> (2 of 2 answered)
                        </p>
                        <span className="badge badge--green" style={{ margin: '8px auto' }}>Grade: Excellent</span>
                        <div style={{ marginTop: 16 }}>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => {
                              setMockTestSubmitted(false);
                              setMockTestAnswers({});
                              setMockTestActiveQ(0);
                            }}
                          >
                            Restart Test
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {visibleModule === 3 && (
                  <div className="cockpit-widget cockpit-widget--code">
                    <div className="cockpit-widget__head">
                      <h4>Code Lab Sandbox</h4>
                      <div style={{ display: 'flex', gap: 8 }}>
                        {Object.keys(codeTemplates).map((key) => (
                          <button
                            key={key}
                            type="button"
                            className={`badge ${codeSnippetKey === key ? 'badge--green' : 'badge--slate'}`}
                            onClick={() => {
                              setCodeSnippetKey(key);
                              setMockCodeRunState('idle');
                            }}
                            style={{ border: 'none', cursor: 'pointer', outline: 'none' }}
                          >
                            {codeTemplates[key].label}
                          </button>
                        ))}
                      </div>
                      <Button size="sm" onClick={runMockCode} loading={mockCodeRunState === 'running'} icon={Play}>Run</Button>
                    </div>
                    <pre className="cockpit-widget__code">
                      {codeTemplates[codeSnippetKey].code}
                    </pre>
                    <div className="cockpit-widget__terminal">
                      <span>Terminal Output:</span>
                      {mockCodeRunState === 'idle' && <p className="muted">Click Run to execute script...</p>}
                      {mockCodeRunState === 'running' && <p className="info">Running code lab script...</p>}
                      {mockCodeRunState === 'success' && (
                        <>
                          <p className="success">{codeTemplates[codeSnippetKey].runResult.stdout}</p>
                          <pre className="meta" style={{ color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', marginTop: 4, fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                            {codeRunCustomDetails}
                          </pre>
                          <p className="meta">Process finished in 14ms (Memory: 8.4MB)</p>
                        </>
                      )}
                    </div>
                  </div>
                )}

                {visibleModule === 4 && (
                  <div className="cockpit-widget cockpit-widget--interview">
                    <div className="cockpit-widget__head">
                      <h4>AI Technical Interview Coach</h4>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button
                          type="button"
                          className={`badge ${interviewQKey === 'team_conflict' ? 'badge--violet' : 'badge--slate'}`}
                          onClick={() => handleSelectInterviewQuestion('team_conflict')}
                          style={{ border: 'none', cursor: 'pointer', outline: 'none' }}
                        >
                          Code Review Conflict
                        </button>
                        <button
                          type="button"
                          className={`badge ${interviewQKey === 'join_reason' ? 'badge--violet' : 'badge--slate'}`}
                          onClick={() => handleSelectInterviewQuestion('join_reason')}
                          style={{ border: 'none', cursor: 'pointer', outline: 'none' }}
                        >
                          Engineering Motivation
                        </button>
                      </div>
                    </div>
                    
                    <div className="cockpit-widget__chat">
                      <div className="chat-bubble chat-bubble--ai">
                        <strong>AI Interviewer:</strong>
                        <p>{interviewScenarios[interviewQKey].q.replace('AI Interviewer: ', '')}</p>
                      </div>
                      
                      {interviewHistory.map((msg, mIdx) => (
                        msg.sender === 'user' ? (
                          <div key={mIdx} className="chat-bubble chat-bubble--user">
                            <strong>You:</strong>
                            <p>{msg.text}</p>
                          </div>
                        ) : (
                          <div key={mIdx} className="chat-bubble chat-bubble--ai" style={{ borderLeft: '3px solid var(--accent-secondary)' }}>
                            <strong>AI Interviewer Feedback:</strong>
                            <p>Score: <strong>{msg.score}/20</strong>. {msg.feedback}</p>
                          </div>
                        )
                      ))}
                      
                      {interviewTyping && (
                        <div className="chat-bubble chat-bubble--ai muted">
                          <p>AI Coach is grading your response...</p>
                        </div>
                      )}
                    </div>

                    {interviewAnswerIndex === null && (
                      <div className="cockpit-widget__answer-selectors" style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 12 }}>
                        <span>Choose your response:</span>
                        {interviewScenarios[interviewQKey].opts.map((opt, oIdx) => (
                          <button
                            key={oIdx}
                            type="button"
                            className="cockpit-option"
                            onClick={() => handleSelectInterviewAnswer(oIdx)}
                            style={{ padding: '10px 12px', fontSize: '0.8rem' }}
                          >
                            <span className="cockpit-option__label">{oIdx === 0 ? 'A' : 'B'}</span>
                            <span>{opt.text}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {visibleModule === 5 && (
                  <div className="cockpit-widget cockpit-widget--analytics">
                    <div className="cockpit-widget__head">
                      <h4>Readiness & Diagnostics</h4>
                      <div style={{ display: 'flex', gap: 6 }}>
                        {['week', 'month', 'all'].map((filterKey) => (
                          <button
                            key={filterKey}
                            type="button"
                            className={`badge ${analyticsPeriod === filterKey ? 'badge--green' : 'badge--slate'}`}
                            onClick={() => setAnalyticsPeriod(filterKey)}
                            style={{ border: 'none', cursor: 'pointer', textTransform: 'capitalize' }}
                          >
                            {filterKey === 'all' ? 'All Time' : filterKey === 'week' ? '7 Days' : '30 Days'}
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    <div className="cockpit-widget__analytics-grid">
                      <div className="analytic-bar">
                        <span>Data Structures</span>
                        <div className="bar-outer">
                          <div className="bar-inner" style={{ width: `${getAnalyticsData().dsa}%` }} />
                        </div>
                        <small>{getAnalyticsData().dsa}% accuracy</small>
                      </div>
                      
                      <div className="analytic-bar">
                        <span>Aptitude & Logic</span>
                        <div className="bar-outer">
                          <div className="bar-inner" style={{ width: `${getAnalyticsData().aptitude}%` }} />
                        </div>
                        <small>{getAnalyticsData().aptitude}% accuracy</small>
                      </div>
                      
                      <div className="analytic-bar">
                        <span>Database Systems</span>
                        <div className="bar-outer">
                          <div className="bar-inner" style={{ width: `${getAnalyticsData().db}%` }} />
                        </div>
                        <small>{getAnalyticsData().db}% accuracy</small>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Live Activity Feed */}
        <section className="landing__feed-section">
          <div className="feed-ticker-container">
            <div className="feed-ticker-title">
              <span className="pulse-dot" />
              <span>LIVE ACTIVITY STREAM</span>
            </div>
            <div className="feed-ticker-list">
              <div className="feed-ticker-track">
                {activityFeedItems.map((item, idx) => (
                  <div key={`ticker-1-${idx}`} className="feed-ticker-card">
                    <span className="avatar">{item.avatar}</span>
                    <div className="info">
                      <strong>{item.user}</strong>
                      <span>{item.action}</span>
                    </div>
                    <span className="time">{item.time}</span>
                    <span className="badge badge--slate">{item.track}</span>
                  </div>
                ))}
                {/* Duplicate for seamless loop */}
                {activityFeedItems.map((item, idx) => (
                  <div key={`ticker-2-${idx}`} className="feed-ticker-card">
                    <span className="avatar">{item.avatar}</span>
                    <div className="info">
                      <strong>{item.user}</strong>
                      <span>{item.action}</span>
                    </div>
                    <span className="time">{item.time}</span>
                    <span className="badge badge--slate">{item.track}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>


        {/* Testimonials */}
        <section className="landing__testimonials">
          <div className="landing__section-head text-center" style={{ margin: '0 auto 48px', textAlign: 'center' }}>
            <span>Student Success</span>
            <h2>Hear from students who got placed.</h2>
          </div>

          <div className="landing__testimonials-grid">
            {testimonials.map((testimonial) => (
              <div key={testimonial.name} className="landing__testimonial-card" onMouseMove={handleCardMouseMove} onMouseLeave={handleCardMouseLeave}>
                <div className="landing__testimonial-header">
                  <div className="landing__testimonial-avatar">{testimonial.image}</div>
                  <div>
                    <div className="landing__testimonial-name">{testimonial.name}</div>
                    <div className="landing__testimonial-role">{testimonial.role}</div>
                  </div>
                  <div className="landing__testimonial-company">{testimonial.company}</div>
                </div>
                <div className="landing__testimonial-stars">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} size={16} fill="currentColor" />
                  ))}
                </div>
                <p className="landing__testimonial-quote">"{testimonial.quote}"</p>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ Section */}
        <section className="landing__faq" id="faq">
          <div className="landing__section-head">
            <span>Common Questions</span>
            <h2>Everything you need to know.</h2>
          </div>

          {(() => {
            const categorizedFaqs = faqs.map((faq, index) => {
              let cat = 'preparation';
              if (index === 3) cat = 'coding';
              if (index === 4 || index === 5) cat = 'platform';
              return { ...faq, category: cat };
            });

            const filteredFaqs = categorizedFaqs.filter((faq) => {
              const matchesSearch = faq.q.toLowerCase().includes(faqSearch.toLowerCase()) || 
                                    faq.a.toLowerCase().includes(faqSearch.toLowerCase());
              const matchesCategory = faqCategory === 'all' || faq.category === faqCategory;
              return matchesSearch && matchesCategory;
            });

            return (
              <>
                <div className="faq-filters" style={{ marginBottom: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <div className="faq-filters__search" style={{ position: 'relative' }}>
                    <Search size={16} className="faq-filters__search-icon" style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input
                      type="text"
                      placeholder="Search FAQs..."
                      value={faqSearch}
                      onChange={(e) => setFaqSearch(e.target.value)}
                      className="faq-filters__input"
                      style={{ width: '100%', padding: '12px 16px 12px 42px', background: 'var(--bg-card)', border: '1px solid var(--border-primary)', borderRadius: 'var(--radius-lg)', color: 'var(--text-primary)', outline: 'none' }}
                    />
                  </div>
                  
                  <div className="faq-filters__tags" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {[
                      { key: 'all', label: 'All FAQs' },
                      { key: 'preparation', label: 'Preparation' },
                      { key: 'coding', label: 'Coding' },
                      { key: 'platform', label: 'Platform & Diagnostics' }
                    ].map((tag) => (
                      <button
                        key={tag.key}
                        type="button"
                        className={`badge ${faqCategory === tag.key ? 'badge--green' : 'badge--slate'}`}
                        onClick={() => setFaqCategory(tag.key)}
                        style={{ border: 'none', cursor: 'pointer', fontSize: '0.8rem', padding: '6px 12px' }}
                      >
                        {tag.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="landing__faq-list">
                  {filteredFaqs.length > 0 ? (
                    filteredFaqs.map((faq) => {
                      const globalIdx = faqs.findIndex(f => f.q === faq.q);
                      return (
                        <div
                          key={faq.q}
                          className={`landing__faq-item ${expandedFaq === globalIdx ? 'expanded' : ''}`}
                        >
                          <button
                            className="landing__faq-question"
                            onClick={() => setExpandedFaq(expandedFaq === globalIdx ? -1 : globalIdx)}
                          >
                            <span>{faq.q}</span>
                            <Zap size={18} />
                          </button>
                          <div className="landing__faq-answer">
                            <p>{faq.a}</p>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="text-center" style={{ padding: '24px 0', color: 'var(--text-muted)', textAlign: 'center' }}>
                      No FAQs match your search or filter options.
                    </div>
                  )}
                </div>
              </>
            );
          })()}
        </section>

        {/* Cinematic Final CTA Section */}
        <section className="landing__cta-footer">
          <div className="cta-gradient-overlay" />
          <div className="cta-content-wrapper">
            <Shield size={44} style={{ color: 'var(--accent-primary)', marginBottom: 16 }} />
            <h2>Your placement command center awaits.</h2>
            <p>Join thousands of career-ready students. Start diagnosing target readiness benchmarks instantly.</p>
            <div className="cta-buttons-row" style={{ display: 'flex', gap: 12, marginTop: 24, justifyContent: 'center' }}>
              <Link to="/signup">
                <Button size="lg">Start Assessment Free <ArrowRight size={18} /></Button>
              </Link>
              <Link to="/login">
                <Button variant="secondary" size="lg">Explore Dashboard</Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="landing__footer">
          <div className="landing__footer-content">
            <div>
              <strong>PrepSmart</strong>
              <p>Placement readiness, systematized.</p>
            </div>
            <div className="landing__footer-links">
              <a href="#features">Features</a>
              <a href="#workflow">Workflow</a>
              <a href="#faq">FAQ</a>
              <a href="/">Privacy Policy</a>
            </div>
          </div>
          <div className="landing__footer-bottom">
            <p>© 2026 PrepSmart. All rights reserved.</p>
          </div>
        </footer>
      </main>
    </div>
  );
}
