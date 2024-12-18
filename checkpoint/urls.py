"""
URL configuration for checkpoint project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.urls import re_path
from django.views.static import serve 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('profile/', include('userProfile.urls')),
    path('create-profile/', include('createUserProfile.urls')),
    path('game-search/',include('gamesearch.urls')),
    path('comments/', include('comments.urls')),
    path('events/', include('events.urls')),
    path('friends/', include('friends.urls', namespace='friends')),
    path('lists/', include('lists.urls')),
    path('chat/', include("chat.urls")),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]

