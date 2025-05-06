from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("index/" , views.users_list , name='index'),
    path("home/", views.chatPage, name="chat-page"),
    path("", LoginView.as_view(template_name="app/LoginPage.htm"), name="login-user"),
    path("auth/logout/", LogoutView.as_view(), name="logout-user"),
    path("chat/<int:user_id>/", views.private_chat_view, name="private-chat"),

]
