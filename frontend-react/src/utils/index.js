/**
 * PrepSmart — Utility Function Library
 * Pure functions used across the entire platform.
 */

/* ─────────────────────────────────────────────────────────────────
   String utilities
   ───────────────────────────────────────────────────────────────── */

/** Capitalize first letter */
export const capitalize = (str = '') => str.charAt(0).toUpperCase() + str.slice(1);

/** Convert to title case */
export const toTitleCase = (str = '') =>
  str.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());

/** Truncate to max length with ellipsis */
export const truncate = (str = '', max = 60) =>
  str.length > max ? str.slice(0, max).trim() + '…' : str;

/** Get initials from a name */
export const getInitials = (name = '', maxChars = 2) =>
  name
    .split(' ')
    .slice(0, maxChars)
    .map((w) => w[0] ?? '')
    .join('')
    .toUpperCase();

/** Slugify a string */
export const slugify = (str = '') =>
  str.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');

/* ─────────────────────────────────────────────────────────────────
   Number utilities
   ───────────────────────────────────────────────────────────────── */

/** Clamp value between min and max */
export const clamp = (val, min, max) => Math.max(min, Math.min(max, val));

/** Clamp percentage (0–100) */
export const clampPercent = (val) => clamp(Number(val) || 0, 0, 100);

/** Format large numbers: 1500 → "1.5K", 1200000 → "1.2M" */
export const formatNumber = (n) => {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K';
  return String(n);
};

/** Format duration: seconds → "2h 14m" */
export const formatDuration = (seconds) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
};

/** Linear interpolation */
export const lerp = (a, b, t) => a + (b - a) * t;

/** Map a value from one range to another */
export const mapRange = (val, inMin, inMax, outMin, outMax) =>
  outMin + ((val - inMin) / (inMax - inMin)) * (outMax - outMin);

/* ─────────────────────────────────────────────────────────────────
   Color utilities
   ───────────────────────────────────────────────────────────────── */

/**
 * Get semantic color for a score/percentage.
 * Returns CSS variable or hex.
 */
export const scoreColor = (score) => {
  if (score >= 80) return '#10b981'; // green
  if (score >= 60) return '#3b82f6'; // blue
  if (score >= 40) return '#f59e0b'; // amber
  return '#ef4444'; // red
};

/** Get badge tone string for a score */
export const scoreTone = (score) => {
  if (score >= 80) return 'green';
  if (score >= 60) return 'cyan';
  if (score >= 40) return 'amber';
  return 'red';
};

/** Hex to rgba */
export const hexToRgba = (hex, alpha = 1) => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
};

/* ─────────────────────────────────────────────────────────────────
   Date/Time utilities
   ───────────────────────────────────────────────────────────────── */

/** Relative time: "2 hours ago", "just now" */
export const timeAgo = (date) => {
  const diff = Date.now() - new Date(date).getTime();
  const min  = Math.floor(diff / 60000);
  const hr   = Math.floor(diff / 3600000);
  const day  = Math.floor(diff / 86400000);
  if (diff < 60000)   return 'just now';
  if (min < 60)       return `${min}m ago`;
  if (hr < 24)        return `${hr}h ago`;
  if (day < 7)        return `${day}d ago`;
  return new Date(date).toLocaleDateString();
};

/** Format date: "Mon, 28 May" */
export const formatDate = (date, options = {}) =>
  new Date(date).toLocaleDateString('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short', ...options,
  });

/** Is today? */
export const isToday = (date) => {
  const d = new Date(date);
  const now = new Date();
  return d.getDate() === now.getDate() &&
         d.getMonth() === now.getMonth() &&
         d.getFullYear() === now.getFullYear();
};

/** Days until a future date */
export const daysUntil = (date) =>
  Math.ceil((new Date(date) - new Date()) / 86400000);

/* ─────────────────────────────────────────────────────────────────
   Array utilities
   ───────────────────────────────────────────────────────────────── */

/** Shuffle array (Fisher-Yates) */
export const shuffle = (arr) => {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
};

/** Group array by key */
export const groupBy = (arr, key) =>
  arr.reduce((acc, item) => {
    const k = typeof key === 'function' ? key(item) : item[key];
    if (!acc[k]) acc[k] = [];
    acc[k].push(item);
    return acc;
  }, {});

/** Unique values */
export const unique = (arr) => [...new Set(arr)];

/** Sort by key ascending/descending */
export const sortBy = (arr, key, dir = 'asc') =>
  [...arr].sort((a, b) => {
    const va = typeof key === 'function' ? key(a) : a[key];
    const vb = typeof key === 'function' ? key(b) : b[key];
    return dir === 'asc' ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1);
  });

/* ─────────────────────────────────────────────────────────────────
   URL / Params utilities
   ───────────────────────────────────────────────────────────────── */

/** Build query string from object */
export const toQueryString = (params = {}) =>
  new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v != null))
  ).toString();

/** Parse query string to object */
export const fromQueryString = (qs = '') =>
  Object.fromEntries(new URLSearchParams(qs));

/* ─────────────────────────────────────────────────────────────────
   Validation utilities
   ───────────────────────────────────────────────────────────────── */

export const isEmail = (str) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str);
export const isEmpty = (val) => val == null || val === '' || (Array.isArray(val) && val.length === 0);
export const isNumber = (val) => !isNaN(parseFloat(val)) && isFinite(val);

/* ─────────────────────────────────────────────────────────────────
   Performance utilities
   ───────────────────────────────────────────────────────────────── */

/** Simple memoize for pure functions */
export const memoize = (fn) => {
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
};

/** Create stable callback that doesn't change reference */
export const stableCallback = (fn) => {
  const ref = { current: fn };
  ref.current = fn;
  return (...args) => ref.current(...args);
};

/* ─────────────────────────────────────────────────────────────────
   Layout utilities
   ───────────────────────────────────────────────────────────────── */

/** Responsive class helper */
export const responsiveClass = (base, modifiers = {}) => {
  return [
    base,
    ...Object.entries(modifiers)
      .filter(([, active]) => active)
      .map(([cls]) => cls),
  ].join(' ');
};

/** Check if element is in viewport */
export const isInViewport = (el) => {
  const rect = el.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= window.innerHeight &&
    rect.right <= window.innerWidth
  );
};

/* ─────────────────────────────────────────────────────────────────
   PrepSmart-specific utilities
   ───────────────────────────────────────────────────────────────── */

/** Generate a daily greeting based on time of day */
export const getDailyGreeting = (name = '') => {
  const hour = new Date().getHours();
  const timeGreet =
    hour < 12 ? 'Good morning' :
    hour < 17 ? 'Good afternoon' :
    hour < 21 ? 'Good evening' : 'Late night grind';
  return name ? `${timeGreet}, ${name}` : timeGreet;
};

/** Calculate overall placement readiness from multiple scores */
export const calcReadiness = (scores = []) => {
  if (!scores.length) return 0;
  const weights = { dsa: 0.3, aptitude: 0.2, sql: 0.1, os: 0.1, communication: 0.15, projects: 0.15 };
  let total = 0, weight = 0;
  scores.forEach(({ topic, score }) => {
    const w = weights[topic?.toLowerCase()] ?? 0.1;
    total  += score * w;
    weight += w;
  });
  return Math.round(weight > 0 ? total / weight : 0);
};

/** Get company avatar color from name */
const COMPANY_COLORS = [
  '#f97316','#3b82f6','#10b981','#8b5cf6',
  '#06b6d4','#ef4444','#f59e0b','#ec4899',
];

export const companyColor = (name = '') => {
  const hash = [...name].reduce((acc, c) => acc + c.charCodeAt(0), 0);
  return COMPANY_COLORS[hash % COMPANY_COLORS.length];
};

/** Get initials for company (2 letters) */
export const companyInitials = (name = '') =>
  name.split(' ').slice(0, 2).map((w) => w[0] ?? '').join('').toUpperCase() || '??';
