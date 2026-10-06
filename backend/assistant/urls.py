from django.urls import path
from .views import test_assistant

urlpatterns = [
    path("test/", test_assistant),
]