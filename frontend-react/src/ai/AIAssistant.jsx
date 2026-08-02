/**
 * PrepSmart — AI Interaction Framework
 * Unified AI assistant personality, components, and interaction system.
 *
 * Exports: AIAssistant, AITypingIndicator, AIResponseCard,
 *          AISuggestionChips, AIRecommendationBanner,
 *          useAIPersonality, AI_PERSONALITY
 */

import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot, X, Send, Sparkles, Minimize2, Maximize2,
  RefreshCw, ThumbsUp, ThumbsDown, Copy,
} from 'lucide-react';
import { aiPanelReveal, aiSuggestion, stagger, fadeUp } from '../animations/motion';
import { useAIStore } from '../stores';
import { useCopyToClipboard } from '../hooks';
import './ai.css';

/* ─────────────────────────────────────────────────────────────────
   AI PERSONALITY CONSTANTS
   ───────────────────────────────────────────────────────────────── */
export const AI_PERSONALITY = {
  name:       'PrepSmart AI',
  tone:       'intelligent, concise, motivational, strategic',
  avatar:     '🤖',
  greetings: [
    "Ready to dominate today's prep?",
    "Let's sharpen your edge.",
    "I've analyzed your progress — here's what matters most.",
    "Your placement goal is within reach. Let's move.",
  ],
  randomGreeting: () =>
    AI_PERSONALITY.greetings[Math.floor(Math.random() * AI_PERSONALITY.greetings.length)],
};

/* Context-aware suggestions by page */
const CONTEXT_SUGGESTIONS = {
  dashboard: [
    '🎯 Build me a 7-day Amazon prep plan',
    '📊 Analyze my top 3 weak areas',
    '🧩 Generate a DP problem set for today',
    '💼 What\'s my Amazon readiness gap?',
  ],
  practice: [
    '💡 Explain the optimal approach for this problem',
    '⏱️ Time-optimize my solution',
    '🔍 Find similar problems on this pattern',
    '📝 Give me hints without the full solution',
  ],
  analytics: [
    '📈 What improved most this week?',
    '🎯 Predict my OA success rate',
    '📉 Why did my score drop on Thursday?',
    '🗓️ Build a recovery plan for weak topics',
  ],
  companies: [
    '🏆 Rank my target companies by readiness',
    '⚡ What\'s stopping me from Amazon eligibility?',
    '📋 Generate a company-specific prep checklist',
    '🔮 Predict my offer probability',
  ],
  resume: [
    '🔍 Analyze my resume for ATS compliance',
    '⚡ Rewrite a generic bullet point with metrics',
    '🎯 How does my resume match Google guidelines?',
    '💬 What is the recruiter eye-scan rejection risk?',
  ],
  passport: [
    '🛡️ Show my verified competency certificates',
    '📈 Check my placement employability score',
    '⚠️ Run an AI credibility analysis audit',
    '🎯 Generate a roadmap to verify my DP skills',
  ],
};

/* ─────────────────────────────────────────────────────────────────
   AI TYPING INDICATOR
   ───────────────────────────────────────────────────────────────── */
export function AITypingIndicator() {
  return (
    <div className="ai-typing">
      <div className="ai-typing__avatar">{AI_PERSONALITY.avatar}</div>
      <div className="ai-typing__dots">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="ai-typing__dot"
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
          />
        ))}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   AI MESSAGE BUBBLE
   ───────────────────────────────────────────────────────────────── */
function AIMessageBubble({ message }) {
  const { copied, copy } = useCopyToClipboard();
  const isAI = message.role === 'assistant';

  return (
    <motion.div
      className={`ai-msg ai-msg--${isAI ? 'ai' : 'user'}`}
      variants={fadeUp}
      initial="hidden"
      animate="show"
    >
      {isAI && <div className="ai-msg__avatar">{AI_PERSONALITY.avatar}</div>}
      <div className="ai-msg__bubble">
        <div className="ai-msg__text">{message.content}</div>
        {isAI && (
          <div className="ai-msg__actions">
            <button className="ai-msg__action" onClick={() => copy(message.content)} title="Copy">
              <Copy size={11} />
              {copied ? 'Copied!' : ''}
            </button>
            <button className="ai-msg__action" title="Helpful">
              <ThumbsUp size={11} />
            </button>
            <button className="ai-msg__action" title="Not helpful">
              <ThumbsDown size={11} />
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   AI SUGGESTION CHIPS
   ───────────────────────────────────────────────────────────────── */
export function AISuggestionChips({ suggestions, onSelect }) {
  return (
    <motion.div className="ai-chips" variants={stagger} initial="hidden" animate="show">
      {suggestions.map((s, i) => (
        <motion.button
          key={i}
          className="ai-chip"
          variants={aiSuggestion}
          whileHover={{ scale: 1.03, borderColor: 'var(--ai-primary)' }}
          whileTap={{ scale: 0.97 }}
          onClick={() => onSelect?.(s)}
        >
          {s}
        </motion.button>
      ))}
    </motion.div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   AI RECOMMENDATION BANNER (inline use anywhere)
   ───────────────────────────────────────────────────────────────── */
export function AIRecommendationBanner({ text, onAction, actionLabel = 'Ask AI' }) {
  return (
    <motion.div
      className="ai-banner"
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="ai-banner__left">
        <span className="ai-banner__icon">✨</span>
        <span className="ai-banner__text">{text}</span>
      </div>
      {onAction && (
        <button className="ai-banner__action" onClick={onAction}>{actionLabel}</button>
      )}
    </motion.div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   AI RESPONSE CARD (for widget embeds)
   ───────────────────────────────────────────────────────────────── */
export function AIResponseCard({ title, content, priority = 'normal', onDismiss }) {
  const priorityMap = { critical: 'red', high: 'amber', normal: 'ai', low: 'green' };
  const tone = priorityMap[priority] || 'ai';

  return (
    <motion.div
      className={`ai-response-card ai-response-card--${tone}`}
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 12 }}
      whileHover={{ x: 3 }}
    >
      <div className="ai-response-card__icon">
        <Sparkles size={13} />
      </div>
      <div className="ai-response-card__body">
        {title && <div className="ai-response-card__title">{title}</div>}
        <div className="ai-response-card__text">{content}</div>
      </div>
      {onDismiss && (
        <button className="ai-response-card__close" onClick={onDismiss}>
          <X size={12} />
        </button>
      )}
    </motion.div>
  );
}

/* ─────────────────────────────────────────────────────────────────
   MAIN AI ASSISTANT PANEL
   ───────────────────────────────────────────────────────────────── */
export function AIAssistant() {
  const { isOpen, isMinimized, close, minimize, restore, toggle,
          messages, isTyping, context, setContext, addMessage, setTyping, clearChat,
          suggestions, setSuggestions } = useAIStore();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const location = useLocation();
  const { user } = useAuth();

  // Sync pathname to AI Assistant context
  useEffect(() => {
    const path = location.pathname.substring(1);
    if (CONTEXT_SUGGESTIONS[path]) {
      setContext(path);
    } else if (location.pathname === '/') {
      setContext('dashboard');
    } else {
      setContext(null);
    }
  }, [location.pathname, setContext]);

  /* Scroll to bottom on new messages */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  /* Update suggestions based on context */
  useEffect(() => {
    if (context && CONTEXT_SUGGESTIONS[context]) {
      setSuggestions(CONTEXT_SUGGESTIONS[context]);
    }
  }, [context, setSuggestions]);

  const handleSend = async (text) => {
    const message = (text || input).trim();
    if (!message) return;
    setInput('');

    addMessage({ role: 'user', content: message });
    setTyping(true);

    /* Simulate AI response (replace with real API call) */
    await new Promise((r) => setTimeout(r, 1400 + Math.random() * 800));
    setTyping(false);
    addMessage({
      role: 'assistant',
      content: generateMockResponse(message),
    });
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (user?.is_admin) return null;

  return (
    <>
      {/* Floating Orb */}
      <motion.button
        className="ai-orb"
        onClick={toggle}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        title="Open AI Assistant"
        aria-label="Toggle AI Assistant"
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.span key="x" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }}>
              <X size={22} />
            </motion.span>
          ) : (
            <motion.span key="bot" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }}>
              <Bot size={22} />
            </motion.span>
          )}
        </AnimatePresence>
        <motion.div className="ai-orb__ring" animate={{ scale: [1, 1.4, 1], opacity: [0.5, 0, 0.5] }} transition={{ duration: 2.5, repeat: Infinity }} />
      </motion.button>

      {/* Panel */}
      <AnimatePresence>
        {isOpen && !isMinimized && (
          <motion.div
            className="ai-panel"
            variants={aiPanelReveal}
            initial="hidden"
            animate="show"
            exit="exit"
          >
            {/* Panel Header */}
            <div className="ai-panel__header">
              <div className="ai-panel__title">
                <span className="ai-panel__avatar">{AI_PERSONALITY.avatar}</span>
                <div>
                  <div className="ai-panel__name">{AI_PERSONALITY.name}</div>
                  <div className="ai-panel__status">
                    <span className="ai-panel__status-dot" />
                    Online · Context: {context || 'Global'}
                  </div>
                </div>
              </div>
              <div className="ai-panel__controls">
                {messages.length > 0 && (
                  <button className="ai-panel__btn" onClick={clearChat} title="Clear chat">
                    <RefreshCw size={13} />
                  </button>
                )}
                <button className="ai-panel__btn" onClick={minimize} title="Minimize">
                  <Minimize2 size={13} />
                </button>
                <button className="ai-panel__btn" onClick={close} title="Close">
                  <X size={14} />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="ai-panel__messages">
              {messages.length === 0 ? (
                <div className="ai-panel__welcome">
                  <div className="ai-panel__welcome-text">
                    {AI_PERSONALITY.randomGreeting()}
                  </div>
                  <AISuggestionChips
                    suggestions={suggestions}
                    onSelect={(s) => handleSend(s.replace(/^[^\s]+ /, ''))}
                  />
                </div>
              ) : (
                <>
                  {messages.map((msg) => (
                    <AIMessageBubble key={msg.id} message={msg} />
                  ))}
                  {isTyping && <AITypingIndicator />}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Input */}
            <div className="ai-panel__input-wrap">
              <textarea
                ref={inputRef}
                className="ai-panel__input"
                placeholder="Ask PrepSmart AI anything..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
              />
              <motion.button
                className="ai-panel__send"
                onClick={() => handleSend()}
                disabled={!input.trim() || isTyping}
                whileHover={{ scale: 1.08 }}
                whileTap={{ scale: 0.92 }}
              >
                <Send size={14} />
              </motion.button>
            </div>
          </motion.div>
        )}

        {/* Minimized pill */}
        {isOpen && isMinimized && (
          <motion.button
            className="ai-pill"
            onClick={restore}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
          >
            <span>{AI_PERSONALITY.avatar}</span>
            <span>PrepSmart AI</span>
            <Maximize2 size={12} />
          </motion.button>
        )}
      </AnimatePresence>
    </>
  );
}

/* ─────────────────────────────────────────────────────────────────
   MOCK RESPONSE GENERATOR (replace with real API)
   ───────────────────────────────────────────────────────────────── */
function generateMockResponse(message) {
  const m = message.toLowerCase();
  if (m.includes('passport') || m.includes('competency') || m.includes('verify') || m.includes('certificate')) {
    return "Your PrepSmart Skills Passport tracks 10 core placement competencies (DSA, DP, SQL, etc.). Currently, 6 of these are verified with cryptographic certificates (overall competency index at 78%). Click 'Run verification sweep' on any unverified skill to check your sandbox footprint and validate it.";
  }
  if (m.includes('credibility') || m.includes('claims') || m.includes('audit')) {
    return "My credibility scanner indicates a discrepancy: you have listed AWS/caching stack skills on your projects, but show no compiled execution logs or test evidence. Solve graph problems and link hosted code repositories to clear warning alerts.";
  }
  if (m.includes('employability') || m.includes('reputation')) {
    return "Your overall Employability Index stands at 74%, placing you in the Top 12% of PrepSmart pool candidates. This score is backed by your Gold Level Verified Profile and 3 active competency badges. Boost System Design validation to reach the Platinum tier.";
  }
  if (m.includes('resume') || m.includes('ats') || m.includes('bullet')) {
    return "I've analyzed your active resume profile. Your overall strength is 68%, with an ATS compatibility score of 65% and a recruiter appeal score of 62%. Your main gaps are (1) lack of quantified impact metrics in your experience bullets and (2) missing critical technology keywords like Kubernetes, Docker, and AWS. Use the AI Rewriter in the Resume command center to instantly optimize these.";
  }
  if (m.includes('eye-scan') || m.includes('rejection') || m.includes('recruiter')) {
    return "According to the Recruiter Simulation eye-tracking engine, your top profile risks are: (1) no cloud/deployment stacks visible in the first 2 seconds of scanning, and (2) your Education section is placed too high for a competitive software engineer profile. Toggle the heat zone overlay on the Resume page to visualize attention hotspots.";
  }
  if (m.includes('amazon')) return "For Amazon readiness, focus on: Graphs (BFS/DFS), Dynamic Programming, and System Design basics. Your current gap is ~28%. At your practice pace, you can close it in 3 weeks.";
  if (m.includes('plan') || m.includes('study')) return "Here's your 7-day plan: Day 1-2: DP patterns (Knapsack, LCS). Day 3-4: Graph algorithms. Day 5: SQL + DBMS revision. Day 6: 2 mock tests. Day 7: Weak area sprint. Want me to add this to your mission center?";
  if (m.includes('weak') || m.includes('improve')) return "Your 3 biggest opportunities: (1) Dynamic Programming — 61% accuracy, target 80%. (2) OS Scheduling — not practiced in 5 days. (3) DBMS Joins — below threshold in last mock. Start with DP today.";
  if (m.includes('hint') || m.includes('help')) return "Look at the problem from a graph traversal perspective. Think about what state you're tracking in each step — you might not need extra space if you modify in-place.";
  return "Got it. Based on your current trajectory and prep data, I'd recommend prioritizing your weakest topics first, then moving to company-specific patterns. Should I generate a detailed breakdown?";
}

export default AIAssistant;
