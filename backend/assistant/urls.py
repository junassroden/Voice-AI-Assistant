from django.urls import path

from .views import chat, speak, test_assistant

urlpatterns = [
    path("test/", test_assistant, name="test_assistant"),
    path("chat/", chat, name="chat"),
    path("speak/", speak, name="speak"),
]