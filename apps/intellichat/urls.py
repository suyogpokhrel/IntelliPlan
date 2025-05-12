from django.urls import path
from . import views

app_name = 'intellichat'

urlpatterns = [
    path('', views.intellichat, name='intellichat'),
    path('message/', views.chat_message, name='message'),
] 