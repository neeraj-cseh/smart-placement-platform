import { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Play, RotateCcw, Terminal, Clock, CheckCircle, XCircle, FileCode2 } from 'lucide-react';
import './code-editor.css';

function CodeEditorPage() {
  const { data, loading, refetch } = useApi('/code/workspace/');
  const [code, setCode] = useState('');
  const [stdin, setStdin] = useState('');
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [status, setStatus] = useState(null);
  const [running, setRunning] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (!data || hydrated) return;
    setCode(data.starter_code || '');
    setStdin(data.default_stdin || '');
    setHydrated(true);
  }, [data, hydrated]);

  const handleRun = async () => {
    setRunning(true);
    setOutput('');
    setError('');
    setStatus(null);

    try {
      const result = await api.post('/code/execute/', { code, stdin, language: data?.language || 'python' });
      setOutput(result.output || '');
      setError(result.error || '');
      setStatus(result);
      refetch().catch(() => {});
    } catch (err) {
      setError(err.message);
      setStatus({ success: false });
    } finally {
      setRunning(false);
    }
  };

  const handleReset = () => {
    setCode(data?.starter_code || '');
    setStdin(data?.default_stdin || '');
    setOutput('');
    setError('');
    setStatus(null);
  };

  const loadExample = (example) => {
    setCode(example.code);
    setStdin(example.stdin || '');
    setOutput('');
    setError('');
    setStatus(null);
  };

  if (loading) return <Layout title="Code Editor"><div className="skeleton skeleton--card" /></Layout>;

  const submissions = data?.recent_submissions || [];

  return (
    <Layout title="Code Editor" subtitle={`${data?.runtime || 'Python'} - ${data?.timeout_seconds || 8}s limit`}>
      <div className="code-editor">
        <div className="code-editor__main">
          <Card className="code-editor__card">
            <div className="code-editor__toolbar">
              <div className="code-editor__lang">
                <Terminal size={16} />
                <span>{data?.language || 'python'}</span>
              </div>
              <div className="code-editor__actions">
                <Button variant="primary" size="sm" onClick={handleRun} loading={running} icon={Play}>
                  Run
                </Button>
                <Button variant="ghost" size="sm" onClick={handleReset} icon={RotateCcw}>
                  Reset
                </Button>
              </div>
            </div>

            <textarea
              className="code-editor__textarea"
              value={code}
              onChange={(event) => setCode(event.target.value)}
              placeholder="Loading backend starter code..."
              spellCheck={false}
            />

            <div className="code-editor__stdin">
              <label htmlFor="stdin">Standard input</label>
              <textarea
                id="stdin"
                value={stdin}
                onChange={(event) => setStdin(event.target.value)}
                placeholder="Input for your program"
                rows={4}
              />
            </div>
          </Card>

          <Card className="code-editor__output">
            <div className="code-editor__output-head">
              <h3>Output</h3>
              {status && (
                <span className={`code-editor__run-status ${status.success ? 'code-editor__run-status--success' : 'code-editor__run-status--error'}`}>
                  {status.success ? <CheckCircle size={14} /> : <XCircle size={14} />}
                  {status.execution_time_ms != null ? `${status.execution_time_ms} ms` : 'Failed'}
                </span>
              )}
            </div>
            {running && <div className="code-editor__loading">Running...</div>}
            {output && <pre className="code-editor__pre code-editor__pre--output">{output}</pre>}
            {error && <pre className="code-editor__pre code-editor__pre--error">{error}</pre>}
            {!output && !error && !running && <p className="code-editor__muted">Run code to see stdout, stderr, and timing.</p>}
          </Card>
        </div>

        <div className="code-editor__side">
          <Card>
            <h3 className="code-editor__side-title">
              <FileCode2 size={14} />
              Examples
            </h3>
            <div className="code-editor__examples">
              {(data?.examples || []).map((example) => (
                <button key={example.title} type="button" onClick={() => loadExample(example)}>
                  {example.title}
                </button>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="code-editor__side-title">
              <Clock size={14} />
              Recent runs
            </h3>
            {submissions.length > 0 ? (
              <div className="code-editor__history">
                {submissions.map((submission) => {
                  const success = !submission.error_output;
                  return (
                    <button
                      key={submission.id}
                      type="button"
                      className="code-editor__history-item"
                      onClick={() => {
                        setCode(submission.code);
                        setStdin(submission.stdin || '');
                        setOutput(submission.output || '');
                        setError(submission.error_output || '');
                        setStatus({ success, execution_time_ms: submission.execution_time_ms });
                      }}
                    >
                      <span className={`code-editor__history-status ${success ? 'code-editor__history-status--success' : 'code-editor__history-status--error'}`} />
                      <code>{submission.code.slice(0, 56)}...</code>
                      <span className="code-editor__history-time">{submission.execution_time_ms || 0} ms</span>
                    </button>
                  );
                })}
              </div>
            ) : (
              <p className="code-editor__muted">No saved runs yet.</p>
            )}
          </Card>
        </div>
      </div>
    </Layout>
  );
}

export default CodeEditorPage;
