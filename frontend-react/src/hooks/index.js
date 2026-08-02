/**
 * PrepSmart — Core Hook Library
 * Production-grade React hooks. All hooks are tree-shakeable.
 *
 * Exports:
 *   useAnimatedCounter, useIntersectionObserver, useDebounce,
 *   useLocalStorage, useMediaQuery, useWindowSize, useClickOutside,
 *   useThrottle, useEventListener, usePageTitle,
 *   useKeyPress, useCopyToClipboard, useCountdown, useInterval,
 */

import {
  useState, useEffect, useRef, useCallback, useMemo,
} from 'react';

/* ─────────────────────────────────────────────────────────────────
   useAnimatedCounter
   Smoothly counts from 0 to a target value with easing.
   ───────────────────────────────────────────────────────────────── */
export function useAnimatedCounter(target, duration = 1200, startDelay = 0) {
  const [value, setValue] = useState(0);
  const startRef = useRef(null);
  const rafRef   = useRef(null);
  const numTarget = parseFloat(target) || 0;

  useEffect(() => {
    let timeout;
    const start = () => {
      startRef.current = null;
      const step = (ts) => {
        if (!startRef.current) startRef.current = ts;
        const elapsed  = ts - startRef.current;
        const progress = Math.min(elapsed / duration, 1);
        // Cubic ease-out
        const eased = 1 - Math.pow(1 - progress, 3);
        setValue(Math.round(eased * numTarget));
        if (progress < 1) rafRef.current = requestAnimationFrame(step);
        else setValue(numTarget);
      };
      rafRef.current = requestAnimationFrame(step);
    };

    timeout = setTimeout(start, startDelay);
    return () => {
      clearTimeout(timeout);
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [numTarget, duration, startDelay]);

  return value;
}

/* ─────────────────────────────────────────────────────────────────
   useIntersectionObserver
   Fires when element enters viewport. Used for lazy animations.
   ───────────────────────────────────────────────────────────────── */
export function useIntersectionObserver(options = {}) {
  const [isVisible, setIsVisible]   = useState(false);
  const [hasEntered, setHasEntered] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        if (!hasEntered) setHasEntered(true);
        if (options.once) observer.unobserve(el);
      } else {
        if (!options.once) setIsVisible(false);
      }
    }, {
      threshold: options.threshold ?? 0.15,
      rootMargin: options.rootMargin ?? '0px',
    });

    observer.observe(el);
    return () => observer.disconnect();
  }, [options.once, options.threshold, options.rootMargin, hasEntered]);

  return { ref, isVisible, hasEntered };
}

/* ─────────────────────────────────────────────────────────────────
   useDebounce
   Returns a debounced value — prevents rapid-fire updates.
   ───────────────────────────────────────────────────────────────── */
export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}

/* ─────────────────────────────────────────────────────────────────
   useThrottle
   Throttles a value update (useful for scroll/resize handlers).
   ───────────────────────────────────────────────────────────────── */
export function useThrottle(value, interval = 200) {
  const [throttled, setThrottled] = useState(value);
  const lastUpdated = useRef(0);

  useEffect(() => {
    const now = Date.now();
    const remaining = interval - (now - lastUpdated.current);
    if (remaining <= 0) {
      lastUpdated.current = now;
      setThrottled(value);
    } else {
      const t = setTimeout(() => {
        lastUpdated.current = Date.now();
        setThrottled(value);
      }, remaining);
      return () => clearTimeout(t);
    }
  }, [value, interval]);

  return throttled;
}

/* ─────────────────────────────────────────────────────────────────
   useLocalStorage
   Typed, safe localStorage binding with JSON serialization.
   ───────────────────────────────────────────────────────────────── */
export function useLocalStorage(key, defaultValue) {
  const [value, setValueState] = useState(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored !== null ? JSON.parse(stored) : defaultValue;
    } catch {
      return defaultValue;
    }
  });

  const setValue = useCallback((newValue) => {
    try {
      const val = typeof newValue === 'function' ? newValue(value) : newValue;
      setValueState(val);
      localStorage.setItem(key, JSON.stringify(val));
    } catch (err) {
      console.error(`useLocalStorage [${key}]`, err);
    }
  }, [key, value]);

  const removeValue = useCallback(() => {
    setValueState(defaultValue);
    localStorage.removeItem(key);
  }, [key, defaultValue]);

  return [value, setValue, removeValue];
}

/* ─────────────────────────────────────────────────────────────────
   useMediaQuery
   Reactive CSS media query hook.
   ───────────────────────────────────────────────────────────────── */
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(query).matches;
  });

  useEffect(() => {
    const mql = window.matchMedia(query);
    const onChange = (e) => setMatches(e.matches);
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, [query]);

  return matches;
}

/* Breakpoint helpers */
export const useIsMobile  = () => useMediaQuery('(max-width: 640px)');
export const useIsTablet  = () => useMediaQuery('(max-width: 1024px)');
export const useIsDesktop = () => useMediaQuery('(min-width: 1280px)');

/* ─────────────────────────────────────────────────────────────────
   useWindowSize
   Returns current window dimensions, throttled for performance.
   ───────────────────────────────────────────────────────────────── */
export function useWindowSize() {
  const [size, setSize] = useState({ width: window.innerWidth, height: window.innerHeight });

  useEffect(() => {
    let rafId;
    const handler = () => {
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        setSize({ width: window.innerWidth, height: window.innerHeight });
      });
    };
    window.addEventListener('resize', handler, { passive: true });
    return () => {
      window.removeEventListener('resize', handler);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return size;
}

/* ─────────────────────────────────────────────────────────────────
   useClickOutside
   Calls handler when user clicks outside the ref element.
   ───────────────────────────────────────────────────────────────── */
export function useClickOutside(ref, handler) {
  useEffect(() => {
    const listener = (e) => {
      if (!ref.current || ref.current.contains(e.target)) return;
      handler(e);
    };
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener, { passive: true });
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}



/* ─────────────────────────────────────────────────────────────────
   useEventListener
   Attaches/removes event listeners safely.
   ───────────────────────────────────────────────────────────────── */
export function useEventListener(event, handler, target = window, options = {}) {
  const savedHandler = useRef(handler);
  useEffect(() => { savedHandler.current = handler; }, [handler]);

  useEffect(() => {
    const el = target?.current ?? target;
    if (!el?.addEventListener) return;
    const fn = (e) => savedHandler.current(e);
    el.addEventListener(event, fn, options);
    return () => el.removeEventListener(event, fn, options);
  }, [event, target, options]);
}

/* ─────────────────────────────────────────────────────────────────
   useKeyPress
   Fires callback on specific key(s) pressed.
   ───────────────────────────────────────────────────────────────── */
export function useKeyPress(keys, handler, options = {}) {
  const { ctrlKey, shiftKey, metaKey } = options;
  const keyList = useMemo(() => (Array.isArray(keys) ? keys : [keys]), [keys]);

  useEffect(() => {
    const fn = (e) => {
      if (ctrlKey && !e.ctrlKey) return;
      if (shiftKey && !e.shiftKey) return;
      if (metaKey && !e.metaKey) return;
      if (keyList.includes(e.key)) handler(e);
    };
    document.addEventListener('keydown', fn);
    return () => document.removeEventListener('keydown', fn);
  }, [keyList, handler, ctrlKey, shiftKey, metaKey]);
}

/* ─────────────────────────────────────────────────────────────────
   useCopyToClipboard
   ───────────────────────────────────────────────────────────────── */
export function useCopyToClipboard() {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      console.error('Copy failed');
    }
  }, []);

  return { copied, copy };
}

/* ─────────────────────────────────────────────────────────────────
   useCountdown
   Countdown timer returning { days, hours, minutes, seconds }.
   ───────────────────────────────────────────────────────────────── */
export function useCountdown(targetDate) {
  const calc = useCallback(() => {
    const diff = new Date(targetDate) - new Date();
    if (diff <= 0) return { days: 0, hours: 0, minutes: 0, seconds: 0 };
    return {
      days:    Math.floor(diff / 86400000),
      hours:   Math.floor((diff % 86400000) / 3600000),
      minutes: Math.floor((diff % 3600000) / 60000),
      seconds: Math.floor((diff % 60000) / 1000),
    };
  }, [targetDate]);

  const [time, setTime] = useState(calc);

  useEffect(() => {
    const id = setInterval(() => setTime(calc()), 1000);
    return () => clearInterval(id);
  }, [calc]);

  return time;
}

/* ─────────────────────────────────────────────────────────────────
   useInterval
   Declarative setInterval hook.
   ───────────────────────────────────────────────────────────────── */
export function useInterval(callback, delay) {
  const saved = useRef(callback);
  useEffect(() => { saved.current = callback; }, [callback]);
  useEffect(() => {
    if (delay === null) return;
    const id = setInterval(() => saved.current(), delay);
    return () => clearInterval(id);
  }, [delay]);
}

/* ─────────────────────────────────────────────────────────────────
   usePageTitle
   Dynamically updates document title.
   ───────────────────────────────────────────────────────────────── */
export function usePageTitle(title) {
  useEffect(() => {
    const prev = document.title;
    document.title = title ? `${title} — PrepSmart` : 'PrepSmart';
    return () => { document.title = prev; };
  }, [title]);
}

/* ─────────────────────────────────────────────────────────────────
   useAsyncFn
   Wraps an async function with loading/error/data state.
   ───────────────────────────────────────────────────────────────── */
export function useAsyncFn(fn) {
  const [state, setState] = useState({ loading: false, data: null, error: null });

  const execute = useCallback(async (...args) => {
    setState({ loading: true, data: null, error: null });
    try {
      const data = await fn(...args);
      setState({ loading: false, data, error: null });
      return data;
    } catch (error) {
      setState({ loading: false, data: null, error });
      throw error;
    }
  }, [fn]);

  return { ...state, execute };
}

/* ─────────────────────────────────────────────────────────────────
   useScrollLock
   Prevents body scroll (for modals, drawers).
   ───────────────────────────────────────────────────────────────── */
export function useScrollLock(locked) {
  useEffect(() => {
    if (!locked) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = prev; };
  }, [locked]);
}

/* ─────────────────────────────────────────────────────────────────
   useHover
   Returns [ref, isHovered] pair.
   ───────────────────────────────────────────────────────────────── */
export function useHover() {
  const [hovered, setHovered] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const on  = () => setHovered(true);
    const off = () => setHovered(false);
    el.addEventListener('mouseenter', on);
    el.addEventListener('mouseleave', off);
    return () => {
      el.removeEventListener('mouseenter', on);
      el.removeEventListener('mouseleave', off);
    };
  }, []);

  return [ref, hovered];
}

/* ─────────────────────────────────────────────────────────────────
   useCompanyTheme
   Applies company-specific accent color to CSS variables.
   ───────────────────────────────────────────────────────────────── */
const COMPANY_THEMES = {
  amazon:    { primary: '#ff9900', secondary: '#232f3e', glow: 'rgba(255,153,0,0.3)' },
  google:    { primary: '#4285f4', secondary: '#34a853', glow: 'rgba(66,133,244,0.3)' },
  microsoft: { primary: '#00a4ef', secondary: '#7fba00', glow: 'rgba(0,164,239,0.3)' },
  apple:     { primary: '#a2aaad', secondary: '#555555', glow: 'rgba(162,170,173,0.3)' },
  tcs:       { primary: '#5b2d8e', secondary: '#002d77', glow: 'rgba(91,45,142,0.3)' },
  infosys:   { primary: '#007cc3', secondary: '#00a3e0', glow: 'rgba(0,124,195,0.3)' },
  zoho:      { primary: '#e42527', secondary: '#f9a825', glow: 'rgba(228,37,39,0.3)' },
};

export function useCompanyTheme(companySlug) {
  useEffect(() => {
    const theme = COMPANY_THEMES[companySlug?.toLowerCase()];
    if (!theme) return;
    const root = document.documentElement;
    root.style.setProperty('--accent-primary', theme.primary);
    root.style.setProperty('--accent-primary-glow', theme.glow);
    return () => {
      root.style.removeProperty('--accent-primary');
      root.style.removeProperty('--accent-primary-glow');
    };
  }, [companySlug]);
}
