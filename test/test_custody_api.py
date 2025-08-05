import sys
import requests
import json

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000'
    url = f'{base_url}/api/custody'
    print(f'Testing endpoint: {url}')
    try:
        response = requests.get(url, headers={'User-Agent': 'CustodesTestScript'})
        print(f'Status code: {response.status_code}')
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except Exception as e:
            print('Failed to parse JSON:', e)
            print('Raw body:', response.text)
    except Exception as e:
        print('Request failed:', e)

if __name__ == '__main__':
    main() 