import os

filepath = 'c:/Users/neera/OneDrive/Desktop/smart-placement-platform/frontend-react/src/pages/problem-solving.css'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Header
header_old = """.ps-header {
  height: 38px;
  min-height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: var(--ps-bg-surface-glass);
  border-bottom: 1px solid var(--ps-border);
  flex-shrink: 0;
  z-index: 100;
}"""

header_new = """.ps-header {
  height: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: linear-gradient(90deg, var(--ps-bg-surface-glass), rgba(59,130,246,0.05));
  border-bottom: 1px solid rgba(59,130,246,0.2);
  flex-shrink: 0;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}"""

# Replace Buttons
btns_old = """.ps-run-btn, .ps-submit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 10px;
  height: 24px;
  border-radius: var(--ps-radius-sm);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  border: none;
}
.ps-run-btn {
  background: var(--ps-bg-active);
  color: var(--ps-text-primary);
}
.ps-run-btn:hover:not(:disabled) { background: var(--ps-bg-hover); }

.ps-submit-btn {
  background: var(--ps-green);
  color: #000;
}
.ps-submit-btn:hover:not(:disabled) { 
  background: #73b870; 
}
.ps-run-btn:disabled, .ps-submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }"""

btns_new = """.ps-run-btn, .ps-submit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  height: 28px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}
.ps-run-btn {
  background: rgba(255,255,255,0.05);
  color: var(--ps-text-primary);
  border: 1px solid var(--ps-border);
}
[data-theme="light"] .ps-run-btn {
  background: rgba(0,0,0,0.05);
}
.ps-run-btn:hover:not(:disabled) { 
  background: rgba(255,255,255,0.1); 
  border-color: var(--ps-border-light);
}
[data-theme="light"] .ps-run-btn:hover:not(:disabled) {
  background: rgba(0,0,0,0.1);
}

.ps-submit-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
}
.ps-submit-btn:hover:not(:disabled) { 
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
  transform: translateY(-1px);
}
.ps-run-btn:disabled, .ps-submit-btn:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; transform: none; }"""

content = content.replace(header_old, header_new)
content = content.replace(btns_old, btns_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("problem-solving.css updated.")
