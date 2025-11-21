"""Script de test rapide pour l'API."""
import httpx
import json

# Login
r = httpx.post('http://127.0.0.1:8000/api/v1/auth/login', data={
    'username': 'admin@ecotrack.com',
    'password': 'admin123'
})
print(f"Login status: {r.status_code}")
if r.status_code != 200:
    print(f"Login failed: {r.text}")
    exit(1)
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test zones
print("=== TEST ZONES ===")
r2 = httpx.get('http://127.0.0.1:8000/api/v1/zones?limit=3', headers=headers)
data = r2.json()
print(f"Status: {r2.status_code}")
print(f"Total zones: {data['total']}")
print(f"Has more: {data['has_more']}")
print(f"Items: {len(data['items'])}")

# Test indicators
print("\n=== TEST INDICATORS ===")
r3 = httpx.get('http://127.0.0.1:8000/api/v1/indicators?limit=5', headers=headers)
data = r3.json()
print(f"Status: {r3.status_code}")
print(f"Total indicators: {data['total']}")
print(f"Has more: {data['has_more']}")
print(f"Items: {len(data['items'])}")

# Test sources
print("\n=== TEST SOURCES ===")
r4 = httpx.get('http://127.0.0.1:8000/api/v1/sources?limit=2', headers=headers)
data = r4.json()
print(f"Status: {r4.status_code}")
print(f"Total sources: {data['total']}")
print(f"Has more: {data['has_more']}")
print(f"Items: {len(data['items'])}")

print("\n✅ Tous les tests réussis !")
