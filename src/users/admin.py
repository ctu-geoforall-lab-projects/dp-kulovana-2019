from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAdminPasswordChangeForm
from .models import CustomUser
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from web_console_project.ldap_sync import SyncDjangoLDAP as snc

import logging
logger = logging.getLogger('django')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm

    # set of fields showed on creation form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'description', 'password1', 'password2')}
        ),
    )

    form = CustomUserChangeForm
    model = CustomUser
    change_password_form = CustomAdminPasswordChangeForm

    list_display = ['username', 'first_name', 'last_name', 'email', 'description', 'is_superuser']
    list_filter = ['is_superuser', 'groups']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'description')}),
        (('Permissions'), {'fields': ('groups', )}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # disable changing username after creation
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username', 'last_login', 'date_joined']
        else:
            return ['last_login', 'date_joined']

    # hide delete_selected option from actions (does not support delete users from LDAP right now)
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        """
        Saves user and its relations to Django.
        Changes user in LDAP if it changed, creates a new one otherwise.
        """

        logger.info('CustomUserAdmin save_model function')

        form.save_m2m()
        super().save_model(request, obj, form, change)

        # call ldap sync functions
        sn = snc(obj)
        if change:
            # change user in LDAP
            sn.change_user(obj, form)
        else:
            # add user into LDAP
            sn.save_user(obj, form.cleaned_data["password1"])

    def delete_model(self, request, obj):
        """Delete user and its relations from Django and LDAP."""

        logger.info('CustomUserAdmin delete_model function')

        # delete user and all its relations from LDAP
        sn = snc(obj)
        sn.delete_user(obj)

        # delete user from Django
        super().delete_model(request, obj)


class CustomGroupAdmin(GroupAdmin):
    list_display = ['name', ]
    fieldsets = ((None, {'fields': ('name', )}), )

    # disable changing name of a group
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["name", ]
        else:
            return []

    # hide delete_selected option from actions (does not support delete users from LDAP right now)
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        """Saves new group to Django and to LDAP."""

        logger.info('CustomGroupAdmin save_model function')

        super().save_model(request, obj, form, change)

        # call ldap sync functions
        sn = snc(obj)
        if not change:
            # add group into LDAP
            sn.save_group(obj, form)

    def delete_model(self, request, obj):
        """Delete group and its relations from Django and LDAP."""

        logger.info('CustomUserAdmin delete_model function')

        # delete group and all its relations from LDAP
        sn = snc(obj)
        sn.delete_group(obj)

        # delete group from Django
        super().delete_model(request, obj)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

admin.site.site_header = "GIS.lab Administration"
admin.site.site_title = "GIS.lab Admin Portal"
admin.site.index_title = "Welcome to GIS.lab Administration Portal"
