import os

filepath = 'c:/Users/neera/OneDrive/Desktop/smart-placement-platform/frontend-react/src/pages/problem-solving.css'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if i == 13: # Line 14: --ps-text-primary: #cccccc;
        new_lines.append(line)
        continue
    
    # Replace #cccccc and #d4d4d4 with var(--ps-text-primary)
    line = line.replace('#cccccc', 'var(--ps-text-primary)')
    line = line.replace('#d4d4d4', 'var(--ps-text-primary)')
    
    new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Colors updated successfully.")
