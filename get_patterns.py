import requests
from requests.auth import HTTPBasicAuth

USERNAME = 'read-036e2f7f09138f9797ff635816bb91c2'
PASSWORD = '/OqdF+GxeN0CnmHTZQrL3vBPh2ZAHMJKYtmThSys'

url = 'https://api.ravelry.com/patterns/search.json'

params = {
    'availability': 'free',
    'craft': 'crochet',   
    'sort': 'best'
}

response = requests.get(url, params=params, auth=HTTPBasicAuth(USERNAME, PASSWORD))

if response.status_code == 200:
    data = response.json()
    patterns = data.get('patterns', [])
    for pattern in patterns:
        print(f"Title: {pattern['name']}")
        print(f"Designer: {pattern.get('designer', {}).get('name', 'Unknown')}") 
        print(f"URL: https://www.ravelry.com/patterns/library/{pattern['permalink']}")
        print("-" * 40)
else:
    print(f"Error: {response.status_code} - {response.text}")