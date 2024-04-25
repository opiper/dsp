from django.urls import path
from . import views

urlpatterns = [

    path("addStock", views.addStock, name="addStock"),
    path("deleteStock", views.deleteStock, name="deleteStock"),
    path("dispatchStock", views.dispatchStock, name="dispatchStock"),
    path("viewIndvChangesStock", views.viewIndvChangesStock, name="viewIndvChangesStock"),
    path("viewChangesStock", views.viewChangesStock, name="viewChangesStock"),
    path("viewDispatches", views.viewDispatches, name="viewDispatches"),
    path("adjustStock", views.adjustStock, name="adjustStock"),
    path("changeLocation", views.changeLocation, name="changeLocation"),
    path("uploadStock", views.uploadStock, name="uploadStock"),
    path("optimise", views.optimise, name="optimise"),

]