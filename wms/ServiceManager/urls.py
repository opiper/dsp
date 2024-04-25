from django.urls import path
from . import views

urlpatterns = [

    path("viewServices", views.viewServices, name="viewServices"),
    path("labelChange", views.labelChange, name="labelChange"),
    path("assorting", views.assorting, name="assorting"),
    path("changeCard", views.changeCard, name="changeCard"),
    path("clearance", views.clearance, name="clearance"),
    path("container", views.container, name="container"),
    path("destroy", views.destroy, name="destroy"),
    path("inspection", views.inspection, name="inspection"),
    path("photo", views.photo, name="photo"),
    path("viewServiceHistoryStock", views.viewServiceHistoryStock, name="viewServiceHistoryStock"),
    path("editServices", views.editServices, name="editServices"),
    path("addService", views.addService, name="addService"),

]