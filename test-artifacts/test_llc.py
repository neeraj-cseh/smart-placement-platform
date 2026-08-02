import requests
import time
from test_execution import get_auth_headers

def run_tests():
    headers = get_auth_headers()
    url = "http://localhost:8000/api/code/problems/linked-list-cycle/submit/"
    
    # Send code that will cause a TypeError (like in the screenshot)
    code = """class Solution:
    def solve(self):
        pass
"""
    payload = {
        "code": code,
        "language": "python"
    }
    
    res = requests.post(url, json=payload, headers=headers)
    print("Submit response:", res.json())

if __name__ == "__main__":
    run_tests()
