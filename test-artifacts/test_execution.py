import requests

base_url = "http://127.0.0.1:8000/api"

def test_code_execution():
    session = requests.Session()
    
    # 1. Register a test user
    test_user = {
        "email": "testexec@example.com",
        "name": "Test Exec",
        "password": "testpassword123",
        "confirm_password": "testpassword123",
        "role": "Student"
    }
    print("Registering user...")
    register_res = session.post(f"{base_url}/auth/register/", json=test_user)
    print(f"Register status: {register_res.status_code}")
    
    # 2. Login
    print("Logging in...")
    login_res = session.post(f"{base_url}/auth/login/", json={
        "email": "testexec@example.com",
        "password": "testpassword123"
    })
    print(f"Login status: {login_res.status_code}")
    if login_res.status_code != 200:
        print("Login failed, aborting.")
        return
        
    print(f"Login Response: {login_res.json()}")
    access_token = login_res.json().get("access")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # 3. Test Run Code (Two Sum)
    print("Testing Code Run...")
    run_payload = {
        "code": '''class Solution:
    def solve(self, nums, target):
        hash_map = {}
        for i, num in enumerate(nums):
            if target - num in hash_map:
                return [hash_map[target - num], i]
            hash_map[num] = i
        return []''',
        "language": "python",
        "stdin": "[2,7,11,15]\n9"
    }
    run_res = session.post(f"{base_url}/code/problems/two-sum/run/", json=run_payload, headers=headers)
    print(f"Run status: {run_res.status_code}")
    print(f"Run response: {run_res.json()}")
    
    # 4. Test Submit Code (Two Sum)
    print("Testing Code Submit...")
    submit_res = session.post(f"{base_url}/code/problems/two-sum/submit/", json=run_payload, headers=headers)
    print(f"Submit status: {submit_res.status_code}")
    print(f"Submit response: {submit_res.json()}")

if __name__ == "__main__":
    test_code_execution()
