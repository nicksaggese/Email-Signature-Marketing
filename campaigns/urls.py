from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^billboard/', views.billboard),
    url(r'^photo/',views.photo),
    url(r'^display/(?P<employee_url>[a-z,A-Z,0-9]+)$',views.display),
    url(r'^clickthrough/',views.clickthrough),
    url(r'^billboard-media/',views.billboardMedia),
    url(r'^billboard-photo/',views.billboardPhoto),
]
