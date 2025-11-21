import httpx
import time

print("En attente du serveur...")
time.sleep(2)

try:
    # Test de connexion au serveur
    r = httpx.get('http://127.0.0.1:8000/health', timeout=5.0)
    print(f"✓ Serveur accessible: {r.status_code}")
    print(f"  Réponse: {r.json()}")
    print()
except Exception as e:
    print(f"✗ Erreur de connexion: {e}")
    print("  Le serveur n'est pas démarré ou n'est pas accessible")
    exit(1)

# Test de création d'utilisateur
print("Test création utilisateur admin...")
try:
    r = httpx.post(
        'http://127.0.0.1:8000/api/v1/auth/signup',
        json={
            'email': 'admin@ecotrack.com',
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin'
        },
        timeout=10.0
    )
    print(f"Status: {r.status_code}")
    
    if r.status_code == 201:
        print("✓ Utilisateur créé avec succès!")
        print(f"  Données: {r.json()}")
    else:
        print(f"✗ Erreur lors de la création")
        print(f"  Réponse: {r.text}")
        
except Exception as e:
    print(f"✗ Exception: {e}")

# Test de login
print("\nTest de connexion...")
try:
    r = httpx.post(
        'http://127.0.0.1:8000/api/v1/auth/login',
        data={
            'username': 'admin',
            'password': 'admin123'
        },
        timeout=10.0
    )
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        print("✓ Connexion réussie!")
        token_data = r.json()
        print(f"  Token: {token_data.get('access_token', 'N/A')[:50]}...")
    else:
        print(f"✗ Erreur de connexion")
        print(f"  Réponse: {r.text}")
        
except Exception as e:
    print(f"✗ Exception: {e}")
