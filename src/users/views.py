from django.shortcuts import render

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomUserChangeForm

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class ChangeUser(LoginRequiredMixin, generic.CreateView):
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('home')
    template_name = 'user_change.html'
    redirect_field_name = 'redirect_to'
