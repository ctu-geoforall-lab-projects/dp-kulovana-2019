from django.urls import path, re_path
from . import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    re_path(r'user_change/(?P<pk>\d+)/$', views.ChangeUser.as_view(), name='user_change'),
    re_path(r'user_change/password/', views.ChangePassword.as_view(), name='password_change'),
]
