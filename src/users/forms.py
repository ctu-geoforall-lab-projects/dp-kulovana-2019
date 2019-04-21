from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from web_console_project.ldap_sync import SyncDjangoLDAP as snc

import logging
logger = logging.getLogger('django')

class FieldsRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmailRequiredMixin, self).__init__(*args, **kwargs)

        # make first_name, last_name nad email fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['description'].required = False

class CustomUserCreationForm(FieldsRequiredMixin, UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'description')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            # save user to Django
            user.save()
            # save user to LDAP
            sn = snc(user)
            sn.save_user_sign_up(user)
        return user

class CustomUserChangeForm(FieldsRequiredMixin, UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'description')
