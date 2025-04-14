from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Sensor, SensorData, Scenario
from .forms import SensorForm, ScenarioForm
from . import wattsense_api
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.utils import timezone





def dashboard(request):
    """Affiche le tableau de bord avec tous les capteurs"""
    sensors = Sensor.objects.all()
    return render(request, 'sensors/dashboard.html', {'sensors': sensors})

def sensor_detail(request, sensor_id):
    """Affiche les détails d'un capteur, ses données et ses scénarios"""
    sensor = get_object_or_404(Sensor, id=sensor_id)
   
    # Récupérer les dernières 24h de données par défaut
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
   
    # Récupérer les données depuis la base
    data_points = SensorData.objects.filter(
        sensor=sensor,
        timestamp__gte=start_time,
        timestamp__lte=end_time
    ).order_by('timestamp')
   
    # Récupérer les scénarios associés
    scenarios = sensor.scenarios.all()
   
    context = {
        'sensor': sensor,
        'data_points': data_points,
        'scenarios': scenarios
    }
    return render(request, 'sensors/sensor_detail.html', context)

def scenario_create(request, sensor_id):
    """Crée un nouveau scénario pour un capteur"""
    sensor = get_object_or_404(Sensor, id=sensor_id)
   
    if request.method == 'POST':
        form = ScenarioForm(request.POST)
        if form.is_valid():
            scenario = form.save(commit=False)
            scenario.sensor = sensor
            scenario.save()
            messages.success(request, 'Scénario créé avec succès.')
            return redirect('sensor_detail', sensor_id=sensor.id)
    else:
        form = ScenarioForm()
   
    return render(request, 'sensors/scenario_form.html', {
        'form': form,
        'sensor': sensor
    })

def scenario_update(request, scenario_id):
    """Modifie un scénario existant"""
    scenario = get_object_or_404(Scenario, id=scenario_id)
   
    if request.method == 'POST':
        form = ScenarioForm(request.POST, instance=scenario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Scénario mis à jour avec succès.')
            return redirect('sensor_detail', sensor_id=scenario.sensor.id)
    else:
        form = ScenarioForm(instance=scenario)
   
    return render(request, 'sensors/scenario_form.html', {
        'form': form,
        'sensor': scenario.sensor
    })

def import_sensors(request):
    """Importe les capteurs depuis l'API Wattsense"""
    if request.method == 'POST':
        sensors_data = wattsense_api.get_sensors()
        counter = 0
       
        for sensor_data in sensors_data:
            # Adapter les champs selon la structure de l'API Wattsense
            try:
                sensor, created = Sensor.objects.update_or_create(
                    sensor_id=sensor_data.get('id'),
                    defaults={
                        'name': sensor_data.get('name', 'Sans nom'),
                        'location': sensor_data.get('location', 'Non spécifié'),
                        'sensor_type': determine_sensor_type(sensor_data.get('type', '')),
                        'unit': sensor_data.get('unit', ''),
                        'description': sensor_data.get('description', '')
                    }
                )
                if created:
                    counter += 1
            except Exception as e:
                print(f"Erreur lors de l'importation du capteur: {e}")
       
        messages.success(request, f'{counter} nouveaux capteurs importés.')
        return redirect('dashboard')
   
    return render(request, 'sensors/import_sensors.html')

def determine_sensor_type(type_string):
    """Détermine le type de capteur à partir de la chaîne fournie par l'API"""
    type_string = type_string.lower()
   
    if 'temp' in type_string:
        return 'temperature'
    elif 'humid' in type_string:
        return 'humidity'
    elif 'press' in type_string:
        return 'pressure'
    elif 'vol' in type_string:
        return 'volume'
    elif 'energy' in type_string or 'power' in type_string:
        return 'energy'
    elif 'status' in type_string or 'state' in type_string:
        return 'status'
    else:
        return 'other'
    
def fetch_data(request):
    """Vue pour déclencher manuellement la récupération des données"""
    if request.method == 'POST':
        from .tasks import fetch_sensor_data
        results = fetch_sensor_data()
       
        message = f"Données récupérées avec succès pour {results['success']} capteurs. "
        if results['errors'] > 0:
            message += f"{results['errors']} capteurs en erreur. "
        message += f"Total: {results['total_data_points']} points de données."
       
        messages.success(request, message)
        return redirect('dashboard')
   
    return render(request, 'sensors/fetch_data.html')


def admin_panel(request):
    """Panneau d'administration simplifié"""
    # Compter les objets dans la base de données
    sensors_count = Sensor.objects.count()
    data_points_count = SensorData.objects.count()
    scenarios_count = Scenario.objects.count()
   
    # Obtenir les derniers capteurs ajoutés
    recent_sensors = Sensor.objects.order_by('-id')[:5]
   
    # Obtenir les dernières données
    recent_data = SensorData.objects.select_related('sensor').order_by('-timestamp')[:10]
   
    context = {
        'sensors_count': sensors_count,
        'data_points_count': data_points_count,
        'scenarios_count': scenarios_count,
        'recent_sensors': recent_sensors,
        'recent_data': recent_data
    }
   
    return render(request, 'sensors/admin_panel.html', context)


def api_sensor_data(request, sensor_id):
    """API pour récupérer les données d'un capteur"""
    try:
        sensor = Sensor.objects.get(id=sensor_id)
       
        # Par défaut, récupérer les dernières 24 heures
        end_time = timezone.now()
        start_time = end_time - timedelta(days=1)
       
        # Permettre de spécifier une période différente
        period = request.GET.get('period', '24h')
        if period == '7d':
            start_time = end_time - timedelta(days=7)
        elif period == '30d':
            start_time = end_time - timedelta(days=30)
        elif period == 'custom':
            # Format attendu: YYYY-MM-DD
            custom_start = request.GET.get('start')
            custom_end = request.GET.get('end')
            if custom_start:
                try:
                    start_time = timezone.datetime.strptime(custom_start, '%Y-%m-%d')
                except ValueError:
                    pass
            if custom_end:
                try:
                    end_time = timezone.datetime.strptime(custom_end, '%Y-%m-%d')
                    # Aller jusqu'à la fin de la journée
                    end_time = end_time.replace(hour=23, minute=59, second=59)
                except ValueError:
                    pass
       
        # Récupérer les données
        data_points = SensorData.objects.filter(
            sensor=sensor,
            timestamp__gte=start_time,
            timestamp__lte=end_time
        ).order_by('timestamp')
       
        # Formater les données pour JSON
        data = [
            {
                'timestamp': point.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'value': point.value
            }
            for point in data_points
        ]
       
        return JsonResponse(data, safe=False)
    except Sensor.DoesNotExist:
        return JsonResponse({'error': 'Capteur non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_sensor_list(request):
    """API pour récupérer la liste des capteurs"""
    sensors = Sensor.objects.all()
    data = [
        {
            'id': sensor.id,
            'sensor_id': sensor.sensor_id,
            'name': sensor.name,
            'location': sensor.location,
            'sensor_type': sensor.sensor_type,
            'unit': sensor.unit
        }
        for sensor in sensors
    ]
    return JsonResponse(data, safe=False)
    
def scenario_delete(request, scenario_id):
    """Supprime un scénario"""
    scenario = get_object_or_404(Scenario, id=scenario_id)
    sensor_id = scenario.sensor.id
   
    if request.method == 'POST':
        scenario.delete()
        messages.success(request, 'Scénario supprimé avec succès.')
        return redirect('sensor_detail', sensor_id=sensor_id)
   
    return render(request, 'sensors/scenario_delete.html', {
        'scenario': scenario
    })
