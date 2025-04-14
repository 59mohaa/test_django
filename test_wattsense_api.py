import requests
import base64
import hashlib
import hmac
import time
from urllib import parse
import warnings

# Ignorer les avertissements SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Remplacez ces valeurs par vos vraies clés
API_KEY = "7VCPRq8GEjT1tvPrg5zOS38eZsYRclCAQIe87fU71YrgfYqhIY2SWGKbDtdjCapP"  # Votre clé API
API_SECRET = "BtEmjHCMw9NlKKJ2mDE95JIynSlbPUtD2yE3qP3k5NbAEykWnYPkgRaepEcMTumbjf0QL3zlnzsaICEbd2qRYz1_sxSAkxV6"  # Votre clé secrète

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

# URL de l'API
url = 'https://api.wattsense.com'

try:
    print('Testing Wattsense API connection')
   
    # Faire une requête pour obtenir la liste des appareils
    req = requests.get(f'{url}/v1/devices',
                      auth=WattsenseAuth(api_key=API_KEY, api_secret=API_SECRET),
                      verify=False)
   
    print(f"Status code: {req.status_code}")
   
    if req.status_code == 200:
        data = req.json()
        print(f"Successfully retrieved {len(data)} devices")
        if len(data) > 0:
            print(f"First device: {data[0]}")
    else:
        print(f"Error message: {req.text}")
       
except Exception as e:
    print(f"Error: {str(e)}")