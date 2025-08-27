from django.contrib import admin
from .models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('project_id', 'title', 'author_name', 'category', 'created_on')
    search_fields = ('title', 'author_name', 'category', 'hashtags')
    list_filter = ('category', 'created_on')

# Register your models here.
