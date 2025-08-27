from django.contrib import admin
from .models import MasterConfig

@admin.register(MasterConfig)
class MasterConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description']
    search_fields = ['key']
