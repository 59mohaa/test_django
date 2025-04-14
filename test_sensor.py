import requests
import base64
import hashlib
import hmac
import time
from urllib import parse
import warnings

# Ignorer les avertissements SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Configuration
url = 'https://api.wattsense.com'
api_key = '7VCPRq8GEjT1tvPrg5zOS38eZsYRclCAQIe87fU71YrgfYqhIY2SWGKbDtdjCapP'  # clé API 
api_secret = 'BtEmjHCMw9NlKKJ2mDE95JIynSlbPUtD2yE3qP3k5NbAEykWnYPkgRaepEcMTumbjf0QL3zlnzsaICEbd2qRYz1_sxSAkxV6'  # clé secrète 

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

if __name__ == '__main__':
    print('Getting devices')
    req = requests.get(f'{url}/v1/devices', auth=WattsenseAuth(api_key=api_key, api_secret=api_secret), verify=False)
    print(f"Status code: {req.status_code}")
   
    if req.status_code == 200:
        devices = req.json()
        print(f"Successfully retrieved {len(devices)} devices")
       
        # Tester les deux devices
        for i, device in enumerate(devices):
            device_id = device['deviceId']
            print(f"\n--- Testing device {i+1}: {device_id} ---")
           
            endpoints = [
                '/properties/all',
                '/properties',
                '/configs/current/properties'
            ]
           
            for endpoint in endpoints:
                full_url = f'{url}/v1/devices/{device_id}{endpoint}'
                print(f'Trying endpoint: {full_url}')
               
                req = requests.get(
                    full_url,
                    auth=WattsenseAuth(api_key=api_key, api_secret=api_secret),
                    verify=False
                )
               
                print(f"Status code: {req.status_code}")
                if req.status_code == 200:
                    print(f"Success! Response length: {len(req.text)} characters")
                    if len(req.text) > 0:
                        try:
                            data = req.json()
                            if isinstance(data, list):
                                print(f"Found {len(data)} items")
                                if len(data) > 0:
                                    print("First item preview:", str(data[0])[:200], "...")
                            else:
                                print("Response is not a list")
                                print(f"Response preview: {str(data)[:200]}...")
                        except Exception as e:
                            print(f"Error parsing JSON: {e}")
                elif req.status_code == 204:
                    print("No content available")
                else:
                    print(f"Error response: {req.text[:500]}...")