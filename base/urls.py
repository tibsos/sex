from django.urls import path

from .views import *

app_name = 'base'

urlpatterns = [

    path('', l, name = 'l'),
    path('test/', test, name = 'l'),

    path('plans/', plans, name = 'pl'),

    path('contact-us/', c, name = 'c'),
    path('c/', cs, name = 'cs'),

    path('terms/', t, name = 't'),
    path('privacy/', p, name = 'p'),
    path('juridical-information/', j, name = 'j'),
    path('data-safety/', ds, name = 'ds'),
    path('payment-safety/', ps, name = 'ps'),
    
    #path('online-payment-safety/', ops, name = 'ops'),
    #path('data-safety/', ds, name = 'ds'),

]