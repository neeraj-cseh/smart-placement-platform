import requests, re
s = requests.Session()
r = s.post('http://127.0.0.1:8000/api/auth/login/', json={'email': 'student@prepsmart.dev', 'password': 'testpass123'})
token = r.json().get('access')
headers = {'Authorization': 'Bearer ' + token}

def check_url(url, label):
    r_api = s.get(url, headers=headers)
    if r_api.status_code != 200:
        html = r_api.text
        try:
            val = re.search(r'<pre class="exception_value">(.*?)</pre>', html, re.DOTALL).group(1)
            print(f"{label} ERROR:", val.strip()[:300])
        except Exception:
            print(f"{label} ERROR: Could not parse exception")
        
        frames = re.findall(r'in <code class="fname">(.*?)</code>.*?<code class="context">(.*?)</code>', html, re.DOTALL)
        for i, (fname, ctx) in enumerate(frames[-5:]):
            print(f"  Frame {i}: {fname.strip()} :: {ctx.strip()[:80]}")
    else:
        print(f"{label} OK!")

check_url('http://127.0.0.1:8000/api/prep/topic/advanced-array-problems/', 'advanced-array-problems')
