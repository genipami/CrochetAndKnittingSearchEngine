
import requests
from requests.auth import HTTPBasicAuth

USERNAME = 'read-036e2f7f09138f9797ff635816bb91c2'
PASSWORD = '/OqdF+GxeN0CnmHTZQrL3vBPh2ZAHMJKYtmThSys'

url = 'https://api.ravelry.com/patterns/search.json'

params = {
    'availability': 'free',
    'craft': 'knitting',
    'sort': 'best',
    'page_size': 100
}

with open('patterns_with_ids_knitting.txt', 'a', encoding='utf-8') as file:
    for page in range(1, 21):
        params['page'] = page
        response = requests.get(url, params=params, auth=HTTPBasicAuth(USERNAME, PASSWORD))

        if response.status_code == 200:
            data = response.json()
            patterns = data.get('patterns', [])
            print(f"[Page {page}] Retrieved {len(patterns)} patterns")

            for pattern in patterns:
                pid = pattern.get('id')
                permalink = pattern.get('permalink')
                if pid and permalink:
                    file.write(f"{pid},{permalink},https://www.ravelry.com/patterns/library/{permalink}\n")
        else:
            print(f"[Page {page}] Error: {response.status_code} - {response.text}")
