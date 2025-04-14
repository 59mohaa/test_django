from django.utils import timezone
from datetime import timedelta
from .models import Sensor, SensorData
from . import wattsense_api

def fetch_sensor_data():
    """
    Récupère les données des capteurs depuis l'API Wattsense et les stocke en base de données.
    Peut être exécuté manuellement ou configuré comme tâche périodique.
    """
    # Récupérer tous les capteurs
    sensors = Sensor.objects.all()
    results = {
        'success': 0,
        'errors': 0,
        'total_data_points': 0
    }
   
    # Pour chaque capteur, récupérer ses données
    for sensor in sensors:
        try:
            # Définir la période (par exemple, les dernières 6 heures)
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=6)
           
            # Récupérer les données via l'API
            sensor_data = wattsense_api.get_sensor_data(
                sensor.sensor_id,
                start_time=start_time,
                end_time=end_time
            )
           
            # Pour chaque point de données, créer une entrée dans la base
            for data_point in sensor_data:
                timestamp = data_point.get('timestamp')
                value = data_point.get('value')
               
                if timestamp and value is not None:
                    # Vérifier si cette donnée existe déjà (pour éviter les doublons)
                    exists = SensorData.objects.filter(
                        sensor=sensor,
                        timestamp=timestamp
                    ).exists()
                   
                    if not exists:
                        SensorData.objects.create(
                            sensor=sensor,
                            timestamp=timestamp,
                            value=float(value)
                        )
                        results['total_data_points'] += 1
           
            results['success'] += 1
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {sensor.name}: {e}")
            results['errors'] += 1
   
    return results