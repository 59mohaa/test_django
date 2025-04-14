from django import forms
from .models import Sensor, Scenario

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['name', 'location', 'sensor_type', 'unit', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'sensor_type': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['name', 'condition_operator', 'condition_value', 'action_type', 'action_details', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'condition_operator': forms.Select(attrs={'class': 'form-select'}),
            'condition_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'action_type': forms.Select(attrs={'class': 'form-select'}),
            'action_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }