from django.urls import path
from . import views

urlpatterns = [    

    path("viewCourier", views.viewCourier, name="viewCourier"),
    path("addCourier", views.addCourier, name="addCourier"),
    path("viewCourierOption", views.viewCourierOption, name="viewCourierOption"),
    path("addCourierOption", views.addCourierOption, name="addCourierOption"),
    
]