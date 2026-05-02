import './ui.css';

function Card({ children, className = '', hover = false, onClick, padding = 'md' }) {
  const classes = [
    'card',
    hover ? 'card--hover' : '',
    `card--${padding}`,
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} onClick={onClick}>
      {children}
    </div>
  );
}

function CardHeader({ children, className = '', action }) {
  return (
    <div className={`card__header ${className}`}>
      {typeof children === 'string' ? <h3 className="card__title">{children}</h3> : children}
      {action && <div className="card__action">{action}</div>}
    </div>
  );
}

function CardBody({ children, className = '' }) {
  return (
    <div className={`card__body ${className}`}>
      {children}
    </div>
  );
}

function CardFooter({ children, className = '' }) {
  return (
    <div className={`card__footer ${className}`}>
      {children}
    </div>
  );
}

Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

export default Card;
