import urllib.request, json

# Get a token first
data = json.dumps({'email': 'student@prepsmart.dev', 'password': 'PrepSmart@123'}).encode()
req = urllib.request.Request(
    'http://localhost:8000/api/auth/login/',
    data=data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)
try:
    resp = urllib.request.urlopen(req, timeout=5)
    token_data = json.loads(resp.read())
    token = token_data.get('access', '')
    print(f'Auth OK. Token: {token[:30]}...')

    # Test DSA topic (Sliding Window)
    req2 = urllib.request.Request(
        'http://localhost:8000/api/prep/topic/sliding-window/',
        headers={'Authorization': f'Bearer {token}'}
    )
    resp2 = urllib.request.urlopen(req2, timeout=5)
    topic_data = json.loads(resp2.read())
    print(f'DSA Topic: {topic_data.get("name")}')
    print(f'  Sections: {len(topic_data.get("sections", []))}')
    print(f'  Questions: {len(topic_data.get("questions", []))}')
    print(f'  Problems: {len(topic_data.get("problems", []))}')
    print(f'  Visualization: {(topic_data.get("visualization") or {}).get("visualization_type")}')
    print(f'  Revision keys: {len((topic_data.get("revision") or {}).get("key_takeaways", []))}')

    # Test Aptitude topic
    req3 = urllib.request.Request(
        'http://localhost:8000/api/prep/topic/percentages-and-profit-loss/',
        headers={'Authorization': f'Bearer {token}'}
    )
    resp3 = urllib.request.urlopen(req3, timeout=5)
    topic2 = json.loads(resp3.read())
    print(f'Aptitude Topic: {topic2.get("name")}')
    print(f'  Sections: {len(topic2.get("sections", []))}')
    print(f'  Questions: {len(topic2.get("questions", []))}')
    print(f'  Problems: {len(topic2.get("problems", []))}')
    print('All checks passed!')

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f'Error: {e}')
