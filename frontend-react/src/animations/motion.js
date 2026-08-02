/**
 * PrepSmart — Global Motion System
 * Framer Motion preset library. Import from anywhere.
 *
 * Usage:
 *   import { fadeUp, stagger, cardHover } from '@/animations/motion';
 *   <motion.div variants={fadeUp} initial="hidden" animate="show" />
 */

/* ─────────────────────────────────────────────────────────────────
   SPRING CONFIGS
   ───────────────────────────────────────────────────────────────── */
export const springs = {
  /** Snappy UI response */
  snappy:  { type: 'spring', stiffness: 500, damping: 30 },
  /** Standard card lift */
  standard:{ type: 'spring', stiffness: 350, damping: 24 },
  /** Smooth modal / panel */
  smooth:  { type: 'spring', stiffness: 260, damping: 22 },
  /** Slow reveal */
  gentle:  { type: 'spring', stiffness: 180, damping: 20 },
  /** Bouncy badges / orbs */
  bouncy:  { type: 'spring', stiffness: 420, damping: 18, mass: 0.8 },
};

/* ─────────────────────────────────────────────────────────────────
   EASING CURVES
   ───────────────────────────────────────────────────────────────── */
export const ease = {
  default:  [0.4, 0, 0.2, 1],
  out:      [0, 0, 0.2, 1],
  in:       [0.4, 0, 1, 1],
  inOut:    [0.4, 0, 0.6, 1],
  spring:   [0.34, 1.56, 0.64, 1],
  smooth:   [0.25, 0.46, 0.45, 0.94],
};

/* ─────────────────────────────────────────────────────────────────
   REVEAL VARIANTS
   ───────────────────────────────────────────────────────────────── */

/** Basic fade from below */
export const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: ease.out },
  },
  exit: { opacity: 0, y: 12, transition: { duration: 0.2, ease: ease.in } },
};

/** Fade from above */
export const fadeDown = {
  hidden: { opacity: 0, y: -16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: ease.out } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.15 } },
};

/** Fade + scale */
export const fadeScale = {
  hidden: { opacity: 0, scale: 0.92 },
  show: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.4, ease: ease.spring },
  },
  exit: { opacity: 0, scale: 0.88, transition: { duration: 0.2 } },
};

/** Slide from left */
export const slideLeft = {
  hidden: { opacity: 0, x: -32 },
  show:   { opacity: 1, x: 0, transition: { duration: 0.45, ease: ease.out } },
  exit:   { opacity: 0, x: -16, transition: { duration: 0.2 } },
};

/** Slide from right */
export const slideRight = {
  hidden: { opacity: 0, x: 32 },
  show:   { opacity: 1, x: 0, transition: { duration: 0.45, ease: ease.out } },
  exit:   { opacity: 0, x: 16, transition: { duration: 0.2 } },
};

/** Expand from zero height */
export const slideExpand = {
  hidden: { opacity: 0, height: 0, scaleY: 0.85 },
  show: {
    opacity: 1,
    height: 'auto',
    scaleY: 1,
    transition: { duration: 0.35, ease: ease.out },
  },
  exit: {
    opacity: 0,
    height: 0,
    scaleY: 0.85,
    transition: { duration: 0.25, ease: ease.in },
  },
};

/** Simple opacity only */
export const fadePlain = {
  hidden: { opacity: 0 },
  show:   { opacity: 1, transition: { duration: 0.3 } },
  exit:   { opacity: 0, transition: { duration: 0.15 } },
};

/* ─────────────────────────────────────────────────────────────────
   STAGGER CONTAINERS
   ───────────────────────────────────────────────────────────────── */

/** Default stagger — children reveal 70ms apart */
export const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07, delayChildren: 0.05 } },
};

/** Fast stagger — tight 40ms */
export const staggerFast = {
  hidden: {},
  show: { transition: { staggerChildren: 0.04 } },
};

/** Slow dramatic stagger — 120ms */
export const staggerSlow = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.1 } },
};

/** Stagger from end (bottom-up) */
export const staggerReverse = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07, staggerDirection: -1 } },
};

/* ─────────────────────────────────────────────────────────────────
   HOVER INTERACTIONS
   ───────────────────────────────────────────────────────────────── */

/** Card lift on hover */
export const cardHover = {
  rest:  { y: 0, scale: 1, transition: springs.standard },
  hover: { y: -4, scale: 1.012, transition: springs.standard },
};

/** Subtle lift */
export const liftSm = {
  rest:  { y: 0, transition: springs.snappy },
  hover: { y: -2, transition: springs.snappy },
};

/** Button press feedback */
export const buttonPress = {
  rest:  { scale: 1 },
  hover: { scale: 1.03, transition: springs.snappy },
  tap:   { scale: 0.96, transition: springs.snappy },
};

/** Magnetic glow button */
export const glowButton = {
  rest:  { scale: 1, boxShadow: '0 0 0px rgba(59,130,246,0)' },
  hover: {
    scale: 1.04,
    boxShadow: '0 0 24px rgba(59,130,246,0.4)',
    transition: springs.snappy,
  },
  tap: { scale: 0.97 },
};

/** Icon spin on hover */
export const iconSpin = {
  rest:  { rotate: 0 },
  hover: { rotate: 360, transition: { duration: 0.5, ease: ease.smooth } },
};

/* ─────────────────────────────────────────────────────────────────
   CONTINUOUS ANIMATIONS (keyframe-style)
   ───────────────────────────────────────────────────────────────── */

/** Floating loop — for AI orb, decorative elements */
export const floatingLoop = {
  y: [0, -10, 0],
  transition: {
    duration: 4,
    ease: ease.smooth,
    repeat: Infinity,
    repeatType: 'loop',
  },
};

/** Pulse glow ring */
export const pulseGlow = {
  scale: [1, 1.12, 1],
  opacity: [0.6, 0.2, 0.6],
  transition: { duration: 2.5, ease: ease.inOut, repeat: Infinity },
};

/** Breathing scale */
export const breathe = {
  scale: [1, 1.04, 1],
  transition: { duration: 3, ease: ease.inOut, repeat: Infinity },
};

/** Shimmer sweep — for loading states */
export const shimmerSweep = {
  x: ['-100%', '100%'],
  transition: { duration: 1.5, ease: ease.default, repeat: Infinity },
};

/* ─────────────────────────────────────────────────────────────────
   PAGE / ROUTE TRANSITIONS
   ───────────────────────────────────────────────────────────────── */
export const pageEnter = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: ease.out, staggerChildren: 0.08 },
  },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2 } },
};

/* ─────────────────────────────────────────────────────────────────
   MODAL / PANEL TRANSITIONS
   ───────────────────────────────────────────────────────────────── */
export const modalBackdrop = {
  hidden: { opacity: 0 },
  show:   { opacity: 1, transition: { duration: 0.25 } },
  exit:   { opacity: 0, transition: { duration: 0.2 } },
};

export const modalPanel = {
  hidden: { opacity: 0, scale: 0.9, y: 20 },
  show: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: springs.smooth,
  },
  exit: {
    opacity: 0,
    scale: 0.88,
    y: 16,
    transition: { duration: 0.2, ease: ease.in },
  },
};

export const drawerRight = {
  hidden: { opacity: 0, x: '100%' },
  show: { opacity: 1, x: 0, transition: springs.smooth },
  exit: { opacity: 0, x: '100%', transition: { duration: 0.25, ease: ease.in } },
};

export const drawerBottom = {
  hidden: { opacity: 0, y: '100%' },
  show: { opacity: 1, y: 0, transition: springs.smooth },
  exit: { opacity: 0, y: '100%', transition: { duration: 0.25, ease: ease.in } },
};

/* ─────────────────────────────────────────────────────────────────
   AI-SPECIFIC TRANSITIONS
   ───────────────────────────────────────────────────────────────── */

/** AI panel opens from bottom-right orb */
export const aiPanelReveal = {
  hidden: { opacity: 0, scale: 0.8, y: 24, transformOrigin: 'bottom right' },
  show: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { ...springs.bouncy, duration: 0.35 },
  },
  exit: {
    opacity: 0,
    scale: 0.82,
    y: 16,
    transition: { duration: 0.2, ease: ease.in },
  },
};

/** AI typing indicator dots */
export const aiTypingDot = (delay = 0) => ({
  y: [0, -6, 0],
  transition: {
    duration: 0.8,
    ease: ease.inOut,
    repeat: Infinity,
    delay,
  },
});

/** AI suggestion card stagger */
export const aiSuggestion = {
  hidden: { opacity: 0, x: -12 },
  show: { opacity: 1, x: 0, transition: { duration: 0.3, ease: ease.out } },
};

/* ─────────────────────────────────────────────────────────────────
   CHART ANIMATIONS
   ───────────────────────────────────────────────────────────────── */

/** SVG bar grow from bottom */
export const barGrow = (delay = 0) => ({
  initial: { scaleY: 0, originY: 1 },
  animate: {
    scaleY: 1,
    transition: { duration: 0.7, ease: ease.spring, delay },
  },
});

/** SVG line draw */
export const lineDraw = {
  initial: { pathLength: 0, opacity: 0 },
  animate: {
    pathLength: 1,
    opacity: 1,
    transition: { duration: 1.2, ease: ease.out },
  },
};

/* ─────────────────────────────────────────────────────────────────
   NOTIFICATION / TOAST
   ───────────────────────────────────────────────────────────────── */
export const toastEnter = {
  hidden: { opacity: 0, x: 60, scale: 0.85 },
  show: {
    opacity: 1,
    x: 0,
    scale: 1,
    transition: springs.bouncy,
  },
  exit: {
    opacity: 0,
    x: 60,
    scale: 0.85,
    transition: { duration: 0.2 },
  },
};

/* ─────────────────────────────────────────────────────────────────
   UTILITY: Create staggered child with index
   ───────────────────────────────────────────────────────────────── */
export function staggerChild(index, baseDelay = 0) {
  return {
    hidden: { opacity: 0, y: 20 },
    show: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.45,
        ease: ease.out,
        delay: baseDelay + index * 0.07,
      },
    },
  };
}

/**
 * Compose motion props for a component
 * @example
 * const props = motionProps(fadeUp, { whileHover: 'hover' });
 */
export function motionProps(variants, extra = {}) {
  return {
    variants,
    initial: 'hidden',
    animate: 'show',
    exit: 'exit',
    ...extra,
  };
}
