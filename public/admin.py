from django.contrib import admin

from public.models import ContactUs


# Register your models here.

@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'created_at')
    search_fields = ('name', 'mobile')
