import { useState } from 'react';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Bot, Send, CheckCircle, XCircle } from 'lucide-react';
import './ai-interview.css';

function AIInterviewPage() {
  const { data: config, loading: configLoading } = useApi('/interview/config/');
  const [sessionId, setSessionId] = useState(null);
  const [category, setCategory] = useState(null);
  const [currentQ, setCurrentQ] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQ, setTotalQ] = useState(0);
  const [answer, setAnswer] = useState('');
  const [qaHistory, setQaHistory] = useState([]);
  const [finalResult, setFinalResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStart = async (cat) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/interview/start/', { category: cat });
      setSessionId(res.session_id);
      setCategory(cat);
      setCurrentQ(res.current_question);
      setQuestionIndex(res.question_index);
      setTotalQ(res.total_questions);
      setQaHistory([]);
      setAnswer('');
      setFinalResult(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || !sessionId) return;
    setLoading(true);
    setError('');

    try {
      const res = await api.post('/interview/submit/', { session_id: sessionId, answer });
      setQaHistory(prev => [...prev, { question: currentQ.question, answer, score: res.score, max_score: res.max_score, feedback: res.feedback }]);
      setAnswer('');

      if (questionIndex + 1 < totalQ) {
        const nextRes = await api.post('/interview/question/', { session_id: sessionId });
        setCurrentQ(nextRes.current_question);
        setQuestionIndex(nextRes.question_index);
      } else {
        const endRes = await api.post('/interview/end/', { session_id: sessionId });
        setFinalResult(endRes);
        setSessionId(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (finalResult) {
    return (
      <Layout title="Interview Complete" subtitle={finalResult.category}>
        <Card>
          <div className="ai-interview__result-score">
            {finalResult.percentage}%
          </div>
          <p>{finalResult.total_score}/{finalResult.max_possible_score} points</p>
          <div className="ai-interview__qa-list">
            {finalResult.qa_pairs.map((qa, i) => (
              <div key={i} className="ai-interview__qa-item">
                <h4>{qa.question}</h4>
                <p className="ai-interview__qa-answer">&ldquo;{qa.your_answer}&rdquo;</p>
                <div className="ai-interview__qa-score">
                  Score: {qa.score}
                </div>
                {qa.feedback && <p className="ai-interview__qa-feedback">{qa.feedback}</p>}
              </div>
            ))}
          </div>
          <Button variant="secondary" onClick={() => { setFinalResult(null); setCategory(null); }}>
            New interview
          </Button>
        </Card>
      </Layout>
    );
  }

  if (category && currentQ) {
    return (
      <Layout title={`${category.charAt(0).toUpperCase() + category.slice(1)} Interview`} subtitle={`Question ${questionIndex + 1} of ${totalQ}`}>
        <Card>
          <h3 style={{ marginBottom: 20, fontSize: '1.125rem' }}>{currentQ.question}</h3>
          <span className={`badge badge--${category === 'general' ? 'cyan' : category === 'technical' ? 'violet' : 'amber'}`}>
            {currentQ.area}
          </span>
          <textarea
            className="ai-interview__textarea"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here..."
            rows={6}
          />
          {error && <div className="ai-interview__error">{error}</div>}
          <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
            <Button variant="primary" onClick={handleSubmitAnswer} loading={loading} icon={Send}>
              Submit answer
            </Button>
          </div>
        </Card>

        {qaHistory.length > 0 && (
          <Card style={{ marginTop: 20 }}>
            <h3 style={{ marginBottom: 12, fontSize: '0.875rem', fontWeight: 600 }}>Previous answers</h3>
            {qaHistory.map((qa, i) => (
              <div key={i} className="ai-interview__qa-item" style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
                  {qa.score >= 12 ? <CheckCircle size={14} style={{ color: 'var(--green)' }} /> : <XCircle size={14} style={{ color: 'var(--red)' }} />}
                  <span className="ai-interview__qa-score">{qa.score}/{qa.max_score}</span>
                </div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{qa.question}</p>
                {qa.feedback && <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>{qa.feedback}</p>}
              </div>
            ))}
          </Card>
        )}
      </Layout>
    );
  }

  if (configLoading) return <Layout title="AI Interview"><div className="skeleton skeleton--card" /></Layout>;

  return (
    <Layout title="AI Interview" subtitle="Practice with AI-powered mock interviews">
      <div className="grid grid--3">
        {(config?.categories || []).map((cat) => (
          <Card key={cat.id} hover className="ai-interview__cat-card" onClick={() => handleStart(cat.id)}>
            <div className="ai-interview__cat-icon">
              <Bot size={28} />
            </div>
            <h3>{cat.label}</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{cat.description}</p>
            <span className="badge badge--slate">{cat.question_count} questions</span>
            <Button variant="primary" size="sm" loading={loading}>Start interview</Button>
          </Card>
        ))}
      </div>
    </Layout>
  );
}

export default AIInterviewPage;
