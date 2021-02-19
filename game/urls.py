"""game URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from gamelinebot import views
from member_profile.views import member_profile

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^callback', views.callback),
    url('member_profile/',member_profile),
    url('^liff',views.liff), 
    url('^win1',views.win1),
    url('^win2',views.win2),
    url('^win3',views.win3),
    url('^win4',views.win4),
    url('^win5',views.win5),
    url('^bet',views.bet),
]

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)