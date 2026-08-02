import os

filepath = 'frontend-react/src/pages/problem-solving.css'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    'color: #fff;': 'color: var(--ps-text-primary);',
    'background: rgba(255,255,255,0.05);': 'background: var(--ps-bg-hover);',
    'background: rgba(255,255,255,0.06);': 'background: var(--ps-bg-hover);',
    'background: rgba(255,255,255,0.03);': 'background: var(--ps-bg-hover);',
    'background: rgba(255,255,255,0.1);': 'background: var(--ps-bg-active);',
    'background: rgba(255,255,255,0.2);': 'background: var(--ps-bg-hover);',
    'background: #1e1e1e;': 'background: var(--ps-bg-surface);'
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("CSS fixed.")
