from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView

app_name="chat"
urlpatterns = [
    path("<str:to>/<str:room_id>/", chat_views.chatPage, name="chat-page"),
    path("", chat_views.save_message, name="save-message")

    # # login-section
    # path("auth/login/", LoginView.as_view
    #      (template_name="chat/LoginPage.html"), name="login-user"),
    # path("auth/logout/", LogoutView.as_view(), name="logout-user"),
]