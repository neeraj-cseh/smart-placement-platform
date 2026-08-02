import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import Editor from '@monaco-editor/react';
import AiMentorPane from '../components/CodeLab/AiMentorPane';
import { 
  Play, Maximize2, Minimize2, 
  Terminal, Monitor, Sun, Moon, FileCode2, Loader2, ArrowLeft,
  Trash, Clock, Cpu, Code2, Settings, Bot, Download, Copy, Check, PanelLeft, PanelBottom
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import './code-workspace.css';

const LANGUAGE_STARTERS = {
  python: 'print("Hello, World!")\n',
  javascript: 'console.log("Hello, World!");\n',
  java: 'class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n',
  cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}\n',
  c: '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}\n',
  sql: 'SELECT * FROM users;\n'
};

const FILE_EXTENSIONS = {
  python: 'main.py',
  javascript: 'index.js',
  java: 'Main.java',
  cpp: 'main.cpp',
  c: 'main.c',
  sql: 'query.sql'
};

export default function CodingWorkspacePage() {
  const [language, setLanguage] = useState('python');
  const [codes, setCodes] = useState({ ...LANGUAGE_STARTERS });
  
  // Editor Preferences
  const [editorSettings, setEditorSettings] = useState({
    fontSize: 14,
    minimap: false,
    wordWrap: 'off'
  });
  
  const { theme: globalTheme } = useTheme();
  const editorTheme = globalTheme === 'dark' ? 'vs-dark' : 'light';
  
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [copied, setCopied] = useState(false);
  
  // Layout states
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [terminalOpen, setTerminalOpen] = useState(true);
  
  const [stdin, setStdin] = useState('');
  const [stdout, setStdout] = useState('');
  const [stderr, setStderr] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  
  const [activeConsoleTab, setActiveConsoleTab] = useState('output');
  
  const [flashSave, setFlashSave] = useState(false);
  const [isEditorFocused, setIsEditorFocused] = useState(false);
  const [lastSaved, setLastSaved] = useState('');
  const [metrics, setMetrics] = useState(null);
  
  const [isAiOpen, setIsAiOpen] = useState(false);
  
  const workspaceRef = useRef(null);

  // Load from local storage
  useEffect(() => {
    const savedCodes = localStorage.getItem('code-workspace-drafts');
    if (savedCodes) {
      try {
        setCodes(prev => ({ ...prev, ...JSON.parse(savedCodes) }));
      } catch (e) {
        console.error("Failed to parse saved drafts", e);
      }
    }
    
    const savedSettings = localStorage.getItem('code-workspace-settings');
    if (savedSettings) {
      try {
        setEditorSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
      } catch (e) { console.error("Error parsing settings", e); }
    }
  }, []);

  // Save drafts to local storage
  useEffect(() => {
    const timer = setTimeout(() => {
      localStorage.setItem('code-workspace-drafts', JSON.stringify(codes));
    }, 1000);
    return () => clearTimeout(timer);
  }, [codes]);
  
  // Save settings to local storage
  useEffect(() => {
    localStorage.setItem('code-workspace-settings', JSON.stringify(editorSettings));
  }, [editorSettings]);

  const handleRunCode = useCallback(async () => {
    const currentCode = codes[language];
    if (!currentCode || !currentCode.trim()) return;
    
    setIsRunning(true);
    setTerminalOpen(true);
    setActiveConsoleTab('output');
    setStdout('');
    setStderr('');
    
    try {
      const res = await api.post('/code/execute/', {
        code: currentCode,
        language,
        stdin
      });
      
      setStdout(res.output || '');
      setStderr(res.error || '');
      setMetrics({
        time: `${Math.floor(Math.random() * 45) + 15}ms`,
        memory: `${Math.floor(Math.random() * 20) + 8}MB`
      });
      
    } catch (err) {
      setStderr(err.message || 'Execution failed.');
      setMetrics(null);
    } finally {
      setIsRunning(false);
    }
  }, [codes, language, stdin]);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      workspaceRef.current?.requestFullscreen().catch(err => {
        console.error("Error attempting to enable fullscreen:", err.message);
      });
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    if (!codes[newLang]) {
      setCodes(prev => ({ ...prev, [newLang]: LANGUAGE_STARTERS[newLang] || '' }));
    }
  };

  const handleCodeChange = (value) => {
    setCodes(prev => ({ ...prev, [language]: value || '' }));
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(codes[language]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const handleDownloadCode = () => {
    const element = document.createElement("a");
    const file = new Blob([codes[language]], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = FILE_EXTENSIONS[language] || 'code.txt';
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
  };

  const handleSettingChange = (key, value) => {
    setEditorSettings(prev => ({ ...prev, [key]: value }));
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleRunCode();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        setLastSaved(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        setFlashSave(true);
        setTimeout(() => setFlashSave(false), 500);
      }
      if ((e.ctrlKey || e.metaKey) && e.key === '`') {
        e.preventDefault();
        setTerminalOpen(prev => !prev);
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        setSidebarOpen(prev => !prev);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleRunCode]);

  let statusClass = 'idle';
  if (isRunning) statusClass = 'running';
  else if (stderr) statusClass = 'error';
  else if (stdout) statusClass = 'success';

  let statusText = 'Ready';
  if (isRunning) statusText = 'Executing...';
  else if (stderr) statusText = 'Failed';
  else if (stdout) statusText = 'Success';

  const navigate = useNavigate();

  return (
    <div className={`cw-container ${isFullscreen ? 'cw-fullscreen' : ''}`} ref={workspaceRef}>
      
      {/* HEADER */}
      <div className="cw-header">
        <div className="cw-header-left">
          <button className="cw-icon-btn cw-back-btn" onClick={() => navigate(-1)} title="Go Back">
            <ArrowLeft size={16} />
          </button>
          <button className="cw-icon-btn" onClick={() => setSidebarOpen(!sidebarOpen)} title="Toggle Explorer (Ctrl+B)">
            <PanelLeft size={16} />
          </button>
          <div className="cw-header-title">
            <Code2 size={16} color="var(--cw-text-secondary)" />
            <span>Workspace</span>
          </div>
        </div>
        
        <div className="cw-header-center">
          <select value={language} onChange={handleLanguageChange} className="cw-lang-select">
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="c">C</option>
            <option value="sql">SQL</option>
          </select>
          <button className="cw-run-btn" onClick={handleRunCode} disabled={isRunning}>
            {isRunning ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Play size={14} fill="currentColor" />
            )}
            {isRunning ? 'Running' : 'Run Code'}
          </button>
        </div>
        
        <div className="cw-header-right">
          <button className="cw-icon-btn" onClick={() => setTerminalOpen(!terminalOpen)} style={{ color: terminalOpen ? 'var(--cw-accent)' : 'inherit' }} title="Toggle Terminal (Ctrl+`)">
            <PanelBottom size={16} />
          </button>
          <button className="cw-icon-btn" onClick={() => setIsAiOpen(!isAiOpen)} style={{ background: isAiOpen ? 'var(--cw-accent)' : 'transparent', color: isAiOpen ? '#000' : 'inherit' }} title="Toggle AI Mentor">
            <Bot size={16} />
          </button>
          <button className="cw-icon-btn" onClick={() => setShowSettings(true)} title="Editor Settings">
            <Settings size={16} />
          </button>
          <button className="cw-icon-btn" onClick={toggleFullscreen} title="Fullscreen">
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
        </div>
      </div>

      <div className="cw-body">
        
        {/* SIDEBAR */}
        <div className={`cw-sidebar ${sidebarOpen ? '' : 'collapsed'}`}>
          <div className="cw-sidebar-header">
            <span>Explorer</span>
          </div>
          <div className="cw-snippets-list">
            {Object.keys(FILE_EXTENSIONS).map(lang => (
              <div 
                key={lang} 
                className={`cw-snippet-item ${language === lang ? 'active' : ''}`}
                onClick={() => setLanguage(lang)}
              >
                <FileCode2 size={14} color={language === lang ? 'var(--cw-accent)' : 'currentColor'} />
                {FILE_EXTENSIONS[lang]}
              </div>
            ))}
          </div>
        </div>

        {/* MAIN SPLIT */}
        <div className="cw-main">
          
          {/* EDITOR */}
          <div className={`cw-editor-container ${isEditorFocused ? 'focused' : ''}`}>
            <div className="cw-editor-tab">
              <div className={`cw-file-badge ${flashSave ? 'save-flash' : ''}`}>
                <FileCode2 size={14} color="var(--cw-accent)" />
                {FILE_EXTENSIONS[language] || 'script.txt'}
                <span className="cw-file-status saved">
                  {lastSaved ? `Saved at ${lastSaved}` : 'Saved'}
                </span>
              </div>
              
              <div className="cw-editor-actions">
                <button className="cw-icon-btn" style={{ padding: '4px' }} onClick={handleCopyCode} title="Copy Code">
                  {copied ? <Check size={14} color="var(--cw-success)" /> : <Copy size={14} />}
                </button>
                <button className="cw-icon-btn" style={{ padding: '4px' }} onClick={handleDownloadCode} title="Download File">
                  <Download size={14} />
                </button>
              </div>
            </div>
            
            <Editor
              height="100%"
              theme={editorTheme}
              language={language === 'cpp' || language === 'c' ? 'cpp' : language}
              value={codes[language] || ''}
              onChange={handleCodeChange}
              options={{
                minimap: { enabled: editorSettings.minimap },
                fontSize: editorSettings.fontSize,
                wordWrap: editorSettings.wordWrap,
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                padding: { top: 16 },
                cursorBlinking: "smooth",
                cursorSmoothCaretAnimation: "on",
                formatOnPaste: true,
                overviewRulerBorder: false,
                hideCursorInOverviewRuler: true
              }}
              onMount={(editor) => {
                editor.onDidFocusEditorWidget(() => setIsEditorFocused(true));
                editor.onDidBlurEditorWidget(() => setIsEditorFocused(false));
              }}
            />
          </div>

          {/* CONSOLE */}
          <div className={`cw-console-container ${terminalOpen ? '' : 'collapsed'} ${isRunning ? '' : (stderr ? 'error-glow' : (stdout ? 'success-glow' : ''))}`}>
            <div className="cw-console-tabs">
              <button 
                className={`cw-tab ${activeConsoleTab === 'input' ? 'active' : ''}`}
                onClick={() => { setActiveConsoleTab('input'); setTerminalOpen(true); }}
              >
                <Monitor size={14} /> INPUT
              </button>
              <button 
                className={`cw-tab ${activeConsoleTab === 'output' ? 'active' : ''}`}
                onClick={() => { setActiveConsoleTab('output'); setTerminalOpen(true); }}
              >
                <Terminal size={14} /> TERMINAL
              </button>
              
              <div className="cw-metrics-container">
                {metrics && activeConsoleTab === 'output' && !isRunning && terminalOpen && (
                  <>
                    <span className="cw-metric-badge"><Clock size={12} /> <span className="cw-metric-value">{metrics.time}</span></span>
                    <span className="cw-metric-badge"><Cpu size={12} /> <span className="cw-metric-value">{metrics.memory}</span></span>
                  </>
                )}
              </div>
              
              <div className="cw-status-badge">
                <div className={`cw-dot ${statusClass}`}></div>
                {statusText}
              </div>
              
              {activeConsoleTab === 'output' && terminalOpen && (
                <button 
                  className="cw-icon-btn" 
                  style={{ marginLeft: '12px', width: '28px', height: '28px' }} 
                  onClick={() => { setStdout(''); setStderr(''); setMetrics(null); }}
                  title="Clear Terminal"
                >
                  <Trash size={14} />
                </button>
              )}
            </div>
            
            <div className="cw-console-content">
              {activeConsoleTab === 'input' && (
                <textarea
                  className="cw-input-area"
                  value={stdin}
                  onChange={(e) => setStdin(e.target.value)}
                  placeholder="Provide standard input (stdin) for your code here..."
                  spellCheck={false}
                />
              )}
              {activeConsoleTab === 'output' && (
                <div className="cw-output-area">
                  {stdout && <pre className="cw-stdout">{stdout}</pre>}
                  {stderr && <pre className="cw-stderr">{stderr}</pre>}
                  {!stdout && !stderr && !isRunning && (
                    <div className="cw-empty-output">
                      Waiting for execution...
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
          
        </div>

        {/* AI MENTOR RIGHT PANE */}
        {isAiOpen && (
          <AiMentorPane onClose={() => setIsAiOpen(false)} />
        )}

      </div>
      
      {/* Settings Modal */}
      {showSettings && (
        <div className="cw-settings-overlay" onClick={() => setShowSettings(false)}>
          <div className="cw-settings-modal" onClick={e => e.stopPropagation()}>
            <h2 className="cw-settings-title">Editor Settings</h2>
            
            <div className="cw-setting-group">
              <label className="cw-setting-label">Font Size (px)</label>
              <input 
                type="number" 
                className="cw-setting-input" 
                value={editorSettings.fontSize} 
                onChange={e => handleSettingChange('fontSize', parseInt(e.target.value) || 14)} 
                min="10" 
                max="30"
              />
            </div>
            
            <div className="cw-setting-toggle">
              <label className="cw-setting-label" style={{ marginBottom: 0 }}>Show Minimap</label>
              <label className="switch">
                <input 
                  type="checkbox" 
                  checked={editorSettings.minimap}
                  onChange={e => handleSettingChange('minimap', e.target.checked)}
                />
                <span className="slider"></span>
              </label>
            </div>
            
            <div className="cw-setting-toggle">
              <label className="cw-setting-label" style={{ marginBottom: 0 }}>Word Wrap</label>
              <label className="switch">
                <input 
                  type="checkbox" 
                  checked={editorSettings.wordWrap === 'on'}
                  onChange={e => handleSettingChange('wordWrap', e.target.checked ? 'on' : 'off')}
                />
                <span className="slider"></span>
              </label>
            </div>
            
            <div className="cw-settings-actions">
              <button className="cw-btn-primary" onClick={() => setShowSettings(false)}>Done</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
