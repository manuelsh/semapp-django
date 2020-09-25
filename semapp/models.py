from django.db import models

class Event(models.Model):
    event_type = models.CharField(
        max_length=10,
        choices=[
            ('view','view'),             # page view event
            ('submit','submit'),         # form submitted event
            ('process', 'process'),      # process done event (e.g. file created, process initiated)
            ('error', 'error')           # error event
        ],
        default='view',
    )
    time = models.DateTimeField()
    user_name = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    info = models.JSONField(blank=True, null=True)