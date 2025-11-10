#!/usr/bin/env python3
import requests
import re
import json

# Get CSRF token
print("Fetching CSRF token...")
response = requests.get('https://maps.yandex.ru')
csrf_match = re.search(r'csrfToken["\s:]+["\']([^"\']+)["\']', response.text)
csrf_token = csrf_match.group(1) if csrf_match else ''
print(f"CSRF token: {csrf_token[:20]}..." if csrf_token else "Not found")

# Get cookies
cookies = response.cookies

# Make API request
params = {
    'text': 'cafe moscow',
    'chain': '',
    'lang': 'ru_RU',
    'origin': 'maps-form',
    'results': '5',
    'snippets': 'business/1.x,masstransit/1.x,panoramas/1.x,businessrating/2.x,photos/1.x,businessreviews/1.x',
    'ask_direct': '0',
    'csrfToken': csrf_token
}

print("\nMaking API request...")
api_response = requests.get(
    'https://maps.yandex.ru/api/search',
    params=params,
    cookies=cookies,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://maps.yandex.ru/',
        'Accept': 'application/json',
    }
)

print(f"Status: {api_response.status_code}")
data = api_response.json()
print(f"\nResponse keys: {list(data.keys())}")

if 'data' in data and 'features' in data['data']:
    features = data['data']['features']
    print(f"Found {len(features)} features")
    if features:
        first = features[0]
        props = first.get('properties', {})
        company = props.get('CompanyMetaData', {})
        print(f"\nFirst result:")
        print(f"  Name: {company.get('name', 'N/A')}")
        print(f"  Address: {company.get('address', 'N/A')}")
else:
    print(f"\nFull response: {json.dumps(data, indent=2)[:500]}")
