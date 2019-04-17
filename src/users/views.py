from django.shortcuts import render

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from web_console_project.ldap_sync import SyncDjangoLDAP as snc

import logging
logger = logging.getLogger('django')


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class ChangeUser(LoginRequiredMixin, generic.UpdateView):
    model = CustomUser

    form_class = CustomUserChangeForm
    success_url = reverse_lazy('home')
    template_name = 'user_change.html'

    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        # change user in Django
        edited_user = form.save(commit=False)
        edited_user.user = self.request.user
        edited_user.save()

        # change user in LDAP
        sn = snc(edited_user)
        sn.change_user(edited_user, form)

        return render(self.request,'home.html', {'userdata': edited_user})
