from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('user_change/', views.ChangeUser.as_view(), name='user_change'),
]
