from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, Permission

admin.site.register(Permission)
admin.site.register(Role)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "full_name", "role", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("بيانات إضافية", {"fields": ("full_name", "phone", "role", "assigned_centers")}),
    )
