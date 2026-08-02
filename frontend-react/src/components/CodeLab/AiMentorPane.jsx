import React, { useState } from 'react';
import { Terminal, X } from 'lucide-react';
import './ai-mentor.css';

export default function AiMentorPane({ onClose }) {
  const [aiInput, setAiInput] = useState('');
  const [aiMessages, setAiMessages] = useState([
    { role: 'assistant', text: "I'm your AI Coding Mentor. Need help optimizing this script or understanding an error?" }
  ]);

  const handleSendAiMessage = () => {
    if (!aiInput.trim()) return;
    setAiMessages(prev => [...prev, { role: 'user', text: aiInput }]);
    setAiInput('');
    
    setTimeout(() => {
      setAiMessages(prev => [
        ...prev,
        { role: 'assistant', text: "Try breaking down the problem into smaller functions. Also check out the time complexity of your approach." }
      ]);
    }, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendAiMessage();
    }
  };

  return (
    <div className="ai-mentor-container">
      <div className="ai-mentor-header">
        <div className="ai-mentor-title">
          <Terminal size={16} /> AI Mentor
        </div>
        {onClose && (
          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={16} />
          </button>
        )}
      </div>
      
      <div className="ai-mentor-messages">
        {aiMessages.map((msg, i) => (
          <div key={i} className={`ai-message ${msg.role}`}>
            {msg.text}
          </div>
        ))}
      </div>

      <div className="ai-mentor-input-wrapper">
        <textarea 
          className="ai-mentor-textarea"
          value={aiInput}
          onChange={e => setAiInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask AI..."
        />
      </div>
    </div>
  );
}
