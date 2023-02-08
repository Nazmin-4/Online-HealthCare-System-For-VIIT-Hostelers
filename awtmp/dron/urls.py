from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name = "index"),
    path('logout', views.logout, name = "logout"),
    path('login', views.login, name = "login"),
    path('register', views.register, name = "register"),
    path('onlineprescription', views.onlineprescription, name = "onlineprescription"),
    path('contactus', views.contactus, name = "contactus"),
    path('doctors', views.doctors, name = "doctors"),
    path('pre', views.pre, name = "pre"),
    path('emergency', views.emergency, name = "emergency"),
    path('doclogin', views.doclogin, name = "doclogin"),
    path('docregister', views.docregister, name = "docregister"),
    path('udp',views.udp ,name = "udp"),
 
    ]