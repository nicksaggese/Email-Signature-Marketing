from django.conf.urls import url
from . import views
# from django.contrib.auth.views import LoginView
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    url(r'^initialize/', views.initialize),
    # url(r'^login/', LoginView.as_view(template_name="login.html"),name="login"),
    # url(r'^login/', views.applogin,),
    # url(r'^logout/', views.applogout),
    url(r'^user/', views.user),
    url(r'^company/', views.company),
    url(r'^employee/' ,views.employee),
    url(r'^group/', views.group),
    url(r'^confirm-user/', views.confirmUser),
    url(r'^confirm-employee/', views.confirmEmployee),
    url(r'^forgot-password/',views.forgotPassword),
    # url(r'group-employees/' views.groupEmployees),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    # url(r'^create-shift/$', views.create_shift),
]
