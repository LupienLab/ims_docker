from django.urls import path
from .views import login_view, logout_view, callback_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('auth/callback/', callback_view, name='keycloak_callback'),
]

