import { useState } from 'react';
import { api } from '../api/client';
import { useApi } from '../hooks/useApi';
import Layout from '../components/Layout';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { ArrowRight, BookOpen } from 'lucide-react';
import './practice.css';

function PracticePage() {
  const { data, loading } = useApi('/practice/');
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [result, setResult] = useState(null);

  if (loading) return <Layout title="Practice"><div className="skeleton skeleton--card" /></Layout>;
  if (!data) return null;

  const handleTopicClick = async (topic) => {
    setSelectedTopic(topic);
    setCurrentQ(0);
    setSelectedAnswer(null);
    setResult(null);
    try {
      const qData = await api.get(`/topics/${topic.id}/questions/`);
      setQuestions(qData);
    } catch {
      setQuestions([]);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer || !questions[currentQ]) return;
    try {
      const r = await api.post(`/questions/${questions[currentQ].id}/submit/`, { answer: selectedAnswer });
      setResult(r);
    } catch {
      setResult({ correct: false });
    }
  };

  const handleNext = () => {
    setCurrentQ(prev => prev + 1);
    setSelectedAnswer(null);
    setResult(null);
  };

  if (selectedTopic && questions.length > 0) {
    const q = questions[currentQ];
    return (
      <Layout title="Practice" subtitle={`${selectedTopic.name} - Question ${currentQ + 1}/${questions.length}`}>
        <Card className="practice__quiz">
          <h3 className="practice__question">{q.question_text}</h3>
          <div className="practice__options">
            {['A', 'B', 'C', 'D'].map((opt) => (
              <button
                key={opt}
                className={`practice__option ${selectedAnswer === opt ? 'practice__option--selected' : ''} ${result ? (result.correct_answer === opt ? 'practice__option--correct' : selectedAnswer === opt ? 'practice__option--wrong' : '') : ''}`}
                onClick={() => !result && setSelectedAnswer(opt)}
                disabled={!!result}
              >
                <span className="practice__option-label">{opt}</span>
                <span className="practice__option-text">{q[`option_${opt.toLowerCase()}`]}</span>
              </button>
            ))}
          </div>

          {result && (
            <div className={`practice__result ${result.correct ? 'practice__result--correct' : 'practice__result--wrong'}`}>
              {result.correct ? 'Correct!' : `Incorrect. The answer is ${result.correct_answer}`}
            </div>
          )}

          <div className="practice__quiz-actions">
            {!result ? (
              <Button variant="primary" onClick={handleSubmitAnswer} disabled={!selectedAnswer}>
                Submit answer
              </Button>
            ) : currentQ < questions.length - 1 ? (
              <Button variant="primary" onClick={handleNext} icon={ArrowRight}>
                Next question
              </Button>
            ) : (
              <Button variant="secondary" onClick={() => { setSelectedTopic(null); setQuestions([]); }}>
                Back to topics
              </Button>
            )}
          </div>
        </Card>
      </Layout>
    );
  }

  return (
    <Layout title="Practice" subtitle={`${data.summary.total_topics} topics - ${data.summary.total_questions} questions`}>
      <div className="grid grid--3">
        <div className="stat-card">
          <div className="stat-card__label">Topics practiced</div>
          <div className="stat-card__value">{data.summary.attempts}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Accuracy</div>
          <div className="stat-card__value">{data.summary.accuracy}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-card__label">Weak topics</div>
          <div className="stat-card__value">{data.summary.weak_topics}</div>
        </div>
      </div>

      <div style={{ marginTop: 24 }}>
        <h3 style={{ marginBottom: 16, fontSize: '1.125rem', fontWeight: 600 }}>Recommended practice</h3>
        <div className="grid grid--3" style={{ marginBottom: 32 }}>
          {data.recommended.map((topic) => (
            <Card key={topic.id} hover className="practice__topic-card" onClick={() => handleTopicClick(topic)}>
              <div className="practice__topic-header">
                <BookOpen size={20} />
                <span className={`badge badge--${topic.priority === 'high' ? 'red' : topic.priority === 'medium' ? 'amber' : 'green'}`}>
                  {topic.priority}
                </span>
              </div>
              <h4>{topic.name}</h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{topic.track}</p>
              <div style={{ marginTop: 12, display: 'flex', gap: 12, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                <span>{topic.question_count} questions</span>
                <span>{topic.accuracy}% accuracy</span>
              </div>
            </Card>
          ))}
        </div>

        <h3 style={{ marginBottom: 16, fontSize: '1.125rem', fontWeight: 600 }}>All topics</h3>
        <div className="practice__all-topics">
          {data.topics.map((topic) => (
            <div key={topic.id} className="practice__topic-row" onClick={() => handleTopicClick(topic)}>
              <span className="practice__topic-name">{topic.name}</span>
              <span className="practice__topic-track">{topic.track}</span>
              <span>{topic.question_count} Qs</span>
              <span className={`badge badge--${topic.tone}`}>{topic.accuracy}%</span>
              <ArrowRight size={14} />
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}

export default PracticePage;
