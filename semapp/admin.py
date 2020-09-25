from django.contrib import admin
from django.contrib.sessions.models import Session
from .models import Event

class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']
    
admin.site.register(Session, SessionAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'time', 'user_name', 'origin', 'info']
admin.site.register(Event, EventAdmin)