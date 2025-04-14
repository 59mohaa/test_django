from django.contrib import admin
from .models import Sensor, SensorData, Scenario

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'sensor_id', 'sensor_type', 'location')
    search_fields = ('name', 'sensor_id', 'location')
    list_filter = ('sensor_type',)

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'timestamp', 'value')
    list_filter = ('sensor', 'timestamp')
    date_hierarchy = 'timestamp'

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'sensor', 'condition_operator', 'condition_value', 'action_type', 'is_active')
    list_filter = ('is_active', 'action_type', 'sensor')
    search_fields = ('name', 'sensor__name')

# Register your models here.
