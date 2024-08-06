from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username',   'is_staff', 'server_id', 'donate_balance', 'job_lvl', 'language', 'telegram_id')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('telegram_id',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom info', {'fields': ('server_id', 'user_id', 'donate_balance', 'job_lvl', 'nickname', 'money', 'job', 'house', 'car', 'yacht', 'couple', 'language', 'username_tg')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'telegram_id'),
        }),
    )
    search_fields = ('username',  'telegram_id')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')

admin.site.register(CustomUser, CustomUserAdmin)
