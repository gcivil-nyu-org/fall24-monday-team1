from django.urls import path
from . import views

app_name = "userProfile"
urlpatterns = [
    path('view/<int:user_id>/', views.viewProfile, name='viewProfile'),
]