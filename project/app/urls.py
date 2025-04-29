from django.urls import path, include
from app import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path("home/", chat_views.chatPage, name="chat-page"),

    # login-section
    path("", LoginView.as_view
         (template_name="app/LoginPage.htm"), name="login-user"),
    path("auth/logout/", LogoutView.as_view(), name="logout-user"),
]