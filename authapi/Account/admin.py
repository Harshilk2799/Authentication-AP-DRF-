from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(BaseUserAdmin):
    list_display = ["id", "first_name", "last_name", "email", "is_staff", "is_active"]
    list_filter = ["is_staff"]
    
    fieldsets = (
        ("User Credentials", {"fields": ("email", "password")}),
        ("Personal Info", {"fields":("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "first_name", "last_name","email", "password1", "password2"
            )}
        ),
    )

    search_fields = ("email",)
    ordering = ("email", "id")

admin.site.register(CustomUser, CustomUserAdmin)