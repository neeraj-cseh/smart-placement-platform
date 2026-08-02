const { chromium } = require('../frontend-react/node_modules/playwright');
const fs = require('fs/promises');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'test-artifacts', 'screenshot-package');
const BASE = 'http://127.0.0.1:5173';
const API = 'http://127.0.0.1:8000/api';

const desktop = { width: 1920, height: 1440, deviceScaleFactor: 1 };

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function apiFetch(endpoint, token, options = {}) {
  const res = await fetch(`${API}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`${endpoint} failed ${res.status}: ${text.slice(0, 300)}`);
  }
  return res.json();
}

async function login(email, password) {
  return apiFetch('/auth/login/', null, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

async function setSession(page, auth) {
  await page.goto(BASE, { waitUntil: 'domcontentloaded' });
  await page.evaluate(({ access, refresh }) => {
    localStorage.setItem('access', access);
    localStorage.setItem('refresh', refresh);
    localStorage.setItem('theme', 'dark');
  }, auth);
}

function safeName(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

async function capture(page, item, rows) {
  const dir = path.join(OUT, item.folder);
  await ensureDir(dir);
  const file = `${item.order.toString().padStart(2, '0')}-${safeName(item.name)}.png`;
  const full = path.join(dir, file);
  await page.goto(`${BASE}${item.route}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(item.wait || 1200);
  await page.screenshot({ path: full, fullPage: true, animations: 'disabled' });
  rows.push({
    filename: path.relative(OUT, full).replace(/\\/g, '/'),
    route: item.route,
    purpose: item.purpose,
    caption: item.caption,
    chapter: item.chapter,
  });
}

async function main() {
  await fs.rm(OUT, { recursive: true, force: true });
  await ensureDir(OUT);

  const student = await login('student@prepsmart.dev', 'PrepSmart@123');
  const admin = await login('admin@prepsmart.dev', 'Admin@12345');

  const [journey, problems, companies, passport, portfolio] = await Promise.all([
    apiFetch('/prep/topic-journey/', student.access).catch(() => null),
    apiFetch('/code/problems/', student.access).catch(() => null),
    apiFetch('/companies/', student.access).catch(() => null),
    apiFetch('/passport/', student.access).catch(() => null),
    apiFetch('/portfolio/', student.access).catch(() => null),
  ]);

  const topicSlug =
    journey?.tracks?.flatMap(t => t.nodes || t.topics || [])
      ?.find(t => t.slug)?.slug || 'arrays-and-strings';
  const problemSlug =
    (Array.isArray(problems?.problems) ? problems.problems : Array.isArray(problems) ? problems : [])
      .find(p => p.slug)?.slug || 'two-sum';
  const companyName =
    (companies?.companies || companies?.targets || companies || [])
      .find?.(c => c.name)?.name || 'TCS';
  const passportToken = passport?.passport?.public_token || passport?.public_token || passport?.share_token || '';
  const portfolioSlug = portfolio?.portfolio?.public_url_slug || portfolio?.public_url_slug || '';

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: desktop, deviceScaleFactor: desktop.deviceScaleFactor });
  const page = await context.newPage();
  page.setDefaultTimeout(30000);

  const rows = [];

  const publicScreens = [
    ['Public', '/', 'Landing Page', 'Public landing and interactive demo entry point.', 'PrepSmart public landing page with platform entry actions.', 'Project Overview'],
    ['Authentication', '/login', 'Login', 'User sign-in screen.', 'Login screen for registered users.', 'Authentication'],
    ['Authentication', '/signup', 'Signup', 'New user registration screen.', 'Signup screen with student profile fields.', 'Authentication'],
  ];

  let order = 1;
  for (const [folder, route, name, purpose, caption, chapter] of publicScreens) {
    await capture(page, { folder, route, name, purpose, caption, chapter, order: order++ }, rows);
  }

  await setSession(page, student);

  const studentScreens = [
    ['Dashboard', '/', 'Student Dashboard', 'Authenticated student dashboard.', 'Student dashboard with readiness metrics and analytics widgets.', 'Frontend Screens'],
    ['Analytics', '/analytics', 'Analytics', 'Student analytics charts and test history.', 'Analytics page showing topic accuracy, momentum, and track progress.', 'Analytics'],
    ['Prep', '/prep/journey', 'Prep Journey', 'Topic journey and active learning path.', 'Prep journey with topic progression and unlock state.', 'Learning Module'],
    ['Prep', '/prep/roadmaps', 'Prep Roadmaps', 'Learning roadmap overview.', 'Roadmaps page listing available preparation tracks.', 'Learning Module'],
    ['Prep', '/prep/milestones', 'Prep Milestones', 'Mock assessment milestone overview.', 'Milestones page showing mock tests and readiness progression.', 'Mock Tests'],
    ['Prep', `/prep/topic/${topicSlug}`, 'Topic Study', 'Detailed topic study workspace.', 'Topic study page with learning, visualization, practice, quiz, and AI tabs.', 'Learning Module'],
    ['CodeLab', '/code-lab/arena', 'Problem Arena', 'Coding problem browser.', 'Problem arena with filters, stats, and problem cards.', 'Code Lab'],
    ['CodeLab', `/code-lab/arena/${problemSlug}`, 'Problem Solving Workspace', 'Fullscreen problem-solving workspace.', 'Problem solving workspace with statement, editor, console, and AI mentor controls.', 'Code Lab'],
    ['CodeLab', '/code-lab/workspace', 'Standalone Code Workspace', 'General purpose code execution workspace.', 'Standalone code workspace with editor, terminal, settings, and AI panel.', 'Code Lab'],
    ['CodeLab', '/code-lab/contests', 'Contest Hub', 'Contest listing and leaderboard entry screen.', 'Contest hub with upcoming/live/past contests.', 'Code Lab'],
    ['AICoach', '/ai/interview', 'AI Interview', 'AI interview setup and session screen.', 'AI interview screen with interview type cards and readiness presentation.', 'AI Interview'],
    ['Career', '/career/companies', 'Companies', 'Company readiness browser.', 'Companies page showing target-company readiness cards.', 'Company Readiness'],
    ['Career', `/career/companies/${encodeURIComponent(companyName)}`, 'Company Detail', 'Company-specific readiness detail.', 'Company detail page with readiness breakdown and radar chart.', 'Company Readiness'],
    ['Profile', '/profile/me', 'Profile Editor', 'Student profile editing screen.', 'Profile editor with academic, contact, and portfolio fields.', 'Profile'],
    ['Profile', '/profile/passport', 'Skills Passport', 'Authenticated skills passport.', 'Skills passport page with employability evidence and charts.', 'Passport'],
    ['Settings', '/settings', 'Settings', 'Account and preference settings.', 'Settings page with account, notification, privacy, and password controls.', 'Settings'],
  ];

  order = 1;
  for (const [folder, route, name, purpose, caption, chapter] of studentScreens) {
    await capture(page, { folder, route, name, purpose, caption, chapter, order: order++ }, rows);
  }

  if (passportToken) {
    await capture(page, {
      folder: 'PublicShared',
      route: `/passport/shared/${passportToken}`,
      name: 'Shared Passport',
      purpose: 'Public shared passport view.',
      caption: 'Public skills passport accessed through a share token.',
      chapter: 'Passport',
      order: 1,
    }, rows);
  }

  if (portfolioSlug) {
    await capture(page, {
      folder: 'PublicShared',
      route: `/portfolio/shared/${portfolioSlug}`,
      name: 'Shared Portfolio',
      purpose: 'Public shared portfolio view.',
      caption: 'Public portfolio accessed through a share slug.',
      chapter: 'Portfolio',
      order: 2,
    }, rows);
  }

  await setSession(page, admin);
  const adminTabs = ['users', 'tracks', 'topics', 'questions', 'tests', 'companies'];
  order = 1;
  for (const tab of adminTabs) {
    await capture(page, {
      folder: 'Admin',
      route: `/admin?tab=${tab}`,
      name: `Admin ${tab}`,
      purpose: `Admin ${tab} management screen.`,
      caption: `Admin console ${tab} table and actions.`,
      chapter: 'Administration',
      order: order++,
    }, rows);
  }

  await capture(page, {
    folder: 'Errors',
    route: '/not-a-real-route',
    name: 'Not Found',
    purpose: '404 fallback screen.',
    caption: 'Not found page for unmatched frontend routes.',
    chapter: 'Error Handling',
    order: 1,
  }, rows);

  const markdown = [
    '# Screenshot Package Index',
    '',
    '| Filename | Purpose | Suggested Figure Caption | Suggested Report Chapter |',
    '|---|---|---|---|',
    ...rows.map(r => `| ${r.filename} | ${r.purpose} | ${r.caption} | ${r.chapter} |`),
    '',
  ].join('\n');
  await fs.writeFile(path.join(OUT, 'SCREENSHOT_INDEX.md'), markdown, 'utf8');
  await fs.writeFile(path.join(OUT, 'screenshots.json'), JSON.stringify(rows, null, 2), 'utf8');

  await browser.close();
  console.log(`Captured ${rows.length} screenshots in ${OUT}`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
