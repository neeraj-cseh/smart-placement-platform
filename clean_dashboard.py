import re

with open('frontend-react/src/pages/DashboardPage.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove MOCK constants
content = re.sub(r'/\* ── Mock data supplements.*?\];', '/* ── Mock data removed ────────────── */', content, flags=re.DOTALL)

# 2. Replace metrics fallback
metrics_fallback = r'\}\) : \(\s+/\* Fallback stat cards \*/.*?\]\.map\(\(s, i\) => \('
content = re.sub(metrics_fallback, r'}) : data.metrics?.map((s, i) => (', content, flags=re.DOTALL)

# 3. Replace ternary fallbacks
ternaries = [
    (r'\(planItems\.length > 0 \? planItems : \[.*?\]\)', r'planItems'),
    (r'\(weekly\.length > 0 \? weekly : \[.*?\]\)', r'weekly'),
    (r'\(companies\.length > 0 \? companies\.slice\(0, 6\) : \[.*?\]\)', r'companies.slice(0, 6)'),
    (r'\(skills\.length > 0 \? skills : \[.*?\]\)', r'skills'),
    (r'\(weakTopics\.length > 0 \? weakTopics\.slice\(0, 3\) : \[.*?\]\)', r'weakTopics.slice(0, 3)'),
    (r'\(activity\.length > 0 \? activity : \[.*?\]\)', r'activity'),
    (r'\(interviewPrep\.length > 0 \? interviewPrep\.slice\(0, 2\) : \[.*?\]\)', r'interviewPrep.slice(0, 2)'),
]

for pattern, replacement in ternaries:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 4. Replace MOCK_RECO, MOCK_EVENTS, MOCK_BADGES mappings
content = content.replace('MOCK_RECO.map', '(data.recommendations || []).map')
content = content.replace('MOCK_EVENTS.map', '(data.events || []).map')
content = content.replace('MOCK_BADGES.map', '(data.badges || []).map')

# 5. Fix possible empty state issues by adding basic "|| []"
content = content.replace('planItems.map', '(planItems || []).map')
content = content.replace('weekly.map', '(weekly || []).map')
content = content.replace('activity.map', '(activity || []).map')

with open('frontend-react/src/pages/DashboardPage.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard cleaned successfully")
