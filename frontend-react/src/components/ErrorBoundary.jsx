import { Component } from 'react';
import { AlertCircle, Home } from 'lucide-react';
import Button from './ui/Button';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--bg-primary)',
          color: 'var(--text-primary)',
          padding: '20px',
        }}>
          <div style={{
            maxWidth: '500px',
            textAlign: 'center',
            padding: '40px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-primary)',
            borderRadius: 'var(--radius-lg)',
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              marginBottom: '24px',
            }}>
              <AlertCircle size={48} color="var(--accent-danger)" />
            </div>
            <h1 style={{ marginBottom: '8px', fontSize: '1.5rem' }}>
              Something went wrong
            </h1>
            <p style={{
              color: 'var(--text-secondary)',
              marginBottom: '24px',
              lineHeight: '1.6',
            }}>
              The application encountered an unexpected error. Please try again or return to the home page.
            </p>
            {import.meta.env.DEV && this.state.error && (
              <details style={{
                marginBottom: '24px',
                textAlign: 'left',
                padding: '12px',
                background: 'var(--bg-secondary)',
                borderRadius: 'var(--radius)',
                fontSize: '0.85rem',
              }}>
                <summary style={{ cursor: 'pointer', marginBottom: '8px' }}>
                  Error details (development only)
                </summary>
                <pre style={{
                  margin: '0',
                  overflow: 'auto',
                  color: 'var(--accent-danger)',
                }}>
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
            <div style={{ display: 'flex', gap: '12px' }}>
              <Button
                onClick={this.handleReset}
                style={{ flex: 1 }}
              >
                Try Again
              </Button>
              <Button
                variant="secondary"
                onClick={() => (window.location.href = '/')}
                style={{ flex: 1 }}
              >
                <Home size={16} /> Go Home
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
