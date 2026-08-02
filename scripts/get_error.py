import requests, re

s = requests.Session()
r = s.post('http://127.0.0.1:8000/api/auth/login/', json={'email': 'student@prepsmart.dev', 'password': 'testpass123'})
token = r.json().get('access')
headers = {'Authorization': 'Bearer ' + token}

r2 = s.get('http://127.0.0.1:8000/api/prep/topic/number-systems/ai-context/', headers=headers)
html = r2.text

# Extract key error info
lines = html.split('\n')
for i, line in enumerate(lines):
    stripped = line.strip()
    if any(x in stripped for x in ['OperationalError', 'exception_value', 'exception_type', 'Table', 'column', 'no such', 'does not exist']):
        print("LINE %d: %s" % (i, stripped[:200]))

print()
print("Status:", r2.status_code)
print("First 800 chars:")
print(html[:800])
