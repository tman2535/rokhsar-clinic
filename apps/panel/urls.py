from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("pulse/", views.pulse, name="pulse"),
    path("appointments/", views.appointments, name="appointments"),
    path("appointments/export.csv", views.appointments_csv, name="appointments_csv"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("appointments/<int:pk>/status/", views.appointment_status, name="appointment_status"),
    path("chats/", views.chats, name="chats"),
    path("chats/<int:pk>/", views.chats, name="chat_detail"),
    path("chats/<int:pk>/api/", views.chat_api, name="chat_api"),
    path("chats/<int:pk>/toggle/", views.chat_toggle, name="chat_toggle"),
    path("settings/", views.settings_view, name="settings"),
    path("settings/channels/new/", views.channel_edit, name="channel_new"),
    path("settings/channels/<int:pk>/", views.channel_edit, name="channel_edit"),
    path("settings/channels/<int:pk>/test/", views.channel_test, name="channel_test"),
    path("settings/channels/<int:pk>/webhook/", views.channel_webhook, name="channel_webhook"),
    path("settings/channels/<int:pk>/delete/", views.channel_delete, name="channel_delete"),
]
