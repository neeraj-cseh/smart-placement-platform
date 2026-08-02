/**
 * PrepSmart — Widget Engine
 * Reusable dashboard widget container system.
 *
 * Usage:
 *   import { Widget, WidgetHeader, WidgetBody } from '@/components/widgets';
 *   <Widget loading={loading} error={error}>
 *     <WidgetHeader title="Skill Mastery" icon={Brain} action={<Button>View all</Button>} />
 *     <WidgetBody>...</WidgetBody>
 *   </Widget>
 */

import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, RefreshCw, MoreHorizontal, Maximize2 } from 'lucide-react';
import { fadeUp } from '../../animations/motion';
import './widget.css';

/* ─────────────────────────────────────────────────────────────────
   WIDGET — Outer container with states
   ───────────────────────────────────────────────────────────────── */
export function Widget({
  children,
  loading      = false,
  error        = null,
  className    = '',
  variant      = 'default',   // 'default' | 'glass' | 'ai' | 'analytics' | 'spotlight'
  glow         = false,
  hover        = true,
  fullHeight   = false,
  id,
  style,
}) {
  return (
    <motion.div
      id={id}
      className={`widget widget--${variant} ${glow ? 'widget--glow' : ''} ${fullHeight ? 'widget--full' : ''} ${className}`}
      variants={fadeUp}
      initial="hidden"
      animate="show"
      whileHover={hover ? 'hover' : undefined}
      style={style}
    >
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div
            key="loader"
            className="widget__loader"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <WidgetSkeleton />
          </motion.div>
        ) : error ? (
          <motion.div
            key="error"
            className="widget__error"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <WidgetError message={error} />
          </motion.div>
        ) : (
          <motion.div
            key="content"
            className="widget__content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.25 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET HEADER
   ───────────────────────────────────────────────────────────────── */
export function WidgetHeader({
  title,
  icon: Icon,
  action,
  badge,
  subtitle,
  onExpand,
  onMore,
  accentColor,
}) {
  return (
    <div className="widget-header">
      <div className="widget-header__left">
        {Icon && (
          <div
            className="widget-header__icon"
            style={accentColor ? { color: accentColor, background: `${accentColor}18` } : undefined}
          >
            <Icon size={15} />
          </div>
        )}
        <div className="widget-header__titles">
          <span className="widget-header__title">{title}</span>
          {subtitle && <span className="widget-header__subtitle">{subtitle}</span>}
        </div>
        {badge && <span className="widget-header__badge">{badge}</span>}
      </div>

      <div className="widget-header__right">
        {action}
        {onExpand && (
          <button className="widget-header__icon-btn" onClick={onExpand} title="Expand">
            <Maximize2 size={13} />
          </button>
        )}
        {onMore && (
          <button className="widget-header__icon-btn" onClick={onMore} title="More options">
            <MoreHorizontal size={15} />
          </button>
        )}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET BODY
   ───────────────────────────────────────────────────────────────── */
export function WidgetBody({ children, padded = true, className = '', scrollable = false }) {
  return (
    <div
      className={`widget-body ${padded ? 'widget-body--padded' : ''} ${scrollable ? 'widget-body--scroll' : ''} ${className}`}
    >
      {children}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET FOOTER
   ───────────────────────────────────────────────────────────────── */
export function WidgetFooter({ children, className = '' }) {
  return <div className={`widget-footer ${className}`}>{children}</div>;
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET ACTIONS — standardized action button
   ───────────────────────────────────────────────────────────────── */
export function WidgetAction({ label, icon: Icon, onClick, variant = 'ghost' }) {
  return (
    <motion.button
      className={`widget-action widget-action--${variant}`}
      onClick={onClick}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.96 }}
    >
      {label}
      {Icon && <Icon size={12} />}
    </motion.button>
  );
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET SKELETON — loading state
   ───────────────────────────────────────────────────────────────── */
export function WidgetSkeleton({ rows = 4 }) {
  return (
    <div className="widget-skeleton">
      <div className="widget-skeleton__header">
        <div className="widget-skeleton__line widget-skeleton__line--sm" />
        <div className="widget-skeleton__line widget-skeleton__line--xs" />
      </div>
      <div className="widget-skeleton__rows">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="widget-skeleton__row">
            <div className="widget-skeleton__circle" />
            <div className="widget-skeleton__lines">
              <div className="widget-skeleton__line" style={{ width: `${60 + i * 8}%` }} />
              <div className="widget-skeleton__line widget-skeleton__line--xs" style={{ width: `${40 + i * 5}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET ERROR — error state
   ───────────────────────────────────────────────────────────────── */
export function WidgetError({ message = 'Something went wrong', onRetry }) {
  return (
    <div className="widget-error">
      <AlertCircle size={28} />
      <p>{message}</p>
      {onRetry && (
        <button className="widget-error__retry" onClick={onRetry}>
          <RefreshCw size={14} /> Try again
        </button>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET EMPTY — empty state
   ───────────────────────────────────────────────────────────────── */
export function WidgetEmpty({ icon: Icon, title, description, action }) {
  return (
    <div className="widget-empty">
      {Icon && <div className="widget-empty__icon"><Icon size={32} /></div>}
      <div className="widget-empty__title">{title}</div>
      {description && <div className="widget-empty__desc">{description}</div>}
      {action && <div className="widget-empty__action">{action}</div>}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET METRIC — mini KPI inside a widget
   ───────────────────────────────────────────────────────────────── */
export function WidgetMetric({ label, value, change, changeType = 'up', color }) {
  return (
    <div className="widget-metric">
      <div
        className="widget-metric__value"
        style={color ? { color } : undefined}
      >
        {value}
      </div>
      <div className="widget-metric__label">{label}</div>
      {change && (
        <div className={`widget-metric__change widget-metric__change--${changeType}`}>
          {change}
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   WIDGET DIVIDER
   ───────────────────────────────────────────────────────────────── */
export function WidgetDivider({ label }) {
  return (
    <div className="widget-divider">
      {label && <span className="widget-divider__label">{label}</span>}
    </div>
  );
}
