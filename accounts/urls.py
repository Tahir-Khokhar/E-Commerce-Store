from django.urls import path
from django.views.generic import RedirectView

from .views import register_view

app_name = 'accounts'

urlpatterns = [
    # Keeps /accounts/ working (optional)
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('register/', register_view, name='register'),
]



