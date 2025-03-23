from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_api, name='chat_api'),
    path('quiz/', views.quiz_api, name='quiz_api'),
    path('upload_pdf/', views.upload_pdf, name='upload_pdf'),
    path('equation/', views.get_equation, name='get_equation'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('summarize_pdf/', views.summarize_pdf, name='summarize_pdf'),
    path('', views.home, name='home'),
]