from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),
    path("logIn", views.logIn, name="logIn"),
    path("logOut", views.logOut, name="logOut"),
    path("signUp", views.signUp, name="signUp"),
    path("viewDailyOperations", views.viewDailyOperations, name="viewDailyOperations"),
    path("clearStock", views.clearStock, name="clearStock"),
    path("clearCompanies", views.clearCompanies, name="clearCompanies"),
    path("clearCouriers", views.clearCouriers, name="clearCouriers"),
    path("clearServices", views.clearServices, name="clearServices"),
    
]