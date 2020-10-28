"""insta_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path

from promoting.views import FollowersCountChart, FollowingCountChart, stat, stat_all, daily_stat

urlpatterns = [
    path('charts/followers_count/', FollowersCountChart.as_view()),
    path('charts/following_count/', FollowingCountChart.as_view()),
    path('stat/', stat_all),
    path('daily/', daily_stat),
    path('stat/<str:ig_account>/', stat),
]
