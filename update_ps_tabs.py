import os

filepath = 'c:/Users/neera/OneDrive/Desktop/smart-placement-platform/frontend-react/src/pages/problem-solving.css'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

tabs_old = """.ps-tab {
  padding: 0 12px;
  height: 38px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: var(--ps-text-secondary);
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}
.ps-tab:hover { color: var(--ps-text-primary); }
.ps-tab.active {
  color: var(--ps-accent);
  border-bottom-color: var(--ps-accent);
}"""

tabs_new = """.ps-tab {
  padding: 0 16px;
  height: 38px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--ps-text-secondary);
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
}
.ps-tab:hover { 
  color: var(--ps-text-primary); 
  background: rgba(255,255,255,0.02);
}
[data-theme="light"] .ps-tab:hover {
  background: rgba(0,0,0,0.02);
}
.ps-tab.active {
  color: var(--ps-accent);
  border-bottom-color: var(--ps-accent);
  background: linear-gradient(to top, rgba(59,130,246,0.1) 0%, transparent 100%);
}"""

content = content.replace(tabs_old, tabs_new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("problem-solving.css tabs updated.")
