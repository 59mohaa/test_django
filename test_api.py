import requests
import warnings

# Ignorer les avertissements SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Remplissez avec vos identifiants
API_URL = "https://api.wattsense.com/"  # URL Wattsense
API_KEY = "7VCPRq8GEjT1tvPrg5zOS38eZsYRclCAQIe87fU71YrgfYqhIY2SWGKbDtdjCapP"  # clé API complète

# Endpoint pour lister les capteurs
url = f"{API_URL}/sensors"

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

try:
    # Désactiver la vérification SSL
    response = requests.get(url, headers=headers, verify=False)
   
    print(f"Statut de la réponse: {response.status_code}")
    print(f"Contenu de la réponse: {response.text}")
   
    if response.status_code == 200:
        try:
            data = response.json()
            print("Données JSON valides")
            print(f"Nombre de capteurs trouvés: {len(data)}")
            if data:
                print("Premier capteur:", data[0])
        except Exception as json_error:
            print(f"Erreur lors du parsing JSON: {json_error}")
   
except Exception as e:
    print(f"Erreur de connexion: {str(e)}")