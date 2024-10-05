"""
URL configuration for memenator project.

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
from rest_framework.routers import DefaultRouter
from .views import MemeTemplateViewSet, MemeViewSet, surprise_me_meme


router = DefaultRouter()
router.register(r'templates', MemeTemplateViewSet)
router.register(r'memes', MemeViewSet)

urlpatterns = [
    path('', include(router.urls)),
        path('memes/surprise-me/', surprise_me_meme, name='surprise-me'),  
]
