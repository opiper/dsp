from django.urls import path
from . import views

urlpatterns = [

    path("viewCompany", views.viewCompany, name="viewCompany"),
    path("editCompany", views.editCompany, name="editCompany"),
    path("viewIndvCompany", views.viewIndvCompany, name="viewIndvCompany"),
    path("addCompany", views.addCompany, name="addCompany"),
    path("deleteCompany", views.deleteCompany, name="deleteCompany"),
    path("viewCompanyStock", views.viewCompanyStock, name="viewCompanyStock"),

]