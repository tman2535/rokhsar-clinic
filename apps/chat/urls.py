from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("state/", views.state, name="state"),
    path("start/", views.start, name="start"),
    path("send/", views.send, name="send"),
    path("reset/", views.reset, name="reset"),
]
