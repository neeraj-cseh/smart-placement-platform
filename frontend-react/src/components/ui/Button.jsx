import { forwardRef } from 'react';
import './ui.css';

const Button = forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className = '',
  icon: Icon,
  ...props
}, ref) => {
  const classes = [
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    loading ? 'btn--loading' : '',
    disabled ? 'btn--disabled' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <button
      ref={ref}
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="btn__spinner" />
      ) : (
        <>
          {Icon && <Icon className="btn__icon" size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />}
          {children}
        </>
      )}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
