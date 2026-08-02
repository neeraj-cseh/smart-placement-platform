import requests
res = requests.post('https://emkc.org/api/v2/piston/execute', json={
    'language': 'java', 
    'version': '15.0.2', 
    'files': [{'content': 'public class Main { public static void main(String[] args) { System.out.println("Hello API"); } }'}]
})
print(res.json())
