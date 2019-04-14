from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

import logging
logger = logging.getLogger('django')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name', 'email', 'description', 'is_superuser']
    list_filter = ['is_superuser', 'groups']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'description')}),
        (('Permissions'), {'fields': ('groups')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        form.save_m2m()
        super().save_model(request, obj, form, change)

        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        from web_console_project.ldap_sync import SyncDjangoLDAP as snc
        sn = snc(obj)
        if change:
            sn.change_user(obj, form)
        else:
            sn.save_user(obj, form)

admin.site.register(CustomUser, CustomUserAdmin)
