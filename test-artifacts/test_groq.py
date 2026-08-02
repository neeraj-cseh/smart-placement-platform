import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from django.conf import settings

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
print("Key exists:", bool(GROQ_API_KEY))

if GROQ_API_KEY:
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": 'Evaluate this answer: test. Respond with strictly valid JSON only: {"score": 10, "feedback": "ok"}'}],
                "response_format": {"type": "json_object"}
            }
        )
        print("Status:", res.status_code)
        print("Body:", res.text)
    except Exception as e:
        print("Exception:", e)
