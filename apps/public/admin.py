from django.contrib import admin

from apps.public.models import Menu
from django.contrib.auth.models import Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
