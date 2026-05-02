import { useState, useEffect, useRef, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { api } from '../api/client';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Play, Clock, CheckCircle, XCircle, AlertCircle, Flag, ClipboardList } from 'lucide-react';
import './mock-tests.css';

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remaining = seconds % 60;
  return `${minutes}:${remaining.toString().padStart(2, '0')}`;
}

function optionList(question) {
  return ['A', 'B', 'C', 'D'].map((key) => ({
    key,
    text: question[`option_${key.toLowerCase()}`],
  }));
}

function MockTestsPage() {
  const { data, loading, refetch } = useApi('/tests/');
  const [activeTest, setActiveTest] = useState(null);
  const [attemptId, setAttemptId] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [answers, setAnswers] = useState({});
  const [marked, setMarked] = useState({});
  const [testResult, setTestResult] = useState(null);
  const [currentQ, setCurrentQ] = useState(0);
  const [error, setError] = useState('');
  const [startingId, setStartingId] = useState(null);
  const timerRef = useRef(null);

  const handleSubmit = useCallback(async () => {
    if (!attemptId) return;

    try {
      const result = await api.post('/tests/submit/', { attempt_id: attemptId, answers });
      setTestResult(result);
      clearInterval(timerRef.current);
      refetch().catch(() => {});
    } catch (err) {
      setError(err.message);
    }
  }, [attemptId, answers, refetch]);

  useEffect(() => {
    if (!activeTest || testResult || timeLeft <= 0) return undefined;

    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [activeTest, testResult, timeLeft, handleSubmit]);

  const handleStartTest = async (test) => {
    setStartingId(test.id);
    setError('');
    try {
      const started = await api.post(`/tests/${test.id}/start/`, {});
      const detail = await api.get(`/tests/${test.id}/`);
      setAttemptId(started.attempt_id);
      setActiveTest(detail);
      setTimeLeft(started.duration_minutes * 60);
      setAnswers({});
      setMarked({});
      setCurrentQ(0);
      setTestResult(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setStartingId(null);
    }
  };

  const handleAnswer = (questionId, option) => {
    setAnswers((prev) => ({ ...prev, [questionId]: option }));
  };

  const toggleMarked = (questionId) => {
    setMarked((prev) => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const exitResult = () => {
    setTestResult(null);
    setActiveTest(null);
    setAttemptId(null);
    setTimeLeft(0);
    setCurrentQ(0);
    setAnswers({});
    setMarked({});
  };

  if (activeTest && !testResult) {
    const questions = activeTest.questions || [];
    const question = questions[currentQ];
    const answeredCount = Object.keys(answers).length;
    const markedCount = Object.values(marked).filter(Boolean).length;

    return (
      <Layout title={activeTest.name} subtitle={`Question ${currentQ + 1}/${questions.length}`}>
        <div className="mock-exam">
          <Card className="mock-exam__top">
            <div className="mock-exam__timer">
              <Clock size={18} />
              <span className={timeLeft < 60 ? 'mock-exam__time mock-exam__time--danger' : 'mock-exam__time'}>
                {formatTime(timeLeft)}
              </span>
            </div>
            <div className="mock-exam__summary">
              <span>{answeredCount} answered</span>
              <span>{questions.length - answeredCount} unanswered</span>
              <span>{markedCount} marked</span>
            </div>
            <Button variant="danger" size="sm" onClick={handleSubmit} icon={AlertCircle}>
              Submit
            </Button>
          </Card>

          {error && <div className="mock-test__error">{error}</div>}

          <div className="mock-exam__layout">
            <Card className="mock-exam__question-card">
              {question ? (
                <>
                  <div className="mock-exam__question-meta">
                    <span>{question.difficulty}</span>
                    <span>{activeTest.marks_per_question} mark</span>
                  </div>
                  <h3>{question.question_text}</h3>
                  <div className="mock-test__options">
                    {optionList(question).map((option) => (
                      <button
                        key={option.key}
                        type="button"
                        className={`mock-test__option ${answers[question.id] === option.key ? 'mock-test__option--selected' : ''}`}
                        onClick={() => handleAnswer(question.id, option.key)}
                      >
                        <span className="mock-test__opt-label">{option.key}</span>
                        <span>{option.text}</span>
                      </button>
                    ))}
                  </div>
                  <div className="mock-test__nav">
                    <Button
                      variant="secondary"
                      disabled={currentQ === 0}
                      onClick={() => setCurrentQ((prev) => prev - 1)}
                    >
                      Previous
                    </Button>
                    <Button
                      variant={marked[question.id] ? 'secondary' : 'ghost'}
                      onClick={() => toggleMarked(question.id)}
                      icon={Flag}
                    >
                      {marked[question.id] ? 'Marked' : 'Mark review'}
                    </Button>
                    {currentQ < questions.length - 1 ? (
                      <Button variant="primary" onClick={() => setCurrentQ((prev) => prev + 1)}>Save and next</Button>
                    ) : (
                      <Button variant="danger" onClick={handleSubmit} icon={AlertCircle}>Submit test</Button>
                    )}
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <div className="empty-state__title">No questions available</div>
                </div>
              )}
            </Card>

            <Card className="mock-exam__palette">
              <Card.Header>Question palette</Card.Header>
              <Card.Body>
                <div className="mock-test__questions-nav">
                  {questions.map((item, index) => (
                    <button
                      key={item.id}
                      type="button"
                      className={[
                        'mock-test__q-dot',
                        index === currentQ ? 'mock-test__q-dot--active' : '',
                        answers[item.id] ? 'mock-test__q-dot--answered' : '',
                        marked[item.id] ? 'mock-test__q-dot--marked' : '',
                      ].filter(Boolean).join(' ')}
                      onClick={() => setCurrentQ(index)}
                    >
                      {index + 1}
                    </button>
                  ))}
                </div>
                <div className="mock-exam__instructions">
                  {(activeTest.instructions || []).map((instruction) => (
                    <p key={instruction}>{instruction}</p>
                  ))}
                </div>
              </Card.Body>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  if (testResult) {
    const pct = testResult.percentage || Math.round((testResult.score / testResult.total) * 100);
    return (
      <Layout title="Test result" subtitle={activeTest?.name}>
        <Card className="mock-test__result">
          <div className="mock-test__result-grid">
            <div>
              <div className="mock-test__result-score" style={{ color: pct >= 70 ? 'var(--green)' : pct >= 50 ? 'var(--amber)' : 'var(--red)' }}>
                {pct}%
              </div>
              <p>{testResult.score}/{testResult.total} correct</p>
            </div>
            <div className="mock-test__result-stats">
              <span>Correct: {testResult.correct}</span>
              <span>Incorrect: {testResult.incorrect}</span>
              <span>Unanswered: {testResult.unanswered}</span>
            </div>
          </div>
          <div className="mock-test__result-details">
            {(testResult.results || []).map((result, index) => (
              <div key={result.question_id} className={`mock-test__result-q ${result.is_correct ? 'mock-test__result-q--correct' : 'mock-test__result-q--wrong'}`}>
                {result.is_correct ? <CheckCircle size={16} /> : <XCircle size={16} />}
                <span>
                  Q{index + 1} - {result.topic}: {result.your_answer || 'Not answered'}
                  {!result.is_correct && ` (Correct: ${result.correct_answer})`}
                </span>
              </div>
            ))}
          </div>
          <Button variant="secondary" onClick={exitResult}>
            Back to tests
          </Button>
        </Card>
      </Layout>
    );
  }

  if (loading) return <Layout title="Mock Tests"><div className="skeleton skeleton--card" /></Layout>;

  const tests = data?.tests || [];
  const summary = data?.summary;

  return (
    <Layout title="Mock Tests" subtitle={summary ? `${summary.test_count} tests - ${summary.total_questions} questions` : 'Timed placement assessments'}>
      <div className="mock-tests">
        {error && <div className="mock-test__error">{error}</div>}

        {summary && (
          <div className="grid grid--4">
            <div className="stat-card">
              <div className="stat-card__label">Tests</div>
              <div className="stat-card__value">{summary.test_count}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Questions</div>
              <div className="stat-card__value">{summary.total_questions}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Completed</div>
              <div className="stat-card__value">{summary.completed_attempts}</div>
            </div>
            <div className="stat-card">
              <div className="stat-card__label">Avg duration</div>
              <div className="stat-card__value">{summary.average_duration}m</div>
            </div>
          </div>
        )}

        <div className="mock-tests__grid">
          {tests.map((test) => (
            <Card key={test.id} hover className="mock-test-card">
              <div className="mock-test-card__head">
                <ClipboardList size={20} />
                <span>{test.topic_count} sections</span>
              </div>
              <h3>{test.name}</h3>
              <p>{test.description}</p>
              <div className="mock-test-card__meta">
                <span><Clock size={14} />{test.duration_minutes} min</span>
                <span>{test.question_count} questions</span>
                <span>{test.total_marks} marks</span>
              </div>
              <div className="mock-test-card__sections">
                {(test.sections || []).slice(0, 4).map((section) => (
                  <span key={section.id}>{section.name}</span>
                ))}
              </div>
              <div className="mock-test-card__scores">
                <span>Last: {test.last_score != null ? `${test.last_score}%` : 'Not attempted'}</span>
                <span>Best: {test.best_score != null ? `${test.best_score}%` : 'Not attempted'}</span>
              </div>
              <Button
                variant="primary"
                size="sm"
                icon={Play}
                onClick={() => handleStartTest(test)}
                loading={startingId === test.id}
                disabled={test.question_count === 0}
              >
                Start test
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </Layout>
  );
}

export default MockTestsPage;
