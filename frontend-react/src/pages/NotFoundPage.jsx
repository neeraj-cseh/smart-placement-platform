import { Link } from 'react-router-dom';
import Button from '../components/ui/Button';
import './not-found.css';

function NotFoundPage() {
  return (
    <div className="not-found">
      <div className="not-found__content">
        <h1 className="not-found__code">404</h1>
        <h2 className="not-found__title">Page not found</h2>
        <p className="not-found__desc">The page you&apos;re looking for doesn&apos;t exist or has been moved.</p>
        <Link to="/">
          <Button variant="primary" size="lg">Go to dashboard</Button>
        </Link>
      </div>
    </div>
  );
}

export default NotFoundPage;
