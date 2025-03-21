from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_api, name='chat_api'),
    path('quiz/', views.quiz_api, name='quiz_api'),
    path('', views.home, name='home'),
]