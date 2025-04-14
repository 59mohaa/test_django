import requests
import base64
import hashlib
import hmac
import time
from urllib import parse
import warnings
from datetime import datetime, timedelta

# Ignorer les avertissements SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configuration
url = 'https://api.wattsense.com'
api_key = '7VCPRq8GEjT1tvPrg5zOS38eZsYRclCAQIe87fU71YrgfYqhIY2SWGKbDtdjCapP'  # Remplacez par votre clé API complète
api_secret = 'BtEmjHCMw9NlKKJ2mDE95JIynSlbPUtD2yE3qP3k5NbAEykWnYPkgRaepEcMTumbjf0QL3zlnzsaICEbd2qRYz1_sxSAkxV6'  # Remplacez par votre clé secrète complète
device_id = 'wc1CO6ip'  # Le second device qui contient des données

class WattsenseAuth(requests.auth.AuthBase):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def __call__(self, r):
        timestamp = int(time.time() * 1000)
        url = parse.urlparse(r.url)
        message = '\n'.join([str(e) for e in [r.method, url.path,
                            (url.query if url.query else None),
                            (r.body.decode('utf-8') if hasattr(r, 'body') and r.body else None),
                            timestamp] if e != None])

        hmac_hash = base64.b64encode(hmac.new(self.api_secret.encode(), message.encode(),
                                     hashlib.sha512).digest()).decode()

        r.headers['X-API-Auth'] = '{}:{}'.format(self.api_key, hmac_hash)
        r.headers['X-API-Timestamp'] = str(timestamp)

        return r

def search_properties(search_term):
    """Recherche des propriétés contenant un terme spécifique"""
    full_url = f'{url}/v1/devices/{device_id}/configs/current/properties'
   
    req = requests.get(
        full_url,
        auth=WattsenseAuth(api_key=api_key, api_secret=api_secret),
        verify=False
    )
   
    if req.status_code == 200:
        properties = req.json()
       
        # Filtrer les propriétés contenant le terme recherché
        matching_properties = []
        for prop in properties:
            name = prop.get('name', '').lower()
            prop_id = prop.get('propertyId', '').lower()
            slug = prop.get('slug', '').lower()
           
            if (search_term.lower() in name or
                search_term.lower() in prop_id or
                search_term.lower() in slug):
                matching_properties.append(prop)
       
        return matching_properties
    else:
        print(f"Erreur: {req.status_code} - {req.text}")
        return []

def get_temperature_properties():
    """Recherche des capteurs de température"""
    full_url = f'{url}/v1/devices/{device_id}/configs/current/properties'
   
    req = requests.get(
        full_url,
        auth=WattsenseAuth(api_key=api_key, api_secret=api_secret),
        verify=False
    )
   
    if req.status_code == 200:
        properties = req.json()
       
        # Filtrer les propriétés qui semblent être des capteurs de température
        temp_properties = []
        for prop in properties:
            name = prop.get('name', '').lower()
            unit = prop.get('unit', '').lower()
           
            # Chercher des mots-clés liés à la température
            if ('temp' in name or
                'température' in name or
                unit == '°c' or
                unit == 'c' or
                unit == 'celsius'):
                temp_properties.append(prop)
       
        return temp_properties
    else:
        print(f"Erreur: {req.status_code} - {req.text}")
        return []

def get_property_data(property_id):
    """Récupère les données d'une propriété"""
    # Récupérer les dernières 24 heures
    end_time = int(time.time() * 1000)
    start_time = end_time - (24 * 60 * 60 * 1000)  # 24 heures en millisecondes
   
    full_url = f'{url}/v1/devices/{device_id}/properties'
    params = {
        'property': property_id,
        'since': start_time,
        'until': end_time
    }
   
    req = requests.get(
        full_url,
        params=params,
        auth=WattsenseAuth(api_key=api_key, api_secret=api_secret),
        verify=False
    )
   
    if req.status_code == 200:
        return req.json()
    else:
        print(f"Erreur: {req.status_code} - {req.text}")
        return []

if __name__ == '__main__':
    print(f"Recherche du capteur '005-SERVEURS-TEMP-A2/Y7'...")
    matching_properties = search_properties('005-SERVEURS-TEMP-A2/Y7')
   
    if matching_properties:
        print(f"Capteur trouvé! {len(matching_properties)} correspondances.")
        for i, prop in enumerate(matching_properties):
            print(f"\n{i+1}. {prop.get('name')} (ID: {prop.get('propertyId')})")
            print(f"   Description: {prop.get('description', 'N/A')}")
            print(f"   Unité: {prop.get('unit', 'N/A')}")
            print(f"   Type d'accès: {prop.get('accessType', 'N/A')}")
    else:
        print("Capteur spécifique non trouvé. Recherche de capteurs de température...")
        temp_properties = get_temperature_properties()
       
        if temp_properties:
            print(f"Trouvé {len(temp_properties)} capteurs de température:")
            for i, prop in enumerate(temp_properties[:20]):  # Afficher les 20 premiers
                print(f"\n{i+1}. {prop.get('name')} (ID: {prop.get('propertyId')})")
                print(f"   Description: {prop.get('description', 'N/A')}")
                print(f"   Unité: {prop.get('unit', 'N/A')}")
                print(f"   Type d'accès: {prop.get('accessType', 'N/A')}")
           
            if len(temp_properties) > 20:
                print(f"\n... et {len(temp_properties) - 20} autres capteurs de température")
           
            # Demander à l'utilisateur de choisir un capteur pour voir ses données
            try:
                choice = int(input("\nEntrez le numéro du capteur que vous souhaitez explorer (0 pour quitter): "))
                if choice == 0:
                    exit()
               
                selected_property = temp_properties[choice-1]
                prop_id = selected_property.get('propertyId')
               
                print(f"\nRécupération des données pour {selected_property.get('name')}...")
                data = get_property_data(prop_id)
               
                if data:
                    print(f"Nombre de points de données: {len(data)}")
                    print("\nDernières valeurs:")
                   
                    # Afficher les 10 dernières valeurs
                    for point in data[:10]:
                        timestamp = datetime.fromtimestamp(point.get('timestamp', 0) / 1000)
                        value = point.get('payload', 'N/A')
                        print(f"{timestamp}: {value} {selected_property.get('unit', '')}")
                else:
                    print("Aucune donnée trouvée pour ce capteur.")
            except (ValueError, IndexError) as e:
                print(f"Erreur de sélection: {e}")
        else:
            print("Aucun capteur de température trouvé.")
