"""
URL configuration for email_client project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from email_client_app import views

urlpatterns = [
    path("", views.index, name="index"),
    path("inbox/", views.get_inbox, name="inbox"),
    path("sent/", views.get_sent, name="sent"),
    path("drafts/", views.get_drafts, name="drafts"),
    path("send_email/", views.send_email, name="send_email"),
    path("get_email_detail/", views.get_email_detail, name="get_email_detail"),
    path("save_draft/", views.save_draft, name="save_draft"),

    path("home/", views.home_view, name="home_view"),
    path("about/", views.about_view, name="about_view"),
]
