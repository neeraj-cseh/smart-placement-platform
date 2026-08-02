import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import Editor from '@monaco-editor/react';
import { useApi } from '../hooks/useApi';
import AiMentorPane from '../components/CodeLab/AiMentorPane';
import { 
  Play, Send, ChevronLeft, Clock, CheckCircle2, XCircle, 
  Terminal, Maximize2, Minimize2, Code2, Loader2, Bot, Timer,
  PanelLeft, Copy, Check, Settings, Activity, FileCode2
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import mermaid from 'mermaid';
import { Panel, Group as PanelGroup, Separator as PanelResizeHandle } from 'react-resizable-panels';
import { useTheme } from '../contexts/ThemeContext';
import './problem-solving.css';

const LANGUAGE_STARTERS = {
  python: 'class Solution:\n    def solve(self):\n        pass\n',
  javascript: '/**\n * @param {number[]} nums\n * @return {number[]}\n */\nvar solve = function(nums) {\n    // Write your solution\n};',
  java: 'class Solution {\n    public int[] solve(int[] nums) {\n        // Write your solution\n        return new int[]{};\n    }\n}',
  cpp: 'class Solution {\npublic:\n    vector<int> solve(vector<int>& nums) {\n        // Write your solution\n        return {};\n    }\n};',
  c: 'int* solve(int* nums, int numsSize, int* returnSize) {\n    // Write your solution\n    return NULL;\n}',
};

// Mermaid integration for Markdown
const Mermaid = ({ chart }) => {
  const ref = useRef(null);
  
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      securityLevel: 'loose',
    });
    
    if (ref.current && chart) {
      try {
        mermaid.render(`mermaid-${Math.random().toString(36).substr(2, 9)}`, chart).then(({ svg }) => {
          if (ref.current) ref.current.innerHTML = svg;
        });
      } catch (e) {
        console.error("Mermaid parsing failed", e);
      }
    }
  }, [chart]);
  
  return <div ref={ref} className="mermaid-chart" style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }} />;
};

export default function ProblemSolvingPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const workspaceRef = useRef(null);

  const { data: realProblem, loading } = useApi('/code/problems/' + slug + '/');
  const problem = realProblem || null;
  const testCases = React.useMemo(() => problem?.test_cases || [], [problem]);
  
  const [language, setLanguage] = useState('python');
  const [codes, setCodes] = useState({ ...LANGUAGE_STARTERS });
  const { theme: globalTheme } = useTheme();
  const theme = globalTheme === 'dark' ? 'vs-dark' : 'light';
  const [fontSize, setFontSize] = useState(14);
  const [showSettings, setShowSettings] = useState(false);
  
  const [isAiOpen, setIsAiOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [terminalOpen, setTerminalOpen] = useState(true);
  const [descriptionOpen, setDescriptionOpen] = useState(true);
  
  const [activeTab, setActiveTab] = useState('description');
  const [activeConsoleTab, setActiveConsoleTab] = useState('testcases');
  
  const { data: editorialData, loading: editorialLoading } = useApi(activeTab === 'editorial' ? '/code/problems/' + slug + '/editorial/' : null);
  const { data: submissionsData, loading: submissionsLoading, refetch: refetchSubmissions } = useApi(activeConsoleTab === 'submissions' ? '/code/problems/' + slug + '/submissions/' : null);
  
  const [isInterviewMode, setIsInterviewMode] = useState(false);
  const [interviewTimer, setInterviewTimer] = useState(2700); // 45 mins
  const [isTimerRunning, setIsTimerRunning] = useState(false);

  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [activeTestCase, setActiveTestCase] = useState(1);
  const [customTestCase, setCustomTestCase] = useState('');
  
  const [runResult, setRunResult] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem(`code_${slug}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setCodes(parsed);
      } catch (e) { console.error("Error parsing code from localStorage", e); }
    } else if (problem?.starter_code) {
      setCodes(prev => ({
        ...prev,
        python: problem.starter_code.python || prev.python,
        javascript: problem.starter_code.javascript || prev.javascript,
        java: problem.starter_code.java || prev.java,
        cpp: problem.starter_code.cpp || prev.cpp,
      }));
    }
  }, [problem, slug]);

  useEffect(() => {
    localStorage.setItem(`code_${slug}`, JSON.stringify(codes));
  }, [codes, slug]);



  useEffect(() => {
    let interval = null;
    if (isTimerRunning && interviewTimer > 0) {
      interval = setInterval(() => {
        setInterviewTimer(t => t - 1);
      }, 1000);
    } else if (interviewTimer <= 0) {
      setIsTimerRunning(false);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, interviewTimer]);

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const handleRunCode = React.useCallback(async () => {
    const code = codes[language];
    if (!code || !code.trim()) return;
    
    setIsRunning(true);
    setTerminalOpen(true);
    setActiveConsoleTab('result');
    setRunResult(null);
    
    try {
      const res = await api.post(`/code/problems/${slug}/run/`, {
        code,
        language,
        stdin: activeConsoleTab === 'custom' ? customTestCase : testCases[activeTestCase - 1]?.input
      });
      setRunResult(res);
    } catch (err) {
      setRunResult({ error: err.message || 'Execution Failed' });
    } finally {
      setIsRunning(false);
    }
  }, [codes, language, activeConsoleTab, customTestCase, testCases, activeTestCase, slug]);

  const handleSubmitCode = async () => {
    const code = codes[language];
    if (!code || !code.trim()) return;
    
    setIsSubmitting(true);
    setTerminalOpen(true);
    setActiveConsoleTab('result');
    setRunResult(null);
    
    try {
      const res = await api.post(`/code/problems/${slug}/submit/`, {
        code,
        language
      });
      setRunResult(res);
      if (res.status === 'Accepted' && isInterviewMode) {
        setIsTimerRunning(false);
      }
      if (activeConsoleTab === 'submissions' && refetchSubmissions) {
        refetchSubmissions();
      }
    } catch (err) {
      setRunResult({ error: err.message || 'Submission Failed' });
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleRunCode();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleRunCode]);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(codes[language] || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading || !problem) {
    return (
      <div className="ps-container" style={{alignItems:'center', justifyContent:'center'}}>
        <div style={{display:'flex', flexDirection:'column', alignItems:'center', gap:'12px'}}>
          <Loader2 size={24} className="animate-spin" color="var(--ps-accent)" />
          <span style={{color: 'var(--ps-text-secondary)', fontSize: '13px'}}>Initializing IDE...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`ps-container ${isFullscreen ? 'ps-fullscreen' : ''}`} ref={workspaceRef}>
      
      {/* COMPACT GLOBAL HEADER */}
      <div className="ps-header">
        <div className="ps-header-left">
          <button className="ps-icon-btn" onClick={() => navigate('/code-lab/arena')} title="Exit Workspace">
            <ChevronLeft size={16} />
          </button>
          <button className="ps-icon-btn" onClick={() => setDescriptionOpen(!descriptionOpen)} title="Toggle Layout">
            <PanelLeft size={14} />
          </button>
          <div className="ps-header-title">
            {problem.title}
          </div>
        </div>
        
        <div className="ps-header-center">
          {isInterviewMode && (
            <div className={`ps-header-metrics ${isTimerRunning ? 'interview-active' : ''}`}>
              <Timer size={12} />
              {formatTimer(interviewTimer)}
            </div>
          )}
        </div>
        
        <div className="ps-header-right">
          <button 
            className="ps-icon-btn" 
            onClick={() => {
              if (!isInterviewMode) {
                setIsInterviewMode(true);
                setIsTimerRunning(true);
              } else {
                setIsInterviewMode(false);
                setIsTimerRunning(false);
                setInterviewTimer(2700);
              }
            }} 
            style={{ color: isInterviewMode ? 'var(--ps-red)' : 'inherit' }} 
            title={isInterviewMode ? "End Interview" : "Interview Mode"}
          >
            <Clock size={14} />
          </button>
          
          <button className="ps-icon-btn" onClick={() => setTerminalOpen(!terminalOpen)} style={{ color: terminalOpen ? 'var(--ps-accent)' : 'inherit' }} title="Toggle Console">
            <Terminal size={14} />
          </button>
          
          <button className="ps-icon-btn" onClick={() => setIsAiOpen(!isAiOpen)} style={{ color: isAiOpen ? 'var(--ps-accent)' : 'inherit' }} title="AI Mentor">
            <Bot size={14} />
          </button>
          
          <div style={{ position: 'relative' }}>
            <button className="ps-icon-btn" onClick={() => setShowSettings(!showSettings)} style={{ color: showSettings ? 'var(--ps-accent)' : 'inherit' }} title="Editor Settings">
              <Settings size={14} />
            </button>
            {showSettings && (
              <div style={{ position: 'absolute', top: '100%', right: 0, marginTop: '8px', background: 'var(--ps-bg-surface)', border: '1px solid var(--ps-border)', padding: '12px', zIndex: 200, width: '200px', boxShadow: '0 4px 20px rgba(0,0,0,0.5)' }}>

                <div>
                  <label style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--ps-text-secondary)', marginBottom: '4px' }}>
                    <span>Font Size</span>
                    <span style={{color: 'var(--ps-accent)'}}>{fontSize}px</span>
                  </label>
                  <input type="range" min="10" max="24" value={fontSize} onChange={e => setFontSize(parseInt(e.target.value))} style={{ width: '100%', accentColor: 'var(--ps-accent)' }} />
                </div>
              </div>
            )}
          </div>
          
          <button className="ps-icon-btn" onClick={() => {
            if (!document.fullscreenElement) {
              workspaceRef.current?.requestFullscreen();
              setIsFullscreen(true);
            } else {
              document.exitFullscreen();
              setIsFullscreen(false);
            }
          }}>
            {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </div>
      
      {/* EDGE-TO-EDGE WORKSPACE BODY */}
      <div className="ps-body">
        
        <PanelGroup direction="horizontal" orientation="horizontal" autoSaveId="ps-workspace-v4">
          
          {/* LEFT PANE: Description / Editorial */}
          {descriptionOpen && (
            <>
              <Panel defaultSize={40} minSize={20} className="ps-panel">
                <div className="ps-panel-header">
                  <div className="ps-console-tabs">
                    <button className={`ps-tab ${activeTab === 'description' ? 'active' : ''}`} onClick={() => setActiveTab('description')}>
                      <FileCode2 size={12} style={{display:'inline', marginRight:'4px'}}/> Description
                    </button>
                    <button className={`ps-tab ${activeTab === 'editorial' ? 'active' : ''}`} onClick={() => setActiveTab('editorial')}>
                      <Activity size={12} style={{display:'inline', marginRight:'4px'}}/> Editorial
                    </button>
                  </div>
                </div>
                
                <div className="ps-markdown-content">
                  {activeTab === 'description' && (
                    <>
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm, remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                        components={{
                          code({node, inline, className, children, ...props}) {
                            const match = /language-(\w+)/.exec(className || '')
                            if (!inline && match && match[1] === 'mermaid') {
                              return <Mermaid chart={String(children).replace(/\n$/, '')} />
                            }
                            return <code className={className} {...props}>{children}</code>
                          }
                        }}
                      >
                        {problem.description || "# Description not available"}
                      </ReactMarkdown>
                  
                      <div className="ps-tags-list">
                        <span className="ps-tag" style={{ color: problem.difficulty?.toLowerCase() === 'easy' ? 'var(--ps-green)' : problem.difficulty?.toLowerCase() === 'medium' ? 'var(--ps-amber)' : 'var(--ps-red)' }}>
                          {problem.difficulty?.toUpperCase()}
                        </span>
                        {problem.topics?.map(topic => (
                          <span key={typeof topic === 'string' ? topic : topic.id || topic.name} className="ps-tag">
                            {typeof topic === 'string' ? topic : topic.name}
                          </span>
                        ))}
                      </div>
                    </>
                  )}

                  {activeTab === 'editorial' && (
                    <>
                      {editorialLoading ? <div style={{textAlign:'center', marginTop: '20px'}}><Loader2 className="animate-spin" size={16} color="var(--ps-accent)"/></div> : 
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {editorialData?.content || "No editorial is currently available for this problem."}
                        </ReactMarkdown>
                      }
                    </>
                  )}
                </div>
              </Panel>
              <PanelResizeHandle className="ps-resizer ps-resizer-vertical" />
            </>
          )}

          {/* RIGHT PANE: Vertical Split for Editor & Console */}
          <Panel defaultSize={60} minSize={30} style={{ display: 'flex', flexDirection: 'column', minHeight: 0, minWidth: 0 }}>
            <PanelGroup direction="vertical" orientation="vertical" autoSaveId="ps-right-v5-vertical">
              
              {/* TOP: Editor Panel */}
              <Panel defaultSize={terminalOpen ? 70 : 100} minSize={20} className="ps-panel">
                <div className="ps-panel-header">
                  <div className="ps-editor-actions">
                    <select 
                      value={language} 
                      onChange={(e) => setLanguage(e.target.value)} 
                      className="ps-lang-select"
                    >
                      <option value="python">Python</option>
                      <option value="javascript">JavaScript</option>
                      <option value="java">Java</option>
                      <option value="cpp">C++</option>
                      <option value="c">C</option>
                    </select>
                  </div>
                  
                  <div className="ps-editor-actions">
                    <button className="ps-icon-btn" style={{ marginRight: '4px' }} onClick={handleCopyCode} title="Copy Code">
                      {copied ? <Check size={14} color="var(--ps-green)" /> : <Copy size={14} />}
                    </button>
                    
                    <button className="ps-run-btn" onClick={handleRunCode} disabled={isRunning || isSubmitting}>
                      {isRunning ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} fill="currentColor" />}
                      Run
                    </button>
                    
                    <button className="ps-submit-btn" onClick={handleSubmitCode} disabled={isRunning || isSubmitting}>
                      {isSubmitting ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
                      Submit
                    </button>
                  </div>
                </div>
                
                <div className="ps-editor-container">
                  <Editor
                    height="100%"
                    theme={theme}
                    language={language === 'cpp' || language === 'c' ? 'cpp' : language}
                    value={codes[language] || ''}
                    onChange={(v) => setCodes(prev => ({ ...prev, [language]: v }))}
                    options={{
                      minimap: { enabled: false },
                      fontSize: fontSize,
                      fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
                      lineNumbers: 'on',
                      scrollBeyondLastLine: false,
                      padding: { top: 12 },
                      overviewRulerBorder: false,
                      hideCursorInOverviewRuler: true,
                      renderLineHighlight: "all",
                    }}
                  />
                </div>
              </Panel>

              {terminalOpen && (
                <>
                  <PanelResizeHandle className="ps-resizer ps-resizer-horizontal" />
                  
                  {/* BOTTOM: Console Panel */}
                  <Panel defaultSize={30} minSize={15} className="ps-panel">
                    <div className="ps-panel-header">
                      <div className="ps-console-tabs">
                        <button 
                          className={`ps-tab ${activeConsoleTab === 'testcases' ? 'active' : ''}`}
                          onClick={() => setActiveConsoleTab('testcases')}
                        >
                          Testcases
                        </button>
                        <button 
                          className={`ps-tab ${activeConsoleTab === 'custom' ? 'active' : ''}`}
                          onClick={() => setActiveConsoleTab('custom')}
                        >
                          Custom Input
                        </button>
                        <button 
                          className={`ps-tab ${activeConsoleTab === 'result' ? 'active' : ''}`}
                          onClick={() => setActiveConsoleTab('result')}
                        >
                          Result
                        </button>
                        <button 
                          className={`ps-tab ${activeConsoleTab === 'submissions' ? 'active' : ''}`}
                          onClick={() => setActiveConsoleTab('submissions')}
                        >
                          Submissions
                        </button>
                      </div>
                    </div>
                    
                    <div className="ps-console-content">
                      {activeConsoleTab === 'testcases' && (
                        <div className="ps-testcase-split">
                          <div className="ps-testcase-list">
                            {testCases.map((tc, idx) => (
                              <button 
                                key={tc.id || idx}
                                className={`ps-tc-btn ${activeTestCase === (idx + 1) ? 'active' : ''}`}
                                onClick={() => setActiveTestCase(idx + 1)}
                              >
                                Case {idx + 1}
                              </button>
                            ))}
                          </div>
                          <div className="ps-testcase-details">
                            <div className="ps-tc-block">
                              <div className="ps-tc-label">Input</div>
                              <div className="ps-tc-val">{testCases[activeTestCase - 1]?.input}</div>
                            </div>
                            <div className="ps-tc-block">
                              <div className="ps-tc-label">Expected Output</div>
                              <div className="ps-tc-val">{testCases[activeTestCase - 1]?.expected}</div>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {activeConsoleTab === 'custom' && (
                        <textarea
                          className="ps-input-area"
                          value={customTestCase}
                          onChange={(e) => setCustomTestCase(e.target.value)}
                          placeholder="Enter your custom stdin parameters here..."
                          spellCheck={false}
                        />
                      )}
                      
                      {activeConsoleTab === 'result' && (
                        <div className="ps-result-pane">
                          {!runResult && !isRunning && !isSubmitting && (
                            <div className="ps-empty-state">
                              Run or submit your code to see output here.
                            </div>
                          )}
                          
                          {(isRunning || isSubmitting) && (
                            <div className="ps-empty-state">
                              <Loader2 size={16} className="animate-spin" color="var(--ps-accent)" />
                              Executing...
                            </div>
                          )}
                          
                          {runResult?.error && (
                            <>
                              <div className="ps-result-header ps-result-error">
                                <XCircle size={18} /> Error
                              </div>
                              <div className="ps-tc-val" style={{color: 'var(--ps-red)', borderColor: 'rgba(244, 135, 113, 0.3)'}}>
                                {runResult.error}
                              </div>
                            </>
                          )}
                          
                          {runResult?.status && !runResult?.error && (
                            <>
                              <div className={`ps-result-header ${runResult.status === 'Accepted' ? 'ps-result-success' : 'ps-result-error'}`}>
                                {runResult.status === 'Accepted' ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                                {runResult.status}
                              </div>
                              
                              <div style={{display:'flex', gap:'12px', flexWrap:'wrap'}}>
                                <div className="ps-metric-pill">
                                  Runtime <span>{runResult.execution_time_ms || 0} ms</span>
                                </div>
                                <div className="ps-metric-pill">
                                  Memory <span>{runResult.memory_kb ? (runResult.memory_kb/1024).toFixed(1) : 0} MB</span>
                                </div>
                                <div className="ps-metric-pill">
                                  Passed <span>{runResult.passed_cases ?? testCases.length}/{runResult.total_cases ?? testCases.length}</span>
                                </div>
                              </div>
                              
                              {runResult.output && !runResult.failed_testcase && (
                                <div className="ps-diff-container">
                                  <div className="ps-diff-header">Stdout</div>
                                  <div className="ps-diff-col" style={{borderRight:'none', padding:'12px'}}>
                                    <div className="ps-diff-content">{runResult.output}</div>
                                  </div>
                                </div>
                              )}
                              
                              {runResult.failed_testcase && (
                                <div className="ps-diff-container">
                                  <div className="ps-diff-header" style={{display:'flex', alignItems:'center', gap:'8px', color: 'var(--ps-red)'}}>
                                    Failed Testcase {runResult.failed_testcase.index}
                                    {runResult.failed_testcase.is_hidden && (
                                      <span style={{marginLeft:'auto', fontSize:'11px', background:'rgba(244,135,113,0.1)', padding:'2px 6px', borderRadius:'2px'}}>Hidden Case</span>
                                    )}
                                  </div>
                                  
                                  {!runResult.failed_testcase.is_hidden && (
                                    <>
                                      <div className="ps-diff-row">
                                        <div className="ps-diff-col" style={{borderRight:'none'}}>
                                          <div className="ps-diff-label">Input</div>
                                          <div className="ps-diff-content">{runResult.failed_testcase.input || 'Hidden'}</div>
                                        </div>
                                      </div>
                                      
                                      {runResult.failed_testcase.reason ? (
                                        <div className="ps-diff-row">
                                          <div className="ps-diff-col" style={{borderRight:'none'}}>
                                            <div className="ps-diff-label" style={{color:'var(--ps-red)'}}>Runtime Error / Exception</div>
                                            <div className="ps-diff-content mismatch" style={{whiteSpace: 'pre-wrap', fontFamily: 'monospace'}}>{runResult.failed_testcase.reason}</div>
                                          </div>
                                        </div>
                                      ) : (
                                        <div className="ps-diff-row">
                                          <div className="ps-diff-col">
                                            <div className="ps-diff-label">Expected Output</div>
                                            <div className="ps-diff-content">{runResult.failed_testcase.expected || 'Hidden'}</div>
                                          </div>
                                          <div className="ps-diff-col">
                                            <div className="ps-diff-label" style={{color:'var(--ps-red)'}}>Your Output</div>
                                            <div className="ps-diff-content mismatch">{runResult.failed_testcase.received || 'null'}</div>
                                          </div>
                                        </div>
                                      )}
                                    </>
                                  )}
                                </div>
                              )}
                             </>
                          )}
                          
                          {runResult && !runResult.status && !runResult.error && (
                            <>
                              <div className={`ps-result-header ${runResult.success ? 'ps-result-success' : 'ps-result-error'}`}>
                                {runResult.success ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                                {runResult.success ? 'Run Successful' : (runResult.timeout ? 'Time Limit Exceeded' : 'Run Failed')}
                              </div>
                              <div style={{display:'flex', gap:'12px'}}>
                                <div className="ps-metric-pill">
                                  Runtime <span>{runResult.execution_time_ms || 0} ms</span>
                                </div>
                                <div className="ps-metric-pill">
                                  Memory <span>{runResult.memory_kb ? (runResult.memory_kb/1024).toFixed(1) : 0} MB</span>
                                </div>
                              </div>
                              {runResult.output && (
                                <div className="ps-diff-container">
                                  <div className="ps-diff-header">Stdout</div>
                                  <div className="ps-diff-col" style={{borderRight:'none', padding:'12px'}}>
                                    <div className="ps-diff-content">{runResult.output}</div>
                                  </div>
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      )}
                      
                      {activeConsoleTab === 'submissions' && (
                        <div className="ps-result-pane">
                          {submissionsLoading ? <div style={{display:'flex', justifyContent:'center', marginTop: '20px'}}><Loader2 className="animate-spin" size={16} color="var(--ps-accent)"/></div> : 
                            submissionsData && submissionsData.length > 0 ? (
                              <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                                {submissionsData.map(sub => (
                                  <div key={sub.id} style={{
                                    padding: '12px', 
                                    border: '1px solid var(--ps-border)', 
                                    borderRadius: 'var(--ps-radius-sm)',
                                    background: sub.status === 'Accepted' ? 'rgba(137, 209, 133, 0.05)' : 'rgba(244, 135, 113, 0.05)'
                                  }}>
                                    <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center'}}>
                                      <strong style={{
                                        color: sub.status === 'Accepted' ? 'var(--ps-green)' : 'var(--ps-red)',
                                        fontSize: '13px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '6px'
                                      }}>
                                        {sub.status === 'Accepted' ? <CheckCircle2 size={14}/> : <XCircle size={14}/>}
                                        {sub.status}
                                      </strong>
                                      <span style={{fontSize: '11px', color: 'var(--ps-text-muted)'}}>
                                        {new Date(sub.created_at).toLocaleString()}
                                      </span>
                                    </div>
                                    <div style={{display: 'flex', gap: '12px'}}>
                                      <span style={{fontSize:'11px', color:'var(--ps-text-secondary)'}}>
                                        {sub.execution_time_ms || 0} ms
                                      </span>
                                      <span style={{fontSize:'11px', color:'var(--ps-text-secondary)'}}>
                                        {sub.language}
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="ps-empty-state">
                                No submissions yet.
                              </div>
                            )
                          }
                        </div>
                      )}
                    </div>
                  </Panel>
                </>
              )}
            </PanelGroup>
          </Panel>
        </PanelGroup>

        {isAiOpen && (
          <AiMentorPane onClose={() => setIsAiOpen(false)} />
        )}

      </div>
    </div>
  );
}
