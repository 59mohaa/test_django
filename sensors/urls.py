from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sensor/<int:sensor_id>/', views.sensor_detail, name='sensor_detail'),
    path('sensor/<int:sensor_id>/scenario/create/', views.scenario_create, name='scenario_create'),
    path('scenario/<int:scenario_id>/update/', views.scenario_update, name='scenario_update'),
    path('import-sensors/', views.import_sensors, name='import_sensors'),
    path('fetch-data/', views.fetch_data, name='fetch_data'),
    path('admin-panel', views.admin_panel, name='admin_panel'),
    path('api/sensors/', views.api_sensor_list, name='api_sensor_list'),
    path('api/sensor/<int:sensor_id>/data/', views.api_sensor_data, name='api_sensor_data'),
    path('scenario/<int:scenario_id>/delete/', views.scenario_delete, name='scenario_delete'),
]