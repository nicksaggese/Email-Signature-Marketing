from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^billboard', views.billboard),
    url(r'pixel',views.trackingPixel)
]
