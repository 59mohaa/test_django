from django.db import models







class Sensor(models.Model): 
    SENSOR_TYPES = (
        ('temperature', 'Température'),
        ('humidity', 'Humidité'),
        ('pressure', 'Pression'),
        ('volume', 'Volume'),
        ('energy', 'Energie'),
        ('status', 'Statut'),
        ('other', 'Others'),
    )

    sensor_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    unit = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.location})"
    





class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data_points')
    timestamp = models.DateTimeField()
    value = models.FloatField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.sensor.name}: {self.value} {self.sensor.unit} at {self.timestamp}"
    




class Scenario(models.Model):
    OPERATORS = (
        ('gt', 'Supérieur à'),
        ('lt', 'Inférieur à'),
        ('eq', 'Egal à'),
        ('neq', 'Différent de'),
        ('gte', 'Supérieur ou égal à'),
        ('lte', 'Inférieur ou égal à'),

    )

    ACTION_TYPES = (
        ('notification', 'Envoyer notification'),
        ('email', 'Envoyer email'),
        ('api_call', 'Appel API externe'),
        ('custom', 'Action personnalisée'),
    )

    name = models.CharField(max_length=100)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='scenarios')
    condition_operator = models.CharField(max_length=3, choices=OPERATORS)
    condition_value = models.FloatField()
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_details = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



# Create your models here.
