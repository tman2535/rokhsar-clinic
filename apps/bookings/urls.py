from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.form_page, name="form"),
    path("submit/", views.book, name="submit"),
    path("slots/", views.slots, name="slots"),
    path("done/<str:code>/", views.done, name="done"),
]
