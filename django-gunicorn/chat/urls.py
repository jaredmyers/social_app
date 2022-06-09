"""chat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from . import views

app_name = 'chat'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name="login"),
    path('index', views.index, name="index"),
    path('register', views.register, name="register"),
    path('home', views.home, name="home"),
    path('friendslist', views.friendslist, name="friendslist"),
    path('forum', views.forum, name="forum"),
    path('chat', views.chat, name="chat"),
    path('logout', views.logout, name="logout"),
    path('thread/<int:id>', views.thread, name="thread"),
    path("details/<str:username>", views.recommended_details, name="details"),
    path("room/<str:chat_recipient>", views.chatroom, name="chatroom"),
    path("sendchat", views.sendchat, name="sendchat"),
    path("getMessages/<str:room_id>", views.getMessages, name="getMessages")
]
