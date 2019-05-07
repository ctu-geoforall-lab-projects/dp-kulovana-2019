from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, AdminPasswordChangeForm

from .models import CustomUser
from .ldap_sync import SyncDjangoLDAP

import logging
logger = logging.getLogger('django')


class FieldsRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(FieldsRequiredMixin, self).__init__(*args, **kwargs)

        # make first_name, last_name nad email fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['description'].required = False


class CustomUserCreationForm(FieldsRequiredMixin, UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'description')
        help_texts = {
            'first_name': 'Required.',
            'last_name': 'Required.',
            'email': 'Required.'
        }

    def save(self, commit=True):
        """Saves new user into Django and LDAP."""

        logger.info('CustomUserCreationForm save function')

        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            # save user to Django
            user.save()

            # save user to LDAP
            sn = SyncDjangoLDAP()
            sn.save_user(user, self.cleaned_data["password1"])
            del sn

        return user


class CustomUserChangeForm(FieldsRequiredMixin, UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'description')


class CustomAdminPasswordChangeForm(AdminPasswordChangeForm):

    def save(self, commit=True):
        """Save the new password."""

        logger.info('CustomAdminPasswordChangeForm save function')

        password = self.cleaned_data["password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()

            # save new password to LDAP
            sn = SyncDjangoLDAP()
            sn.change_password(self.user, self.cleaned_data["password1"])
            del sn

        return self.user


class CustomPasswordChangeForm(PasswordChangeForm):

    def save(self, commit=True):
        """Save the new password."""

        logger.info('CustomPasswordChangeForm save function')

        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()

            # save new password to LDAP
            sn = SyncDjangoLDAP()
            sn.change_password(self.user, self.cleaned_data["new_password1"])
            del sn

        return self.user
