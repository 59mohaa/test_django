import requests
from datetime import datetime
from django.conf import settings

def get_sensors():
    """Récupère la liste des capteurs disponibles dans Wattsense"""
    url = f"{settings.WATTSENSE_API_URL}/sensors"
    headers = {
        'Authorization': f'Bearer {settings.WATTSENSE_API_KEY}',
        'Content-Type': 'application/json'
    }
   
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur API: {response.status_code} - {response.text}")
        return []

def get_sensor_data(sensor_id, start_time=None, end_time=None):
    """Récupère les données d'un capteur spécifique"""
    url = f"{settings.WATTSENSE_API_URL}/sensors/{sensor_id}/data"
    headers = {
        'Authorization': f'Bearer {settings.WATTSENSE_API_KEY}',
        'Content-Type': 'application/json'
    }
   
    params = {}
    if start_time:
        params['start'] = start_time.isoformat()
    if end_time:
        params['end'] = end_time.isoformat()
   
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur API: {response.status_code} - {response.text}")
        return []