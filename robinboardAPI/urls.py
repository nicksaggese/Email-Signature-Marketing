"""robinboardAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from directory import urls as directory_urls
from campaigns import urls as campaigns_urls
from analytics import urls as analytics_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^directory/', include(directory_urls, namespace='directory')),
    url(r'^campaigns/', include(campaigns_urls, namespace='campaigns')),
    url(r'^analytics/', include(analytics_urls, namespace='analytics')),
]
