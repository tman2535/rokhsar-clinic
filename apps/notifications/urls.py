from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("hooks/bot/<int:pk>/<str:secret>/", views.bot_webhook, name="bot_webhook"),
]
