from django.urls import path

from . import views

app_name = "procedures"

urlpatterns = [
    path("", views.procedure_list, name="list"),
    path("results/", views.results, name="results"),
    path("<slug:slug>/", views.procedure_detail, name="detail"),
]
